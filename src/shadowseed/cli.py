"""Command line interface for Shadow Seed Learning."""

from __future__ import annotations

import argparse

from shadowseed.benchmark.absencebench_local import run_local_absencebench
from shadowseed.benchmark.absencebench_runner import AbsenceBenchRunner
from shadowseed.benchmark.result_writer import ResultWriter
from shadowseed.benchmark.run_types import RunType


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="shadowseed")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare-absencebench")
    prepare.add_argument(
        "--output",
        default="absencebench/preparation_result.json",
        help="Relatief pad binnen benchmarks/results.",
    )

    local = subparsers.add_parser("run-local-absencebench")
    local.add_argument("--input", required=True, help="JSON-bestand met lokale scenario's.")
    local.add_argument(
        "--output",
        default="absencebench/local_result.json",
        help="Relatief pad binnen benchmarks/results.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "prepare-absencebench":
        bundle = AbsenceBenchRunner().build_execution_bundle(
            requested_run_type=RunType.PREPARATION.value
        )
        path = ResultWriter().write_payload(bundle.result, args.output)
        print(path)
        return 0

    if args.command == "run-local-absencebench":
        path = run_local_absencebench(args.input, args.output)
        print(path)
        return 0

    raise ValueError(f"Onbekend commando: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
