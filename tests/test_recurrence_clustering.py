"""Tests for cluster-based recurrence (W9e) — no network."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from shadowseed.benchmark.recurrence_clustering import (
    RecurrenceClusterer,
    auto_calibrated_min_occurrences,
)
from shadowseed.benchmark.ssl_session_suite import run_ssl_session


def test_paraphrases_cluster_unrelated_split():
    c = RecurrenceClusterer(threshold=0.6)
    # three near-parallel vectors (paraphrases) + one orthogonal (unrelated)
    a1 = np.array([1.0, 0.0, 0.0])
    a2 = np.array([0.9, 0.1, 0.0])
    a3 = np.array([0.85, 0.15, 0.0])
    b1 = np.array([0.0, 0.0, 1.0])
    ca = c.add("privacy", a1)
    assert c.add("datagebruik", a2) == ca
    assert c.add("vertrouwen", a3) == ca
    assert c.recurrence(ca) == 3  # paraphrases accumulate recurrence
    cb = c.add("iets heel anders", b1)
    assert cb != ca and c.recurrence(cb) == 1  # unrelated stays a singleton


def test_auto_calibrated_bar_clamped():
    assert auto_calibrated_min_occurrences(4) == 2
    assert auto_calibrated_min_occurrences(9) == 3
    assert auto_calibrated_min_occurrences(30) == 4  # clamped at hi


def test_cluster_mode_promotes_at_safe_bar(tmp_path: Path, monkeypatch):
    # 6-turn convo; detector emits paraphrases of ONE gap; strict dedup (0.85)
    # keeps them distinct, but cluster recurrence lets the SAFE bar (min_occ 3)
    # promote -> cross-turn event. Proves W9e works without loosening dedup/Gate.
    conv = {"version": "t", "conversations": [
        {"id": "C", "domain": "d", "turns": [{"question": f"Q{i}?"} for i in range(6)]}]}
    inp = tmp_path / "in.json"
    inp.write_text(json.dumps(conv), encoding="utf-8")

    paraphrases = [
        "Privacy van gebruikersdata als kernzorg.",
        "Bescherming van persoonlijke data van gebruikers.",
        "Datagebruik en vertrouwen van gebruikers op lange termijn.",
        "Verantwoord omgaan met gevoelige gebruikersgegevens.",
        "Transparantie over hoe gebruikersdata wordt benut.",
        "Waarborgen van dataprivacy voor gebruikers.",
    ]

    class _Model:
        name = "fake"
        def generate(self, prompt, scenario, mode, seeds):
            return "SSL." if mode == "ssl" else "Baseline."

    class _Det:
        name = "d"
        def __init__(self): self.i = 0
        def detect_seeds(self, item, max_seeds=5):
            t = paraphrases[self.i % len(paraphrases)]; self.i += 1
            return [t]

    def _emb(backend, model_id=None, **kw):
        # paraphrases -> near-identical vector (cluster together, but each is a
        # distinct string so strict 0.85 dedup keeps them as separate seeds only
        # if vectors differ slightly); make them cluster at 0.6 yet not all merge.
        def embed(text: str):
            base = np.ones(16) * 0.5
            # tiny per-text jitter so strict dedup may keep some distinct
            h = sum(map(ord, text)) % 16
            base[h] += 0.05
            return base / np.linalg.norm(base)
        return embed, 16

    monkeypatch.setattr(sessmod(), "make_backend", lambda **k: _Model())
    monkeypatch.setattr(sessmod(), "make_detector_backend", lambda *a, **k: _Det())
    monkeypatch.setattr(sessmod(), "make_embedding_fn", _emb)

    out = tmp_path / "s.json"
    run_ssl_session(str(inp), str(out), backend="openai",
                    recurrence_mode="cluster", cluster_threshold=0.6)  # min_occ stays default 3
    payload = json.loads(out.read_text(encoding="utf-8"))
    c = payload["conversations"][0]
    assert c["applied_thresholds"]["recurrence_mode"] == "cluster"
    assert c["applied_thresholds"]["min_occurrences"] == "default(3)"  # SAFE bar
    assert any(tr["promoted_total"] for tr in c["turns"]), "cluster recurrence should promote at the safe bar"


def sessmod():
    import shadowseed.benchmark.ssl_session_suite as m
    return m
