"""Command line interface for Shadow Seed Learning."""

from __future__ import annotations

import argparse

from shadowseed.cli_dispatch import execute_command


VECTOR_BACKENDS = ["memory", "faiss", "chroma"]
MODEL_BACKENDS = ["fixture", "hf-transformers"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shadowseed",
        description=(
            "CLI voor Shadow Seed Learning 4.5.\n"
            "Standaard regressie- en smoke-routes leven naast handmatige research-routes.\n"
            "Legacy command aliases blijven voorlopig ondersteund voor compatibiliteit."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser(
        "prepare-absencebench-bundle",
        aliases=["prepare-absencebench"],
        help="[absencebench] bouw een preparation bundle",
    )
    prepare.set_defaults(command="prepare-absencebench-bundle")
    prepare.add_argument(
        "--output",
        default="absencebench/preparation_result.json",
        help="Relatief pad binnen benchmarks/results.",
    )

    local = subparsers.add_parser(
        "run-absencebench-local",
        aliases=["run-local-absencebench"],
        help="[absencebench] draai een lokale AbsenceBench-run",
    )
    local.set_defaults(command="run-absencebench-local")
    local.add_argument("--input", required=True, help="JSON-bestand met lokale scenario's.")
    local.add_argument(
        "--output",
        default="absencebench/local_result.json",
        help="Relatief pad binnen benchmarks/results.",
    )

    hf = subparsers.add_parser(
        "fetch-absencebench-sample",
        aliases=["fetch-absencebench"],
        help="[absencebench] haal een sample op voor lokale inspectie",
    )
    hf.set_defaults(command="fetch-absencebench-sample")
    hf.add_argument("--output", default="data/absencebench_sample.json")
    hf.add_argument("--limit", type=int, default=10)

    ssl = subparsers.add_parser(
        "run-gap-suite",
        help="[standard] regressiesuite voor bekende SSL-gaps",
    )
    ssl.add_argument("--input", default="src/shadowseed/data/gap_test_suite_4_5.json")
    ssl.add_argument("--output", default="results/ssl45_gap_suite.json")
    ssl.add_argument("--turns", type=int, default=3)

    fp = subparsers.add_parser(
        "run-false-positive-suite",
        help="[standard] negatieve controle en Gate-ruisfiltering",
    )
    fp.add_argument(
        "--input",
        default="src/shadowseed/data/gap_test_suite_false_positive_4_5.json",
    )
    fp.add_argument("--output", default="results/ssl45_false_positive_suite.json")

    benefit = subparsers.add_parser(
        "run-benefit-suite",
        help="[standard] kleine benchmark voor antwoordwinst",
    )
    benefit.add_argument(
        "--input",
        default="src/shadowseed/data/ssl45_benefit_suite.json",
    )
    benefit.add_argument("--output", default="results/ssl45_benefit_suite.json")
    benefit.add_argument("--turns", type=int, default=3)

    model_benefit = subparsers.add_parser(
        "run-model-benefit-suite",
        help="[standard/manual] fixture-smoke of optionele echte modelrun",
    )
    model_benefit.add_argument(
        "--input",
        default="src/shadowseed/data/ssl45_model_benefit_suite.json",
    )
    model_benefit.add_argument("--output", default="results/ssl45_model_benefit_suite.json")
    model_benefit.add_argument("--turns", type=int, default=3)
    model_benefit.add_argument(
        "--backend",
        choices=MODEL_BACKENDS,
        default="fixture",
    )
    model_benefit.add_argument("--model-id", default=None)
    model_benefit.add_argument("--max-new-tokens", type=int, default=220)

    blind = subparsers.add_parser(
        "run-blind-benchmark",
        help="[standard] methodologische smoke voor labelscheiding",
    )
    blind.add_argument(
        "--input",
        default="src/shadowseed/data/blind_suite_public.json",
        help="Publieke scenario's zonder evaluator-labels.",
    )
    blind.add_argument(
        "--labels",
        required=True,
        help="Privébestand met expected_gaps en must_not_add labels.",
    )
    blind.add_argument("--output", default="results/blind_benchmark.json")
    blind.add_argument("--turns", type=int, default=3)
    blind.add_argument("--max-seeds", type=int, default=5)

    open_set_hf = subparsers.add_parser(
        "fetch-open-set-hf-batch",
        help="[manual] haal een kleine HF-batch op voor open-set seed review",
    )
    open_set_hf.add_argument(
        "--source-id",
        default="ag_news_test",
        help="Bron-id uit de open-set HF source registry.",
    )
    open_set_hf.add_argument(
        "--registry",
        default="src/shadowseed/data/open_set_hf_sources.json",
        help="JSON-bestand met brondefinities voor HF open-set intake.",
    )
    open_set_hf.add_argument(
        "--output",
        default="benchmarks/open_review/input/hf_ag_news_test_batch.json",
        help="Waar de genormaliseerde open-set batch wordt opgeslagen.",
    )
    open_set_hf.add_argument("--limit", type=int, default=12)
    open_set_hf.add_argument("--offset", type=int, default=0)

    open_set = subparsers.add_parser(
        "run-open-set-seed-review",
        help="[manual] open-set scaffold met review-packets",
    )
    open_set.add_argument("--input", default="src/shadowseed/data/open_set_seed_review_sample.json")
    open_set.add_argument("--output", default="results/open_review/open_set_seed_output.json")
    open_set.add_argument(
        "--review-packets",
        default="results/open_review/open_set_review_packets.json",
        help="Waar de review-packets voor menselijke beoordeling worden opgeslagen.",
    )

    open_set_summary = subparsers.add_parser(
        "summarize-open-set-seed-review",
        help="[manual/reporting] vat ingevulde open-set review-packets samen",
    )
    open_set_summary.add_argument(
        "--input",
        default="results/open_review/open_set_review_packets.json",
        help="JSON-bestand met ingevulde review-packets.",
    )
    open_set_summary.add_argument(
        "--output",
        default="results/open_review/open_set_seed_review_summary.json",
        help="Waar de geaggregeerde review-samenvatting wordt opgeslagen.",
    )
    open_set_summary.add_argument(
        "--disagreements-output",
        default="results/open_review/open_set_disagreements.json",
        help="Waar seed-level disagreements voor handmatige follow-up worden opgeslagen.",
    )
    open_set_summary.add_argument(
        "--report-output",
        default="results/open_review/open_set_review_report.md",
        help="Waar de leesbare open-set samenvatting wordt opgeslagen.",
    )

    adversarial = subparsers.add_parser(
        "run-adversarial-gate-benchmark",
        help="[manual] vergelijk current Gate met zwakkere promotieregels",
    )
    adversarial.add_argument(
        "--input",
        default="src/shadowseed/data/adversarial_gate_benchmark.json",
    )
    adversarial.add_argument(
        "--output",
        default="results/adversarial_gate_benchmark.json",
    )
    adversarial.add_argument(
        "--casebook",
        default="results/adversarial_gate_casebook.md",
        help="Waar de leesbare casebook met baseline-vs-gate blokkades wordt opgeslagen.",
    )

    probe = subparsers.add_parser(
        "run-probe-utility-benchmark",
        help="[manual] gedragsmatige scaffold voor follow-up, retrieval en dialectiek",
    )
    probe.add_argument("--input", default="src/shadowseed/data/ssl45_probe_utility_suite.json")
    probe.add_argument("--output", default="results/ssl45_probe_utility_suite.json")

    vectorstore = subparsers.add_parser(
        "run-vectorstore-smoke",
        help="[manual] vectorstore backend smoke-test",
    )
    vectorstore.add_argument("--output", default="results/vectorstore_smoke.json")
    vectorstore.add_argument("--backend", choices=VECTOR_BACKENDS, default="memory")

    ssot = subparsers.add_parser(
        "run-ssot-smoke",
        help="[manual] SSOT en falsificatiebasis smoke-test",
    )
    ssot.add_argument("--output", default="results/ssot_smoke.json")
    ssot.add_argument("--backend", choices=VECTOR_BACKENDS, default="memory")

    retrieval = subparsers.add_parser(
        "run-retrieval-benchmark",
        help="[manual] retrievalkwaliteit van de gekozen vectorstore",
    )
    retrieval.add_argument("--input", default="src/shadowseed/data/retrieval_benchmark.json")
    retrieval.add_argument("--output", default="results/retrieval_benchmark.json")
    retrieval.add_argument("--backend", choices=VECTOR_BACKENDS, default="memory")
    retrieval.add_argument("--k", type=int, default=3)

    retrieval_model = subparsers.add_parser(
        "run-retrieval-model-benchmark",
        help="[manual] effect van opgehaalde context op modelantwoord",
    )
    retrieval_model.add_argument("--input", default="src/shadowseed/data/retrieval_output_benchmark.json")
    retrieval_model.add_argument("--retrieval-input", default="src/shadowseed/data/retrieval_benchmark.json")
    retrieval_model.add_argument("--output", default="results/retrieval_model_benchmark.json")
    retrieval_model.add_argument("--vector-backend", choices=VECTOR_BACKENDS, default="memory")
    retrieval_model.add_argument("--model-backend", choices=MODEL_BACKENDS, default="fixture")
    retrieval_model.add_argument("--model-id", default=None)
    retrieval_model.add_argument("--max-new-tokens", type=int, default=220)
    retrieval_model.add_argument("--top-k", type=int, default=3)

    analyze = subparsers.add_parser(
        "analyze-results",
        help="[reporting] maak rapport en grafieken uit resultaatbestanden",
    )
    analyze.add_argument("--results-dir", default="results")
    analyze.add_argument("--output-dir", default="results/analysis")

    nlp = subparsers.add_parser(
        "run-absencebench-smoke",
        aliases=["run-nlp-smoke"],
        help="[standard] technische smoke voor de lokale AbsenceBench-route",
    )
    nlp.set_defaults(command="run-absencebench-smoke")
    nlp.add_argument("--input", default="examples/local_absencebench_sample.json")
    nlp.add_argument("--output", default="absencebench_smoke.json")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = execute_command(args)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
