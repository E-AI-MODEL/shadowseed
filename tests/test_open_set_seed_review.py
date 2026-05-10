from __future__ import annotations

import json
from pathlib import Path

from shadowseed.benchmark.open_set_seed_review import run_open_set_seed_review


DATA = "src/shadowseed/data/open_set_seed_review_sample.json"


def _seed_key(packet: dict) -> tuple[str, str]:
    return (str(packet["item_id"]), str(packet["seed_text"]))


def test_open_set_seed_review_outputs_packets(tmp_path: Path) -> None:
    output = tmp_path / "open_set.json"
    packets = tmp_path / "open_set_packets.json"
    run_open_set_seed_review(DATA, str(output), review_packet_path=str(packets))

    payload = json.loads(output.read_text(encoding="utf-8"))
    review_payload = json.loads(packets.read_text(encoding="utf-8"))

    assert payload["summary"]["evidence_layer"] == "open_set_seed_quality"
    assert payload["summary"]["artifact_contract_version"] == "open-review-0.2"
    assert payload["summary"]["item_count"] == 3
    assert payload["summary"]["accepted_count"] > 0
    assert payload["summary"]["rejected_count"] > 0
    assert payload["summary"]["reviewer_ids"] == ["reviewer_a", "reviewer_b"]
    assert payload["summary"]["reviewer_count"] == 2
    assert payload["summary"]["review_packet_count"] == review_payload["summary"]["packet_count"]
    assert payload["summary"]["review_packet_count"] == payload["summary"]["accepted_count"] * 2
    assert payload["summary"]["artifacts"]["seed_output"] == str(output)
    assert payload["summary"]["artifacts"]["review_packets"] == str(packets)
    assert review_payload["summary"]["reject_codes"]
    assert review_payload["summary"]["seed_count"] == payload["summary"]["accepted_count"]
    assert review_payload["summary"]["reviewer_ids"] == ["reviewer_a", "reviewer_b"]
    assert review_payload["summary"]["reviewer_count"] == 2
    assert review_payload["summary"]["expected_summary_artifacts"] == [
        "open_set_seed_review_summary.json",
        "open_set_disagreements.json",
        "open_set_review_report.md",
    ]
    assert review_payload["packets"][0]["review_status"] == "pending"
    assert "reviewer_id" in review_payload["packets"][0]
    assert "reviewer_slot" in review_payload["packets"][0]
    assert "reject_reason" in review_payload["packets"][0]

    reviewers_by_seed: dict[tuple[str, str], set[str]] = {}
    slots_by_seed: dict[tuple[str, str], set[int]] = {}
    for packet in review_payload["packets"]:
        key = _seed_key(packet)
        reviewers_by_seed.setdefault(key, set()).add(packet["reviewer_id"])
        slots_by_seed.setdefault(key, set()).add(packet["reviewer_slot"])

    assert reviewers_by_seed
    assert all(reviewers == {"reviewer_a", "reviewer_b"} for reviewers in reviewers_by_seed.values())
    assert all(slots == {1, 2} for slots in slots_by_seed.values())


def test_open_set_seed_review_accepts_custom_reviewer_ids(tmp_path: Path) -> None:
    output = tmp_path / "open_set.json"
    packets = tmp_path / "open_set_packets.json"
    run_open_set_seed_review(
        DATA,
        str(output),
        review_packet_path=str(packets),
        reviewer_ids=["alpha", "beta", "alpha", ""],
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    review_payload = json.loads(packets.read_text(encoding="utf-8"))

    assert payload["summary"]["reviewer_ids"] == ["alpha", "beta"]
    assert payload["summary"]["reviewer_count"] == 2
    assert review_payload["summary"]["reviewer_ids"] == ["alpha", "beta"]
    assert review_payload["summary"]["packet_count"] == payload["summary"]["accepted_count"] * 2

    reviewers_by_seed: dict[tuple[str, str], set[str]] = {}
    for packet in review_payload["packets"]:
        reviewers_by_seed.setdefault(_seed_key(packet), set()).add(packet["reviewer_id"])

    assert all(reviewers == {"alpha", "beta"} for reviewers in reviewers_by_seed.values())
