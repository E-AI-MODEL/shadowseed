"""Command dispatch helpers for the Shadow Seed Learning CLI."""

from __future__ import annotations

import argparse
from collections.abc import Callable

from shadowseed.analysis.ssl45_result_analyzer import analyze_results
from shadowseed.benchmark.absencebench_hf import fetch_absencebench_sample
from shadowseed.benchmark.absencebench_local import run_local_absencebench
from shadowseed.benchmark.absencebench_runner import AbsenceBenchRunner
from shadowseed.benchmark.adversarial_gate_benchmark import run_adversarial_gate_benchmark
from shadowseed.benchmark.adversarial_payoff_suite import run_adversarial_payoff_suite
from shadowseed.benchmark.wild_payoff_suite import run_wild_payoff_suite
from shadowseed.benchmark.blind.runner import run_blind_benchmark
from shadowseed.benchmark.open_set_review_summary import summarize_open_set_seed_review
from shadowseed.benchmark.open_set_seed_review import run_open_set_seed_review
from shadowseed.benchmark.ssl_vs_rag_benchmark import run_ssl_vs_rag_benchmark
from shadowseed.benchmark.result_writer import ResultWriter
from shadowseed.benchmark.retrieval_benchmark import run_retrieval_benchmark
from shadowseed.benchmark.retrieval_model_benchmark import run_retrieval_model_benchmark
from shadowseed.benchmark.run_types import RunType
from shadowseed.benchmark.ssl45_benefit_suite import run_ssl45_benefit_suite
from shadowseed.benchmark.ssl45_false_positive_suite import run_ssl45_false_positive_suite
from shadowseed.benchmark.ssl45_gap_suite import run_ssl45_gap_suite
from shadowseed.benchmark.ssl45_model_benefit_suite import run_ssl45_model_benefit_suite
from shadowseed.benchmark.probe_feedback_behavior_suite import run_probe_feedback_behavior_suite
from shadowseed.benchmark.ssl45_probe_utility_suite import run_ssl45_probe_utility_suite
from shadowseed.benchmark.ssot_smoke import run_ssot_smoke
from shadowseed.benchmark.vectorstore_smoke import run_vectorstore_smoke


CommandHandler = Callable[[argparse.Namespace], str]


COMMAND_ALIASES = {
    "prepare-absencebench": "prepare-absencebench-bundle",
    "fetch-absencebench": "fetch-absencebench-sample",
    "run-local-absencebench": "run-absencebench-local",
    "run-nlp-smoke": "run-absencebench-smoke",
}


def _prepare_absencebench_bundle(args: argparse.Namespace) -> str:
    bundle = AbsenceBenchRunner().build_execution_bundle(
        requested_run_type=RunType.PREPARATION.value
    )
    return ResultWriter().write_payload(bundle.result, args.output)


def _run_absencebench_local(args: argparse.Namespace) -> str:
    return run_local_absencebench(args.input, args.output)


def _run_absencebench_smoke(args: argparse.Namespace) -> str:
    return run_local_absencebench(args.input, args.output)


def _fetch_absencebench_sample(args: argparse.Namespace) -> str:
    return fetch_absencebench_sample(args.output, limit=args.limit)


def _run_gap_suite(args: argparse.Namespace) -> str:
    return run_ssl45_gap_suite(args.input, args.output, turns=args.turns)


def _run_false_positive_suite(args: argparse.Namespace) -> str:
    return run_ssl45_false_positive_suite(args.input, args.output)


def _run_benefit_suite(args: argparse.Namespace) -> str:
    return run_ssl45_benefit_suite(args.input, args.output, turns=args.turns)


def _run_model_benefit_suite(args: argparse.Namespace) -> str:
    return run_ssl45_model_benefit_suite(
        args.input,
        args.output,
        turns=args.turns,
        backend=args.backend,
        model_id=args.model_id,
        max_new_tokens=args.max_new_tokens,
        semantic_embedding_backend=getattr(args, "semantic_embedding_backend", "none"),
        embedding_model=getattr(args, "embedding_model", None),
        semantic_threshold=getattr(args, "semantic_threshold", 0.55),
    )


def _run_blind_benchmark(args: argparse.Namespace) -> str:
    return run_blind_benchmark(
        args.input,
        args.labels,
        args.output,
        turns=args.turns,
        max_seeds=args.max_seeds,
    )


def _fetch_open_set_hf_batch(args: argparse.Namespace) -> str:
    try:
        from shadowseed.benchmark.open_set_hf import fetch_open_set_hf_batch
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "HF open-set intake is not available in this checkout. "
            "Merge or restore src/shadowseed/benchmark/open_set_hf.py first."
        ) from exc
    return str(
        fetch_open_set_hf_batch(
            args.output,
            source_id=args.source_id,
            registry_path=args.registry,
            limit=args.limit,
            offset=args.offset,
        )
    )


def _run_ssl_vs_rag_benchmark(args: argparse.Namespace) -> str:
    return str(
        run_ssl_vs_rag_benchmark(
            args.data,
            args.output,
            model_backend=args.model_backend,
            model_id=args.model_id,
            max_new_tokens=args.max_new_tokens,
            top_k=args.top_k,
            use_centroid=args.use_centroid,
            embedding_backend=getattr(args, "embedding_backend", "lexical"),
            embedding_model=getattr(args, "embedding_model", None),
        )
    )


