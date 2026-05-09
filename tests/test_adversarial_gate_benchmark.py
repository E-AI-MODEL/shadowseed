from __future__ import annotations

import json
from pathlib import Path

from shadowseed.analysis.ssl45_result_analyzer import analyze_results
from shadowseed.benchmark.adversarial_gate_benchmark import run_adversarial_gate_benchmark


DATA = "src/shadowseed/data/adversarial_gate_benchmark.json"


def test_adversarial_gate_benchmark_blocks_lures_and_writes_casebook(tmp_path: Path) -> None:
    output = tmp_path / "adversarial_gate.json"
    casebook = tmp_path / "adversarial_gate_casebook.md"
    run_adversarial_gate_benchmark(DATA, str(output), casebook_path=str(casebook))

    payload = json.loads(output.read_text(encoding="utf-8"))
    summary = payload["summary"]
    baseline_summaries = payload["baseline_summaries"]
    false_positive_log = payload["false_positive_log"]
    casebook_text = casebook.read_text(encoding="utf-8")

    assert summary["scenario_count"] == 5
    assert summary["candidate_count"] == 10
    assert summary["gate_promoted_count"] == 0
    assert summary["trace_only_promoted_count"] > 0
    assert summary["gate_vs_trace_only_delta"] > 0
    assert summary["baseline_only_blocked_count"] > 0
    assert summary["current_gate_false_promotion_rate"] == 0.0
    assert summary["trace_only_false_promotion_rate"] > 0.0
    assert summary["gate_relative_reduction_vs_trace_only"] > 0.0
    assert summary["passed"] is True

    assert baseline_summaries["current_gate"]["promoted_count"] == 0
    assert baseline_summaries["trace_only"]["promoted_count"] == summary["trace_only_promoted_count"]
    assert len(false_positive_log) == summary["candidate_count"]
    assert any(row["baseline_only_blocked"] for row in false_positive_log)

    assert "Adversarial Gate Casebook" in casebook_text
    assert "Trace-only promoted" in casebook_text
    assert "Gate reductie vs trace-only" in casebook_text


def test_analyze_results_includes_adversarial_gate_metrics(tmp_path: Path) -> None:
    results_dir = tmp_path / "results"
    output_dir = tmp_path / "analysis"
    results_dir.mkdir()

    adversarial_payload = {
        "summary": {
            "scenario_count": 2,
            "candidate_count": 4,
            "current_gate_false_promotion_rate": 0.0,
            "trace_only_false_promotion_rate": 0.5,
            "trace_without_contradiction_false_promotion_rate": 0.25,
            "gate_relative_reduction_vs_trace_only": 1.0,
            "gate_relative_reduction_vs_trace_without_contradiction": 1.0,
            "gate_vs_trace_only_delta": 2,
        },
        "baseline_summaries": {
            "current_gate": {"promoted_count": 0, "false_promotion_rate": 0.0},
            "trace_only": {"promoted_count": 2, "false_promotion_rate": 0.5},
            "trace_without_contradiction": {"promoted_count": 1, "false_promotion_rate": 0.25},
        },
        "false_positive_log": [],
        "results": [],
    }
    (results_dir / "adversarial_gate_benchmark.json").write_text(
        json.dumps(adversarial_payload, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    report_path = analyze_results(str(results_dir), str(output_dir))
    report_text = report_path.read_text(encoding="utf-8")
    summary_payload = json.loads((output_dir / "analysis_summary.json").read_text(encoding="utf-8"))

    assert summary_payload["adversarial_gate"]["current_gate_false_promotion_rate"] == 0.0
    assert summary_payload["conclusion"]["metrics"]["adversarial_trace_only_false_promotion_rate"] == 0.5
    assert "Adversarial Gate current FP rate" in report_text
    assert "Gate reductie vs trace-only" in report_text
    assert "De adversarial Gate-laag laat zien" in report_text


def test_analyze_results_includes_open_set_review_metrics(tmp_path: Path) -> None:
    results_dir = tmp_path / "results"
    output_dir = tmp_path / "analysis"
    results_dir.mkdir()

    open_set_payload = {
        "summary": {
            "packet_count": 6,
            "completed_packet_count": 6,
            "accepted_packet_count": 4,
            "rejected_packet_count": 2,
            "unique_seed_count": 3,
            "accepted_seed_count": 2,
            "rejected_seed_count": 1,
            "mixed_seed_count": 0,
            "pending_seed_count": 0,
            "seed_acceptance_rate": 0.6666666667,
            "seed_rejection_rate": 0.3333333333,
            "agreement_eligible_seed_count": 3,
            "unanimous_seed_count": 2,
            "unanimous_verdict_rate": 0.6666666667,
            "pairwise_decision_agreement_rate": 0.8333333333,
            "status": "review_complete",
        },
        "results": [],
    }
    (results_dir / "open_set_seed_review_summary.json").write_text(
        json.dumps(open_set_payload, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    report_path = analyze_results(str(results_dir), str(output_dir))
    report_text = report_path.read_text(encoding="utf-8")
    summary_payload = json.loads((output_dir / "analysis_summary.json").read_text(encoding="utf-8"))

    assert summary_payload["open_set_review"]["seed_acceptance_rate"] == open_set_payload["summary"]["seed_acceptance_rate"]
    assert summary_payload["conclusion"]["metrics"]["open_set_unanimous_verdict_rate"] == open_set_payload["summary"]["unanimous_verdict_rate"]
    assert "Open-set seed acceptance rate" in report_text
    assert "Open-set unanimous verdict rate" in report_text
    assert "## Open-set review" in report_text
    assert "reviewer-consensus" in report_text
