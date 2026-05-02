"""Create reproducible AbsenceBench preparation outputs for Shadow Seed Learning."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from shadowseed.benchmark.absencebench import build_preparation_record, build_run_card
from shadowseed.benchmark.result_writer import ResultWriter
from shadowseed.benchmark.run_types import ExecutionStatus, RunType
from shadowseed.benchmark.schemas import BenchmarkResult


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Maak reproduceerbare voorbereidingsartefacten voor AbsenceBench."
    )
    parser.add_argument(
        "--output",
        default="runs/absencebench/preparation.json",
        help="Pad naar het JSON-bestand voor de voorbereidingsstatus.",
    )
    parser.add_argument(
        "--result-output",
        default="absencebench/preparation_result.json",
        help="Relatief pad binnen benchmarks/results voor het resultaatschema-bestand.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    record = build_preparation_record()
    run_card = build_run_card().to_dict()

    output_path.write_text(
        json.dumps({"preparation": record, "run_card": run_card}, indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )

    writer = ResultWriter(root=REPO_ROOT / "benchmarks" / "results")
    result = BenchmarkResult(
        benchmark_name="AbsenceBench",
        run_type=RunType.PREPARATION.value,
        execution_status=ExecutionStatus.PREPARATION.value,
        ssl_input_basis=record["ssl_sources"],
        host_platform=run_card["host_platform"],
        dataset_status=record["dataset_status"],
        runner_status=record["runner_status"],
        score=None,
        score_type=record["score_type"],
        interpretation="Voorbereidingsrecord zonder live benchmarkscore of geverifieerde runner.",
        limitations=record["missing_components"],
        execution_gap=True,
    )
    result_path = writer.write_result(result, args.result_output)

    print(f"AbsenceBench voorbereidingsrecord geschreven naar: {output_path}")
    print(f"AbsenceBench resultaatschema-bestand geschreven naar: {result_path}")
    print("Executionstatus:", record["execution_status"])
    print("Execution-gap aanwezig:", "ja" if record["execution_gap_aanwezig"] else "nee")


if __name__ == "__main__":
    main()
