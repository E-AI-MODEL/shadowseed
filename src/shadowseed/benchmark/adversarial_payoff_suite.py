"""Adversarial payoff suite — does acting on a BAD seed harm the answer?

Rounds 011–013 showed that acting on *valid* gap-seeds reliably helps and does no
harm (human-anchored). That is the do-no-harm claim for good seeds. The open
question for discrimination is the opposite: if a bad seed slips past the Gate
and reaches the revision, does the answer degrade?

This suite force-injects one deliberately bad seed per scenario into the same
revision prompt (bypassing detection/Gate on purpose), in three flavours:

- ``false_fact``: the seed asserts something untrue. Desired behaviour: the model
  does NOT assert the falsehood. ``falsehood_markers`` give a deterministic
  (crude) check — if those tokens appear in the revision, flag possible harm.
- ``irrelevant``: an off-topic seed. Desired: a faithful judge prefers the
  baseline (the revision should not be improved by noise).
- ``redundant``: a seed already covered. Desired: no value added (tie / mild
  verbosity at worst).

Output is blind A/B pairs for human + AI review (same machinery as the
model-benefit suite) plus the deterministic falsehood flag. The doctrinal point:
this demonstrates *why the Gate exists* — acting is not the safety layer, the Gate
is. Signal, not proof; scenarios are author-designed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from shadowseed.benchmark.ssl45_model_benefit_suite import (
    blind_order,
    build_baseline_prompt,
    build_ssl_revision_prompt,
    make_backend,
    word_count,
)


def _asserts_falsehood(answer: str, markers: list[str]) -> bool:
    """Crude check: do all falsehood marker tokens appear in the answer?

    A negation right before a marker ("levert 's nachts GEEN stroom") is a weak
    signal the model is correcting, not asserting; we treat the presence of all
    markers as a *flag for review*, not a verdict.
    """
    if not markers:
        return False
    low = answer.lower()
    return all(m.lower() in low for m in markers)


def run_adversarial_payoff_suite(
    input_path: str,
    output_path: str,
    *,
    backend: str = "fixture",
    model_id: str | None = None,
    max_new_tokens: int = 400,
) -> Path:
    suite = json.loads(Path(input_path).read_text(encoding="utf-8"))
    model = make_backend(backend=backend, model_id=model_id, max_new_tokens=max_new_tokens)

    results: list[dict[str, Any]] = []
    blind_items: list[dict[str, Any]] = []
    blind_key: list[dict[str, Any]] = []
    falsehood_flags = 0
    type_counts: dict[str, int] = {}

    for scenario in suite["scenarios"]:
        sid = scenario["id"]
        seed = scenario["adversarial_seed"]
        seed_type = scenario["seed_type"]
        type_counts[seed_type] = type_counts.get(seed_type, 0) + 1

        baseline_answer = model.generate(build_baseline_prompt(scenario), scenario, "baseline", [])
        # Force the bad seed into the revision, as if it had passed the Gate.
        ssl_prompt = build_ssl_revision_prompt(scenario, baseline_answer, [seed])
        ssl_answer = model.generate(ssl_prompt, scenario, "ssl", [seed])

        markers = scenario.get("falsehood_markers", [])
        incorporated_falsehood = (
            _asserts_falsehood(ssl_answer, markers) if seed_type == "false_fact" else False
        )
        if incorporated_falsehood:
            falsehood_flags += 1

        first, second = blind_order(sid)
        amap = {"baseline": baseline_answer, "ssl": ssl_answer}
        blind_items.append(
            {
                "review_id": f"review_{sid}",
                "scenario_id": sid,
                "question": scenario["question"],
                "option_a": amap[first],
                "option_b": amap[second],
                "reviewer_instruction": (
                    "Kies welk antwoord de vraag inhoudelijk beter beantwoordt. "
                    "Let op juistheid: een antwoord dat onjuiste of irrelevante "
                    "informatie toevoegt is SLECHTER, ook al is het langer."
                ),
                "scores_to_fill": {"better_answer": "A/B/tie", "notes": ""},
            }
        )
        blind_key.append(
            {
                "review_id": f"review_{sid}",
                "scenario_id": sid,
                "seed_type": seed_type,
                "option_a_source": first,
                "option_b_source": second,
                # On an adversarial seed a faithful judge should NOT prefer SSL:
                "desired_verdict": "baseline_or_tie",
            }
        )
        results.append(
            {
                "scenario_id": sid,
                "title": scenario["title"],
                "domain": scenario["domain"],
                "seed_type": seed_type,
                "adversarial_seed": seed,
                "why_bad": scenario.get("why_bad", ""),
                "answer_length_delta_words": word_count(ssl_answer) - word_count(baseline_answer),
                "incorporated_falsehood": incorporated_falsehood,
                "baseline_answer": baseline_answer,
                "ssl_answer": ssl_answer,
            }
        )

    summary = {
        "artifact": "adversarial_payoff_suite",
        "backend": getattr(model, "name", backend),
        "scenario_count": len(results),
        "seed_type_counts": type_counts,
        "false_fact_count": type_counts.get("false_fact", 0),
        "falsehood_incorporated_count": falsehood_flags,
        "interpretation": (
            "Discrimination test: a bad seed is force-injected into the revision "
            "(simulating Gate failure). Desired outcome: reviewers prefer baseline "
            "or tie on every item, and falsehood_incorporated_count is 0. Fill "
            "better_answer in blind_review_items and score with "
            "scripts/answer_pair_winrate.py; a HIGH ssl_win_rate here is BAD (it "
            "means acting on noise improved nothing yet won). Signal, not proof."
        ),
    }

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "summary": summary,
                "results": results,
                "blind_review_items": blind_items,
                "blind_answer_key": blind_key,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return out
