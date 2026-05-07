"""Probe utility benchmark for SSL 4.5.

This benchmark is a first behavioral layer beyond scenario ground truth. It does
not ask whether a candidate matches a fixed expected seed list. Instead it asks
whether a promoted atomic seed can drive a useful active probe.

The benchmark compares an SSL probe against a weak generic baseline probe on:

- specificity to the source context;
- specificity to the promoted seed;
- atomicity of the question;
- absence of implementation leakage such as "seed" or "gap";
- open-question form.

This keeps scenarios as regression evidence while moving the test stack toward
open-set, reviewer-friendly behavioral value.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from shadowseed.benchmark.ssl45_gap_suite import jaccard, tokenize


GENERIC_BASELINE_PROBE = "Kunt u dit verder toelichten?"
FORBIDDEN_LEAKAGE_TERMS = {"seed", "shadow seed", "gap", "ssl", "validation gate"}
OPEN_QUESTION_STARTS = (
    "welke",
    "hoe",
    "waarom",
    "wat",
    "in hoeverre",
    "op welke manier",
)


def _keyword_candidates(text: str) -> list[str]:
    tokens = [token for token in tokenize(text) if len(token) > 3]
    stop = {
        "deze",
        "door",
        "voor",
        "zijn",
        "wordt",
        "worden",
        "heeft",
        "niet",
        "maar",
        "naar",
        "data",
        "recht",
    }
    seen: set[str] = set()
    result = []
    for token in tokens:
        if token in stop or token in seen:
            continue
        seen.add(token)
        result.append(token)
    return result[:8]


def generate_socratic_probe(seed_text: str, source_text: str) -> str:
    """Generate a narrow one-sentence Socratic probe from a promoted seed.

    This intentionally remains deterministic. The goal is to test the SSL
    behavior layer, not model prose quality.
    """
    seed = seed_text.strip().rstrip(".")
    source_keywords = _keyword_candidates(source_text)
    anchor = source_keywords[0] if source_keywords else "dit onderwerp"
    return f"Welke rol speelt {seed} binnen {anchor}?"


def _sentence_count(text: str) -> int:
    parts = [part for part in re.split(r"[.!?]+", text.strip()) if part.strip()]
    return len(parts)


def is_open_question(text: str) -> bool:
    lowered = text.strip().lower()
    return lowered.endswith("?") and lowered.startswith(OPEN_QUESTION_STARTS)


def leaks_internal_terms(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in FORBIDDEN_LEAKAGE_TERMS)


def probe_utility_score(probe: str, seed_text: str, source_text: str) -> dict[str, Any]:
    seed_overlap = jaccard(probe, seed_text)
    source_overlap = jaccard(probe, source_text)
    one_sentence = _sentence_count(probe) == 1
    open_question = is_open_question(probe)
    no_leakage = not leaks_internal_terms(probe)
    not_too_broad = len(tokenize(probe)) <= 18

    score = 0.0
    score += min(seed_overlap / 0.45, 1.0) * 0.35
    score += min(source_overlap / 0.20, 1.0) * 0.20
    score += 0.15 if one_sentence else 0.0
    score += 0.15 if open_question else 0.0
    score += 0.10 if no_leakage else 0.0
    score += 0.05 if not_too_broad else 0.0

    return {
        "score": round(score, 4),
        "seed_overlap": round(seed_overlap, 4),
        "source_overlap": round(source_overlap, 4),
        "one_sentence": one_sentence,
        "open_question": open_question,
        "no_internal_leakage": no_leakage,
        "not_too_broad": not_too_broad,
    }


def run_probe_utility_benchmark(input_path: str, output_path: str) -> Path:
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    items = payload.get("items", [])
    results = []
    ssl_scores: list[float] = []
    baseline_scores: list[float] = []

    for item in items:
        source_text = item.get("source_text") or item.get("text") or item.get("input") or ""
        seed_text = item["promoted_seed"]
        ssl_probe = generate_socratic_probe(seed_text, source_text)
        baseline_probe = item.get("baseline_probe", GENERIC_BASELINE_PROBE)

        ssl_utility = probe_utility_score(ssl_probe, seed_text, source_text)
        baseline_utility = probe_utility_score(baseline_probe, seed_text, source_text)
        ssl_scores.append(float(ssl_utility["score"]))
        baseline_scores.append(float(baseline_utility["score"]))

        results.append(
            {
                "item_id": item.get("id"),
                "domain": item.get("domain"),
                "source_text": source_text,
                "promoted_seed": seed_text,
                "ssl_probe": ssl_probe,
                "baseline_probe": baseline_probe,
                "ssl_utility": ssl_utility,
                "baseline_utility": baseline_utility,
                "utility_delta": round(float(ssl_utility["score"]) - float(baseline_utility["score"]), 4),
            }
        )

    ssl_mean = sum(ssl_scores) / len(ssl_scores) if ssl_scores else 0.0
    baseline_mean = sum(baseline_scores) / len(baseline_scores) if baseline_scores else 0.0
    positive_delta_count = sum(
        1 for ssl_score, baseline_score in zip(ssl_scores, baseline_scores) if ssl_score > baseline_score
    )
    summary = {
        "suite_version": payload.get("version"),
        "item_count": len(items),
        "ssl_mean_probe_utility": round(ssl_mean, 4),
        "baseline_mean_probe_utility": round(baseline_mean, 4),
        "mean_utility_delta": round(ssl_mean - baseline_mean, 4),
        "positive_delta_count": positive_delta_count,
        "positive_delta_rate": (positive_delta_count / len(items)) if items else 0.0,
        "passed": bool(items) and positive_delta_count == len(items) and ssl_mean > baseline_mean,
        "claim_boundary": "Behavioral probe utility only. This is not a fixed ground-truth gap match and still needs human review for mature open-set validation.",
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"summary": summary, "results": results}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output
