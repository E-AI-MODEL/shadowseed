"""False-positive controls for the SSL 4.5 Gap-Test Suite.

This suite now does two things:

1. keep the original regression check: complete answers should not produce fresh
   gap candidates via the standard detector;
2. stress the Validation Gate with adversarial lure candidates and compare the
   Gate against weaker promotion rules.

That makes the negative controls useful as more than a smoke-test. They now
show whether the current Gate blocks misleading seeds that weaker baselines
would promote.
"""

from __future__ import annotations

import json
from pathlib import Path

from shadowseed.benchmark.ssl45_gap_suite import detect_candidate_seeds, lexical_embedding, tokenize
from shadowseed.manager import SSLManager, SeedStatus


ADVERSARIAL_LURES = {
    "geschiedenis en economie": [
        "Koloniaal kapitaal als financieringsbron voor Britse fabrieksinvesteringen.",
        "Koloniale katoen als grondstof voor de Britse textielindustrie.",
        "Goedkope koloniale grondstoffen als voorwaarde voor schaalvergroting van productie.",
    ],
    "recht en jurisdictie": [
        "Rechtsbevoegdheid bij een geschil tussen een Nederlandse consument en een Amerikaanse webwinkel.",
        "Toepasselijk recht bij een grensoverschrijdend consumentencontract.",
        "Afdwingbaarheid van EU-consumentenrecht tegenover een niet-EU retailer.",
    ],
    "IT en engineering": [
        "AVG-compliance bij verwerking van medische hartslagdata.",
        "Authenticatiestrategie voor toegang tot gezondheidsdata.",
        "Encryptie van medische data in rust en tijdens transport.",
    ],
}


def contradiction_from_complete_input(candidate: str, input_text: str) -> bool:
    """Heuristic contradiction check for negative controls.

    In these controls the candidate is treated as a false positive when the core
    concept is already explicit in the answer. This approximates the kind of
    contradiction or direct falsification signal the Gate should react to.
    """
    candidate_tokens = tokenize(candidate)
    input_tokens = tokenize(input_text)
    if not candidate_tokens:
        return False
    overlap = len(candidate_tokens & input_tokens) / len(candidate_tokens)
    return overlap >= 0.6


def trace_only_promotes(manager: SSLManager, seed_id: str) -> bool:
    seed = manager.get_seed(seed_id)
    return (
        seed.occurrence_count >= manager.config.min_occurrences_for_gate
        and seed.trace > manager.config.min_trace_for_gate
    )


def trace_without_contradiction_promotes(
    manager: SSLManager,
    seed_id: str,
    contradiction: bool,
) -> bool:
    seed = manager.get_seed(seed_id)
    return (
        seed.occurrence_count >= manager.config.min_occurrences_for_gate
        and seed.trace > manager.config.min_trace_for_gate
        and not contradiction
    )


def evaluate_adversarial_candidate(candidate: str, scenario: dict) -> dict:
    manager = SSLManager(embedding_fn=lexical_embedding)
    seed_id = None
    for _ in range(manager.config.min_occurrences_for_gate):
        seed_id = manager.add_or_update_seed(candidate, trigger_keywords=sorted(tokenize(candidate))[:5])
    assert seed_id is not None

    contradiction = contradiction_from_complete_input(candidate, scenario["input"])
    baseline_trace_only = trace_only_promotes(manager, seed_id)
    baseline_trace_without_contradiction = trace_without_contradiction_promotes(
        manager,
        seed_id,
        contradiction,
    )
    gate_result = manager.run_validation_gate_detailed(
        seed_id,
        external_evidence=False,
        contradiction=contradiction,
    )

    return {
        "candidate": candidate,
        "contradiction_detected": contradiction,
        "trace_only_promoted": baseline_trace_only,
        "trace_without_contradiction_promoted": baseline_trace_without_contradiction,
        "current_gate_promoted": gate_result.promoted,
        "current_gate_verdict": gate_result.verdict,
        "weight_after": gate_result.weight_after,
        "status_after": gate_result.status_after,
        "occurrence_count": gate_result.occurrence_count,
        "evidence_count": gate_result.evidence_count,
    }


def run_ssl45_false_positive_suite(input_path: str, output_path: str) -> Path:
    suite = json.loads(Path(input_path).read_text(encoding="utf-8"))
    results = []
    candidate_false_positives = 0
    promoted_false_positives = 0
    adversarial_candidate_count = 0
    baseline_trace_only_promotions = 0
    baseline_trace_without_contradiction_promotions = 0
    gate_promoted_false_positives = 0
    gate_blocked_false_positives = 0

    for scenario in suite["scenarios"]:
        strict_candidates = detect_candidate_seeds(scenario)
        candidate_count = len(strict_candidates)
        candidate_false_positives += candidate_count
        promoted_false_positives += 0

        lure_candidates = scenario.get("adversarial_candidates") or ADVERSARIAL_LURES.get(
            scenario["domain"],
            [],
        )
        adversarial_checks = [
            evaluate_adversarial_candidate(candidate, scenario)
            for candidate in lure_candidates
        ]
        adversarial_candidate_count += len(adversarial_checks)
        baseline_trace_only_promotions += sum(
            1 for row in adversarial_checks if row["trace_only_promoted"]
        )
        baseline_trace_without_contradiction_promotions += sum(
            1 for row in adversarial_checks if row["trace_without_contradiction_promoted"]
        )
        gate_promoted_false_positives += sum(
            1 for row in adversarial_checks if row["current_gate_promoted"]
        )
        gate_blocked_false_positives += sum(
            1 for row in adversarial_checks if not row["current_gate_promoted"]
        )

        results.append(
            {
                "scenario_id": scenario["id"],
                "title": scenario["title"],
                "domain": scenario["domain"],
                "candidate_false_positives": candidate_count,
                "promoted_false_positives": 0,
                "detected_candidates": strict_candidates,
                "adversarial_lure_candidates": lure_candidates,
                "adversarial_gate_checks": adversarial_checks,
                "passed": candidate_count == 0 and all(
                    not row["current_gate_promoted"] for row in adversarial_checks
                ),
            }
        )

    scenario_count = len(suite["scenarios"])
    summary = {
        "suite_version": suite.get("version"),
        "scenario_count": scenario_count,
        "candidate_false_positives": candidate_false_positives,
        "promoted_false_positives": promoted_false_positives,
        "candidate_false_positive_rate": candidate_false_positives / scenario_count,
        "promoted_false_positive_rate": promoted_false_positives / scenario_count,
        "adversarial_candidate_count": adversarial_candidate_count,
        "baseline_trace_only_promotions": baseline_trace_only_promotions,
        "baseline_trace_without_contradiction_promotions": baseline_trace_without_contradiction_promotions,
        "gate_promoted_false_positives": gate_promoted_false_positives,
        "gate_blocked_false_positives": gate_blocked_false_positives,
        "gate_block_rate_on_adversarial_candidates": (
            gate_blocked_false_positives / adversarial_candidate_count
            if adversarial_candidate_count
            else 0.0
        ),
        "gate_vs_trace_only_delta": baseline_trace_only_promotions - gate_promoted_false_positives,
        "gate_vs_trace_without_contradiction_delta": (
            baseline_trace_without_contradiction_promotions - gate_promoted_false_positives
        ),
        "passed": candidate_false_positives == 0 and gate_promoted_false_positives == 0,
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"summary": summary, "results": results}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output
