#!/usr/bin/env python3
"""Build a blind A/B review pack from an ssl_session_suite.json artifact.

The script extracts only cross-turn payoff events from the SSL session suite,
balances whether baseline or SSL is shown as answer A, and writes:

- w9f_blind_ab_review_items.json: blinded review items for the reviewer
- w9f_blind_ab_answer_key.json: hidden answer key for analysis
- w9f_blind_ab_review_form.md: human-readable review form
- w9f_blind_ab_scoring_template.csv: optional structured scoring sheet
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Any


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _turn_number(turn: dict[str, Any]) -> int:
    raw = turn.get("turn") or turn.get("turn_index") or 0
    try:
        return int(raw)
    except (TypeError, ValueError):
        return 0


def _item_id(conversation_id: str, turn: dict[str, Any], index: int) -> str:
    turn_no = _turn_number(turn)
    return f"{conversation_id}-t{turn_no:02d}-{index:02d}"


def _balanced_ssl_a_assignments(count: int, *, seed: int) -> list[bool]:
    """Return a reproducible, near-balanced SSL-as-A assignment list.

    A plain stream of random bits can produce a long prefix with the same value
    for small review packs. The W9f pack has only nine payoff items, so that
    can accidentally put every SSL answer on the same side. Instead we build a
    balanced bag first and shuffle it reproducibly.
    """
    if count <= 0:
        return []

    rng = random.Random(seed)
    ssl_a_count = count // 2
    if count % 2:
        ssl_a_count += rng.randrange(2)
    assignments = [True] * ssl_a_count + [False] * (count - ssl_a_count)
    rng.shuffle(assignments)
    return assignments


def _cross_turn_candidates(payload: dict[str, Any]) -> list[tuple[str, str, dict[str, Any]]]:
    candidates: list[tuple[str, str, dict[str, Any]]] = []
    for conv in payload.get("conversations", []):
        conversation_id = _safe_text(conv.get("conversation_id") or conv.get("id") or "conversation")
        domain = _safe_text(conv.get("domain"))
        for turn in conv.get("turns", []):
            if not turn.get("is_cross_turn_payoff"):
                continue
            baseline_answer = _safe_text(turn.get("baseline_answer"))
            ssl_answer = _safe_text(turn.get("ssl_answer"))
            if not baseline_answer or not ssl_answer:
                continue
            candidates.append((conversation_id, domain, turn))
    return candidates


def build_review_pack(payload: dict[str, Any], *, seed: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    review_items: list[dict[str, Any]] = []
    answer_key: list[dict[str, Any]] = []

    candidates = _cross_turn_candidates(payload)
    assignments = _balanced_ssl_a_assignments(len(candidates), seed=seed)

    for global_index, ((conversation_id, domain, turn), ssl_is_a) in enumerate(
        zip(candidates, assignments),
        start=1,
    ):
        baseline_answer = _safe_text(turn.get("baseline_answer"))
        ssl_answer = _safe_text(turn.get("ssl_answer"))
        answer_a = ssl_answer if ssl_is_a else baseline_answer
        answer_b = baseline_answer if ssl_is_a else ssl_answer
        item_id = _item_id(conversation_id, turn, global_index)

        surfaced_seeds = list(turn.get("surfaced_cross_turn_seeds") or [])
        promoted_seeds = list(turn.get("promoted_seeds") or turn.get("promoted_this_turn") or [])

        review_items.append(
            {
                "item_id": item_id,
                "conversation_id": conversation_id,
                "domain": domain,
                "turn": _turn_number(turn),
                "question": _safe_text(turn.get("question")),
                "answer_A": answer_a,
                "answer_B": answer_b,
                "post_choice_seed_context": {
                    "surfaced_cross_turn_seeds": surfaced_seeds,
                    "promoted_seeds_this_turn": promoted_seeds,
                },
                "review": {
                    "winner": "",  # A, B, or tie
                    "scores": {
                        "content_completeness": {"A": "", "B": ""},
                        "question_relevance": {"A": "", "B": ""},
                        "specificity_sharpness": {"A": "", "B": ""},
                        "no_noise_or_hallucinated_relevance": {"A": "", "B": ""},
                        "usefulness": {"A": "", "B": ""},
                    },
                    "motivation": "",
                    "seed_effect_after_choice": "",  # clear_help, some_help, no_difference, noise
                    "noise_or_hallucinated_relevance": "",  # yes/no
                },
            }
        )
        answer_key.append(
            {
                "item_id": item_id,
                "conversation_id": conversation_id,
                "turn": _turn_number(turn),
                "A": "ssl" if ssl_is_a else "baseline",
                "B": "baseline" if ssl_is_a else "ssl",
                "ssl_answer_key": "A" if ssl_is_a else "B",
                "baseline_answer_key": "B" if ssl_is_a else "A",
                "surfaced_cross_turn_seeds": surfaced_seeds,
            }
        )

    return review_items, answer_key


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_form(path: Path, review_items: list[dict[str, Any]], *, title: str) -> None:
    parts: list[str] = [
        f"# {title}",
        "",
        "Blind A/B-review van cross-turn payoff events.",
        "",
        "Werkwijze:",
        "",
        "1. Kies eerst A, B of gelijk zonder naar de seed-context te kijken.",
        "2. Score daarna beide antwoorden op de criteria.",
        "3. Bekijk pas daarna de seed-context en beoordeel het seed-effect.",
        "",
        "Scores: 1 = zwak, 5 = sterk.",
        "",
    ]
    for item in review_items:
        parts.extend(
            [
                f"## Item {item['item_id']}",
                "",
                f"- Conversation: `{item['conversation_id']}`",
                f"- Turn: `{item['turn']}`",
                "",
                "### Vraag/context",
                "",
                item["question"],
                "",
                "### Antwoord A",
                "",
                item["answer_A"],
                "",
                "### Antwoord B",
                "",
                item["answer_B"],
                "",
                "### Keuze",
                "",
                "- [ ] A is beter",
                "- [ ] B is beter",
                "- [ ] Gelijk / geen duidelijke winnaar",
                "",
                "### Scores",
                "",
                "| Criterium | A | B |",
                "|---|---:|---:|",
                "| Inhoudelijke volledigheid |  |  |",
                "| Relevantie voor de vraag |  |  |",
                "| Specificiteit / scherpte |  |  |",
                "| Geen ruis of hallucinated relevance |  |  |",
                "| Bruikbaarheid als antwoord |  |  |",
                "",
                "### Korte motivatie",
                "",
                "",
                "### Seed-context, pas bekijken na keuze",
                "",
                "Surfaced cross-turn seeds:",
                "",
            ]
        )
        seeds = item["post_choice_seed_context"].get("surfaced_cross_turn_seeds") or []
        if seeds:
            parts.extend([f"- {seed}" for seed in seeds])
        else:
            parts.append("- n.v.t.")
        parts.extend(
            [
                "",
                "Seed-effect:",
                "",
                "- [ ] promoted seed helpt duidelijk",
                "- [ ] promoted seed helpt een beetje",
                "- [ ] promoted seed maakt geen verschil",
                "- [ ] promoted seed veroorzaakt ruis",
                "",
            ]
        )
    path.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")


def write_scoring_csv(path: Path, review_items: list[dict[str, Any]]) -> None:
    fields = [
        "item_id",
        "conversation_id",
        "turn",
        "winner",
        "content_completeness_A",
        "content_completeness_B",
        "question_relevance_A",
        "question_relevance_B",
        "specificity_sharpness_A",
        "specificity_sharpness_B",
        "no_noise_A",
        "no_noise_B",
        "usefulness_A",
        "usefulness_B",
        "seed_effect_after_choice",
        "noise_or_hallucinated_relevance",
        "motivation",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for item in review_items:
            writer.writerow(
                {
                    "item_id": item["item_id"],
                    "conversation_id": item["conversation_id"],
                    "turn": item["turn"],
                }
            )


def write_summary(path: Path, payload: dict[str, Any], review_items: list[dict[str, Any]], answer_key: list[dict[str, Any]]) -> None:
    by_conv: dict[str, int] = {}
    for item in review_items:
        by_conv[item["conversation_id"]] = by_conv.get(item["conversation_id"], 0) + 1
    summary = {
        "source_summary": payload.get("summary", {}),
        "blind_review_item_count": len(review_items),
        "items_by_conversation": by_conv,
        "ssl_answer_distribution": {
            "A": sum(1 for key in answer_key if key["ssl_answer_key"] == "A"),
            "B": sum(1 for key in answer_key if key["ssl_answer_key"] == "B"),
        },
    }
    write_json(path, summary)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to ssl_session_suite.json")
    parser.add_argument("--output-dir", required=True, help="Directory for generated review files")
    parser.add_argument("--seed", type=int, default=45, help="Randomization seed for balanced A/B assignment")
    parser.add_argument("--title", default="W9f blind A/B review", help="Review form title")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = json.loads(input_path.read_text(encoding="utf-8"))
    review_items, answer_key = build_review_pack(payload, seed=args.seed)

    write_json(output_dir / "w9f_blind_ab_review_items.json", review_items)
    write_json(output_dir / "w9f_blind_ab_answer_key.json", answer_key)
    write_form(output_dir / "w9f_blind_ab_review_form.md", review_items, title=args.title)
    write_scoring_csv(output_dir / "w9f_blind_ab_scoring_template.csv", review_items)
    write_summary(output_dir / "w9f_blind_ab_summary.json", payload, review_items, answer_key)

    print(f"Generated {len(review_items)} blind A/B review items in {output_dir}")


if __name__ == "__main__":
    main()
