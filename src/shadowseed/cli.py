"""Command line interface for Shadow Seed Learning."""

from __future__ import annotations

import argparse

from shadowseed.benchmark.absencebench_local import run_local_absencebench
from shadowseed.benchmark.absencebench_runner import AbsenceBenchRunner
from shadowseed.benchmark.absencebench_hf import fetch_absencebench_sample
from shadowseed.benchmark.result_writer import ResultWriter
from shadowseed.benchmark.run_types import RunType
from shadowseed.benchmark.ssl45_benefit_suite import run_ssl45_benefit_suite
from shadowseed.benchmark.ssl45_false_positive_suite import run_ssl45_false_positive_suite
from shadowseed.benchmark.ssl45_gap_suite import run_ssl45_gap_suite


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

    hf = subparsers.add_parser("fetch-absencebench")
    hf.add_argument("--output", default="data/absencebench_sample.json")
    hf.add_argument("--limit", type=int, default=10)

    ssl = subparsers.add_parser("run-gap-suite")
    ssl.add_argument("--input", default="src/shadowseed/data/gap_test_suite_4_5.json")
    ssl.add_argument("--output", default="results/ssl45_gap_suite.json")
    ssl.add_argument("--turns", type=int, default=3)

    fp = subparsers.add_parser("run-false-positive-suite")
    fp.add_argument(
        "--input",
        default="src/shadowseed/data/gap_test_suite_false_positive_4_5.json",
    )
    fp.add_argument("--output", default="results/ssl45_false_positive_suite.json")

    benefit = subparsers.add_parser("run-benefit-suite")
    benefit.add_argument(
        "--input",
        default="src/shadowseed/data/ssl45_benefit_suite.json",
    )
    benefit.add_argument("--output", default="results/ssl45_benefit_suite.json")
    benefit.add_argument("--turns", type=int, default=3)

    nlp = subparsers.add_parser("run-nlp-smoke")
    nlp.add_argument("--input", default="examples/local_absencebench_sample.json")
    nlp.add_argument("--output", default="results/absencebench_smoke.json")

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

    if args.command == "fetch-absencebench":
        path = fetch_absencebench_sample(args.output, limit=args.limit)
        print(path)
        return 0

    if args.command == "run-gap-suite":
        path = run_ssl45_gap_suite(args.input, args.output, turns=args.turns)
        print(path)
        return 0

    if args.command == "run-false-positive-suite":
        path = run_ssl45_false_positive_suite(args.input, args.output)
        print(path)
        return 0

    if args.command == "run-benefit-suite":
        path = run_ssl45_benefit_suite(args.input, args.output, turns=args.turns)
        print(path)
        return 0

    if args.command == "run-nlp-smoke":
        path = run_local_absencebench(args.input, args.output)
        print(path)
        return 0

    raise ValueError(f"Onbekend commando: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
