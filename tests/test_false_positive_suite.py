import json
from pathlib import Path

from shadowseed.benchmark.ssl45_false_positive_suite import run_ssl45_false_positive_suite


def test_false_positive_suite_has_zero_promotions(tmp_path: Path):
    output = tmp_path / "false_positive_results.json"

    run_ssl45_false_positive_suite(
        "src/shadowseed/data/gap_test_suite_false_positive_4_5.json",
        str(output),
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    summary = payload["summary"]

    assert summary["candidate_false_positives"] == 0
    assert summary["promoted_false_positives"] == 0
    assert summary["passed"] is True
