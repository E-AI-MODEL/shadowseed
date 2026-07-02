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
from shadowseed.benchmark.ssl45_model_benefit_suite import make_backend
from shadowseed.benchmark.ssl_session_suite import build_chat_prompt, select_cross_turn_seeds
from shadowseed.manager import SSLManager, SeedStatus
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

        answer = self.model.generate(
            build_chat_prompt(self.history, question, surfaced),
            {"question": question, "turn": t},
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
                    self.seed_to_cluster[sid] = cid
                    self.cluster_rep.setdefault(cid, sid)
                else:
                    self.clusterer.bump(self.seed_to_cluster[sid])
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
