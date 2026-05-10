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

_ENTITY_STOPWORDS = {
    "A",
    "An",
    "And",
    "At",
    "For",
    "From",
    "In",
    "On",
    "Or",
    "The",
    "This",
    "To",
    "With",
    "AG",
    "News",
    "Business",
    "Sci",
    "Tech",
    "World",
    "Sports",
    "AP",
    "Reuters",
}

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
_ENTITY_PATTERN = re.compile(
    r"\b[A-Z][A-Za-z0-9&./#-]*(?:\s+[A-Z][A-Za-z0-9&./#-]*){0,2}\b"
)


def compact_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def item_text(item: dict[str, Any]) -> str:
    return compact_text(item.get("text") or item.get("input") or "")


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def _clean_entity(entity: str) -> str | None:
    clean = compact_text(entity.strip(" -:;,.()[]{}'\""))
    if not clean:
        return None
    parts = clean.split()
    if all(part in _ENTITY_STOPWORDS for part in parts):
        return None
    if len(clean) <= 1:
        return None
    if clean.isupper() and len(clean) <= 3:
        return None
    return clean


def _extract_first_entity(text: str) -> str | None:
    for match in _ENTITY_PATTERN.findall(text):
        clean = _clean_entity(match)
        if clean is not None:
            return clean
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
