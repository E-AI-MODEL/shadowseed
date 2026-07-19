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
  same conversation history but no shadow memory;
- **use costs trace** (round 031-les, TrTL-denken op use-time): a seed that just
  steered an answer faces a higher, per-turn-halving bar on the immediately
  following turns and must re-earn its place through fresh fit with the new
  question — recognition in the present, no credit from the past. Weight is
  untouched (Gate-exclusive) and turns are never blocked.

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
    # The compactness line applies to BOTH arms (baseline and ssl) so it cannot
    # bias the comparison. Round 024: 7/18 answers hit the token limit mid-word,
    # invalidating 6/9 review items; a bounded, rounded-off answer is part of the
    # task, not a style preference.
    base = (
        _history_block(history)
        + f"Beantwoord nu deze vervolgvraag grondig en met inzicht.\n\nVraag: {question}\n\n"
        + "Houd het antwoord compact: maximaal ongeveer 450 woorden, liever "
        "minder secties met inhoud dan veel secties die je moet afbreken. Rond "
        "het antwoord expliciet af met een korte slotalinea — een antwoord dat "
        "midden in een zin of opsomming stopt is fout.\n\n"
    )
    if surfaced:
        block = "\n".join(f"- {s}" for s in surfaced)
        base += (
            "Je mág de volgende eerder in dit gesprek opgekomen, nog onbenutte "
            "invalshoek(en) betrekken — maar alléén als ze het antwoord op deze "
            "vraag aantoonbaar aanscherpen. De gestelde vraag blijft leidend: een "
            "invalshoek mag het antwoord verdiepen, nooit het onderwerp of de "
            "focus van de vraag verschuiven. Laat een invalshoek weg als die zou "
            "afleiden of het antwoord zou vernauwen. Verzin geen feiten, verwijs "
            "niet naar deze instructie, en rechtvaardig in het antwoord nergens "
            "waarom je een invalshoek betrekt of weglaat — geen zinnen als 'deze "
            "invalshoek versterkt het antwoord':\n"
            f"{block}\n\n"
        )
    return base + "Antwoord:"