def _run_adversarial_payoff_suite(args: argparse.Namespace) -> str:
    return str(
        run_adversarial_payoff_suite(
            args.input,
            args.output,
            backend=args.backend,
            model_id=args.model_id,
            max_new_tokens=args.max_new_tokens,
        )
    )


def _run_wild_payoff_suite(args: argparse.Namespace) -> str:
    return str(
        run_wild_payoff_suite(
            args.input,
            args.output,
            backend=args.backend,
            model_id=args.model_id,
            max_new_tokens=args.max_new_tokens,
            semantic_embedding_backend=getattr(args, "semantic_embedding_backend", "none"),
            embedding_model=getattr(args, "embedding_model", None),
        )
    )


def _run_open_set_seed_review(args: argparse.Namespace) -> str:
    return run_open_set_seed_review(
        args.input,
        args.output,
        review_packet_path=args.review_packets,
        reviewer_ids=args.reviewer_ids,
        detector=args.detector,
        model_backend=args.model_backend,
        model_id=args.model_id,
        max_new_tokens=args.max_new_tokens,
        prompt_variant=getattr(args, "prompt_variant", "absence"),
    )


def _summarize_open_set_seed_review(args: argparse.Namespace) -> str:
    return summarize_open_set_seed_review(
        args.input,
        args.output,
        disagreements_output_path=args.disagreements_output,
        report_output_path=args.report_output,
    )


def _run_adversarial_gate_benchmark(args: argparse.Namespace) -> str:
    return run_adversarial_gate_benchmark(
        args.input,
        args.output,
        casebook_path=args.casebook,
    )


def _run_probe_utility_benchmark(args: argparse.Namespace) -> str:
    return run_ssl45_probe_utility_suite(args.input, args.output)


def _list_open_set_models(args: argparse.Namespace) -> str:
    from shadowseed.benchmark.open_set_models import run_list_open_set_models

    return run_list_open_set_models(output_path=args.output, registry_path=args.registry)


def _run_probe_feedback_behavior_suite(args: argparse.Namespace) -> str:
    return run_probe_feedback_behavior_suite(
        args.input, args.output, casebook_path=args.casebook
    )


def _run_vectorstore_smoke(args: argparse.Namespace) -> str:
    return run_vectorstore_smoke(args.output, backend=args.backend)


def _run_ssot_smoke(args: argparse.Namespace) -> str:
    return run_ssot_smoke(args.output, backend=args.backend)


def _run_retrieval_benchmark(args: argparse.Namespace) -> str:
    return run_retrieval_benchmark(
        args.input,
        args.output,
        backend=args.backend,
        k=args.k,
    )


def _run_retrieval_model_benchmark(args: argparse.Namespace) -> str:
    return run_retrieval_model_benchmark(
        args.input,
        args.retrieval_input,
        args.output,
        vector_backend=args.vector_backend,
        model_backend=args.model_backend,
        model_id=args.model_id,
        max_new_tokens=args.max_new_tokens,
        top_k=args.top_k,
    )


def _analyze_results(args: argparse.Namespace) -> str:
    return analyze_results(args.results_dir, args.output_dir)


COMMAND_HANDLERS: dict[str, CommandHandler] = {
    "prepare-absencebench-bundle": _prepare_absencebench_bundle,
    "run-absencebench-local": _run_absencebench_local,
    "fetch-absencebench-sample": _fetch_absencebench_sample,
    "run-gap-suite": _run_gap_suite,
    "run-false-positive-suite": _run_false_positive_suite,
    "run-benefit-suite": _run_benefit_suite,
    "run-model-benefit-suite": _run_model_benefit_suite,
    "run-blind-benchmark": _run_blind_benchmark,
    "fetch-open-set-hf-batch": _fetch_open_set_hf_batch,
    "run-open-set-seed-review": _run_open_set_seed_review,
    "run-ssl-vs-rag": _run_ssl_vs_rag_benchmark,
    "run-adversarial-payoff": _run_adversarial_payoff_suite,
    "run-wild-payoff": _run_wild_payoff_suite,
    "summarize-open-set-seed-review": _summarize_open_set_seed_review,
    "run-adversarial-gate-benchmark": _run_adversarial_gate_benchmark,
    "run-probe-utility-benchmark": _run_probe_utility_benchmark,
    "run-probe-feedback-behavior-suite": _run_probe_feedback_behavior_suite,
    "list-open-set-models": _list_open_set_models,
    "run-vectorstore-smoke": _run_vectorstore_smoke,
    "run-ssot-smoke": _run_ssot_smoke,
    "run-retrieval-benchmark": _run_retrieval_benchmark,
    "run-retrieval-model-benchmark": _run_retrieval_model_benchmark,
    "analyze-results": _analyze_results,
    "run-absencebench-smoke": _run_absencebench_smoke,
}


def normalize_command(command: str) -> str:
    return COMMAND_ALIASES.get(command, command)


def execute_command(args: argparse.Namespace) -> str:
    command = normalize_command(args.command)
    try:
        handler = COMMAND_HANDLERS[command]
    except KeyError as exc:
        raise ValueError(f"Onbekend commando: {command}") from exc
    return handler(args)
