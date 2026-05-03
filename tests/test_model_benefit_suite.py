import json
from pathlib import Path

from shadowseed.benchmark.ssl45_model_benefit_suite import run_ssl45_model_benefit_suite


def test_model_benefit_fixture_improves_gap_coverage(tmp_path: Path):
    output = tmp_path / "model_benefit_results.json"

    run_ssl45_model_benefit_suite(
        "src/shadowseed/data/ssl45_model_benefit_suite.json",
        str(output),
        turns=3,
        backend="fixture",
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    summary = payload["summary"]

    assert summary["backend"] == "fixture"
    assert summary["baseline_mean_gap_coverage"] < summary["ssl_mean_gap_coverage"]
    assert summary["coverage_delta"] > 0.0
    assert summary["unsupported_ssl_additions"] == 0
