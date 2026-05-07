from __future__ import annotations

import json
from pathlib import Path

from shadowseed.benchmark.open_set_seed_review import run_open_set_seed_review


DATA = "src/shadowseed/data/open_set_seed_review_sample.json"


def test_open_set_seed_review_outputs_packets(tmp_path: Path) -> None:
    output = tmp_path / "open_set.json"
    packets = tmp_path / "open_set_packets.json"
    run_open_set_seed_review(DATA, str(output), review_packet_path=str(packets))

    payload = json.loads(output.read_text(encoding="utf-8"))
    review_payload = json.loads(packets.read_text(encoding="utf-8"))

    assert payload["summary"]["item_count"] == 3
    assert payload["summary"]["accepted_count"] > 0
    assert payload["summary"]["rejected_count"] > 0
    assert review_payload["summary"]["packet_count"] == payload["summary"]["review_packet_count"]
    assert review_payload["packets"][0]["review_status"] == "pending"
