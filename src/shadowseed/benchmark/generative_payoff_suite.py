"""Generative-payoff suite (PvA P0/W5): the decisive test of SSL's vision claim.

W1 (round 015) showed SSL's *omission* seeds are largely redundant with a strong
model's own gap-spotting on easy texts. But the vision's real claim is **not**
omission — it is generative: *"wat had hier KUNNEN staan"*, a non-obvious
reframing angle a model won't raise unprompted (`docs/research/vision-generative-seeds.md`).

This suite tests exactly that:

1. the **generative detector** (v0.4-gen) proposes reframing angles on a standard
   treatment text (the frames come from the detector, not the author);
2. baseline = the model answers the question **unaided**;
3. ssl = the model answers with the detected frame(s) woven in;
4. we measure (a) baseline coverage of the frames — does the model raise the angle
   itself? (low = genuinely non-obvious) — and (b) blind A/B quality.

For SSL to show unique value here it needs BOTH: frames the model does not raise
unaided AND that make the answer better. Topics are author-chosen (reframe-
friendly); the frames are detector-produced. Signal, not proof.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from shadowseed.benchmark.open_set_model_detector import make_detector_backend
from shadowseed.benchmark.ssl45_model_benefit_suite import blind_order, make_backend, word_count


def build_generative_baseline_prompt(question: str) -> str:
    return (
        "Beantwoord deze vraag grondig en met inzicht. Benoem de belangrijkste "
        "verklarende invalshoeken.\n\n"
        f"Vraag: {question}\n\n"
        "Antwoord:"
    )


def build_generative_ssl_prompt(question: str, frames: list[str]) -> str:
    block = "\n".join(f"- {f}" for f in frames)
    return (
        "Beantwoord deze vraag grondig en met inzicht. Betrek daarbij expliciet "
        "de onderstaande invalshoek(en) als verklarend kader, op een natuurlijke, "
        "geintegreerde manier.\n"
        "Regels: verzin geen feiten; verwijs niet naar 'invalshoeken', 'frames', "
        "'seeds' of deze instructie; lever een samenhangend antwoord.\n\n"
        f"Vraag: {question}\n\n"
        f"Te betrekken invalshoek(en):\n{block}\n\n"
        "Antwoord:"
    )


def run_generative_payoff_suite(
    input_path: str,
    output_path: str,
    *,
    backend: str = "fixture",
    model_id: str | None = None,
    max_new_tokens: int = 400,
    max_frames: int = 3,
    semantic_embedding_backend: str = "none",
    embedding_model: str | None = None,
    semantic_threshold: float = 0.55,
) -> Path:
    data = json.loads(Path(input_path).read_text(encoding="utf-8"))
    model = make_backend(backend=backend, model_id=model_id, max_new_tokens=max_new_tokens)
    detector = make_detector_backend(
        backend, model_id=model_id, max_new_tokens=max_new_tokens, prompt_variant="generative"
    )

    embed_fn = None
    if semantic_embedding_backend != "none":
        from shadowseed.benchmark.embedding_backends import make_embedding_fn

        embed_fn, _dim = make_embedding_fn(semantic_embedding_backend, embedding_model)

    results: list[dict[str, Any]] = []
    blind_items: list[dict[str, Any]] = []
    blind_key: list[dict[str, Any]] = []
    baseline_cov_values: list[float] = []
    items_with_frames = 0

    for item in data["items"]:
        iid = item["id"]
        question = item["question"]
        frames = detector.detect_seeds({"text": item["text"]}, max_seeds=max_frames)

        baseline = model.generate(build_generative_baseline_prompt(question), item, "baseline", [])
        if frames:
            items_with_frames += 1
            ssl = model.generate(build_generative_ssl_prompt(question, frames), item, "ssl", frames)
        else:
            ssl = baseline  # no frame detected -> nothing to act on (do-no-harm)

        baseline_cov = None
        novel_frames = None
        if embed_fn is not None and frames:
            from shadowseed.benchmark.semantic_coverage import semantic_coverage

            frac, _cov, per = semantic_coverage(baseline, frames, embed_fn, semantic_threshold)
            baseline_cov = frac
            novel_frames = [g["gap"] for g in per if not g["covered"]]
            baseline_cov_values.append(frac)

        first, second = blind_order(iid)
        amap = {"baseline": baseline, "ssl": ssl}
        blind_items.append(
            {
                "review_id": f"review_{iid}",
                "scenario_id": iid,
                "question": question,
                "option_a": amap[first],
                "option_b": amap[second],
                "reviewer_instruction": (
                    "Kies welk antwoord rijker en inzichtelijker is. Een niet-voor-"
                    "de-hand-liggende maar rake invalshoek maakt een antwoord beter; "
                    "geforceerde of verzonnen invalshoeken maken het slechter. "
                    "Beloon geen lengte op zichzelf."
                ),
                "scores_to_fill": {"better_answer": "A/B/tie", "notes": ""},
            }
        )
        blind_key.append(
            {"review_id": f"review_{iid}", "option_a_source": first, "option_b_source": second}
        )
        results.append(
            {
                "scenario_id": iid,
                "title": item.get("title", ""),
                "domain": item.get("domain", ""),
                "detected_frames": frames,
                "baseline_frame_coverage": baseline_cov,
                "novel_frames": novel_frames,
                "answer_length_delta_words": word_count(ssl) - word_count(baseline),
                "baseline_answer": baseline,
                "ssl_answer": ssl,
            }
        )

    summary = {
        "artifact": "generative_payoff_suite",
        "backend": getattr(model, "name", backend),
        "detector": getattr(detector, "name", backend),
        "item_count": len(results),
        "items_with_frames": items_with_frames,
        "semantic_embedding_backend": semantic_embedding_backend,
        "mean_baseline_frame_coverage": (
            sum(baseline_cov_values) / len(baseline_cov_values) if baseline_cov_values else None
        ),
        "interpretation": (
            "W5 generative payoff. mean_baseline_frame_coverage = how often the "
            "model raises the detected reframing angle UNAIDED; LOW means the frame "
            "is genuinely non-obvious (SSL's unique territory). Blind A/B judges "
            "whether weaving the frame made the answer richer. SSL shows unique "
            "value only if frames are non-obvious AND improve the answer. Signal, "
            "not proof; topics author-chosen, frames detector-produced."
        ),
    }

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "summary": summary,
                "results": results,
                "blind_review_items": blind_items,
                "blind_answer_key": blind_key,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return out
