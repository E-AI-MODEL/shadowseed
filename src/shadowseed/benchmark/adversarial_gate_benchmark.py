"""Dedicated adversarial Gate benchmark for SSL 4.5.

This benchmark isolates one question that used to be hidden inside the broader
false-positive controls: does the current Validation Gate block misleading seed
promotion better than weaker baseline promotion rules?

The suite is intentionally still deterministic and local. It is not yet a full
human-reviewed adversarial layer, but it does make three things explicit:

- contradiction-heavy cases where a lure candidate is already covered by the
  answer and therefore should not survive promotion;
- tempting but unsupported lure candidates that weaker baselines would still
  promote;
- casebook artifacts that make the blocked-vs-baseline contrast readable.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from shadowseed.benchmark.ssl45_false_positive_suite import evaluate_adversarial_candidate


def _casebook_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Adversarial Gate Casebook",
        "",
        "Deze casebook laat zien waar zwakkere promotieregels een lure-seed zouden doorlaten terwijl de huidige Gate die blokkeert.",
        "",
        "## Samenvatting",
        "",
        f"- Scenario's: {payload['summary']['scenario_count']}",
        f"- Adversarial candidates: {payload['summary']['candidate_count']}",
        f"- Trace-only promoties: {payload['summary']['trace_only_promoted_count']}",
        f"- Trace zonder contradictiecheck promoties: {payload['summary']['trace_without_contradiction_promoted_count']}",
        f"- Gate-promoties: {payload['summary']['gate_promoted_count']}",
        f"- Baseline-only blokkades: {payload['summary']['baseline_only_blocked_count']}",
        "",
    ]

    for scenario in payload["results"]:
        lines.extend(
            [
                f"## {scenario['scenario_id']} - {scenario['title']}",
                "",
                f"- Domein: {scenario['domain']}",
                f"- Type: {scenario['scenario_type']}",
                f"- Verwachte label: {scenario['expected_label']}",
                "",
            ]
        )
        for check in scenario["candidate_checks"]:
            lines.extend(
                [
                    f"### {check['candidate']}",
                    "",
                    f"- Contradiction detected: {check['contradiction_detected']}",
                    f"- Trace-only promoted: {check['trace_only_promoted']}",
                    f"- Trace zonder contradictiecheck promoted: {check['trace_without_contradiction_promoted']}",
                    f"- Current gate promoted: {check['current_gate_promoted']}",
                    f"- Current gate verdict: {check['current_gate_verdict']}",
                    "",
                ]
            )
    return "\n".join(lines) + "\n"


def run_adversarial_gate_benchmark(
    input_path: str,
    output_path: str,
    casebook_path: str | None = None,
) -> Path:
    suite = json.loads(Path(input_path).read_text(encoding="utf-8"))
    results = []
    candidate_count = 0
    trace_only_promoted_count = 0
    trace_without_contradiction_promoted_count = 0
    gate_promoted_count = 0
    gate_blocked_count = 0
    contradiction_case_count = 0
    no_contradiction_case_count = 0
    baseline_only_blocked_count = 0

    for scenario in suite["scenarios"]:
        candidate_checks = []
        for candidate in scenario["adversarial_candidates"]:
            check = evaluate_adversarial_candidate(candidate, scenario)
            candidate_count += 1
            trace_only_promoted_count += int(check["trace_only_promoted"])
            trace_without_contradiction_promoted_count += int(
                check["trace_without_contradiction_promoted"]
            )
            gate_promoted_count += int(check["current_gate_promoted"])
            gate_blocked_count += int(not check["current_gate_promoted"])
            contradiction_case_count += int(check["contradiction_detected"])
            no_contradiction_case_count += int(not check["contradiction_detected"])
            baseline_only_blocked_count += int(
                (check["trace_only_promoted"] or check["trace_without_contradiction_promoted"])
                and not check["current_gate_promoted"]
            )
            candidate_checks.append(check)

        results.append(
            {
                "scenario_id": scenario["id"],
                "title": scenario["title"],
                "domain": scenario["domain"],
                "scenario_type": scenario["scenario_type"],
                "expected_label": scenario.get("expected_label", "not_gap"),
                "candidate_checks": candidate_checks,
                "passed": all(not check["current_gate_promoted"] for check in candidate_checks),
            }
        )

    summary = {
        "suite_version": suite.get("version"),
        "scenario_count": len(suite["scenarios"]),
        "candidate_count": candidate_count,
        "trace_only_promoted_count": trace_only_promoted_count,
        "trace_without_contradiction_promoted_count": trace_without_contradiction_promoted_count,
        "gate_promoted_count": gate_promoted_count,
        "gate_blocked_count": gate_blocked_count,
        "contradiction_case_count": contradiction_case_count,
        "no_contradiction_case_count": no_contradiction_case_count,
        "baseline_only_blocked_count": baseline_only_blocked_count,
        "gate_block_rate": (gate_blocked_count / candidate_count) if candidate_count else 0.0,
        "gate_vs_trace_only_delta": trace_only_promoted_count - gate_promoted_count,
        "gate_vs_trace_without_contradiction_delta": (
            trace_without_contradiction_promoted_count - gate_promoted_count
        ),
        "passed": gate_promoted_count == 0 and baseline_only_blocked_count > 0,
        "interpretation": (
            "Positive deltas mean weaker baselines would promote lure seeds that the current Gate blocks in this deterministic scaffold."
        ),
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {"summary": summary, "results": results}
    output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    casebook_file = Path(casebook_path) if casebook_path else output.with_name("adversarial_gate_casebook.md")
    casebook_file.parent.mkdir(parents=True, exist_ok=True)
    casebook_file.write_text(_casebook_markdown(payload), encoding="utf-8")
    return output
