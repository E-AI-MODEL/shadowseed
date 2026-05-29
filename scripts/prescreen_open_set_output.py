"""Mechanical prescreen for open-set model-detector output (triage aid).

This script reads an ``open_set_seed_output.json`` produced by
``shadowseed run-open-set-seed-review --detector model`` and flags candidate
gaps ("kandidaat-lacunes") against the v0.3e prompt's own guardrails.

IMPORTANT — what this is and is NOT:

- It is a *deterministic* triage aid. It only flags failure modes that can be
  detected without reading for meaning (absence-phrasing, parse leaks, HTML
  entities, English echo, few-shot copying, non-atomic shape).
- It is NOT human review. It does NOT count as ``reviewer_a``/``reviewer_b``
  and NOT as ``open_set_seed_quality`` (Layer C) evidence.
- It is NOT even the AI-judgment prescreen used in round 004: it makes no
  accept/borderline/reject verdict, because that needs reading.
- ``false_gap`` (naming something absent that is actually in the text),
  ``mistranslation`` and ``grammar`` are explicitly NOT checked here; they
  require a human or AI reader. They are listed so a reader knows to look.

Consistent with merge #109: detector output is candidate-only. Status (seed,
evidence, Round) is granted later by review/manager/gate/core, never here.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from shadowseed.benchmark.open_set_model_detector import (
    _HTML_ENTITY,
    _looks_like_citation_fragment,
    _looks_like_fewshot_leak,
)
from shadowseed.manager import SSLManager

# Absence markers that match the v0.3e prompt's required forms
# ("... wordt niet genoemd", "... is niet aangegeven", "... ontbreekt").
_ABSENCE_MARKERS: tuple[str, ...] = (
    "ontbreek",  # ontbreekt / ontbreken
    "wordt niet",
    "worden niet",
    "word niet",
    "is niet vermeld",
    "niet vermeld",
    "niet genoemd",
    "niet benoemd",
    "niet aangegeven",
    "niet gespecificeerd",
    "niet beschreven",
    "niet toegelicht",
    "niet uitgelegd",
    "niet gegeven",
    "niet bekend",
    "niet duidelijk",
    "niet gemaakt",  # "... wordt niet duidelijk gemaakt"
    "onduidelijk",
    "onbekend",
    "onvermeld",
)

# A short list of English function words. Two or more as whole words inside a
# nominally-Dutch gap signals an untranslated echo from the source text.
_ENGLISH_STOPWORDS: frozenset[str] = frozenset(
    {
        "the", "of", "and", "for", "with", "is", "are", "was", "were", "to",
        "in", "on", "at", "by", "from", "that", "this", "their", "his", "her",
        "has", "have", "been", "will", "would", "after", "about", "into",
    }
)

# An embedded "<n>. " mid-sentence indicates a parser/numbering leak: a second
# numbered item bled into one candidate.
_EMBEDDED_NUMBER = re.compile(r"\S\s+\d+[.)]\s+[A-Z]")

# Mechanically detectable codes.
MECHANICAL_CODES: tuple[str, ...] = (
    "claim_vs_gap",
    "parse_leak",
    "language_leak",
    "entity_bleed",
    "citation_fragment",
    "fewshot_leak",
    "not_atomic",
)

# Codes that need a reader; surfaced for transparency but never auto-assigned.
NON_MECHANICAL_CODES: tuple[str, ...] = ("false_gap", "mistranslation", "grammar")


def prescreen_seed(seed: str, source_text: str = "") -> list[str]:
    """Return the mechanical failure codes for one candidate gap."""
    codes: list[str] = []
    lowered = seed.lower()

    if not any(marker in lowered for marker in _ABSENCE_MARKERS):
        codes.append("claim_vs_gap")

    if _EMBEDDED_NUMBER.search(seed):
        codes.append("parse_leak")

    english_hits = sum(1 for tok in re.findall(r"[a-zA-Z]+", lowered) if tok in _ENGLISH_STOPWORDS)
    if english_hits >= 2:
        codes.append("language_leak")

    if _HTML_ENTITY.search(seed):
        codes.append("entity_bleed")

    if _looks_like_citation_fragment(seed, source_text):
        codes.append("citation_fragment")

    if _looks_like_fewshot_leak(seed):
        codes.append("fewshot_leak")

    if not SSLManager.is_atomic_seed(seed):
        codes.append("not_atomic")

    return codes


def _source_text_index(input_batch: dict[str, Any] | None) -> dict[str, str]:
    if not input_batch:
        return {}
    index: dict[str, str] = {}
    for item in input_batch.get("items", []):
        item_id = str(item.get("id") or item.get("item_id") or "")
        text = str(item.get("text") or item.get("input") or "")
        if item_id:
            index[item_id] = text
    return index


def prescreen_output(
    seed_output: dict[str, Any],
    input_batch: dict[str, Any] | None = None,
    round_label: str = "unknown",
) -> dict[str, Any]:
    """Build a mechanical prescreen report over a seed_output payload."""
    summary = seed_output.get("summary", {})
    source_index = _source_text_index(input_batch)

    verdicts: list[dict[str, Any]] = []
    failure_code_counts: dict[str, int] = {code: 0 for code in MECHANICAL_CODES}
    flagged = 0

    results = seed_output.get("results", [])
    item_count = len(results)
    items_empty = 0

    for result in results:
        item_id = str(result.get("item_id", ""))
        source_text = source_index.get(item_id, "")
        candidates = result.get("normalized_candidates") or result.get("raw_candidates") or []
        if not candidates:
            items_empty += 1
        for position, seed in enumerate(candidates, start=1):
            codes = prescreen_seed(seed, source_text)
            for code in codes:
                failure_code_counts[code] += 1
            if codes:
                flagged += 1
            verdicts.append(
                {
                    "item_id": item_id,
                    "position": position,
                    "seed": seed,
                    "codes": codes,
                    "clean": not codes,
                }
            )

    seed_count = len(verdicts)
    return {
        "artifact": "mechanical_prescreen",
        "disclaimer": (
            "Deterministische prescreen, GEEN menselijke review. Telt NIET als "
            "reviewer_a/reviewer_b en niet als open_set_seed_quality (Laag C) "
            "evidence, en geeft GEEN accept/reject-verdict. Bedoeld om aandacht "
            "te richten en de v0.3e-prompt te toetsen aan haar eigen regels."
        ),
        "round": round_label,
        "detector": summary.get("detector"),
        "model_backend": summary.get("model_backend"),
        "yield": {
            "item_count": item_count,
            "items_with_candidates": item_count - items_empty,
            "items_empty": items_empty,
            "empty_rate": round(items_empty / item_count, 3) if item_count else 0.0,
            "mean_candidates_per_item": round(seed_count / item_count, 3) if item_count else 0.0,
        },
        "mechanical_codes": list(MECHANICAL_CODES),
        "not_mechanically_checkable": list(NON_MECHANICAL_CODES),
        "seed_count": seed_count,
        "flagged_count": flagged,
        "clean_count": seed_count - flagged,
        "clean_rate": round((seed_count - flagged) / seed_count, 3) if seed_count else 0.0,
        "failure_code_counts": failure_code_counts,
        "verdicts": verdicts,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# Mechanische prescreen — {report['round']} (GEEN menselijke review)")
    lines.append("")
    lines.append(f"> **Status: deterministisch hulpmiddel, geen evidence.** {report['disclaimer']}")
    lines.append("")
    lines.append(
        f"Detector: `{report.get('detector')}` · backend: `{report.get('model_backend')}`"
    )
    lines.append("")
    y = report["yield"]
    lines.append("## Yield (levert het model kandidaten op?)")
    lines.append("")
    lines.append(
        f"- items: **{y['item_count']}** · met kandidaten: **{y['items_with_candidates']}** "
        f"· leeg: **{y['items_empty']}** (empty-rate **{y['empty_rate']}**)"
    )
    lines.append(f"- gemiddeld kandidaten per item: **{y['mean_candidates_per_item']}**")
    lines.append("")
    lines.append(
        f"## Kwaliteit van geleverde kandidaten ({report['seed_count']} kandidaat-lacunes)"
    )
    lines.append("")
    lines.append(f"- clean (geen mechanische vlag): **{report['clean_count']}**")
    lines.append(f"- geflagd: **{report['flagged_count']}**")
    lines.append(f"- clean-rate: **{report['clean_rate']}**")
    lines.append("")
    lines.append("## Mechanische faalcodes")
    lines.append("")
    for code, count in sorted(
        report["failure_code_counts"].items(), key=lambda kv: (-kv[1], kv[0])
    ):
        lines.append(f"- `{code}`: {count}")
    lines.append("")
    lines.append("## Niet mechanisch te checken (vraagt een lezer)")
    lines.append("")
    lines.append("- " + ", ".join(f"`{c}`" for c in report["not_mechanically_checkable"]))
    lines.append("")
    return "\n".join(lines) + "\n"


def _load_json(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "seed_output",
        help="Pad naar open_set_seed_output.json ({summary, results}).",
    )
    parser.add_argument(
        "--input",
        default=None,
        help="Optioneel: HF input-batch (items met id+text) voor citaat-/contextchecks.",
    )
    parser.add_argument(
        "--round",
        default="unknown",
        help="Label voor de ronde, bijv. round_005.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Pad voor de prescreen-JSON; ook .md wordt ernaast geschreven. "
        "Leeg = naar stdout.",
    )
    args = parser.parse_args(argv)

    seed_output = _load_json(args.seed_output)
    assert seed_output is not None
    input_batch = _load_json(args.input)
    report = prescreen_output(seed_output, input_batch, round_label=args.round)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        out.with_suffix(".md").write_text(render_markdown(report), encoding="utf-8")
        print(f"Wrote {out} and {out.with_suffix('.md')}")
    else:
        print(render_markdown(report))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
