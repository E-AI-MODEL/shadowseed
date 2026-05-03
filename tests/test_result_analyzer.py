from pathlib import Path

from shadowseed.analysis.ssl45_result_analyzer import analyze_results
from shadowseed.benchmark.ssl45_benefit_suite import run_ssl45_benefit_suite
from shadowseed.benchmark.ssl45_false_positive_suite import run_ssl45_false_positive_suite
from shadowseed.benchmark.ssl45_gap_suite import run_ssl45_gap_suite
from shadowseed.benchmark.ssl45_model_benefit_suite import run_ssl45_model_benefit_suite


def test_result_analyzer_writes_report_json_and_charts(tmp_path: Path):
    results_dir = tmp_path / "results"
    output_dir = results_dir / "analysis"

    run_ssl45_gap_suite(
        "src/shadowseed/data/gap_test_suite_4_5.json",
        str(results_dir / "ssl45_gap_suite.json"),
    )
    run_ssl45_false_positive_suite(
        "src/shadowseed/data/gap_test_suite_false_positive_4_5.json",
        str(results_dir / "ssl45_false_positive_suite.json"),
    )
    run_ssl45_benefit_suite(
        "src/shadowseed/data/ssl45_benefit_suite.json",
        str(results_dir / "ssl45_benefit_suite.json"),
    )
    run_ssl45_model_benefit_suite(
        "src/shadowseed/data/ssl45_model_benefit_suite.json",
        str(results_dir / "ssl45_model_benefit_suite.json"),
        backend="fixture",
    )

    report = analyze_results(str(results_dir), str(output_dir))

    assert report.exists()
    assert (output_dir / "analysis_summary.json").exists()
    assert (output_dir / "coverage.svg").exists()
    assert (output_dir / "false_positive.svg").exists()
    assert "SSL 4.5 resultaatanalyse" in report.read_text(encoding="utf-8")
