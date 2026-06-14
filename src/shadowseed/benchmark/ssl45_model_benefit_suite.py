"""Phase 2 model benefit suite for SSL 4.5.

This runner compares the same model in two conditions:

1. baseline: answer the question directly;
2. SSL-guided: revise the baseline answer using promoted SSL seeds.

The default backend is ``fixture`` so CI stays free and fast. Real local model
runs can use ``hf-transformers`` with an installed transformers stack.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Protocol

from shadowseed.benchmark.ssl45_benefit_suite import (
    UNSUPPORTED_ADDITION_PENALTY_WEIGHT,
    coverage_delta_per_100_added_words,
    penalized_coverage_delta,
)
from shadowseed.benchmark.ssl45_gap_suite import (
    detect_candidate_seeds,
    jaccard,
    score_seed,
    tokenize,
)
from shadowseed.manager import SSLManager, SeedStatus


class ModelBackend(Protocol):
    name: str

    def generate(self, prompt: str, scenario: dict, mode: str, ssl_seeds: list[str]) -> str:
        ...


class FixtureBackend:
    """Deterministic CI backend.

    It simulates a weak baseline and a model that follows SSL-guided revision
    instructions. This checks the harness mechanics without downloading a model.
    """

    name = "fixture"

    def generate(self, prompt: str, scenario: dict, mode: str, ssl_seeds: list[str]) -> str:
        if mode == "baseline":
            return scenario.get("baseline_answer", "")
        additions = " ".join(ssl_seeds)
        return f"{scenario.get('baseline_answer', '')}\n\nSSL-guided revision: {additions}".strip()


class HFTransformersBackend:
    """Local Hugging Face transformers backend.

    This is opt-in because model downloads can be slow and are not suitable for
    default CI. Recommended small model examples include TinyLlama-style instruct
    models or any local text-generation model available in the HF cache.
    """

    def __init__(self, model_id: str, max_new_tokens: int = 220) -> None:
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "Install optional model dependencies first: pip install -e '.[models]' transformers torch"
            ) from exc

        self.name = f"hf-transformers:{model_id}"
        self.model_id = model_id
        self.max_new_tokens = max_new_tokens
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        if torch.cuda.is_available():
            model_kwargs = {"torch_dtype": torch.float16, "device_map": "auto"}
        else:
            # CPU: keep the checkpoint's native (half) precision instead of
            # upcasting to float32 — halves memory on CPU-only runners.
            model_kwargs = {"torch_dtype": "auto"}
        model = AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)
        self.generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=self.tokenizer,
            device=0 if torch.cuda.is_available() else -1,
        )

    def generate(self, prompt: str, scenario: dict, mode: str, ssl_seeds: list[str]) -> str:
        output = self.generator(
            prompt,
            max_new_tokens=self.max_new_tokens,
            do_sample=False,
            return_full_text=False,
        )
        return output[0]["generated_text"].strip()


class OllamaBackend:
    """Local Ollama backend.

    Talks to a running Ollama server over HTTP instead of loading weights in
    process. This keeps real small-model runs lightweight enough for a standard
    CI runner: install Ollama, ``ollama pull`` a quantized model, then point the
    run at it. Decoding is greedy (temperature 0, fixed seed) for reproducibility.
    """

    def __init__(self, model_id: str, max_new_tokens: int = 220, host: str | None = None) -> None:
        from shadowseed.benchmark.ollama_client import OllamaClient

        self.name = f"ollama:{model_id}"
        self.model_id = model_id
        self.max_new_tokens = max_new_tokens
        self.client = OllamaClient(model=model_id, host=host)

    def generate(self, prompt: str, scenario: dict, mode: str, ssl_seeds: list[str]) -> str:
        return self.client.generate(prompt, max_new_tokens=self.max_new_tokens)


def make_backend(backend: str, model_id: str | None, max_new_tokens: int) -> ModelBackend:
    if backend == "fixture":
        return FixtureBackend()
    if backend == "hf-transformers":
        if not model_id:
            raise ValueError("--model-id is required for backend hf-transformers")
        return HFTransformersBackend(model_id=model_id, max_new_tokens=max_new_tokens)
    if backend == "ollama":
        if not model_id:
            raise ValueError("--model-id is required for backend ollama")
        return OllamaBackend(model_id=model_id, max_new_tokens=max_new_tokens)
    raise ValueError(f"Unknown backend: {backend}")


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-zÀ-ÿ0-9_]+", text))


def answer_fragments(answer: str) -> list[str]:
    fragments = [
        part.strip()
        for part in re.split(r"[\n.;:]+", answer)
        if part.strip()
    ]
    return fragments or [answer]


def expected_is_covered(answer: str, expected: str, threshold: float = 0.70) -> bool:
    answer_lower = answer.lower()
    expected_lower = expected.lower()
    if expected_lower in answer_lower:
        return True
    return max(jaccard(fragment, expected) for fragment in answer_fragments(answer)) >= threshold


def coverage(answer: str, expected_additions: list[str]) -> tuple[float, list[str]]:
    covered = [
        expected
        for expected in expected_additions
        if expected_is_covered(answer, expected)
    ]
    if not expected_additions:
        return 1.0, covered
    return len(covered) / len(expected_additions), covered


def blind_order(scenario_id: str) -> tuple[str, str]:
    """Deterministically blind the pair order for review packets."""
    checksum = sum(ord(ch) for ch in scenario_id)
    if checksum % 2 == 0:
        return "baseline", "ssl"
    return "ssl", "baseline"


def build_blind_review_item(scenario: dict, baseline_answer: str, ssl_answer: str) -> tuple[dict, dict]:
    first, second = blind_order(scenario["id"])
    answer_map = {"baseline": baseline_answer, "ssl": ssl_answer}
    item = {
        "review_id": f"review_{scenario['id']}",
        "scenario_id": scenario["id"],
        "question": scenario["question"],
        "option_a": answer_map[first],
        "option_b": answer_map[second],
        "reviewer_instruction": (
            "Kies welk antwoord inhoudelijk beter is. Let op juiste gap-dekking, "
            "geen unsupported additions, helderheid en geen beloning voor lengte alleen."
        ),
        "scores_to_fill": {
            "better_answer": "A/B/tie",
            "gap_coverage_a_0_5": None,
            "gap_coverage_b_0_5": None,
            "unsupported_claims_a_0_5": None,
            "unsupported_claims_b_0_5": None,
            "notes": "",
        },
    }
    key = {
        "review_id": item["review_id"],
        "option_a_source": first,
        "option_b_source": second,
    }
    return item, key


def build_baseline_prompt(scenario: dict) -> str:
    return (
        "Beantwoord de vraag helder en compact.\n\n"
        f"Vraag: {scenario['question']}\n\n"
        "Antwoord:"
    )


def build_ssl_revision_prompt(scenario: dict, baseline_answer: str, ssl_seeds: list[str]) -> str:
    seed_block = "\n".join(f"- {seed}" for seed in ssl_seeds)
    return (
        "Je herschrijft hetzelfde antwoord met alleen de gevalideerde SSL-seeds als extra aandachtspunten.\n"
        "Voeg geen nieuwe claims toe buiten deze seeds.\n\n"
        f"Vraag: {scenario['question']}\n\n"
        f"Eerste antwoord:\n{baseline_answer}\n\n"
        f"Gevalideerde SSL-seeds:\n{seed_block}\n\n"
        "Herschreven antwoord:"
    )


def ssl_append_answer(baseline_answer: str, ssl_seeds: list[str]) -> str:
    """No-harm seed injection: keep the baseline answer verbatim and append a
    bounded paragraph naming the validated seeds as open points.

    This is the round-008 "do no harm" strategy (run 02). Unlike the free
    rewrite (`build_ssl_revision_prompt`), the baseline cannot be corrupted —
    it is preserved byte-for-byte — and the seeds are added as a clearly
    delimited addendum, with no model call in the merge. It honours the
    weightless-seed / Gate principle at the answer level: acting on seeds can
    only add, never overwrite a good answer.
    """
    baseline = baseline_answer.strip()
    seeds = [s.strip() for s in ssl_seeds if s and s.strip()]
    if not seeds:
        return baseline
    addendum = "Aanvullende aandachtspunten die in het antwoord ontbreken:\n" + "\n".join(
        f"- {seed}" for seed in seeds
    )
    return f"{baseline}\n\n{addendum}" if baseline else addendum


def promoted_ssl_seeds(scenario: dict, baseline_answer: str, turns: int) -> tuple[list[str], list[dict], list[list[str]]]:
    manager = SSLManager(
        embedding_fn=lambda text: __import__(
            "shadowseed.benchmark.ssl45_gap_suite",
            fromlist=["lexical_embedding"],
        ).lexical_embedding(text)
    )
    detected_by_turn: list[list[str]] = []

    for _turn in range(turns):
        candidates = detect_candidate_seeds(
            {"domain": scenario["domain"], "input": baseline_answer}
        )
        detected_by_turn.append(candidates)
        for candidate in candidates:
            try:
                manager.add_or_update_seed(candidate, trigger_keywords=sorted(tokenize(candidate))[:5])
            except ValueError:
                continue

    seed_scores = []
    ground_truth = [{"text": expected} for expected in scenario["expected_ssl_additions"]]
    for seed_id, seed in manager.seeds.items():
        scored = score_seed(seed.text, ground_truth)
        seed_scores.append(scored.__dict__)
        if scored.score == 2:
            seed.evidence_count = max(seed.evidence_count, 2)
            for _ in range(3):
                manager.run_validation_gate(seed_id)
        elif scored.score == 0:
            manager.run_validation_gate(seed_id, contradiction=True)

    promoted = [
        seed.text
        for seed in manager.seeds.values()
        if seed.status == SeedStatus.PROMOTED
    ]
    return promoted, seed_scores, detected_by_turn


def unsupported_additions(promoted: list[str], expected: list[str]) -> list[str]:
    return [
        seed
        for seed in promoted
        if all(jaccard(seed, expected_seed) < 0.70 for expected_seed in expected)
    ]


def run_ssl45_model_benefit_suite(
    input_path: str,
    output_path: str,
    turns: int = 3,
    backend: str = "fixture",
    model_id: str | None = None,
    max_new_tokens: int = 220,
) -> Path:
    suite = json.loads(Path(input_path).read_text(encoding="utf-8"))
    model = make_backend(backend=backend, model_id=model_id, max_new_tokens=max_new_tokens)

    results = []
    blind_review_items = []
    blind_answer_key = []
    baseline_coverages: list[float] = []
    ssl_coverages: list[float] = []
    length_deltas: list[int] = []
    unsupported_total = 0
    promoted_total = 0

    for scenario in suite["scenarios"]:
        baseline_prompt = build_baseline_prompt(scenario)
        baseline_answer = model.generate(baseline_prompt, scenario, "baseline", [])
        promoted, seed_scores, detected_by_turn = promoted_ssl_seeds(
            scenario,
            baseline_answer,
            turns=turns,
        )
        ssl_prompt = build_ssl_revision_prompt(scenario, baseline_answer, promoted)
        ssl_answer = model.generate(ssl_prompt, scenario, "ssl", promoted)

        baseline_cov, baseline_covered = coverage(baseline_answer, scenario["expected_ssl_additions"])
        ssl_cov, ssl_covered = coverage(ssl_answer, scenario["expected_ssl_additions"])
        unsupported = unsupported_additions(promoted, scenario["expected_ssl_additions"])
        baseline_words = word_count(baseline_answer)
        ssl_words = word_count(ssl_answer)
        length_delta = ssl_words - baseline_words
        coverage_delta = ssl_cov - baseline_cov
        gain_per_100_added_words = coverage_delta_per_100_added_words(coverage_delta, length_delta)
        unsupported_rate = len(unsupported) / len(promoted) if promoted else 0.0
        blind_item, blind_key = build_blind_review_item(scenario, baseline_answer, ssl_answer)

        baseline_coverages.append(baseline_cov)
        ssl_coverages.append(ssl_cov)
        length_deltas.append(length_delta)
        unsupported_total += len(unsupported)
        promoted_total += len(promoted)
        blind_review_items.append(blind_item)
        blind_answer_key.append(blind_key)

        results.append(
            {
                "scenario_id": scenario["id"],
                "title": scenario["title"],
                "domain": scenario["domain"],
                "baseline_gap_coverage": baseline_cov,
                "ssl_gap_coverage": ssl_cov,
                "coverage_delta": coverage_delta,
                "coverage_delta_raw": coverage_delta,
                "baseline_word_count": baseline_words,
                "ssl_word_count": ssl_words,
                "answer_length_delta_words": length_delta,
                "coverage_delta_per_100_added_words": gain_per_100_added_words,
                "unsupported_ssl_addition_rate": unsupported_rate,
                "penalized_coverage_delta": penalized_coverage_delta(coverage_delta, unsupported_rate),
                "baseline_covered": baseline_covered,
                "ssl_covered": ssl_covered,
                "promoted_seeds": promoted,
                "unsupported_ssl_additions": unsupported,
                "baseline_answer": baseline_answer,
                "ssl_answer": ssl_answer,
                "detected_by_turn": detected_by_turn,
                "seed_scores": seed_scores,
            }
        )

    baseline_mean = sum(baseline_coverages) / len(baseline_coverages)
    ssl_mean = sum(ssl_coverages) / len(ssl_coverages)
    mean_length_delta = sum(length_deltas) / len(length_deltas)
    coverage_delta = ssl_mean - baseline_mean
    unsupported_rate = unsupported_total / promoted_total if promoted_total else 0.0
    summary = {
        "suite_version": suite.get("version"),
        "backend": model.name,
        "scenario_count": len(suite["scenarios"]),
        "baseline_mean_gap_coverage": baseline_mean,
        "ssl_mean_gap_coverage": ssl_mean,
        "coverage_delta": coverage_delta,
        "coverage_delta_raw": coverage_delta,
        "mean_answer_length_delta_words": mean_length_delta,
        "coverage_delta_per_100_added_words": coverage_delta_per_100_added_words(coverage_delta, mean_length_delta),
        "unsupported_penalty_weight": UNSUPPORTED_ADDITION_PENALTY_WEIGHT,
        "penalized_coverage_delta": penalized_coverage_delta(coverage_delta, unsupported_rate),
        "promoted_seed_count": promoted_total,
        "unsupported_ssl_additions": unsupported_total,
        "unsupported_ssl_addition_rate": unsupported_rate,
        "interpretation": (
            "Phase 2 compares the same backend in baseline and SSL-guided revision modes. "
            "Coverage delta is reported raw and length-aware; length-aware values must be read when SSL answers are longer. "
            "The fixture backend is a CI smoke test; hf-transformers is the real local model mode. "
            "Blind review items are included so human judges can score quality without knowing which answer used SSL."
        ),
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "summary": summary,
                "results": results,
                "blind_review_items": blind_review_items,
                "blind_answer_key": blind_answer_key,
            },
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )
    return output
