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
