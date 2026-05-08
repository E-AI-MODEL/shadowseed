import json
from pathlib import Path
import subprocess
import sys


def test_cli_prepare(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "shadowseed.cli", "prepare-absencebench", "--output", "test.json"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_cli_local(tmp_path):
    data = {"scenarios": [{"detected": True}, {"detected": False}]}
    input_file = tmp_path / "input.json"
    input_file.write_text(json.dumps(data))

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "shadowseed.cli",
            "run-local-absencebench",
            "--input",
            str(input_file),
            "--output",
            "local.json",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_cli_open_set_review_summary(tmp_path):
    review_packets = {
        "summary": {"packet_count": 1},
        "packets": [
            {
                "item_id": "OPEN_LAW_001",
                "title": "Consumentenrecht zonder procedurele uitwerking",
                "domain": "recht en jurisdictie",
                "seed_id": "ss_001",
                "seed_text": "Toepasselijk recht bij een grensoverschrijdend consumentencontract.",
                "reviewer_id": "reviewer_a",
                "review_status": "accepted",
                "review_fields": {
                    "atomicity": True,
                    "relevance": True,
                    "testability": True,
                    "non_triviality": True,
                    "follow_up_utility": True,
                },
                "reject_reason": None,
                "reviewer_notes": "Sterke seed.",
            }
        ],
    }
    input_file = tmp_path / "review_packets.json"
    output_file = tmp_path / "review_summary.json"
    disagreements_file = tmp_path / "review_disagreements.json"
    input_file.write_text(json.dumps(review_packets), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "shadowseed.cli",
            "summarize-open-set-seed-review",
            "--input",
            str(input_file),
            "--output",
            str(output_file),
            "--disagreements-output",
            str(disagreements_file),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert output_file.exists()
    assert disagreements_file.exists()
