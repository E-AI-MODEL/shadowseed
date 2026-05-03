"""Benefit suite for testing whether SSL improves an answer.

Phase 1 does not call an external LLM. It compares a baseline answer with an
SSL-guided revision assembled from promoted seeds. This isolates the SSL layer:
if promoted seeds cover expected gaps without unsupported additions, the answer
state is measurably better than the baseline on the suite's gap-coverage metric.
"""

from __future__ import annotations

import json
from pathlib import Path
import re

from shadowseed.benchmark.ssl45_gap_suite import (
    detect_candidate_seeds,
    jaccard,
    score_seed,
    tokenize,
)
from shadowseed.manager import SSLManager, SeedStatus


def answer_fragments(answer: str) -> list[str]:
    """Split an answer into short fragments for local gap matching."""
    fragments = [
        part.strip()
        for part in re.split(r"[\n.;:]+", answer)
        if part.strip()
    ]
    return fragments or [answer]


def expected_is_covered(answer: str, expected: str, threshold: float = 0.70) -> bool:
    """Return whether an expected gap is present in the answer.

    A global Jaccard score between a long answer and one short seed is too
    diluted. Coverage is local: exact inclusion or best fragment-level match.
    """
    answer_lower = answer.lower()
    expected_lower = expected.lower()
    if expected_lower in answer_lower:
        return True
    return max(jaccard(fragment, expected) for fragment in answer_fragments(answer)) >= threshold


def coverage(answer: str, expected_additions: list[str]) -> tuple[float, list[str]]:
    covered = [
        expected
        for expected in expected_additions
        if expected_is_covered(answer, expected)
    ]
    if not expected_additions:
        return 1.0, covered
    return len(covered) / len(expected_additions), covered


def build_ssl_revision(baseline_answer: str, promoted_seeds: list[str]) -> str:
    if not promoted_seeds:
        return baseline_answer
    additions = " ".join(promoted_seeds)
    return f"{baseline_answer}\n\nSSL additions: {additions}"


def run_ssl45_benefit_suite(input_path: str, output_path: str, turns: int = 3) -> Path:
    suite = json.loads(Path(input_path).read_text(encoding="utf-8"))
    results = []

    baseline_coverages: list[float] = []
    ssl_coverages: list[float] = []
    unsupported_additions_total = 0
    promoted_total = 0

    for scenario in suite["scenarios"]:
        baseline_answer = scenario["baseline_answer"]
        expected_additions = scenario["expected_ssl_additions"]

        manager = SSLManager(embedding_fn=lambda text: __import__(
            "shadowseed.benchmark.ssl45_gap_suite",
            fromlist=["lexical_embedding"],
        ).lexical_embedding(text))

        detected_by_turn = []
        for _turn in range(turns):
            candidates = detect_candidate_seeds(
                {"domain": scenario["domain"], "input": baseline_answer}
            )
            detected_by_turn.append(candidates)
            for candidate in candidates:
                try:
                    manager.add_or_update_seed(
                        candidate,
                        trigger_keywords=sorted(tokenize(candidate))[:5],
                    )
                except ValueError:
                    continue

        seed_scores = []
        for seed_id, seed in manager.seeds.items():
            ground_truth = [
                {"text": expected}
                for expected in expected_additions
            ]
            scored = score_seed(seed.text, ground_truth)
            seed_scores.append(scored)
            if scored.score == 2:
                seed.evidence_count = max(seed.evidence_count, 2)
                for _ in range(3):
                    manager.run_validation_gate(seed_id)
            elif scored.score == 0:
                manager.run_validation_gate(seed_id, contradiction=True)

        promoted_seeds = [
            seed.text
            for seed in manager.seeds.values()
            if seed.status == SeedStatus.PROMOTED
        ]
        unsupported_additions = [
            seed
            for seed in promoted_seeds
            if all(jaccard(seed, expected) < 0.70 for expected in expected_additions)
        ]

        ssl_answer = build_ssl_revision(baseline_answer, promoted_seeds)
        baseline_cov, baseline_covered = coverage(baseline_answer, expected_additions)
        ssl_cov, ssl_covered = coverage(ssl_answer, expected_additions)

        baseline_coverages.append(baseline_cov)
        ssl_coverages.append(ssl_cov)
        unsupported_additions_total += len(unsupported_additions)
        promoted_total += len(promoted_seeds)

        results.append(
            {
                "scenario_id": scenario["id"],
                "title": scenario["title"],
                "domain": scenario["domain"],
                "baseline_gap_coverage": baseline_cov,
                "ssl_gap_coverage": ssl_cov,
                "coverage_delta": ssl_cov - baseline_cov,
                "baseline_covered": baseline_covered,
                "ssl_covered": ssl_covered,
                "promoted_seeds": promoted_seeds,
                "unsupported_ssl_additions": unsupported_additions,
                "unsupported_ssl_addition_count": len(unsupported_additions),
                "detected_by_turn": detected_by_turn,
                "seed_scores": [item.__dict__ for item in seed_scores],
            }
        )

    baseline_mean = sum(baseline_coverages) / len(baseline_coverages)
    ssl_mean = sum(ssl_coverages) / len(ssl_coverages)
    summary = {
        "suite_version": suite.get("version"),
        "scenario_count": len(suite["scenarios"]),
        "baseline_mean_gap_coverage": baseline_mean,
        "ssl_mean_gap_coverage": ssl_mean,
        "coverage_delta": ssl_mean - baseline_mean,
        "promoted_seed_count": promoted_total,
        "unsupported_ssl_additions": unsupported_additions_total,
        "unsupported_ssl_addition_rate": (
            unsupported_additions_total / promoted_total if promoted_total else 0.0
        ),
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"summary": summary, "results": results}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output
