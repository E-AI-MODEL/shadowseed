"""
[!] NIET-PIJPLIJN — single-shot afgeleide. Deze suite gebruikt de SSLManager-
pijplijn NIET (geen weight-0 seeding, Gate, recurrence, TTL/TrTL, constellation
of probe). Ze test "detector-string -> in de prompt -> meten". De echte,
pijplijn-getrouwe payoff-test is ssl_session_suite.py (W9). Bewaard als
baseline/contrast; lees resultaten (W1/W5/W14) NIET als oordeel over SSL-de-pijplijn.

Wild-payoff suite (PvA P0/W1): real detected seeds through the payoff pipeline.

Rounds 011–013 proved acting on *author-designed* valid seeds helps. The open
honest gap was: are SSL's *own* detected gaps (open-set, not hand-written) worth
acting on — especially over a strong model that can spot gaps itself? This suite
closes that loop.

Per item (round 006 batch1, AI-reviewed accepted seeds, κ 0.63 vs human):

- baseline arm: the model reads the source text and does its OWN "what is missing
  for full understanding" analysis — unaided gap-spotting.
- ssl arm: the same, but the detector's accepted gap-seeds are supplied to weave
  in.

Two readouts:

1. **Detector added value** = the fraction of detected gaps the *baseline* model
   did NOT already surface (semantic coverage). High baseline coverage ⇒ the
   detector adds little over a strong model; low ⇒ the detector found things the
   model missed.
2. Blind A/B answer pairs for human/AI review of overall analysis quality.

Honest: the detected gaps are the "ground truth" here, so the ssl arm trivially
contains them — the informative number is the baseline's own coverage and the
blind reader's preference, not ssl coverage.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from shadowseed.benchmark.ssl45_model_benefit_suite import blind_order, make_backend, word_count


def build_wild_baseline_prompt(text: str) -> str:
    return (
        "Lees dit korte bericht. Geef een beknopte analyse en benoem expliciet "
        "welke cruciale informatie ontbreekt voor een volledig begrip.\n\n"
        f"Bericht:\n{text}\n\n"
        "Analyse:"
    )


def build_wild_ssl_prompt(text: str, seeds: list[str]) -> str:
    block = "\n".join(f"- {s}" for s in seeds)
    return (
        "Lees dit korte bericht en schrijf een beknopte analyse die expliciet "
        "benoemt welke cruciale informatie ontbreekt voor een volledig begrip.\n"
        "Verwerk daarbij elk van de onderstaande ontbrekende punten op een "
        "natuurlijke manier in lopende tekst.\n"
        "Regels: verzin geen feiten buiten het bericht; verwijs niet naar "
        "'seeds', 'punten' of deze instructie; lever één samenhangende analyse.\n\n"
        f"Bericht:\n{text}\n\n"
        f"Te benoemen ontbrekende punten:\n{block}\n\n"
        "Analyse:"
    )


def run_wild_payoff_suite(
    input_path: str,
    output_path: str,
    *,
    backend: str = "fixture",
    model_id: str | None = None,
    max_new_tokens: int = 400,
    semantic_embedding_backend: str = "none",
    embedding_model: str | None = None,
    semantic_threshold: float = 0.55,
) -> Path:
    data = json.loads(Path(input_path).read_text(encoding="utf-8"))
    model = make_backend(backend=backend, model_id=model_id, max_new_tokens=max_new_tokens)

    embed_fn = None
    if semantic_embedding_backend != "none":
        from shadowseed.benchmark.embedding_backends import make_embedding_fn

        embed_fn, _dim = make_embedding_fn(semantic_embedding_backend, embedding_model)

    results: list[dict[str, Any]] = []
    blind_items: list[dict[str, Any]] = []
    blind_key: list[dict[str, Any]] = []
    baseline_cov_values: list[float] = []

    for item in data["items"]:
        iid = item["id"]
        text = item["text"]
        seeds = item["detected_seeds"]

        baseline = model.generate(build_wild_baseline_prompt(text), item, "baseline", [])
        ssl = model.generate(build_wild_ssl_prompt(text, seeds), item, "ssl", seeds)

        baseline_cov = None
        novel_gaps = None
        if embed_fn is not None:
            from shadowseed.benchmark.semantic_coverage import semantic_coverage

            frac, covered, per_gap = semantic_coverage(baseline, seeds, embed_fn, semantic_threshold)
            baseline_cov = frac
            novel_gaps = [g["gap"] for g in per_gap if not g["covered"]]
            baseline_cov_values.append(frac)

        first, second = blind_order(iid)
        amap = {"baseline": baseline, "ssl": ssl}
        blind_items.append(
            {
                "review_id": f"review_{iid}",
                "scenario_id": iid,
                "question": f"Welke cruciale informatie ontbreekt in dit bericht?\n\nBericht: {text}",
                "option_a": amap[first],
                "option_b": amap[second],
                "reviewer_instruction": (
                    "Kies welke analyse de ontbrekende informatie scherper en "
                    "juister benoemt. Beloon geen lengte; verzonnen of irrelevante "
                    "punten maken een analyse slechter."
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
                "detected_seeds": seeds,
                "baseline_gap_coverage": baseline_cov,
                "detector_novel_gaps": novel_gaps,
                "answer_length_delta_words": word_count(ssl) - word_count(baseline),
                "baseline_answer": baseline,
                "ssl_answer": ssl,
            }
        )

    summary = {
        "artifact": "wild_payoff_suite",
        "backend": getattr(model, "name", backend),
        "item_count": len(results),
        "source": data.get("source", ""),
        "semantic_embedding_backend": semantic_embedding_backend,
        "mean_baseline_gap_coverage": (
            sum(baseline_cov_values) / len(baseline_cov_values) if baseline_cov_values else None
        ),
        "interpretation": (
            "W1 wild loop: detected (not author-designed) gap-seeds through the "
            "payoff pipeline. mean_baseline_gap_coverage = how much of the "
            "detector's gaps a strong model already finds unaided; LOW means the "
            "detector adds value the model missed. Blind A/B pairs judge overall "
            "analysis quality. Signal, not proof; detected gaps are the ground "
            "truth so ssl coverage is not informative on its own."
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
