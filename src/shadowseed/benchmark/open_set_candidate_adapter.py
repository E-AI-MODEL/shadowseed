"""Open-set candidate adapter for the SSL 4.5 detection pass.

This adapter is not a second SSL core. It only supplies candidate seed text for
unknown open-set items. The existing SSLManager still performs normalization,
atomicity checks, deduplication and storage with weight starting at 0.0.

The adapter deliberately avoids fixed scenario priors, expected gaps and ground
truth seeds. Human review remains the quality layer for these candidates.
"""

from __future__ import annotations

import re
from typing import Any


OPEN_SET_CANDIDATE_ADAPTER_ID = "ssl45_open_set_candidate_adapter_v0.1"
EXPLICIT_CANDIDATE_SOURCE = "explicit_candidate_seeds"
OPEN_SET_ADAPTER_SOURCE = "open_set_candidate_adapter"

_COMMON_SENTENCE_INITIALS = frozenset(
    {
        "the",
        "a",
        "an",
        "this",
        "that",
        "these",
        "those",
        "it",
        "they",
        "we",
        "you",
        "he",
        "she",
        "i",
        "company",
        "companies",
        "people",
        "person",
        "someone",
        "everyone",
        "everybody",
        "anyone",
        "anybody",
        "de",
        "het",
        "een",
        "deze",
        "die",
        "dat",
        "dit",
        "ze",
        "zij",
        "hij",
        "wij",
        "jullie",
        "men",
        "bedrijf",
        "bedrijven",
        "iemand",
        "iedereen",
        "niemand",
        "today",
        "yesterday",
        "tomorrow",
        "here",
        "there",
        "vandaag",
        "gisteren",
        "morgen",
        "hier",
        "daar",
    }
)

_CLAIM_TERMS = (
    "says",
    "said",
    "claim",
    "claims",
    "announced",
    "reported",
    "report",
    "according",
)
_TIME_TERMS = (
    "after",
    "before",
    "during",
    "deadline",
    "today",
    "yesterday",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)
_AFFECTED_GROUP_TERMS = (
    "workers",
    "customers",
    "users",
    "patients",
    "investors",
    "students",
    "residents",
    "teams",
    "unions",
)
_DECISION_TERMS = (
    "wins",
    "won",
    "sets",
    "agrees",
    "rejects",
    "approves",
    "plans",
    "launches",
    "cuts",
    "raises",
)

_NUMBER_PATTERN = re.compile(
    r"(?:[$#€£]\s?\d|\d+(?:\.\d+)?\s?(?:million|billion|percent|%))",
    re.IGNORECASE,
)
_ENTITY_PATTERN = re.compile(r"\b[A-ZÀ-Þ][a-zA-ZÀ-ÿ0-9]{2,}\b")


def compact_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def item_text(item: dict[str, Any]) -> str:
    return compact_text(item.get("text") or item.get("input") or "")


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def _extract_first_entity(text: str) -> str | None:
    """Return the first proper-noun-like token in text."""
    if not text:
        return None
    for token in _ENTITY_PATTERN.findall(text):
        if token.lower() in _COMMON_SENTENCE_INITIALS:
            continue
        return token
    return None


def _append_unique(candidates: list[str], candidate: str, max_seeds: int) -> None:
    clean = compact_text(candidate)
    if clean and clean not in candidates and len(candidates) < max_seeds:
        candidates.append(clean)


def detect_open_set_candidates(item: dict[str, Any], max_seeds: int = 5) -> list[str]:
    """Create reviewable candidate seeds for an unknown open-set item.

    The candidates follow the 4.5 detection-pass shape: small, concrete and
    testable missing relations. They are hypotheses for review, not labels.
    """
    title = compact_text(item.get("title", ""))
    text = item_text(item)
    if not (title or text):
        return []

    combined = compact_text(f"{title} {text}")
    entity = _extract_first_entity(combined)
    candidates: list[str] = []

    if entity:
        _append_unique(candidates, f"Rol van {entity} in de gebeurtenis.", max_seeds)
    else:
        _append_unique(candidates, "Hoofdactor in de beschreven gebeurtenis.", max_seeds)

    if _contains_any(combined, _CLAIM_TERMS):
        _append_unique(candidates, "Bron van de centrale bewering.", max_seeds)
    else:
        _append_unique(candidates, "Onderbouwing van de centrale bewering.", max_seeds)

    if _contains_any(combined, _TIME_TERMS):
        _append_unique(candidates, "Tijdlijn van de beschreven gebeurtenis.", max_seeds)
    else:
        _append_unique(candidates, "Tijdstip van de beschreven gebeurtenis.", max_seeds)

    if _contains_any(combined, _AFFECTED_GROUP_TERMS):
        _append_unique(candidates, "Direct geraakte groep in het item.", max_seeds)
    else:
        _append_unique(candidates, "Betrokken partij buiten de hoofdactor.", max_seeds)

    if _NUMBER_PATTERN.search(combined):
        _append_unique(candidates, "Herkomst van de genoemde cijfers.", max_seeds)
    elif _contains_any(combined, _DECISION_TERMS):
        _append_unique(candidates, "Reden voor de beschreven beslissing.", max_seeds)
    else:
        _append_unique(candidates, "Onzekerheid rond de centrale bewering.", max_seeds)

    return candidates[:max_seeds]


def raw_open_set_candidates(item: dict[str, Any]) -> tuple[list[str], str]:
    """Return explicit sample candidates or generated open-set candidates."""
    explicit = item.get("candidate_seeds")
    if isinstance(explicit, list) and explicit:
        candidates = [str(seed).strip() for seed in explicit if str(seed).strip()]
        return candidates, EXPLICIT_CANDIDATE_SOURCE
    return detect_open_set_candidates(item), OPEN_SET_ADAPTER_SOURCE
