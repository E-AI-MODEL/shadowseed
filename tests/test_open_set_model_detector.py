"""Tests for the v0.3 open-set taalmodel-detector (fixture backend only).

The hf-transformers backend is exercised via construction-time validation
and lazy import behavior; its actual generation path requires a real
model download and is not unit-tested.
"""

from __future__ import annotations

import pytest

from shadowseed.benchmark.open_set_candidate_adapter import (
    SUPPORTED_DETECTORS,
    raw_open_set_candidates,
)
from shadowseed.benchmark.open_set_model_detector import (
    OPEN_SET_MODEL_DETECTOR_SOURCE,
    FixtureDetectorBackend,
    build_detection_prompt,
    make_detector_backend,
    parse_numbered_seeds,
)


def _sample_item() -> dict[str, str]:
    return {
        "id": "AG_NEWS_TEST_0",
        "title": "AG News Business #0",
        "domain": "nieuws - Business",
        "text": (
            "Fears for T N pension after talks Unions representing workers at "
            "Turner Newall say they are disappointed after talks with stricken "
            "parent firm Federal Mogul."
        ),
    }


def test_supported_detectors_includes_model() -> None:
    assert "model" in SUPPORTED_DETECTORS


def test_fixture_backend_returns_text_grounded_seeds_with_fixture_prefix() -> None:
    backend = FixtureDetectorBackend()
    seeds = backend.detect_seeds(_sample_item())

    assert seeds, "expected non-empty seeds"
    assert all(seed.startswith("[FIXTURE]") for seed in seeds)
    # at least one seed must contain a token taken from the input text
    text_tokens = set(_sample_item()["text"].split())
    assert any(
        any(token.strip(".,") in seed for token in text_tokens)
        for seed in seeds
    )


def test_fixture_backend_returns_empty_on_empty_text() -> None:
    assert FixtureDetectorBackend().detect_seeds({"text": ""}) == []
    assert FixtureDetectorBackend().detect_seeds({}) == []


def test_make_detector_backend_fixture() -> None:
    backend = make_detector_backend("fixture")
    assert backend.name == "fixture"


def test_make_detector_backend_hf_requires_model_id() -> None:
    with pytest.raises(ValueError, match="model-id"):
        make_detector_backend("hf-transformers", model_id=None)


def test_make_detector_backend_rejects_unknown_backend() -> None:
    with pytest.raises(ValueError, match="Onbekende model-backend"):
        make_detector_backend("not-a-backend")


def test_raw_open_set_candidates_routes_to_model_detector() -> None:
    backend = FixtureDetectorBackend()
    item = _sample_item()
    candidates, source = raw_open_set_candidates(
        item, detector="model", model_backend=backend
    )
    assert source == OPEN_SET_MODEL_DETECTOR_SOURCE
    assert candidates == backend.detect_seeds(item)


def test_raw_open_set_candidates_model_requires_backend() -> None:
    with pytest.raises(ValueError, match="model_backend"):
        raw_open_set_candidates(_sample_item(), detector="model")


def test_explicit_candidates_still_win_over_model_detector() -> None:
    item = dict(_sample_item())
    item["candidate_seeds"] = ["expliciete seed"]
    backend = FixtureDetectorBackend()
    candidates, source = raw_open_set_candidates(
        item, detector="model", model_backend=backend
    )
    assert source == "explicit_candidate_seeds"
    assert candidates == ["expliciete seed"]


def test_parse_numbered_seeds_handles_typical_model_output() -> None:
    raw = """
1. Rol van koloniaal kapitaal in de financiering van fabrieken.
2. AVG-compliance voor de verwerking van hartslagdata.
3. [seed]
4. Rol van koloniaal kapitaal in de financiering van fabrieken.
ignored chatter
5. Rate-limiting op API's die gezondheidsdata verwerken.
""".strip()
    seeds = parse_numbered_seeds(raw)
    assert seeds == [
        "Rol van koloniaal kapitaal in de financiering van fabrieken.",
        "AVG-compliance voor de verwerking van hartslagdata.",
        "Rate-limiting op API's die gezondheidsdata verwerken.",
    ]


def test_parse_numbered_seeds_respects_max() -> None:
    raw = "\n".join(f"{i}. seed {i}" for i in range(1, 11))
    seeds = parse_numbered_seeds(raw, max_seeds=3)
    assert seeds == ["seed 1", "seed 2", "seed 3"]


def test_parse_numbered_seeds_returns_empty_on_no_numbered_lines() -> None:
    assert parse_numbered_seeds("just some prose") == []
    assert parse_numbered_seeds("") == []


def test_build_detection_prompt_includes_text_and_constraints() -> None:
    prompt = build_detection_prompt("De Industriële Revolutie in Groot-Brittannië.")
    assert "De Industriële Revolutie in Groot-Brittannië." in prompt
    assert "maximaal 5 seeds" in prompt
    assert "meta-categorie" in prompt
    assert prompt.endswith("1.")
