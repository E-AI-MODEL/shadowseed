"""Helpers for turning broad detection output into reviewable seed candidates.

SSL 4.5 requires a normalization step before storage. This module keeps that
step explicit and conservative: it splits broad lists into smaller candidates,
but it does not pretend to prove that every fragment is already a valid atomic
seed. The manager still decides what is accepted or rejected.
"""

from __future__ import annotations

import re

BROAD_PREFIXES = (
    "voeg een volledig analysekader toe met aandacht voor",
    "voeg een analysekader toe met aandacht voor",
    "ontbrekende context:",
    "ontbrekende onderdelen:",
    "let op:",
)

LIST_PATTERN = re.compile(r"\s*(?:,|;|\ben\b|\bof\b)\s*", re.IGNORECASE)


def clean_candidate_text(text: str) -> str:
    text = re.sub(r"^[-*\d.)\s]+", "", text.strip())
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .")


def strip_broad_prefix(text: str) -> str:
    lowered = text.lower()
    for prefix in BROAD_PREFIXES:
        if lowered.startswith(prefix):
            return text[len(prefix) :].strip(" :.-")
    return text


def maybe_expand_fragment(fragment: str) -> str:
    fragment = clean_candidate_text(fragment)
    if not fragment:
        return ""
    if re.search(r"[.!?]$", fragment):
        return fragment
    lowered = fragment.lower()
    if " ontbreekt" in lowered or lowered.startswith("ontbrekend "):
        return fragment + "."
    if len(fragment.split()) <= 4:
        return f"{fragment} ontbreekt."
    return fragment + "."


def split_broad_seed_text(text: str) -> list[str]:
    normalized = strip_broad_prefix(clean_candidate_text(text))
    if not normalized:
        return []
    fragments = [maybe_expand_fragment(part) for part in LIST_PATTERN.split(normalized)]
    return [fragment for fragment in fragments if fragment]


def normalize_detection_candidates(candidates: list[str] | tuple[str, ...]) -> list[str]:
    normalized: list[str] = []
    for candidate in candidates:
        cleaned = clean_candidate_text(candidate)
        if not cleaned:
            continue
        parts = split_broad_seed_text(cleaned)
        if len(parts) <= 1:
            normalized.append(maybe_expand_fragment(cleaned))
            continue
        normalized.extend(parts)
    return normalized
