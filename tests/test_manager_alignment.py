from __future__ import annotations

import numpy as np

from shadowseed.manager import SSLManager, SeedStatus, ShadowSeed


def _embedding(text: str) -> np.ndarray:
    values = np.array(
        [
            float((len(text) % 7) + 1),
            float((sum(ord(char) for char in text) % 11) + 1),
        ],
        dtype=float,
    )
    norm = np.linalg.norm(values)
    return values / norm


def _manager() -> SSLManager:
    return SSLManager(embedding_fn=_embedding)


def test_contradiction_score_starts_at_zero() -> None:
    manager = _manager()
    seed_id = manager.add_or_update_seed("AVG-compliance bij verwerking van medische data.")
    assert manager.get_seed(seed_id).contradiction_score == 0.0
