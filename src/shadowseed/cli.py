"""Command line interface for Shadow Seed Learning."""

from __future__ import annotations

import argparse

from shadowseed.analysis.ssl45_result_analyzer import analyze_results
from shadowseed.benchmark.absencebench_local import run_local_absencebench
from shadowseed.benchmark.absencebench_runner import AbsenceBenchRunner
from shadowseed.benchmark.absencebench_hf import fetch_absencebench_sample
from shadowseed.benchmark.result_writer import ResultWriter
from shadowseed.benchmark.retrieval_benchmark import run_retrieval_benchmark
from shadowseed.benchmark.run_types import RunType
from shadowseed.benchmark.ssl45_benefit_suite import run_ssl45_benefit_suite
from shadowseed.benchmark.ssl45_false_positive_suite import run_ssl45_false_positive_suite
from shadowseed.benchmark.ssl45_gap_suite import run_ssl45_gap_suite
from shadowseed.benchmark.ssl45_model_benefit_suite import run_ssl45_model_benefit_suite
from shadowseed.benchmark.ssot_smoke import run_ssot_smoke
from shadowseed.benchmark.vectorstore_smoke import run_vectorstore_smoke


VECTOR_BACKENDS = ["memory", "faiss", "chroma"]


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

    model_benefit = subparsers.add_parser("run-model-benefit-suite")
    model_benefit.add_argument(
        "--input",
        default="src/shadowseed/data/ssl45_model_benefit_suite.json",
    )
    model_benefit.add_argument("--output", default="results/ssl45_model_benefit_suite.json")
    model_benefit.add_argument("--turns", type=int, default=3)
    model_benefit.add_argument(
        "--backend",
        choices=["fixture", "hf-transformers"],
        default="fixture",
    )
    model_benefit.add_argument("--model-id", default=None)
    model_benefit.add_argument("--max-new-tokens", type=int, default=220)

    vectorstore = subparsers.add_parser("run-vectorstore-smoke")
    vectorstore.add_argument("--output", default="results/vectorstore_smoke.json")
    vectorstore.add_argument("--backend", choices=VECTOR_BACKENDS, default="memory")

    ssot = subparsers.add_parser("run-ssot-smoke")
    ssot.add_argument("--output", default="results/ssot_smoke.json")
    ssot.add_argument("--backend", choices=VECTOR_BACKENDS, default="memory")

    retrieval = subparsers.add_parser("run-retrieval-benchmark")
    retrieval.add_argument("--input", default="src/shadowseed/data/retrieval_benchmark.json")
    retrieval.add_argument("--output", default="results/retrieval_benchmark.json")
    retrieval.add_argument("--backend", choices=VECTOR_BACKENDS, default="memory")
    retrieval.add_argument("--k", type=int, default=3)

    analyze = subparsers.add_parser("analyze-results")
    analyze.add_argument("--results-dir", default="results")
    analyze.add_argument("--output-dir", default="results/analysis")

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

    if args.command == "run-model-benefit-suite":
        path = run_ssl45_model_benefit_suite(
            args.input,
            args.output,
            turns=args.turns,
            backend=args.backend,
            model_id=args.model_id,
            max_new_tokens=args.max_new_tokens,
        )
        print(path)
        return 0

    if args.command == "run-vectorstore-smoke":
        path = run_vectorstore_smoke(args.output, backend=args.backend)
        print(path)
        return 0

    if args.command == "run-ssot-smoke":
        path = run_ssot_smoke(args.output, backend=args.backend)
        print(path)
        return 0

    if args.command == "run-retrieval-benchmark":
        path = run_retrieval_benchmark(
            args.input,
            args.output,
            backend=args.backend,
            k=args.k,
        )
        print(path)
        return 0

    if args.command == "analyze-results":
        path = analyze_results(args.results_dir, args.output_dir)
        print(path)
        return 0

    if args.command == "run-nlp-smoke":
        path = run_local_absencebench(args.input, args.output)
        print(path)
        return 0

    raise ValueError(f"Onbekend commando: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
