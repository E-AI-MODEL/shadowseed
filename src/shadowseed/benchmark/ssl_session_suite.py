"""SSL session suite (PvA W9) — test SSL through the REAL pipeline, multi-turn.

This replaces the earlier standalone payoff derivatives (wild/generative/
adversarial), which bypassed the manager entirely. Here a conversation is driven
through the actual ``SSLManager``:

- each turn the detector proposes gaps which are ingested as **weight-0 seeds**
  (``ingest_detection_candidates``); a recurring gap is deduped, bumping its
  occurrence_count (recurrence);
- recurrence grants evidence and the **Validation Gate** decides promotion
  (``run_validation_gate``) — only genuinely recurring, uncontradicted gaps reach
  PROMOTED;
- between turns ``decay_traces`` (TTL) ages seeds and ``scan_trtl_triggers``
  (TrTL) revives dormant ones the new turn re-recognises;
- only a **pipeline-PROMOTED seed born in an EARLIER turn**, still relevant to the
  current turn, may shape the SSL answer. The baseline is the same model with the
  same conversation history but no shadow memory.

The cross-turn payoff question: does a seed that earned promotion across the
conversation surface value at a later turn that the history-equipped baseline does
not re-derive? It can fail (a strong model re-derives from history); that is the
honest test. Topics author-chosen; seeds detector-produced; signal not proof.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from shadowseed.benchmark.embedding_backends import make_embedding_fn
from shadowseed.benchmark.open_set_model_detector import make_detector_backend
from shadowseed.benchmark.ssl45_model_benefit_suite import blind_order, make_backend, word_count
from shadowseed.manager import SSLManager, SeedStatus


def _history_block(history: list[tuple[str, str]]) -> str:
    if not history:
        return ""
    turns = "\n".join(f"Vraag: {q}\nAntwoord: {a}" for q, a in history)
    return f"Gesprek tot nu toe:\n{turns}\n\n"


def build_chat_prompt(history: list[tuple[str, str]], question: str, surfaced: list[str]) -> str:
    base = (
        _history_block(history)
        + f"Beantwoord nu deze vervolgvraag grondig en met inzicht.\n\nVraag: {question}\n\n"
    )
    if surfaced:
        block = "\n".join(f"- {s}" for s in surfaced)
        base += (
            "Betrek daarbij expliciet, op een natuurlijke manier, de volgende eerder "
            "in dit gesprek opgekomen maar nog onbenutte invalshoek(en); verzin geen "
            "feiten en verwijs niet naar deze instructie:\n"
            f"{block}\n\n"
        )
    return base + "Antwoord:"


def run_ssl_session(
    input_path: str,
    output_path: str,
    *,
    backend: str = "fixture",
    model_id: str | None = None,
    max_new_tokens: int = 400,
    embedding_backend: str = "lexical",
    embedding_model: str | None = None,
    surface_threshold: float = 0.30,
    max_seeds_per_turn: int = 5,
    dedup_threshold: float | None = None,
    min_occurrences: int | None = None,
    promotion_threshold: float | None = None,
    recurrence_mode: str = "pairwise",
    cluster_threshold: float | None = None,
    auto_calibrate: bool = False,
) -> Path:
    data = json.loads(Path(input_path).read_text(encoding="utf-8"))
    embed_fn, _dim = make_embedding_fn(embedding_backend, embedding_model)
    model = make_backend(backend=backend, model_id=model_id, max_new_tokens=max_new_tokens)
    detector = make_detector_backend(
        backend, model_id=model_id, max_new_tokens=max_new_tokens, prompt_variant="generative"
    )

    # Gate strictness — "how much is held back vs let through" — is topic-dependent
    # (maintainer note, 2026-06-21). So thresholds are tunable at TWO levels, with
    # the global SSLCoreConfig doctrine defaults always intact:
    #   1. per-run: the dedup_threshold / min_occurrences / promotion_threshold args;
    #   2. per-topic: a conversation may carry its own overrides (same keys), which
    #      win over the run-level values. This lets a noisy topic hold more back and
    #      a sparse topic let more through.
    from dataclasses import replace as _replace

    from shadowseed.benchmark.recurrence_clustering import (
        DEFAULT_CLUSTER_THRESHOLD,
        RecurrenceClusterer,
        auto_calibrated_min_occurrences,
    )
    from shadowseed.core_config import SSLCoreConfig

    def _new_manager(conv: dict[str, Any]) -> tuple[SSLManager, dict[str, Any]]:
        d = conv.get("dedup_threshold", dedup_threshold)
        mo = conv.get("min_occurrences", min_occurrences)
        pt = conv.get("promotion_threshold", promotion_threshold)
        # per-topic auto-calibration of the recurrence bar (W9e), only when not set
        ac = conv.get("auto_calibrate", auto_calibrate)
        if mo is None and ac:
            mo = auto_calibrated_min_occurrences(len(conv.get("turns", [])))
        cfg = SSLCoreConfig()
        if mo is not None:
            cfg = _replace(cfg, min_occurrences_for_gate=mo)
        kwargs: dict[str, Any] = {"embedding_fn": embed_fn, "config": cfg}
        if d is not None:
            kwargs["dedup_threshold"] = d
        if pt is not None:
            kwargs["promotion_threshold"] = pt
        mode = conv.get("recurrence_mode", recurrence_mode)
        cth = conv.get("cluster_threshold", cluster_threshold)
        cth = cth if cth is not None else DEFAULT_CLUSTER_THRESHOLD
        applied = {
            "dedup_threshold": d if d is not None else "default(0.85)",
            "min_occurrences": mo if mo is not None else "default(3)",
            "promotion_threshold": pt if pt is not None else "default(0.5)",
            "recurrence_mode": mode,
            "cluster_threshold": cth if mode == "cluster" else None,
        }
        clusterer = RecurrenceClusterer(threshold=cth) if mode == "cluster" else None
        return SSLManager(**kwargs), applied, clusterer

    conversations: list[dict[str, Any]] = []
    blind_items: list[dict[str, Any]] = []
    blind_key: list[dict[str, Any]] = []
    cross_turn_events = 0

    for conv in data["conversations"]:
        manager, applied_thresholds, clusterer = _new_manager(conv)
        seed_to_cluster: dict[str, int] = {}
        cluster_rep: dict[int, str] = {}
        born_turn: dict[str, int] = {}
        history: list[tuple[str, str]] = []
        turn_records: list[dict[str, Any]] = []

        for t, turn in enumerate(conv["turns"]):
            q = turn["question"]

            # --- pipeline aging/reactivation BEFORE answering this turn ---
            if t > 0:
                manager.decay_traces(turns_passed=1)
            reactivated = manager.scan_trtl_triggers(q)

            # baseline answer: history only, no shadow memory
            baseline = model.generate(build_chat_prompt(history, q, []), turn, "baseline", [])

            # --- surface pipeline-PROMOTED seeds born earlier, relevant to q ---
            q_emb = manager.get_embedding(q)
            surfaced: list[str] = []
            surfaced_ids: list[str] = []
            for sid, seed in manager.seeds.items():
                if seed.status != SeedStatus.PROMOTED:
                    continue
                if born_turn.get(sid, t) >= t:  # must be born in an EARLIER turn
                    continue
                sim = float(np.dot(q_emb, seed.embedding))
                if sim >= surface_threshold:
                    surfaced.append(seed.text)
                    surfaced_ids.append(sid)
            if surfaced:
                cross_turn_events += 1
                ssl = model.generate(build_chat_prompt(history, q, surfaced), turn, "ssl", surfaced)
            else:
                ssl = baseline  # nothing the pipeline promoted from earlier -> do-no-harm

            # --- detect gaps in this turn's answer, ingest as weight-0 seeds ---
            candidates = detector.detect_seeds({"text": baseline}, max_seeds=max_seeds_per_turn)
            ingest = manager.ingest_detection_candidates(candidates)
            for acc in ingest.get("accepted", []):
                born_turn.setdefault(acc["seed_id"], t)

            # --- cluster-based recurrence (W9e): paraphrastic gaps count together,
            # so a seed's effective recurrence reflects its semantic cluster size.
            # This drives the SAFE-default Gate without loosening the strict 0.85
            # storage dedup. (Identity stays distinct; recurrence is semantic.)
            if clusterer is not None:
                for acc in ingest.get("accepted", []):
                    sid = acc["seed_id"]
                    seed = manager.seeds.get(sid)
                    if seed is not None and sid not in seed_to_cluster:
                        cid = clusterer.add(seed.text, seed.embedding)
                        seed_to_cluster[sid] = cid
                        # the earliest-born member anchors the cluster; record it once
                        # as the representative. It is also naturally the one eligible
                        # to surface cross-turn (born first), keeping the two notions
                        # aligned.
                        cluster_rep.setdefault(cid, sid)
                # --- W9f: credit semantic recurrence to ONE representative per
                # cluster, not every member. Round 020 bumped *all* members to the
                # cluster size, so a single recurring (paraphrastic) gap promoted the
                # whole cluster (49 promotions on tightly-themed convos). Crediting
                # only the representative cuts that to ~one promotion per qualifying
                # cluster, while keeping the strict 0.85 dedup, the SAFE Gate bar, and
                # the same cross-turn surfacing (surfacing is relevance-gated, not
                # volume-gated). Non-representative members keep their own (low)
                # occurrence_count and stay below the bar.
                for cid, rep_sid in cluster_rep.items():
                    if rep_sid in manager.seeds:
                        manager.seeds[rep_sid].occurrence_count = max(
                            manager.seeds[rep_sid].occurrence_count,
                            clusterer.recurrence(cid),
                        )

            # --- recurrence -> evidence -> Validation Gate ---
            promoted_now: list[str] = []
            for sid, seed in manager.seeds.items():
                if seed.status == SeedStatus.EXPIRED:
                    continue
                # recurrence (seen >1 time) is treated as confirming evidence
                ext = seed.occurrence_count >= 2
                verdict = manager.run_validation_gate(sid, external_evidence=ext)
                if verdict and seed.status == SeedStatus.PROMOTED:
                    promoted_now.append(seed.text)

            history.append((q, baseline))
            turn_records.append(
                {
                    "turn": t,
                    "question": q,
                    "reactivated_trtl": reactivated,
                    "detected_candidates": candidates,
                    "promoted_total": [
                        s.text for s in manager.seeds.values() if s.status == SeedStatus.PROMOTED
                    ],
                    "surfaced_cross_turn_seeds": surfaced,
                    "answer_length_delta_words": word_count(ssl) - word_count(baseline),
                    "baseline_answer": baseline,
                    "ssl_answer": ssl,
                    "is_cross_turn_payoff": bool(surfaced),
                }
            )

            if surfaced:
                rid = f"review_{conv['id']}_t{t}"
                first, second = blind_order(rid)
                amap = {"baseline": baseline, "ssl": ssl}
                blind_items.append(
                    {
                        "review_id": rid,
                        "scenario_id": f"{conv['id']}_t{t}",
                        "question": q,
                        "option_a": amap[first],
                        "option_b": amap[second],
                        "reviewer_instruction": (
                            "Beide antwoorden kennen het hele gesprek. Kies welk antwoord "
                            "rijker/inzichtelijker is. Een meegedragen invalshoek telt alleen "
                            "als die echt iets toevoegt; geforceerd of verzonnen = slechter."
                        ),
                        "scores_to_fill": {"better_answer": "A/B/tie", "notes": ""},
                    }
                )
                blind_key.append(
                    {"review_id": rid, "option_a_source": first, "option_b_source": second}
                )

        conversations.append(
            {
                "conversation_id": conv["id"],
                "domain": conv.get("domain", ""),
                "applied_thresholds": applied_thresholds,
                "turns": turn_records,
                "diagnostics": {
                    "total_candidates_detected": sum(
                        len(tr["detected_candidates"]) for tr in turn_records
                    ),
                    "distinct_seeds_created": len(manager.seeds),
                    "max_occurrence_count": max(
                        (s.occurrence_count for s in manager.seeds.values()), default=0
                    ),
                    "promoted_ever": sorted(
                        {txt for tr in turn_records for txt in tr["promoted_total"]}
                    ),
                    "status_counts": {
                        st.value: sum(1 for s in manager.seeds.values() if s.status == st)
                        for st in {s.status for s in manager.seeds.values()}
                    },
                },
                "final_constellations": [c.to_dict() for c in manager.find_constellations()],
            }
        )

    all_diag = [c["diagnostics"] for c in conversations]
    summary = {
        "artifact": "ssl_session_suite",
        "backend": getattr(model, "name", backend),
        "detector": getattr(detector, "name", backend),
        "embedding_backend": embedding_backend,
        "conversation_count": len(conversations),
        "cross_turn_payoff_events": cross_turn_events,
        "dedup_threshold": dedup_threshold if dedup_threshold is not None else "default(0.85)",
        "min_occurrences": min_occurrences if min_occurrences is not None else "default(3)",
        "diagnostics": {
            "total_candidates_detected": sum(d["total_candidates_detected"] for d in all_diag),
            "max_occurrence_count": max((d["max_occurrence_count"] for d in all_diag), default=0),
            "total_seeds_ever_promoted": sum(len(d["promoted_ever"]) for d in all_diag),
            "why_zero_hint": (
                "Als max_occurrence_count laag is (~1) recidiveren gaps niet genoeg om "
                "de Gate te halen (geen promotie -> geen cross-turn). Als er wel promoties "
                "zijn maar 0 events, promoveerden ze pas in de laatste beurt of niet relevant."
            ),
        },
        "interpretation": (
            "SSL through the REAL pipeline (manager: weight-0 seeding, recurrence "
            "dedup, Validation Gate across turns, TTL decay, TrTL reactivation). "
            "Only a pipeline-PROMOTED seed born in an earlier turn may shape a later "
            "answer; baseline has the same history without shadow memory. "
            "cross_turn_payoff_events = turns where such a seed surfaced. Blind A/B "
            "pairs exist only for those turns. Signal, not proof."
        ),
    }

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "summary": summary,
                "conversations": conversations,
                "blind_review_items": blind_items,
                "blind_answer_key": blind_key,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return out
