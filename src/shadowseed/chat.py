"""Living shadow layer: an interactive SSL chat session (vision item 5).

`docs/research/vision-generative-seeds.md` §6.5 names the missing piece: the
lifecycle is unit-tested and benchmark-harnessed (W9), but the "shadow" in
shadow seed never had an *operational* demonstration — a seed born in turn 1,
dormant in the shadow, revalidated in turn 3, steering only then. This module is
that demonstration: the same pipeline semantics as ``ssl_session_suite`` (W9e
cluster recurrence, W9f representative promotion, round-023 use-time
discipline), but driving a real conversation instead of a benchmark, with the
`shadowseed_agent` safety contract enforced at the influence boundary and a
replayable audit trail.

Doctrine, enforced in code rather than assumed:

- seeds are born weightless every turn (trace only);
- influence exists only after Validation Gate promotion, and the
  ``AgentSafetyContract`` re-checks that at use time (weight > 0, PROMOTED,
  logged promotion, no active contradiction);
- use-time discipline: a promoted seed is *potential, not must* — ranked, capped
  (``surface_top_k``) and woven only where it sharpens;
- falsification is user-driven (``/falsify``): a contradicted seed loses weight
  and the contract blocks it from then on;
- every attempted influence is recorded as an ``AgentInfluenceRecord``; audit
  replay (``/audit``) fails hard on any weightless influence.

This is an application demo on top of the validated mechanics, not a new
evidence layer. Claim boundaries in the research docs are unchanged.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

from shadowseed.benchmark.embedding_backends import make_embedding_fn
from shadowseed.benchmark.open_set_model_detector import make_detector_backend
from shadowseed.benchmark.recurrence_clustering import (
    DEFAULT_CLUSTER_THRESHOLD,
    RecurrenceClusterer,
)
from shadowseed.benchmark.seed_retrieval_probe import retrieval_probe_vs_question
from shadowseed.benchmark.ssl45_model_benefit_suite import make_backend
from shadowseed.benchmark.ssl_session_suite import build_chat_prompt, select_cross_turn_seeds
from shadowseed.manager import SSLManager, SeedStatus
from shadowseed.vectorstore.memory import InMemoryVectorStore
from shadowseed_agent import (
    AgentInfluenceRecord,
    AgentSafetyContract,
    InfluenceAction,
    assert_no_weightless_influence,
)


class ShadowChatSession:
    """One live conversation with a shadow layer of weightless seeds."""

    def __init__(
        self,
        *,
        backend: str = "fixture",
        model_id: str | None = None,
        max_new_tokens: int = 700,
        embedding_backend: str = "lexical",
        embedding_model: str | None = None,
        surface_threshold: float = 0.30,
        surface_top_k: int = 2,
        max_seeds_per_turn: int = 5,
        recurrence_mode: str = "cluster",
        cluster_threshold: float | None = None,
        contract: AgentSafetyContract | None = None,
        probe_corpus: str | None = None,
        probe_top_k: int = 3,
    ) -> None:
        embed_fn, _dim = make_embedding_fn(embedding_backend, embedding_model)
        self.model = make_backend(backend=backend, model_id=model_id, max_new_tokens=max_new_tokens)
        self.detector = make_detector_backend(
            backend, model_id=model_id, max_new_tokens=max_new_tokens, prompt_variant="generative"
        )
        self.manager = SSLManager(embedding_fn=embed_fn)
        self.contract = contract or AgentSafetyContract()
        self.surface_threshold = surface_threshold
        self.surface_top_k = surface_top_k
        self.max_seeds_per_turn = max_seeds_per_turn
        self.clusterer = (
            RecurrenceClusterer(threshold=cluster_threshold or DEFAULT_CLUSTER_THRESHOLD)
            if recurrence_mode == "cluster"
            else None
        )
        self.seed_to_cluster: dict[str, int] = {}
        self.cluster_rep: dict[int, str] = {}
        self.born_turn: dict[str, int] = {}
        self.history: list[tuple[str, str]] = []
        self.influence_records: list[AgentInfluenceRecord] = []
        self.turn_reports: list[dict[str, Any]] = []
        self._turn = 0
        # SSL->RAG bridge (vision item 2): promoted seeds probe this corpus so
        # the report can show what the seed finds that the question does not.
        self.probe_top_k = probe_top_k
        self.probe_store = self._load_probe_corpus(probe_corpus) if probe_corpus else None

    # -- doctrine boundary ---------------------------------------------------

    def _contract_filter(self, candidates: list[tuple[float, str, str]]) -> list[str]:
        """Re-check every candidate at use time; record each attempted influence."""
        surfaced: list[str] = []
        for _sim, sid, text in candidates:
            seed = self.manager.seeds[sid]
            decision = self.contract.decide(
                seed, InfluenceAction.ANSWER_MODIFICATION, self.manager.validation_log
            )
            self.influence_records.append(
                AgentInfluenceRecord(
                    seed_id=sid,
                    action=decision.action,
                    seed_weight=float(seed.weight),
                    seed_status=seed.status.value,
                    allowed=decision.allowed,
                    reason=decision.reason,
                )
            )
            if decision.allowed:
                surfaced.append(text)
        return surfaced

    def audit(self) -> int:
        """Replay all influence decisions; raise on any weightless influence."""
        assert_no_weightless_influence(self.influence_records)
        return len(self.influence_records)

    def _refresh_cluster_representative(self, rep_seed: Any, source_seed: Any) -> None:
        """Keep the representative live when its cluster recurs through a member.

        Mirrors ``ssl_session_suite``: only the representative is fed to the
        Gate, so without this a sparse-but-recurring theme grows cluster
        recurrence while the representative's trace decays below the Gate bar.
        """
        if rep_seed.status == SeedStatus.EXPIRED:
            return
        rep_seed.trace = min(
            self.manager.max_trace,
            max(
                rep_seed.trace,
                source_seed.trace,
                self.manager.config.min_trace_for_gate + 1e-9,
            ),
        )
        rep_seed.turns_dormant = 0
        if rep_seed.status != SeedStatus.PROMOTED:
            rep_seed.status = SeedStatus.ACTIVE
        self.manager._touch_seed(rep_seed)

    # -- SSL->RAG bridge (retrieval = presence, never steering) ----------------

    def _load_probe_corpus(self, path: str) -> InMemoryVectorStore:
        """Load a corpus into an in-memory store, embedded like the seeds.

        Accepts the repo retrieval-corpus schema (``documents[].chunks`` with
        ``chunk_id``, as indexed by ``index_retrieval_corpus``), a flat JSON
        list of ``{"id"|"chunk_id": ..., "text": ...}`` chunks (also under a
        top-level ``"chunks"`` key), or plain text split on blank lines.
        Raises when nothing indexes: an empty store must fail loudly, not probe
        silently against nothing.
        """
        raw = Path(path).read_text(encoding="utf-8")
        chunks: list[tuple[str, str, str | None]] = []  # (chunk_id, text, doc_id)
        if path.endswith(".json"):
            data = json.loads(raw)
            if isinstance(data, dict) and "documents" in data:
                items = [
                    {**chunk, "doc_id": doc.get("doc_id")}
                    for doc in data["documents"]
                    for chunk in doc.get("chunks", [])
                ]
            elif isinstance(data, dict):
                items = data.get("chunks", [])
            else:
                items = data
            for i, item in enumerate(items):
                text = str(item.get("text", "")).strip()
                if text:
                    chunk_id = str(item.get("chunk_id") or item.get("id") or f"chunk_{i:03d}")
                    chunks.append((chunk_id, text, item.get("doc_id")))
        else:
            for i, block in enumerate(p.strip() for p in raw.split("\n\n")):
                if block:
                    chunks.append((f"chunk_{i:03d}", block, None))
        if not chunks:
            raise ValueError(
                f"Probe-corpus '{path}' bevat geen indexeerbare chunks "
                "(verwacht: documents[].chunks, een JSON-lijst met 'text', of platte tekst)."
            )
        store = InMemoryVectorStore()
        for chunk_id, text, doc_id in chunks:
            store.add(
                chunk_id,
                self.manager.get_embedding(text),
                {"text": text, "chunk_id": chunk_id, "doc_id": doc_id},
            )
        return store

    def _run_retrieval_probe(self, question: str) -> dict[str, Any] | None:
        """Probe the corpus with promoted seeds; report presence, change nothing.

        Doctrine: what a seed *finds* is never *true* or *steering* — the hits go
        into the report only, never into the answer prompt, and probing mutates
        no seed state. When the manager sees a retrieval-grade constellation,
        its centroid is the query (the manager-centroid finally consumed);
        otherwise each promoted seed (representative only, in cluster mode)
        probes on its own.
        """
        if self.probe_store is None:
            return None
        seed_texts: list[str] = []
        for sid, seed in self.manager.seeds.items():
            if seed.status != SeedStatus.PROMOTED:
                continue
            if self.clusterer is not None:
                cid = self.seed_to_cluster.get(sid)
                if cid is not None and self.cluster_rep.get(cid) != sid:
                    continue
            seed_texts.append(seed.text)
        if not seed_texts:
            return None
        retrieval_consts = [
            c for c in self.manager.find_constellations() if c.probe_type == "retrieval"
        ]
        use_centroid = bool(retrieval_consts)
        if use_centroid:
            members = set(retrieval_consts[0].members)
            seed_texts = [
                self.manager.seeds[sid].text for sid in members if sid in self.manager.seeds
            ] or seed_texts
        res = retrieval_probe_vs_question(
            self.probe_store,
            question,
            seed_texts,
            top_k=self.probe_top_k,
            use_centroid=use_centroid,
            embed_fn=self.manager.get_embedding,
        )
        seed_only = set(res["seed_only_chunk_ids"])
        return {
            "use_centroid": res["use_centroid"],
            "probe_seed_texts": res["seed_texts"],
            "question_chunk_ids": res["question_chunk_ids"],
            "probe_chunk_ids": res["probe_chunk_ids"],
            "shared_chunk_ids": res["shared_chunk_ids"],
            "seed_only_chunk_ids": res["seed_only_chunk_ids"],
            "seed_only_hits": [h for h in res["probe_hits"] if h["chunk_id"] in seed_only],
        }

    # -- one live turn ---------------------------------------------------------

    def turn(self, question: str) -> dict[str, Any]:
        t = self._turn
        if t > 0:
            self.manager.decay_traces(turns_passed=1)
        reactivated = self.manager.scan_trtl_triggers(question)

        # candidate surfacing: pipeline-PROMOTED, born earlier, relevant now,
        # ranked + capped (round-023 use-time discipline)...
        q_emb = self.manager.get_embedding(question)
        eligible: list[tuple[float, str, str]] = []
        for sid, seed in self.manager.seeds.items():
            if seed.status != SeedStatus.PROMOTED:
                continue
            if self.born_turn.get(sid, t) >= t:
                continue
            sim = float(np.dot(q_emb, seed.embedding))
            if sim >= self.surface_threshold:
                eligible.append((sim, sid, seed.text))
        selected = select_cross_turn_seeds(eligible, self.surface_top_k)
        # ...and the safety contract re-checks each one at the influence boundary.
        surfaced = self._contract_filter(selected)

        # FixtureBackend echoes scenario["baseline_answer"] (real backends ignore
        # the scenario dict); a chat turn has no authored baseline, so give the
        # fixture a deterministic echo of the question. Without it the fixture
        # answers blank, the detector sees empty text and the demo never births
        # a seed.
        answer = self.model.generate(
            build_chat_prompt(self.history, question, surfaced),
            {
                "question": question,
                "turn": t,
                "baseline_answer": f"Antwoord (fixture-echo) op: {question}",
            },
            "chat",
            surfaced,
        )

        # detect gaps in the fresh answer; every candidate is born weightless
        candidates = self.detector.detect_seeds({"text": answer}, max_seeds=self.max_seeds_per_turn)
        ingest = self.manager.ingest_detection_candidates(candidates)
        born: list[str] = []
        for acc in ingest.get("accepted", []):
            self.born_turn.setdefault(acc["seed_id"], t)
            born.append(acc["seed_id"])

        # cluster recurrence (W9e) credited to the representative only (W9f)
        if self.clusterer is not None:
            for acc in ingest.get("accepted", []):
                sid = acc["seed_id"]
                seed = self.manager.seeds.get(sid)
                if seed is None:
                    continue
                if sid not in self.seed_to_cluster:
                    cid = self.clusterer.add(seed.text, seed.embedding)
                    had_rep = cid in self.cluster_rep
                    self.seed_to_cluster[sid] = cid
                    self.cluster_rep.setdefault(cid, sid)
                    rep_sid = self.cluster_rep.get(cid)
                    if had_rep and rep_sid is not None and rep_sid != sid:
                        rep_seed = self.manager.seeds.get(rep_sid)
                        if rep_seed is not None:
                            self._refresh_cluster_representative(rep_seed, seed)
                else:
                    cid = self.seed_to_cluster[sid]
                    self.clusterer.bump(cid)
                    rep_seed = self.manager.seeds.get(self.cluster_rep.get(cid, ""))
                    if rep_seed is not None and rep_seed is not seed:
                        self._refresh_cluster_representative(rep_seed, seed)
            for cid, rep_sid in self.cluster_rep.items():
                if rep_sid in self.manager.seeds:
                    self.manager.seeds[rep_sid].occurrence_count = max(
                        self.manager.seeds[rep_sid].occurrence_count,
                        self.clusterer.recurrence(cid),
                    )

        # recurrence -> evidence -> Validation Gate (skip non-reps in cluster mode)
        promoted_now: list[str] = []
        for sid, seed in list(self.manager.seeds.items()):
            if seed.status == SeedStatus.EXPIRED:
                continue
            if self.clusterer is not None:
                cid = self.seed_to_cluster.get(sid)
                if cid is not None and self.cluster_rep.get(cid) != sid:
                    continue
            ext = seed.occurrence_count >= 2
            verdict = self.manager.run_validation_gate(sid, external_evidence=ext)
            if verdict and seed.status == SeedStatus.PROMOTED:
                promoted_now.append(sid)

        self.history.append((question, answer))
        self._turn += 1
        report = {
            "turn": t,
            "question": question,
            "answer": answer,
            "surfaced_seeds": surfaced,
            "influence_decisions": [asdict(r) for r in self.influence_records[-len(selected) :]]
            if selected
            else [],
            "seeds_born_weightless": born,
            "promoted_this_turn": promoted_now,
            "reactivated_trtl": reactivated,
            "shadow_size": len(self.manager.seeds),
            "retrieval_probe": self._run_retrieval_probe(question),
        }
        self.turn_reports.append(report)
        return report

    # -- user-driven falsification (the dialectic, made operable) -------------

    def falsify(self, seed_id: str) -> dict[str, Any]:
        """User contradicts a seed: weight drops, trace decays, contract blocks it."""
        if seed_id not in self.manager.seeds:
            raise KeyError(f"Unknown seed id: {seed_id}")
        self.manager.run_validation_gate(seed_id, contradiction=True)
        seed = self.manager.seeds[seed_id]
        blocked = not self.contract.can_influence(
            seed, InfluenceAction.ANSWER_MODIFICATION, self.manager.validation_log
        )
        return {
            "seed_id": seed_id,
            "weight_after": seed.weight,
            "status_after": seed.status.value,
            "blocked_from_influence": blocked,
        }

    # -- introspection ---------------------------------------------------------

    def shadow_report(self) -> dict[str, Any]:
        seeds = []
        for sid, seed in self.manager.seeds.items():
            seeds.append(
                {
                    "id": sid,
                    "text": seed.text,
                    "weight": seed.weight,
                    "trace": round(seed.trace, 3),
                    "status": seed.status.value,
                    "occurrence_count": seed.occurrence_count,
                    "born_turn": self.born_turn.get(sid),
                }
            )
        return {
            "turns": self._turn,
            "seeds": seeds,
            "influence_records": [asdict(r) for r in self.influence_records],
        }

    def transcript(self) -> dict[str, Any]:
        return {
            "artifact": "shadow_chat_transcript",
            "doctrine": (
                "seeds born weightless; influence only via Gate promotion, re-checked "
                "by AgentSafetyContract at use time; potential-not-must surfacing "
                "(top_k cap); user-driven falsification; audited influence trail."
            ),
            "turn_reports": self.turn_reports,
            "shadow": self.shadow_report(),
        }


def run_chat(
    *,
    backend: str = "fixture",
    model_id: str | None = None,
    max_new_tokens: int = 700,
    embedding_backend: str = "lexical",
    embedding_model: str | None = None,
    surface_threshold: float = 0.30,
    surface_top_k: int = 2,
    recurrence_mode: str = "cluster",
    script_path: str | None = None,
    transcript_path: str | None = None,
    show_shadow: bool = False,
    probe_corpus: str | None = None,
    probe_top_k: int = 3,
) -> Path | None:
    """CLI entrypoint: interactive REPL, or scripted turns via --script."""
    session = ShadowChatSession(
        backend=backend,
        model_id=model_id,
        max_new_tokens=max_new_tokens,
        embedding_backend=embedding_backend,
        embedding_model=embedding_model,
        surface_threshold=surface_threshold,
        surface_top_k=surface_top_k,
        recurrence_mode=recurrence_mode,
        probe_corpus=probe_corpus,
        probe_top_k=probe_top_k,
    )

    def _emit(report: dict[str, Any]) -> None:
        print(f"\n[antwoord]\n{report['answer']}\n")
        if report["surfaced_seeds"]:
            print("[schaduw → antwoord] gevalideerde invalshoeken meegegeven:")
            for s in report["surfaced_seeds"]:
                print(f"  • {s}")
        if show_shadow:
            print(
                f"[schaduw] seeds: {report['shadow_size']} | geboren (gewichtloos): "
                f"{len(report['seeds_born_weightless'])} | promoties: "
                f"{len(report['promoted_this_turn'])} | TrTL-reactivaties: "
                f"{len(report['reactivated_trtl'])}"
            )
        probe = report.get("retrieval_probe")
        if probe and probe["seed_only_chunk_ids"]:
            print(
                "[probe] seed vindt wat de vraag niet vindt (aanwezigheid, geen sturing): "
                + ", ".join(probe["seed_only_chunk_ids"])
            )

    if script_path:
        lines = [
            line.strip()
            for line in Path(script_path).read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        for line in lines:
            print(f"\n>>> {line}")
            _emit(session.turn(line))
    else:  # pragma: no cover - interactive path
        print(
            "shadowseed chat — levende schaduwlaag. Commando's: /shadow, /audit, "
            "/falsify <seed_id>, /quit"
        )
        while True:
            try:
                line = input("\nvraag> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not line:
                continue
            if line in {"/quit", "/exit"}:
                break
            if line == "/shadow":
                print(json.dumps(session.shadow_report(), indent=2, ensure_ascii=False))
                continue
            if line == "/audit":
                count = session.audit()
                print(f"audit OK: {count} influence-decisions gerepeteerd, geen gewichtloze invloed.")
                continue
            if line.startswith("/falsify "):
                try:
                    print(json.dumps(session.falsify(line.split(None, 1)[1]), indent=2))
                except KeyError as exc:
                    print(str(exc))
                continue
            _emit(session.turn(line))

    session.audit()  # hard doctrine check before the transcript is written
    if transcript_path:
        out = Path(transcript_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(session.transcript(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"\ntranscript (incl. audit-trail) → {out}")
        return out
    return None
