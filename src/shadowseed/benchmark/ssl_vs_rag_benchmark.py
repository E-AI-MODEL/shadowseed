"""SSL-vs-RAG head-to-head (vision gap 3): does retrieving toward the *gap* beat
retrieving toward the *question*?

This is the experiment that tests the core claim — "a shadow seed finds a better
answer than an LLM with ordinary RAG would". It isolates one variable: the same
model and the same retrieval-prompt template answer the same question, differing
only in WHICH context was retrieved:

- RAG arm: query = the question (ordinary retrieval);
- SSL-probe arm: query = the seed(s)/gap (the gat-2 bridge).

Both answers go into a blind, order-shuffled pair (reusing the round-008
machinery) and `scripts/answer_pair_winrate.py` reports whether the SSL-probe
arm wins. A deterministic, model-free cross-check reports, per item, the chunks
the seed probe surfaced that the question retrieval did not (`seed_only`).

Default backend is ``fixture`` (CI-safe); ``hf-transformers`` is the real run.
This produces a signal, not proof: small n, reader-judged.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from shadowseed.benchmark.retrieval_model_benchmark import (
    build_retrieval_prompt,
    index_retrieval_corpus,
    make_output_model,
    model_generate,
)
from shadowseed.benchmark.seed_retrieval_probe import retrieval_probe_vs_question
from shadowseed.benchmark.ssl45_model_benefit_suite import blind_order, word_count
from shadowseed.vectorstore import create_vector_store


def _chunks_from_hits(hits: list[dict[str, Any]]) -> list[str]:
    return [h["text"] for h in hits if h.get("text")]


def run_ssl_vs_rag_benchmark(
    data_path: str,
    output_path: str,
    *,
    model_backend: str = "fixture",
    model_id: str | None = None,
    max_new_tokens: int = 220,
    top_k: int = 3,
    use_centroid: bool = False,
    vector_backend: str = "memory",
) -> Path:
    data = json.loads(Path(data_path).read_text(encoding="utf-8"))
    store = create_vector_store(backend=vector_backend, dimensions=128)
    index_retrieval_corpus(store, data)
    model = make_output_model(model_backend, model_id, max_new_tokens)

    results: list[dict[str, Any]] = []
    blind_items: list[dict[str, Any]] = []
    blind_key: list[dict[str, Any]] = []

    for item in data["items"]:
        qid = item["id"]
        question = item["question"]
        seeds = item["seed_texts"]

        contrast = retrieval_probe_vs_question(
            store, question, seeds, top_k=top_k, use_centroid=use_centroid
        )
        rag_chunks = _chunks_from_hits(contrast["question_hits"])
        probe_chunks = _chunks_from_hits(contrast["probe_hits"])

        rag_answer = model_generate(
            model, build_retrieval_prompt(question, rag_chunks), rag_chunks, "retrieval"
        )
        probe_answer = model_generate(
            model, build_retrieval_prompt(question, probe_chunks), probe_chunks, "retrieval"
        )

        # blind pair: baseline arm = RAG, ssl arm = SSL-probe (so the round-008
        # answer_pair_winrate scorer reports ssl_win_rate = probe beats RAG).
        first, second = blind_order(qid)
        answers = {"baseline": rag_answer, "ssl": probe_answer}
        blind_items.append(
            {
                "review_id": f"review_{qid}",
                "scenario_id": qid,
                "question": question,
                "option_a": answers[first],
                "option_b": answers[second],
                "reviewer_instruction": (
                    "Kies welk antwoord de vraag inhoudelijk beter beantwoordt. "
                    "Let op juistheid en dekking; beloon geen lengte alleen."
                ),
                "scores_to_fill": {"better_answer": "A/B/tie", "notes": ""},
            }
        )
        blind_key.append(
            {"review_id": f"review_{qid}", "option_a_source": first, "option_b_source": second}
        )
        results.append(
            {
                "scenario_id": qid,
                "question": question,
                "seed_texts": seeds,
                "answer_length_delta_words": word_count(probe_answer) - word_count(rag_answer),
                "rag_chunk_ids": contrast["question_chunk_ids"],
                "probe_chunk_ids": contrast["probe_chunk_ids"],
                "seed_only_chunk_ids": contrast["seed_only_chunk_ids"],
                "rag_answer": rag_answer,
                "ssl_probe_answer": probe_answer,
            }
        )

    payload = {
        "summary": {
            "artifact": "ssl_vs_rag_benchmark",
            "backend": getattr(model, "name", model_backend),
            "item_count": len(results),
            "top_k": top_k,
            "use_centroid": use_centroid,
            "interpretation": (
                "Gap 3 head-to-head. baseline arm = ordinary RAG (query=question); "
                "ssl arm = SSL Retrieval Probe (query=gap). Fill better_answer in "
                "blind_review_items and score with scripts/answer_pair_winrate.py "
                "(ssl_win_rate = SSL-probe beats RAG). seed_only_chunk_ids is the "
                "deterministic, model-free signal that the probe reached context the "
                "question did not. Signal, not proof."
            ),
        },
        "results": results,
        "blind_review_items": blind_items,
        "blind_answer_key": blind_key,
    }
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
