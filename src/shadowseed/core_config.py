"""Central SSL 4.5 core configuration.

This module keeps the canonical default thresholds in one place so the core
manager, benchmark runners and future evaluators can stay aligned.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class SSLCoreConfig:
    """Canonical defaults for the SSL 4.5 core lifecycle."""

    trace_start: float = 2.0
    half_life_turns: float = 3.0
    dedup_threshold: float = 0.85
    promotion_threshold: float = 0.5
    dormant_threshold: float = 0.05
    validation_increment: float = 0.2
    contradiction_penalty: float = 0.3
    reward_step: float = 0.1
    penalty_step: float = 0.2
    max_trace: float = 3.0
    reactivation_increment: float = 2.0
    min_occurrences_for_gate: int = 3
    min_evidence_for_gate: int = 2
    min_trace_for_gate: float = 0.5
    max_seed_words: int = 18

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
