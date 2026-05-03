import json
from pathlib import Path

from shadowseed.benchmark.ssl45_benefit_suite import run_ssl45_benefit_suite


def test_benefit_suite_improves_gap_coverage(tmp_path: Path):
    output = tmp_path / "benefit_results.json"

    run_ssl45_benefit_suite(
        "src/shadowseed/data/ssl45_benefit_suite.json",
        str(output),
        turns=3,
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    summary = payload["summary"]

    assert summary["baseline_mean_gap_coverage"] == 0.0
    assert summary["ssl_mean_gap_coverage"] == 1.0
    assert summary["coverage_delta"] == 1.0
    assert summary["unsupported_ssl_additions"] == 0
