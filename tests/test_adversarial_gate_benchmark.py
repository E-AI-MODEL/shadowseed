from __future__ import annotations

import json
from pathlib import Path

from shadowseed.benchmark.adversarial_gate_benchmark import run_adversarial_gate_benchmark


DATA = "src/shadowseed/data/adversarial_gate_benchmark.json"


def test_adversarial_gate_benchmark_blocks_lures_and_writes_casebook(tmp_path: Path) -> None:
    output = tmp_path / "adversarial_gate.json"
    casebook = tmp_path / "adversarial_gate_casebook.md"
    run_adversarial_gate_benchmark(DATA, str(output), casebook_path=str(casebook))

    payload = json.loads(output.read_text(encoding="utf-8"))
    summary = payload["summary"]
    casebook_text = casebook.read_text(encoding="utf-8")

    assert summary["scenario_count"] == 5
    assert summary["candidate_count"] == 10
    assert summary["gate_promoted_count"] == 0
    assert summary["trace_only_promoted_count"] > 0
    assert summary["gate_vs_trace_only_delta"] > 0
    assert summary["baseline_only_blocked_count"] > 0
    assert summary["passed"] is True
    assert "Adversarial Gate Casebook" in casebook_text
    assert "Trace-only promoted" in casebook_text
