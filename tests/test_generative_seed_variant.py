"""Tests for the generative 'kunnen staan' detector variant (vision gap 1)."""
from __future__ import annotations

from shadowseed.benchmark.open_set_model_detector import (
    PROMPT_VARIANTS,
    build_detection_prompt,
    make_detector_backend,
)


def test_variants_registered():
    assert PROMPT_VARIANTS == ("absence", "generative")


def test_absence_prompt_asks_what_is_missing():
    p = build_detection_prompt("Een korte testtekst.", variant="absence")
    assert "ONTBREK" in p.upper()
    assert "KUNNEN" not in p.split("Inputtekst")[0].upper().replace("KUNNEN STAAN", "")  # absence prompt is omission-framed


def test_generative_prompt_asks_what_could_have_been():
    p = build_detection_prompt("Een korte testtekst.", variant="generative")
    assert "had KUNNEN staan" in p or "KUNNEN staan" in p
    assert "niet-genomen weg" in p
    # doctrine guardrail survives: no invented facts, only a direction
    assert "Verzin GEEN concrete feiten" in p
    assert "RICHTING" in p
    # generative few-shot frames, not omission examples
    assert "verklarend kader" in p


def test_unknown_variant_rejected():
    import pytest
    with pytest.raises(ValueError):
        build_detection_prompt("x", variant="bogus")
    with pytest.raises(ValueError):
        make_detector_backend("fixture", prompt_variant="bogus")


def test_fixture_backend_reflects_variant():
    item = {"text": "Manchester en Watt dreven de Industriële Revolutie."}
    absence = make_detector_backend("fixture", prompt_variant="absence").detect_seeds(item)
    generative = make_detector_backend("fixture", prompt_variant="generative").detect_seeds(item)
    assert absence and generative
    assert any("Ontbrekende toelichting" in s for s in absence)
    assert any("verklarend kader" in s for s in generative)
