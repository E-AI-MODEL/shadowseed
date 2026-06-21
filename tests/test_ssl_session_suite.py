"""Tests for the SSL session suite (W9) — proves it drives the REAL pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from shadowseed.benchmark import ssl_session_suite as sess
from shadowseed.benchmark.ssl_session_suite import build_chat_prompt, run_ssl_session


def test_fixture_smoke_runs(tmp_path: Path):
    out = tmp_path / "s.json"
    run_ssl_session(
        "src/shadowseed/data/ssl_session_suite.json", str(out), backend="fixture"
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["summary"]["artifact"] == "ssl_session_suite"
    assert payload["summary"]["conversation_count"] == 2


def test_chat_prompt_includes_history_and_surfaced():
    p = build_chat_prompt([("Q1", "A1")], "Q2", ["Een meegedragen invalshoek."])
    assert "Q1" in p and "A1" in p and "Q2" in p
    assert "Een meegedragen invalshoek." in p


def test_recurring_seed_promotes_and_surfaces_cross_turn(tmp_path: Path, monkeypatch):
    # 6-turn conversation so a recurring seed can clear the Gate (weight>=0.5
    # needs ~3 validated passes) and then surface at a later turn.
    conv = {
        "version": "t",
        "conversations": [
            {"id": "C", "domain": "d", "turns": [{"question": f"Vraag {i}?"} for i in range(6)]}
        ],
    }
    inp = tmp_path / "in.json"
    inp.write_text(json.dumps(conv), encoding="utf-8")

    class _Model:
        name = "fake"

        def generate(self, prompt, scenario, mode, seeds):
            return ("SSL-antwoord met invalshoek." if mode == "ssl" else "Baseline-antwoord.")

    class _Detector:
        name = "fake-det"

        def detect_seeds(self, item, max_seeds=5):
            return ["Koloniaal kapitaal als verklarend kader."]  # same gap every turn -> recurs

    def _all_ones_embedder(backend, model_id=None, **kw):
        def embed(text: str) -> np.ndarray:
            v = np.ones(8)
            return v / np.linalg.norm(v)

        return embed, 8

    monkeypatch.setattr(sess, "make_backend", lambda **kw: _Model())
    monkeypatch.setattr(sess, "make_detector_backend", lambda *a, **kw: _Detector())
    monkeypatch.setattr(sess, "make_embedding_fn", _all_ones_embedder)

    out = tmp_path / "s.json"
    run_ssl_session(str(inp), str(out), backend="openai")
    payload = json.loads(out.read_text(encoding="utf-8"))

    # the recurring gap must have reached PROMOTED via the real Gate...
    turns = payload["conversations"][0]["turns"]
    assert any(tr["promoted_total"] for tr in turns), "recurring seed should promote via the Gate"
    # ...and then surfaced as a CROSS-TURN seed (born earlier) shaping a later answer
    assert payload["summary"]["cross_turn_payoff_events"] >= 1
    assert any(tr["is_cross_turn_payoff"] for tr in turns)
    assert payload["blind_review_items"], "a blind pair should exist for the cross-turn turn"
    # and on that turn the SSL answer differs from baseline (the seed was used)
    ct = next(tr for tr in turns if tr["is_cross_turn_payoff"])
    assert ct["ssl_answer"] != ct["baseline_answer"]
