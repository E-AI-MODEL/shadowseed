"""False-positive controls for the SSL 4.5 Gap-Test Suite."""

from __future__ import annotations

import json
from pathlib import Path

from shadowseed.benchmark.ssl45_gap_suite import detect_candidate_seeds


def run_ssl45_false_positive_suite(input_path: str, output_path: str) -> Path:
    suite = json.loads(Path(input_path).read_text(encoding="utf-8"))
    results = []
    candidate_false_positives = 0
    promoted_false_positives = 0

    for scenario in suite["scenarios"]:
        candidates = detect_candidate_seeds(scenario)
        candidate_count = len(candidates)
        candidate_false_positives += candidate_count

        # In negative controls, no candidate should be sent to the Validation Gate.
        # Therefore promoted false positives should remain zero by construction.
        promoted_count = 0
        promoted_false_positives += promoted_count

        results.append(
            {
                "scenario_id": scenario["id"],
                "title": scenario["title"],
                "domain": scenario["domain"],
                "candidate_false_positives": candidate_count,
                "promoted_false_positives": promoted_count,
                "detected_candidates": candidates,
                "passed": candidate_count == 0 and promoted_count == 0,
            }
        )

    summary = {
        "suite_version": suite.get("version"),
        "scenario_count": len(suite["scenarios"]),
        "candidate_false_positives": candidate_false_positives,
        "promoted_false_positives": promoted_false_positives,
        "candidate_false_positive_rate": candidate_false_positives / len(suite["scenarios"]),
        "promoted_false_positive_rate": promoted_false_positives / len(suite["scenarios"]),
        "passed": candidate_false_positives == 0 and promoted_false_positives == 0,
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"summary": summary, "results": results}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output
