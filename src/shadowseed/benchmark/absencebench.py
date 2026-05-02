"""AbsenceBench preparation helpers for the Shadow Seed Learning benchmark lane."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


@dataclass
class AbsenceBenchPreparation:
    benchmark_name: str = "AbsenceBench"
    executionstatus: str = "benchmarkvoorbereiding"
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
    runner_route: str = "nog niet hard geverifieerd"
    startcommando: str = "nog te verifiëren"
    missing_components: list[str] = field(
        default_factory=lambda: [
            "actuele runnerverificatie",
            "hard bevestigd startcommando",
            "provider- en modelkeuze voor baseline",
            "provider- en modelkeuze voor ssl_condition",
            "score-output pad of schema",
        ]
    )
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return asdict(self)


def build_preparation_record() -> dict:
    """Build a reproducible preparation record without claiming a live benchmark run."""
    return AbsenceBenchPreparation().to_dict()
