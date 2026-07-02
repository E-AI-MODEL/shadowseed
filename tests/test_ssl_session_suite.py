"""Tests for the SSL session suite (W9) — proves it drives the REAL pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from shadowseed.benchmark import ssl_session_suite as sess
from shadowseed.benchmark.ssl_session_suite import (
    build_chat_prompt,
    run_ssl_session,
    select_cross_turn_seeds,
)


def test_select_cross_turn_seeds_ranks_and_caps():
    # round 023 use-time discipline: rank by similarity desc, keep top_k
    cands = [(0.4, "a", "A"), (0.9, "b", "B"), (0.6, "c", "C")]
    assert [t for _s, _i, t in select_cross_turn_seeds(cands, 2)] == ["B", "C"]
    assert [t for _s, _i, t in select_cross_turn_seeds(cands, -1)] == ["B", "C", "A"]  # no cap
    assert select_cross_turn_seeds(cands, 0) == []  # nothing steers


def test_chat_prompt_is_potential_not_must():
    p = build_chat_prompt([("Q1", "A1")], "Q2", ["Een meegedragen invalshoek."])
    assert "Een meegedragen invalshoek." in p
    # potential-not-must: may include only if it sharpens, may be dropped if it narrows
    assert "aanscherpen" in p and "vernauwen" in p
    assert "Betrek daarbij expliciet" not in p  # the old hard must-instruction is gone
    # round 025: no self-justifying meta sentences in the answer (round-024 leak)
    assert "rechtvaardig" in p and "versterkt het antwoord" in p


def test_chat_prompt_compactness_applies_to_both_arms():
    # round 025: the rounded-off/compact instruction must be in BOTH arms so it
    # cannot bias the A/B comparison (round 024: 7/18 answers truncated mid-word).
    baseline = build_chat_prompt([("Q1", "A1")], "Q2", [])
    ssl = build_chat_prompt([("Q1", "A1")], "Q2", ["Invalshoek."])
    for p in (baseline, ssl):
        assert "compact" in p and "slotalinea" in p
    # and the baseline arm carries no weave block at all
    assert "invalshoek(en) betrekken" not in baseline


def test_transfer_suite_runs_through_pipeline(tmp_path: Path):
    # W10: the doctrine-transfer dataset (new domains) must run through the same
    # pipeline. Fixture backend -> deterministic, no model/secret needed.
    out = tmp_path / "t.json"
    run_ssl_session(
        "src/shadowseed/data/ssl_session_transfer_suite.json", str(out), backend="fixture"
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["summary"]["artifact"] == "ssl_session_suite"
    assert payload["summary"]["conversation_count"] == 3
    domains = {c["domain"] for c in payload["conversations"]}
    assert domains == {"onderwijs", "publieke gezondheid", "beleid"}


def test_surface_settings_recorded(tmp_path: Path):
    out = tmp_path / "s.json"
    run_ssl_session(
        "src/shadowseed/data/ssl_session_suite.json", str(out), backend="fixture", surface_top_k=1
    )
    appl = json.loads(out.read_text(encoding="utf-8"))["conversations"][0]["applied_thresholds"]
    assert appl["surface_top_k"] == 1
    assert "surface_threshold" in appl


def test_fixture_smoke_runs(tmp_path: Path):
    out = tmp_path / "s.json"
    run_ssl_session(
        "src/shadowseed/data/ssl_session_suite.json", str(out), backend="fixture"
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["summary"]["artifact"] == "ssl_session_suite"
    assert payload["summary"]["conversation_count"] == 3


def test_per_topic_thresholds_override_run_level(tmp_path: Path):
    # one conversation carries its own thresholds; they must win over run-level
    conv = {
        "version": "t",
        "conversations": [
            {"id": "A", "domain": "d", "dedup_threshold": 0.55, "min_occurrences": 2,
             "turns": [{"question": "Q1?"}, {"question": "Q2?"}]},
            {"id": "B", "domain": "d", "turns": [{"question": "Q1?"}, {"question": "Q2?"}]},
        ],
    }
    inp = tmp_path / "in.json"
    inp.write_text(json.dumps(conv), encoding="utf-8")
    out = tmp_path / "s.json"
    run_ssl_session(str(inp), str(out), backend="fixture", dedup_threshold=0.8)
    payload = json.loads(out.read_text(encoding="utf-8"))
    by_id = {c["conversation_id"]: c for c in payload["conversations"]}
    # A overrides to 0.55 / min_occ 2; B inherits run-level 0.8 / default min_occ
    assert by_id["A"]["applied_thresholds"]["dedup_threshold"] == 0.55
    assert by_id["A"]["applied_thresholds"]["min_occurrences"] == 2
    assert by_id["B"]["applied_thresholds"]["dedup_threshold"] == 0.8
    assert by_id["B"]["applied_thresholds"]["min_occurrences"] == "default(3)"


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
