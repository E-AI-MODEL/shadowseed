"""Dispatch benchmark scans, readiness checks, and future live runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from shadowseed.benchmark.absencebench_runner import AbsenceBenchRunner
from shadowseed.benchmark.run_types import RunType



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run benchmarkscan of readinesscontrole voor Shadow Seed Learning."
    )
    parser.add_argument(
        "--benchmark",
        default="absencebench",
        choices=["absencebench"],
        help="Te gebruiken benchmark.",
    )
    parser.add_argument(
        "--run-type",
        default=RunType.PREPARATION.value,
        choices=[item.value for item in RunType],
        help="Aangevraagde benchmarkmodus.",
    )
    parser.add_argument(
        "--output",
        default="runs/benchmark/latest.json",
        help="Pad voor de gebundelde benchmarkuitkomst.",
    )
    return parser.parse_args()



def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.benchmark != "absencebench":
        raise ValueError("Alleen AbsenceBench is in fase 3 operationeel gemodelleerd.")

    bundle = AbsenceBenchRunner().build_execution_bundle(
        requested_run_type=args.run_type
    ).to_dict()

    output_path.write_text(
        json.dumps(bundle, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Benchmarkuitkomst geschreven naar: {output_path}")
    print("Executionstatus:", bundle["decision"]["execution_status"])
    print("Run type:", bundle["decision"]["run_type"])


if __name__ == "__main__":
    main()