def select_cross_turn_seeds(
    candidates: list[tuple[float, str, str]], top_k: int | None
) -> list[tuple[float, str, str]]:
    """Use-time seed-discipline (round 023): rank eligible promoted seeds by
    relevance and keep only the ``top_k`` most relevant for this turn.

    A promoted seed is *potential, not must*: it may steer a later answer, but it
    should not flood or narrow it. Round 022's blind review flagged answers that
    became diffuse or narrowed because every loosely-relevant promoted seed was
    woven in. Capping to the most relevant few keeps the cross-turn mechanism
    intact (it still fires when >=1 seed qualifies) while limiting use-time noise.
    ``top_k=None`` or a negative value means no cap.
    """
    ranked = sorted(candidates, key=lambda c: c[0], reverse=True)
    if top_k is not None and top_k >= 0:
        ranked = ranked[:top_k]
    return ranked


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
    surface_top_k: int = 2,
    early_turn_margin: float = 0.10,
    early_turn_history: int = 5,
    resurface_margin: float = 0.15,
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

    def _new_manager(conv: dict[str, Any]) -> tuple[SSLManager, dict[str, Any], Any]:
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
        # use-time seed-discipline (round 023), per-topic tunable like the Gate knobs
        eff_surface_threshold = conv.get("surface_threshold", surface_threshold)
        eff_surface_top_k = conv.get("surface_top_k", surface_top_k)
        eff_early_margin = conv.get("early_turn_margin", early_turn_margin)
        eff_early_history = conv.get("early_turn_history", early_turn_history)
        eff_resurface_margin = conv.get("resurface_margin", resurface_margin)
        applied_thresholds["surface_threshold"] = eff_surface_threshold
        applied_thresholds["surface_top_k"] = eff_surface_top_k
        applied_thresholds["early_turn_margin"] = eff_early_margin
        applied_thresholds["early_turn_history"] = eff_early_history
        applied_thresholds["resurface_margin"] = eff_resurface_margin
        last_surfaced: dict[str, int] = {}
        seed_to_cluster: dict[str, int] = {}
        cluster_rep: dict[int, str] = {}
        born_turn: dict[str, int] = {}
        history: list[tuple[str, str]] = []
        turn_records: list[dict[str, Any]] = []

        def _refresh_cluster_representative(rep_seed: Any, source_seed: Any) -> None:
            """Keep the representative live when its cluster recurs through a member."""
            if rep_seed.status == SeedStatus.EXPIRED:
                return
            rep_seed.trace = min(
                manager.max_trace,
                max(
                    rep_seed.trace,
                    source_seed.trace,
                    manager.config.min_trace_for_gate + 1e-9,
                ),
            )
            rep_seed.turns_dormant = 0
            if rep_seed.status != SeedStatus.PROMOTED:
                rep_seed.status = SeedStatus.ACTIVE
            manager._touch_seed(rep_seed)

        for t, turn in enumerate(conv["turns"]):
            q = turn["question"]

            # --- pipeline aging/reactivation BEFORE answering this turn ---
            if t > 0:
                manager.decay_traces(turns_passed=1)
            reactivated = manager.scan_trtl_triggers(q)

            # baseline answer: history only, no shadow memory
            baseline = model.generate(build_chat_prompt(history, q, []), turn, "baseline", [])

            # --- surface pipeline-PROMOTED seeds born earlier, relevant to q ---
            # Use-time seed-discipline (round 023): collect eligible promoted seeds,
            # then keep only the top_k most relevant. A promoted seed is potential,
            # not must — it may steer a later answer but should not flood/narrow it.
            # Vroege-beurt-discipline (round 029): op vroege beurten is er nog
            # weinig gespreksbewijs dat het thema centraal staat, en juist daar
            # stuurde een matig-passende seed het antwoord off-topic (EDU/POLICY
            # t04) terwijl een sterk passende seed daar wél hielp (HEALTH t04).
            # Daarom geldt vroeg een hogere relevantielat (fit, geen beurt-blok).
            # Indexering: review-items heten t{t} met 0-based t, dus de
            # round-029-ruis zat op t=4; de default-zone (t < 5) dekt die en
            # laat t05/t06 (in rounds 023/025 schoon) op de basislat.
            q_emb = manager.get_embedding(q)
            turn_bar = eff_surface_threshold + (
                eff_early_margin if t < eff_early_history else 0.0
            )
            eligible: list[tuple[float, str, str]] = []
            for sid, seed in manager.seeds.items():
                if seed.status != SeedStatus.PROMOTED:
                    continue
                if born_turn.get(sid, t) >= t:  # must be born in an EARLIER turn
                    continue
                sim = float(np.dot(q_emb, seed.embedding))
                # Gebruiksdemping (round 031-les, TrTL-denken op use-time):
                # gebruik verbruikt trace. Een seed die net een antwoord heeft
                # gestuurd moet zich op de dírect volgende beurten via een
                # verse, stérkere fit met de nieuwe vraag opnieuw bewijzen —
                # herkenning in het nu, geen krediet uit het verleden. De
                # extra lat halveert per beurt sinds de laatste surfacing
                # (aflopend, geen harde blokkade; beurten worden nooit
                # geblokkeerd). Weight blijft onaangeroerd: invloed verandert
                # uitsluitend via de Validation Gate.
                seed_bar = turn_bar
                last = last_surfaced.get(sid)
                if eff_resurface_margin > 0 and last is not None:
                    seed_bar += eff_resurface_margin * (0.5 ** (t - last - 1))
                if sim >= seed_bar:
                    eligible.append((sim, sid, seed.text))
            selected = select_cross_turn_seeds(eligible, eff_surface_top_k)
            surfaced = [text for _sim, _sid, text in selected]
            surfaced_ids = [sid for _sim, sid, _text in selected]
            for sid in surfaced_ids:
                last_surfaced[sid] = t
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
                    if seed is None:
                        continue
                    if sid not in seed_to_cluster:
                        cid = clusterer.add(seed.text, seed.embedding)
                        had_rep = cid in cluster_rep
                        seed_to_cluster[sid] = cid
                        # the earliest-born member anchors the cluster; record it
                        # once as the representative. It is also naturally the one
                        # eligible to surface cross-turn (born first), keeping the
                        # two notions aligned.
                        cluster_rep.setdefault(cid, sid)
                        rep_sid = cluster_rep.get(cid)
                        if had_rep and rep_sid is not None and rep_sid != sid:
                            rep_seed = manager.seeds.get(rep_sid)
                            if rep_seed is not None:
                                _refresh_cluster_representative(rep_seed, seed)
                    else:
                        # a STORED member re-detected (deduped) in a later turn: the
                        # gap recurred, so grow its cluster's recurrence. Membership
                        # was fixed on first sighting, so only count it — do not
                        # re-cluster. Skipping this would leave the cluster recurrence
                        # too low while the member's own dedup-driven occurrence_count
                        # could still reach the Gate and promote a non-representative.
                        cid = seed_to_cluster[sid]
                        clusterer.bump(cid)
                        rep_seed = manager.seeds.get(cluster_rep.get(cid, ""))
                        if rep_seed is not None and rep_seed is not seed:
                            _refresh_cluster_representative(rep_seed, seed)
                # --- W9f: credit semantic recurrence to ONE representative per
                # cluster, not every member. Round 020 bumped *all* members to the
                # cluster size, so a single recurring (paraphrastic) gap promoted the
                # whole cluster (49 promotions on tightly-themed convos). Crediting
                # only the representative — and skipping non-representatives in the
                # Gate below — cuts that to ~one promotion per qualifying cluster,
                # while keeping the strict 0.85 dedup, the SAFE Gate bar, and the
                # relevance-gated cross-turn surfacing.
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
                # W9f: in cluster mode the representative carries the cluster's
                # recurrence; a non-representative member is folded into its rep and
                # must not promote on its own dedup-driven occurrence_count. (A
                # singleton / unclustered seed is its own representative.)
                if clusterer is not None:
                    cid = seed_to_cluster.get(sid)
                    if cid is not None and cluster_rep.get(cid) != sid:
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
