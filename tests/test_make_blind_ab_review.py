"""Tests for the W9f blind A/B review pack generator."""
from __future__ import annotations

import importlib.util

_spec = importlib.util.spec_from_file_location("blind_ab", "scripts/make_blind_ab_review.py")
assert _spec and _spec.loader
blind_ab = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(blind_ab)


def _payload(count: int):
    return {
        "summary": {"cross_turn_payoff_events": count},
        "conversations": [
            {
                "conversation_id": "C",
                "domain": "test",
                "turns": [
                    {
                        "turn": i,
                        "is_cross_turn_payoff": True,
                        "question": f"Q{i}?",
                        "baseline_answer": f"baseline {i}",
                        "ssl_answer": f"ssl {i}",
                        "surfaced_cross_turn_seeds": [f"seed {i}"],
                    }
                    for i in range(count)
                ],
            }
        ],
    }


def test_seed_45_assignment_is_balanced_for_w9f_pack():
    _, answer_key = blind_ab.build_review_pack(_payload(9), seed=45)
    ssl_as_a = sum(1 for key in answer_key if key["ssl_answer_key"] == "A")
    ssl_as_b = sum(1 for key in answer_key if key["ssl_answer_key"] == "B")

    assert len(answer_key) == 9
    assert abs(ssl_as_a - ssl_as_b) == 1
    assert {key["ssl_answer_key"] for key in answer_key} == {"A", "B"}


def test_even_pack_splits_ssl_answers_equally():
    _, answer_key = blind_ab.build_review_pack(_payload(10), seed=45)
    ssl_as_a = sum(1 for key in answer_key if key["ssl_answer_key"] == "A")
    ssl_as_b = sum(1 for key in answer_key if key["ssl_answer_key"] == "B")

    assert ssl_as_a == 5
    assert ssl_as_b == 5
