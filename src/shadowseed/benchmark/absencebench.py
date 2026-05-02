"""AbsenceBench preparation helpers for the Shadow Seed Learning benchmark lane."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from importlib import resources
from pathlib import Path

from .run_types import ExecutionStatus, RunType


@dataclass
class AbsenceBenchPreparation:
    benchmark_name: str = "AbsenceBench"
    run_type: str = RunType.PREPARATION.value
    execution_status: str = ExecutionStatus.PREPARATION.value
    repo_status: str = "te verifiëren"
    execution_gap_aanwezig: bool = True
    ssl_sources: list[str] = field(
        default_factory=lambda: [
            "shadow_seed_learning_4_5_clean.md",
            "ssl_4_5_public_release/",
            "benchmark_bibliotheek/",
        ]
    )
    data_host: str = "Hugging Face dataset: harveyfin/AbsenceBench"
    paper_host: str = "Hugging Face paper: 2506.11440"
    code_host: str = "GitHub repo: harvey-fin/absence-bench"
    public_site: str = "absencebench.github.io"
    dataset_status: str = "bibliografisch vastgelegd"
    runner_route: str = "README + evaluate.py aanwezig, live route nog niet hard geverifieerd"
    runner_status: str = "runnerstructuur aanwezig"
    startcommando: str = (
        "python evaluate.py --model_family <provider> --model <model> "
        "--in_dir tests --out_dir results"
    )
    score_type: str = "F1 of benchmarkoutput uit upstream runner"
    missing_components: list[str] = field(
        default_factory=lambda: [
            "actuele live hostverificatie",
            "end-to-end runneruitvoering vanuit deze repo of gecontroleerde adapter",
            "provider- en modelkeuze voor baseline",
            "provider- en modelkeuze voor ssl_condition",
            "score-output mapping van upstream runner naar shadowseed schema",
        ]
    )
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AbsenceBenchRunCard:
    benchmark_name: str
    run_type: str
    execution_status: str
    host_platform: str
    ssl_input_basis: list[str]
    baseline_label: str
    ssl_condition_label: str
    dataset_status: str
    runner_status: str
    execution_gap: bool
    scenarios_loaded: int
    start_command_template: str
    notes: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def load_gap_test_suite() -> dict:
    with resources.files("shadowseed.data").joinpath("gap_test_suite_4_5.json").open(
        "r", encoding="utf-8"
    ) as handle:
        return json.load(handle)


def load_gap_test_suite_from_path(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_preparation_record() -> dict:
    """Build a reproducible preparation record without claiming a live benchmark run."""
    return AbsenceBenchPreparation().to_dict()


def build_run_card() -> AbsenceBenchRunCard:
    suite = load_gap_test_suite()
    return AbsenceBenchRunCard(
        benchmark_name="AbsenceBench",
        run_type=RunType.PREPARATION.value,
        execution_status=ExecutionStatus.PREPARATION.value,
        host_platform="Hugging Face dataset + GitHub runnerroute",
        ssl_input_basis=[
            "shadow_seed_learning_4_5_clean.md",
            "ssl_4_5_public_release/",
            "benchmark_bibliotheek/",
        ],
        baseline_label="baseline",
        ssl_condition_label="ssl_condition",
        dataset_status="bibliografisch vastgelegd",
        runner_status="runnerstructuur aanwezig",
        execution_gap=True,
        scenarios_loaded=len(suite.get("scenarios", [])),
        start_command_template=(
            "python evaluate.py --model_family <provider> --model <model> "
            "--in_dir tests --out_dir results"
        ),
        notes=[
            "upstream runnerstructuur is zichtbaar",
            "status blijft benchmarkvoorbereiding tot live route hard is bevestigd",
        ],
    )
