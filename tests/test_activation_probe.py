"""Tests for the Laag G activation probe (spoor 2, harness mechanics).

Doctrine pinned: the probe touches no seed state (signal != verdict), the
analysis core is deterministic, and a fake backend proves mechanics only.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from shadowseed.benchmark.activation_probe import (
    FakeActivationModel,
    class_separation,
    probe_report,
    find_focus_span,
    load_verdict_labels,
    permutation_control,
    run_activation_probe,
    select_focus_positions,
)
from shadowseed.benchmark.dialectic_falsification import build_dialectic_prompt

FIXTURE = Path("src/shadowseed/data/dialectic_falsification_fixture.json")


def test_class_separation_detects_separated_means():
    a = [np.array([1.0, 0.0, 0.0]) for _ in range(3)]
    b = [np.array([0.0, 1.0, 0.0]) for _ in range(3)]
    rep = class_separation({"WEERLEGD": a, "HOUDT_STAND": b})
    assert rep["separable"] is True
    assert rep["cosine_distance"] > 0.9
    dims = {d["dim"] for d in rep["candidate_dimensions"][:2]}
    assert dims == {0, 1}


def test_class_separation_requires_two_nonempty_classes():
    rep = class_separation({"WEERLEGD": [np.ones(3)]})
    assert rep["separable"] is False
    rep = class_separation({"WEERLEGD": [np.ones(3)], "HOUDT_STAND": []})
    assert rep["separable"] is False


def test_probe_report_picks_strongest_layer():
    sep = {"A": [np.array([1.0, 0.0])], "B": [np.array([0.0, 1.0])]}
    close = {"A": [np.array([1.0, 0.1])], "B": [np.array([1.0, 0.0])]}
    rep = probe_report({"mlp.far": sep, "mlp.close": close})
    assert rep["strongest_layer"] == "mlp.far"


def test_fake_model_is_deterministic_and_class_blind():
    model = FakeActivationModel()
    a1 = model.activations_for("prompt X")
    a2 = model.activations_for("prompt X")
    for layer in model.layer_names:
        assert np.allclose(a1[layer], a2[layer])
    # different text -> different vector (hash-driven), no class info involved
    b = model.activations_for("prompt Y")
    assert not np.allclose(a1["mlp.0"], b["mlp.0"])


def test_probe_run_end_to_end_writes_signal_artifact(tmp_path: Path):
    out = tmp_path / "probe.json"
    result = run_activation_probe(str(FIXTURE), output_path=str(out))
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["artifact"] == "activation_probe"
    assert payload["evidence_layer"] == "G"
    assert "Signaal != verdict" in payload["doctrine"]
    # both verdict classes present in the fixture set (2 houdt_stand, 1 weerlegd)
    verdicts = {c["verdict"] for c in result["cases"]}
    assert verdicts == {"WEERLEGD", "HOUDT_STAND"}
    for layer_report in result["report"]["layers"].values():
        assert layer_report["separable"] is True
    assert result["report"]["strongest_layer"] in FakeActivationModel.layer_names


def test_select_focus_positions_overlap_semantics():
    offsets = [(0, 5), (5, 10), (10, 15), (15, 20), (0, 0)]  # (0,0) = special token
    # span [7, 12) overlapt token 1 en 2; special tokens nooit
    assert select_focus_positions(offsets, 7, 12) == [1, 2]
    assert select_focus_positions(offsets, 0, 20) == [0, 1, 2, 3]
    assert select_focus_positions(offsets, 90, 99) == []


def test_stelling_pooling_isolates_the_focus_span(tmp_path: Path):
    # same stelling in a different source: under stelling-pooling the fake
    # vector depends only on the focus span; under full pooling it does not
    model = FakeActivationModel()
    p1 = "BRON A ...\nSTELLING:\nHet ontbrekende punt.\nREST"
    p2 = "BRON B (anders) ...\nSTELLING:\nHet ontbrekende punt.\nEINDE"
    focus = "Het ontbrekende punt."
    a = model.activations_for(p1, focus=focus)
    b = model.activations_for(p2, focus=focus)
    assert np.allclose(a["mlp.0"], b["mlp.0"])  # focus-scoped: identiek
    a_full = model.activations_for(p1)
    b_full = model.activations_for(p2)
    assert not np.allclose(a_full["mlp.0"], b_full["mlp.0"])  # full: niet


def test_focus_span_anchors_after_stelling_marker():
    # a covered/quoted seed appears verbatim in the BRONTEKST: the span must
    # point at the STELLING copy, not the earlier source copy
    seed = "De uitstootcijfers worden jaarlijks gepubliceerd."
    source = f"Inleiding. {seed} Verder beschrijft het rapport de voortgang."
    prompt = build_dialectic_prompt(seed, source)
    span = find_focus_span(prompt, seed)
    assert span is not None
    start, end = span
    assert prompt[start:end] == seed
    assert start > prompt.find("STELLING:")
    assert start > prompt.find(seed)  # niet de bron-kopie

    # fallback: geen marker -> ongeankerd; geen hit -> None
    assert find_focus_span(f"x {seed} y", seed) == (2, 2 + len(seed))
    assert find_focus_span("niets hier", seed) is None
    assert find_focus_span(prompt, "") is None


def test_probe_records_pooling_mode(tmp_path: Path):
    out = tmp_path / "probe.json"
    result = run_activation_probe(str(FIXTURE), output_path=str(out), pooling="full")
    assert result["pooling"] == "full"
    result = run_activation_probe(str(FIXTURE), output_path=str(out))
    assert result["pooling"] == "stelling"


def test_permutation_control_exact_on_separable_data():
    rng = np.random.default_rng(7)
    a = [np.array([1.0, 0.0, 0.0]) + rng.normal(0, 0.01, 3) for _ in range(4)]
    b = [np.array([0.0, 1.0, 0.0]) + rng.normal(0, 0.01, 3) for _ in range(4)]
    rep = permutation_control(a + b, ["W"] * 4 + ["H"] * 4)
    assert rep["exact"] is True
    assert rep["n_assignments"] == 70  # C(8,4)
    # perfect scheiding: alleen de echte toewijzing en zijn spiegel halen het
    # maximum; bij gebalanceerde klassen is de haalbare vloer dus 2/70
    assert rep["p_value"] == pytest.approx(2 / 70)
    assert rep["min_possible_p"] == pytest.approx(2 / 70)
    assert rep["p_value"] >= rep["min_possible_p"] - 1e-12


def test_permutation_control_on_random_data_is_not_significant():
    rng = np.random.default_rng(11)
    vecs = [rng.normal(size=6) for _ in range(8)]
    rep = permutation_control(vecs, ["W"] * 4 + ["H"] * 4)
    assert rep["valid"] is True
    assert rep["p_value"] > 0.05  # ruis hoort niet significant te scheiden


def test_permutation_control_quantifies_tiny_n():
    # n=3 (2 vs 1): slechts 3 toewijzingen mogelijk -> p kan nooit onder 1/3
    vecs = [np.array([1.0, 0.0]), np.array([0.9, 0.1]), np.array([0.0, 1.0])]
    rep = permutation_control(vecs, ["H", "H", "W"])
    assert rep["exact"] is True and rep["n_assignments"] == 3
    assert rep["min_possible_p"] == pytest.approx(1 / 3)
    assert rep["p_value"] >= 1 / 3


def test_probe_report_includes_permutation(tmp_path: Path):
    out = tmp_path / "probe.json"
    result = run_activation_probe(str(FIXTURE), output_path=str(out))
    strongest = result["report"]["strongest_layer"]
    perm = result["report"]["layers"][strongest]["permutation"]
    assert perm["valid"] is True and perm["exact"] is True
    assert result["report"]["strongest_permutation_p"] == perm["p_value"]
    # n=3 in de fixture: de controle laat zien dat p nooit onder 1/3 kan
    assert perm["min_possible_p"] == pytest.approx(1 / 3)


def test_load_verdict_labels_filters_and_maps(tmp_path: Path):
    payload = {
        "records": [
            {"seed_text": "A", "verdict": "WEERLEGD"},
            {"seed_text": "B", "verdict": "HOUDT_STAND"},
            {"seed_text": "C", "verdict": "ONBESLIST"},  # geen klasse
            {"seed_text": "D", "skipped": "niet geaccepteerd"},  # geen verdict
        ]
    }
    p = tmp_path / "vd.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    labels = load_verdict_labels(str(p))
    assert labels == {"A": "WEERLEGD", "B": "HOUDT_STAND"}


def test_probe_uses_external_verdicts(tmp_path: Path):
    # decoupling: de sonde leest de internals (fake), maar de labels komen uit
    # een extern dialectiek-artifact — hier bewust omgekeerd t.o.v. de fixture
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    seeds = [c["seed_text"] for c in fixture["cases"]]
    external = tmp_path / "verdicts.json"
    external.write_text(
        json.dumps(
            {"records": [
                {"seed_text": seeds[0], "verdict": "WEERLEGD"},
                {"seed_text": seeds[1], "verdict": "WEERLEGD"},
                {"seed_text": seeds[2], "verdict": "HOUDT_STAND"},
            ]}
        ),
        encoding="utf-8",
    )
    out = tmp_path / "probe.json"
    result = run_activation_probe(
        str(FIXTURE), output_path=str(out), verdicts_path=str(external)
    )
    assert result["verdict_source"] == "extern"
    got = {c["seed_text"]: c["verdict"] for c in result["cases"]}
    assert got[seeds[0]] == "WEERLEGD" and got[seeds[2]] == "HOUDT_STAND"


def test_probe_default_verdict_source_is_fixture(tmp_path: Path):
    result = run_activation_probe(str(FIXTURE), output_path=str(tmp_path / "p.json"))
    assert result["verdict_source"] == "fixture"


def test_probe_touches_no_seed_state():
    # doctrine guard: the probe module must not import or construct a manager
    import shadowseed.benchmark.activation_probe as mod

    src = Path(mod.__file__).read_text(encoding="utf-8")
    assert "SSLManager" not in src
    assert "run_validation_gate" not in src
    assert "apply_probe_feedback" not in src
