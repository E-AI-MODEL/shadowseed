"""Open-set seed quality review scaffold for SSL 4.5.

This runner is intentionally simple. It does not claim to solve open-world
validation; it creates the first honest bridge away from fixed ground-truth
scenario scoring by producing:

- candidate seeds for unknown texts;
- normalization and atomicity filtering results;
- reviewer packets with explicit scoring fields;
- run artifacts that can be compared across domains.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from shadowseed.benchmark.ssl45_gap_suite import detect_candidate_seeds
from shadowseed.manager import SSLManager


REVIEW_CRITERIA = [
    "atomicity",
    "relevance",
    "testability",
    "non_triviality",
    "follow_up_utility",
]


def _scenario_like_record(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("id", "unknown"),
        "title": item.get("title", "Untitled"),
        "domain": item.get("domain", ""),
        "input": item.get("text") or item.get("input") or "",
    }


def _raw_candidates(item: dict[str, Any]) -> list[str]:
    explicit = item.get("candidate_seeds")
    if isinstance(explicit, list) and explicit:
        return [str(seed).strip() for seed in explicit if str(seed).strip()]
    scenario = _scenario_like_record(item)
    if scenario["domain"] and scenario["input"]:
        return detect_candidate_seeds(scenario)
    return []


def _review_entry(item: dict[str, Any], seed_row: dict[str, Any]) -> dict[str, Any]:
    excerpt = (item.get("text") or item.get("input") or "").strip()
    excerpt = excerpt[:400] + ("..." if len(excerpt) > 400 else "")
    return {
        "item_id": item.get("id"),
        "title": item.get("title"),
        "domain": item.get("domain"),
        "source_excerpt": excerpt,
        "seed_id": seed_row.get("seed_id"),
        "seed_text": seed_row.get("text"),
        "review_fields": {criterion: None for criterion in REVIEW_CRITERIA},
        "review_status": "pending",
        "reviewer_notes": "",
    }


def run_open_set_seed_review(
    input_path: str,
    output_path: str,
    review_packet_path: str | None = None,
) -> Path:
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    items = payload.get("items", [])
    results = []
    review_packets = []

    raw_candidate_count = 0
    normalized_candidate_count = 0
    accepted_count = 0
    rejected_count = 0
    domain_counts: dict[str, int] = {}

    for item in items:
        manager = SSLManager(embedding_fn=detect_embedding)
        raw_candidates = _raw_candidates(item)
        ingest = manager.ingest_detection_candidates(raw_candidates)
        raw_candidate_count += ingest["input_count"]
        normalized_candidate_count += len(ingest["normalized_candidates"])
        accepted_count += len(ingest["accepted"])
        rejected_count += len(ingest["rejected"])
        domain = item.get("domain", "unknown")
        domain_counts[domain] = domain_counts.get(domain, 0) + len(ingest["accepted"])

        for accepted in ingest["accepted"]:
            review_packets.append(_review_entry(item, accepted))

        results.append(
            {
                "item_id": item.get("id"),
                "title": item.get("title"),
                "domain": domain,
                "raw_candidates": raw_candidates,
                "normalized_candidates": ingest["normalized_candidates"],
                "accepted": ingest["accepted"],
                "rejected": ingest["rejected"],
            }
        )

    summary = {
        "corpus_version": payload.get("version"),
        "item_count": len(items),
        "raw_candidate_count": raw_candidate_count,
        "normalized_candidate_count": normalized_candidate_count,
        "accepted_count": accepted_count,
        "rejected_count": rejected_count,
        "acceptance_rate": (accepted_count / normalized_candidate_count) if normalized_candidate_count else 0.0,
        "domain_accept_counts": domain_counts,
        "review_packet_count": len(review_packets),
        "review_criteria": REVIEW_CRITERIA,
        "status": "review_pending",
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"summary": summary, "results": results}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    review_packet_file = Path(review_packet_path) if review_packet_path else output.with_name(output.stem + "_review_packets.json")
    review_packet_file.parent.mkdir(parents=True, exist_ok=True)
    review_packet_file.write_text(
        json.dumps(
            {
                "summary": {
                    "item_count": len(items),
                    "packet_count": len(review_packets),
                    "criteria": REVIEW_CRITERIA,
                    "instructions": "Score each seed on atomicity, relevance, testability, non-triviality and follow-up utility.",
                },
                "packets": review_packets,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return output


def detect_embedding(text: str) -> np.ndarray:
    """Cheap deterministic lexical embedding for review scaffolding."""
    dims = 128
    vector = np.zeros(dims, dtype=float)
    for token in text.lower().split():
        vector[hash(token) % dims] += 1.0
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm
