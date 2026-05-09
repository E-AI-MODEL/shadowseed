"""Aggregate completed open-set review packets into usable evaluation summaries."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from shadowseed.benchmark.open_set_seed_review import REVIEW_CRITERIA


ACCEPT_STATES = {"accept", "accepted", "approved", "pass", "passed"}
REJECT_STATES = {"reject", "rejected", "failed", "fail"}
TRUE_VALUES = {"true", "yes", "y", "1", "pass", "passed", "accept", "accepted"}
FALSE_VALUES = {"false", "no", "n", "0", "fail", "failed", "reject", "rejected"}


def _normalize_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        if value == 1:
            return True
        if value == 0:
            return False
        return None
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in TRUE_VALUES:
            return True
        if lowered in FALSE_VALUES:
            return False
    return None


def _packet_decision(packet: dict[str, Any]) -> str:
    review_status = str(packet.get("review_status") or "").strip().lower()
    reject_reason = packet.get("reject_reason")
    fields = packet.get("review_fields", {})
    normalized = [_normalize_bool(fields.get(criterion)) for criterion in REVIEW_CRITERIA]

    if review_status == "pending":
        return "pending"
    if review_status in ACCEPT_STATES:
        return "accepted"
    if review_status in REJECT_STATES:
        return "rejected"
    if reject_reason:
        return "rejected"
    if normalized and all(value is True for value in normalized):
        return "accepted"
    if any(value is False for value in normalized):
        return "rejected"
    return "pending"


def _pairwise_agreement_ratio(values: list[str]) -> float | None:
    if len(values) < 2:
        return None
    total_pairs = 0
    matching_pairs = 0
    for index, left in enumerate(values):
        for right in values[index + 1 :]:
            total_pairs += 1
            if left == right:
                matching_pairs += 1
    return (matching_pairs / total_pairs) if total_pairs else None


def summarize_open_set_seed_review(
    review_packet_path: str,
    output_path: str,
    disagreements_output_path: str | None = None,
) -> Path:
    payload = json.loads(Path(review_packet_path).read_text(encoding="utf-8"))
    packets = payload.get("packets", [])

    by_seed: dict[tuple[str, str], dict[str, Any]] = {}
    reviewer_ids: set[str] = set()
    reject_reason_counter: Counter[str] = Counter()
    criterion_completed_counts: Counter[str] = Counter()
    criterion_true_counts: Counter[str] = Counter()
    domain_seed_counts: Counter[str] = Counter()

    packet_count = len(packets)
    completed_packet_count = 0
    accepted_packet_count = 0
    rejected_packet_count = 0

    for packet in packets:
        key = (str(packet.get("item_id") or "unknown"), str(packet.get("seed_text") or ""))
        entry = by_seed.setdefault(
            key,
            {
                "item_id": packet.get("item_id"),
                "title": packet.get("title"),
                "domain": packet.get("domain"),
                "seed_id": packet.get("seed_id"),
                "seed_text": packet.get("seed_text"),
                "reviewers": [],
                "criterion_true_counts": {criterion: 0 for criterion in REVIEW_CRITERIA},
                "criterion_false_counts": {criterion: 0 for criterion in REVIEW_CRITERIA},
                "criterion_pending_counts": {criterion: 0 for criterion in REVIEW_CRITERIA},
                "reject_reason_counts": {},
            },
        )
        reviewer_id = str(packet.get("reviewer_id") or "unknown")
        reviewer_ids.add(reviewer_id)
        decision = _packet_decision(packet)
        fields = packet.get("review_fields", {})
        reject_reason = packet.get("reject_reason")

        reviewer_row = {
            "reviewer_id": reviewer_id,
            "review_status": packet.get("review_status", "pending"),
            "decision": decision,
            "review_fields": fields,
            "reject_reason": reject_reason,
            "reviewer_notes": packet.get("reviewer_notes", ""),
        }
        entry["reviewers"].append(reviewer_row)

        if decision != "pending":
            completed_packet_count += 1
        if decision == "accepted":
            accepted_packet_count += 1
        elif decision == "rejected":
            rejected_packet_count += 1

        for criterion in REVIEW_CRITERIA:
            normalized = _normalize_bool(fields.get(criterion))
            if normalized is True:
                entry["criterion_true_counts"][criterion] += 1
                criterion_true_counts[criterion] += 1
                criterion_completed_counts[criterion] += 1
            elif normalized is False:
                entry["criterion_false_counts"][criterion] += 1
                criterion_completed_counts[criterion] += 1
            else:
                entry["criterion_pending_counts"][criterion] += 1

        if reject_reason:
            reject_reason_counter[str(reject_reason)] += 1
            local_counter = Counter(entry["reject_reason_counts"])
            local_counter[str(reject_reason)] += 1
            entry["reject_reason_counts"] = dict(local_counter)

    accepted_seed_count = 0
    rejected_seed_count = 0
    mixed_seed_count = 0
    pending_seed_count = 0
    unanimous_seed_count = 0
    agreement_eligible_seed_count = 0
    pairwise_decision_agreement_sum = 0.0
    disagreements: list[dict[str, Any]] = []
    aggregated_results: list[dict[str, Any]] = []

    for entry in by_seed.values():
        decisions = [reviewer["decision"] for reviewer in entry["reviewers"] if reviewer["decision"] != "pending"]
        domain = str(entry.get("domain") or "unknown")
        domain_seed_counts[domain] += 1

        if not decisions:
            verdict = "pending"
            pending_seed_count += 1
        elif all(decision == "accepted" for decision in decisions):
            verdict = "accepted"
            accepted_seed_count += 1
        elif all(decision == "rejected" for decision in decisions):
            verdict = "rejected"
            rejected_seed_count += 1
        else:
            verdict = "mixed"
            mixed_seed_count += 1

        pairwise_decision_agreement = _pairwise_agreement_ratio(decisions)
        if len(decisions) >= 2:
            agreement_eligible_seed_count += 1
            if len(set(decisions)) == 1:
                unanimous_seed_count += 1
            if pairwise_decision_agreement is not None:
                pairwise_decision_agreement_sum += pairwise_decision_agreement
            else:
                pairwise_decision_agreement = 0.0
            if len(set(decisions)) != 1:
                disagreements.append(
                    {
                        "item_id": entry["item_id"],
                        "title": entry["title"],
                        "domain": entry["domain"],
                        "seed_id": entry["seed_id"],
                        "seed_text": entry["seed_text"],
                        "decisions": decisions,
                        "pairwise_decision_agreement": pairwise_decision_agreement,
                        "reviewers": entry["reviewers"],
                    }
                )

        entry["completed_reviewer_count"] = len(decisions)
        entry["reviewer_count"] = len(entry["reviewers"])
        entry["aggregate_verdict"] = verdict
        entry["pairwise_decision_agreement"] = pairwise_decision_agreement
        aggregated_results.append(entry)

    summary = {
        "packet_count": packet_count,
        "completed_packet_count": completed_packet_count,
        "pending_packet_count": packet_count - completed_packet_count,
        "accepted_packet_count": accepted_packet_count,
        "rejected_packet_count": rejected_packet_count,
        "packet_acceptance_rate": (accepted_packet_count / completed_packet_count) if completed_packet_count else 0.0,
        "unique_seed_count": len(aggregated_results),
        "accepted_seed_count": accepted_seed_count,
        "rejected_seed_count": rejected_seed_count,
        "mixed_seed_count": mixed_seed_count,
        "pending_seed_count": pending_seed_count,
        "seed_acceptance_rate": (accepted_seed_count / len(aggregated_results)) if aggregated_results else 0.0,
        "seed_rejection_rate": (rejected_seed_count / len(aggregated_results)) if aggregated_results else 0.0,
        "agreement_eligible_seed_count": agreement_eligible_seed_count,
        "unanimous_seed_count": unanimous_seed_count,
        "unanimous_verdict_rate": (unanimous_seed_count / agreement_eligible_seed_count) if agreement_eligible_seed_count else 0.0,
        "pairwise_decision_agreement_rate": (
            pairwise_decision_agreement_sum / agreement_eligible_seed_count
        ) if agreement_eligible_seed_count else 0.0,
        "criteria": REVIEW_CRITERIA,
        "criterion_pass_rates": {
            criterion: (criterion_true_counts[criterion] / criterion_completed_counts[criterion])
            if criterion_completed_counts[criterion]
            else 0.0
            for criterion in REVIEW_CRITERIA
        },
        "reject_reason_counts": dict(reject_reason_counter),
        "reviewer_ids": sorted(reviewer_ids),
        "domain_seed_counts": dict(domain_seed_counts),
        "status": "review_complete" if packet_count and completed_packet_count == packet_count else "review_in_progress",
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"summary": summary, "results": aggregated_results}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    disagreements_output = Path(disagreements_output_path) if disagreements_output_path else output.with_name(output.stem + "_disagreements.json")
    disagreements_output.parent.mkdir(parents=True, exist_ok=True)
    disagreements_output.write_text(
        json.dumps(
            {
                "summary": {
                    "disagreement_count": len(disagreements),
                    "agreement_eligible_seed_count": agreement_eligible_seed_count,
                    "unanimous_verdict_rate": summary["unanimous_verdict_rate"],
                    "pairwise_decision_agreement_rate": summary["pairwise_decision_agreement_rate"],
                },
                "disagreements": disagreements,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return output
