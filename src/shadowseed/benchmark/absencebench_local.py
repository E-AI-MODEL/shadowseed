"""Local lightweight AbsenceBench runner for reproducible scoring."""

from __future__ import annotations

import json
from pathlib import Path

from .result_writer import ResultWriter
from .schemas import BenchmarkResult
from .run_types import RunType, ExecutionStatus


def run_local_absencebench(input_path: str, output_path: str) -> Path:
    data = json.loads(Path(input_path).read_text(encoding="utf-8"))

    scenarios = data.get("scenarios", [])
    if not scenarios:
        raise ValueError("Geen scenarios gevonden in input JSON")

    total = len(scenarios)
    detected = sum(1 for s in scenarios if s.get("detected") is True)

    score = detected / total if total > 0 else 0.0

    result = BenchmarkResult(
        benchmark_name="AbsenceBench",
        run_type=RunType.SCAN.value,
        execution_status=ExecutionStatus.SCAN.value,
        ssl_input_basis=["local-json"],
        host_platform="local",
        dataset_status="lokaal",
        runner_status="lokale runner",
        score=score,
        score_type="simple ratio",
        interpretation="Lokale benadering van absence detectie",
        limitations=["geen echte upstream runner"],
        execution_gap=False,
    )

    return ResultWriter().write_result(result, output_path)
