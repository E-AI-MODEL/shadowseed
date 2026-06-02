"""Tests for the mechanical open-set prescreen triage aid.

The prescreen is a deterministic triage helper, not Layer C evidence. These
tests lock the deterministic failure-code behavior so the v0.3e run can be
compared against the round 004 baseline on stable ground.
"""

import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("src").resolve()))

_SCRIPT = Path("scripts/prescreen_open_set_output.py").resolve()
_spec = importlib.util.spec_from_file_location("prescreen_open_set_output", _SCRIPT)
assert _spec and _spec.loader
prescreen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(prescreen)


def test_claim_is_flagged_as_claim_vs_gap() -> None:
    codes = prescreen.prescreen_seed(
        "De toezichthouder heeft geen onderzoek gedaan naar de zaak."
    )
    assert "claim_vs_gap" in codes


def test_absence_form_is_not_flagged_as_claim_vs_gap() -> None:
    codes = prescreen.prescreen_seed(
        "Of de toezichthouder onderzoek heeft gedaan, wordt niet vermeld."
    )
    assert "claim_vs_gap" not in codes


def test_embedded_numbering_is_a_parse_leak() -> None:
    codes = prescreen.prescreen_seed(
        "De prijs wordt niet genoemd. 1. De leverancier wordt niet vermeld."
    )
    assert "parse_leak" in codes


def test_html_entity_is_entity_bleed() -> None:
    codes = prescreen.prescreen_seed("De besparing van #36;5 wordt niet genoemd.")
    assert "entity_bleed" in codes


def test_dutch_homographs_do_not_trigger_language_leak() -> None:
    # Every v0.3e gap starts with "Of ..." and often contains "in"/"is";
    # these Dutch words must not be counted as an English echo.
    codes = prescreen.prescreen_seed(
        "Of de Prediction Unit een bepaalde periode in dienst is, wordt niet vermeld."
    )
    assert "language_leak" not in codes


def test_real_english_echo_is_language_leak() -> None:
    codes = prescreen.prescreen_seed("Apple Launches Graphics Software with the new bundle.")
    assert "language_leak" in codes


def test_round_004_baseline_is_dominated_by_claim_vs_gap() -> None:
    seed_output = json.loads(
        Path("benchmarks/open_review/rounds/round_004/open_set_seed_output.json").read_text(
            encoding="utf-8"
        )
    )
    report = prescreen.prescreen_output(seed_output, round_label="round_004")
    assert report["seed_count"] > 0
    assert report["flagged_count"] > 0
    counts = report["failure_code_counts"]
    # claim_vs_gap was the headline failure mode of the v0.3d round 004 run.
    assert counts["claim_vs_gap"] == max(counts.values())


def test_report_carries_non_evidence_disclaimer() -> None:
    report = prescreen.prescreen_output({"summary": {}, "results": []})
    assert "GEEN menselijke review" in report["disclaimer"]
    assert report["artifact"] == "mechanical_prescreen"


def test_yield_counts_empty_items() -> None:
    seed_output = {
        "summary": {},
        "results": [
            {"item_id": "a", "normalized_candidates": ["De prijs wordt niet genoemd."]},
            {"item_id": "b", "normalized_candidates": []},
            {"item_id": "c", "raw_candidates": []},
        ],
    }
    report = prescreen.prescreen_output(seed_output)
    y = report["yield"]
    assert y["item_count"] == 3
    assert y["items_empty"] == 2
    assert y["items_with_candidates"] == 1
