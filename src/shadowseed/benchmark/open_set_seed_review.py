"""Open-set seed quality review scaffold for SSL 4.5."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from shadowseed.benchmark.ssl45_gap_suite import detect_candidate_seeds
from shadowseed.hash_utils import stable_bucket_index
from shadowseed.manager import SSLManager


REVIEW_CRITERIA = [
    "atomicity",
    "relevance",
    "testability",
    "non_triviality",
    "follow_up_utility",
]
REJECT_CODES = [
    "too_broad",
    "too_vague",
    "trivial",
    "not_relevant",
    "not_testable",
    "duplicate",
    "style_not_gap",
]
DEFAULT_REVIEWER_IDS = ["reviewer_a", "reviewer_b"]
EVIDENCE_LAYER = "open_set_seed_quality"
ARTIFACT_CONTRACT_VERSION = "open-review-0.2"


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


def _normalize_reviewer_ids(reviewer_ids: list[str] | tuple[str, ...] | None) -> list[str]:
    ids = reviewer_ids or DEFAULT_REVIEWER_IDS
    normalized: list[str] = []
    seen: set[str] = set()
    for reviewer_id in ids:
        clean = str(reviewer_id).strip()
        if clean and clean not in seen:
            normalized.append(clean)
            seen.add(clean)
    if not normalized:
        raise ValueError("At least one reviewer id is required for open-set review packets.")
    return normalized


def _review_entry(
    item: dict[str, Any],
    seed_row: dict[str, Any],
    reviewer_id: str,
    reviewer_slot: int,
) -> dict[str, Any]:
    excerpt = (item.get("text") or item.get("input") or "").strip()
    excerpt = excerpt[:400] + ("..." if len(excerpt) > 400 else "")
    return {
        "item_id": item.get("id"),
        "title": item.get("title"),
        "domain": item.get("domain"),
        "source_excerpt": excerpt,
        "seed_id": seed_row.get("seed_id"),
        "seed_text": seed_row.get("text"),
        "reviewer_id": reviewer_id,
        "reviewer_slot": reviewer_slot,
        "review_fields": {criterion: None for criterion in REVIEW_CRITERIA},
        "review_status": "pending",
        "reject_reason": None,
        "reviewer_notes": "",
    }


def run_open_set_seed_review(
    input_path: str,
    output_path: str,
    review_packet_path: str | None = None,
    reviewer_ids: list[str] | tuple[str, ...] | None = None,
) -> Path:
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    items = payload.get("items", [])
    reviewer_ids_normalized = _normalize_reviewer_ids(reviewer_ids)
    results = []
    review_packets = []
    raw_candidate_count = 0
    normalized_candidate_count = 0
    accepted_count = 0
    rejected_count = 0
    domain_accept_counts: dict[str, int] = {}
    domain_item_counts: dict[str, int] = {}

    for item in items:
        manager = SSLManager(embedding_fn=detect_embedding)
        raw_candidates = _raw_candidates(item)
        ingest = manager.ingest_detection_candidates(raw_candidates)
        raw_candidate_count += ingest["input_count"]
        normalized_candidate_count += len(ingest["normalized_candidates"])
        accepted_count += len(ingest["accepted"])
        rejected_count += len(ingest["rejected"])
        domain = item.get("domain", "unknown")
        domain_item_counts[domain] = domain_item_counts.get(domain, 0) + 1
        domain_accept_counts[domain] = domain_accept_counts.get(domain, 0) + len(ingest["accepted"])

        for accepted in ingest["accepted"]:
            for reviewer_slot, reviewer_id in enumerate(reviewer_ids_normalized, start=1):
                review_packets.append(_review_entry(item, accepted, reviewer_id, reviewer_slot))

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

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    review_packet_file = Path(review_packet_path) if review_packet_path else output.with_name(output.stem + "_review_packets.json")
    review_packet_file.parent.mkdir(parents=True, exist_ok=True)

    summary = {
        "evidence_layer": EVIDENCE_LAYER,
        "artifact_contract_version": ARTIFACT_CONTRACT_VERSION,
        "corpus_version": payload.get("version"),
        "item_count": len(items),
        "raw_candidate_count": raw_candidate_count,
        "normalized_candidate_count": normalized_candidate_count,
        "accepted_count": accepted_count,
        "rejected_count": rejected_count,
        "acceptance_rate": (accepted_count / normalized_candidate_count) if normalized_candidate_count else 0.0,
        "domain_item_counts": domain_item_counts,
        "domain_accept_counts": domain_accept_counts,
        "reviewer_ids": reviewer_ids_normalized,
        "reviewer_count": len(reviewer_ids_normalized),
        "review_packet_count": len(review_packets),
        "review_criteria": REVIEW_CRITERIA,
        "reject_codes": REJECT_CODES,
        "status": "review_pending",
        "next_step": "Fill review packets and run summarize-open-set-seed-review.",
        "artifacts": {
            "seed_output": str(output),
            "review_packets": str(review_packet_file),
        },
    }

    output.write_text(json.dumps({"summary": summary, "results": results}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    review_packet_file.write_text(
        json.dumps(
            {
                "summary": {
                    "evidence_layer": EVIDENCE_LAYER,
                    "artifact_contract_version": ARTIFACT_CONTRACT_VERSION,
                    "item_count": len(items),
                    "seed_count": accepted_count,
                    "reviewer_ids": reviewer_ids_normalized,
                    "reviewer_count": len(reviewer_ids_normalized),
                    "packet_count": len(review_packets),
                    "criteria": REVIEW_CRITERIA,
                    "reject_codes": REJECT_CODES,
                    "instructions": (
                        "One packet row is generated per reviewer per seed. "
                        "Do not edit a single row sequentially for multiple reviewers. "
                        "Score each seed on atomicity, relevance, testability, "
                        "non-triviality and follow-up utility."
                    ),
                    "status": "review_pending",
                    "expected_summary_artifacts": [
                        "open_set_seed_review_summary.json",
                        "open_set_disagreements.json",
                        "open_set_review_report.md",
                    ],
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
        vector[stable_bucket_index(token, dims)] += 1.0
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm
