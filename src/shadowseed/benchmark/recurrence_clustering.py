"""Cluster-based recurrence (PvA W9e).

Round 018 found the bottleneck: an LLM detector phrases the same underlying gap
differently each turn, and strict pairwise dedup (cosine >= 0.85) does not merge
paraphrases, so recurrence never accumulates and the Validation Gate never
promotes. Round 019 showed that *lowering* the dedup/recurrence bars makes the
cross-turn payoff appear — but that is doctrine-adjacent (looser dedup risks
collapsing genuinely distinct gaps; a lower Gate bar re-opens the noise door).

This module decouples the two concerns:

- **identity / storage** stays strict (the manager's 0.85 dedup keeps distinct
  seeds distinct);
- **recurrence counting** becomes semantic via clustering: a paraphrase joins the
  nearest cluster within ``threshold`` cosine, and the cluster's member count is
  the recurrence signal fed to the Gate.

So a gap that recurs across turns *in different words* accumulates recurrence
(cluster grows) and can promote at the SAFE default Gate bar (>=3), while a
one-off irrelevant gap stays a singleton cluster and never promotes. This
reconciles round-014 safety with round-019 payoff.
"""

from __future__ import annotations

import numpy as np

DEFAULT_CLUSTER_THRESHOLD = 0.6


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


class RecurrenceClusterer:
    """Counts semantic recurrence across paraphrastic gaps without merging them.

    ``add(text, embedding)`` assigns the gap to the nearest cluster whose centroid
    is within ``threshold`` cosine (updating that centroid as a running mean), or
    starts a new cluster. ``recurrence(cluster_id)`` returns the cluster size.
    """

    def __init__(self, threshold: float = DEFAULT_CLUSTER_THRESHOLD) -> None:
        self.threshold = threshold
        self.centroids: list[np.ndarray] = []
        self.counts: list[int] = []
        self.members: list[list[str]] = []

    def add(self, text: str, embedding: np.ndarray) -> int:
        emb = np.asarray(embedding, dtype=float)
        best = -1
        best_sim = self.threshold
        for i, c in enumerate(self.centroids):
            s = _cosine(emb, c)
            if s >= best_sim:
                best_sim = s
                best = i
        if best < 0:
            self.centroids.append(emb.copy())
            self.counts.append(1)
            self.members.append([text])
            return len(self.centroids) - 1
        n = self.counts[best]
        self.centroids[best] = (self.centroids[best] * n + emb) / (n + 1)
        self.counts[best] += 1
        self.members[best].append(text)
        return best

    def recurrence(self, cluster_id: int) -> int:
        return self.counts[cluster_id]


def auto_calibrated_min_occurrences(n_turns: int, lo: int = 2, hi: int = 4) -> int:
    """Per-topic heuristic (v1): scale the recurrence bar to conversation length.

    A longer conversation gives a recurring theme more chances, so it can carry a
    slightly higher bar; a short one needs a lower one. Clamped to [lo, hi].
    """
    return max(lo, min(hi, n_turns // 3))
