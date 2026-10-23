#!/usr/bin/env python3
"""One-shot, cost-bounded GPT-5 vs GPT-6 Astra Shadowseed core pilot.

Uses the existing GitHub Actions OPENAI_API_KEY secret; never copies or logs
credentials. Exercises canonical SSLManager on shadowseed-pro main at a fixed
SHA, not obsolete experimental detector v0.7.

Evidence boundary: model-generated inquiry is a proposed, weightless seed,
NOT truth, independent verification, latent neurons, or demonstrated benefit.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any
import urllib.error
import urllib.request

import numpy as np

MODEL_IDS = ("gpt-5", "gpt-6-astra")
CORE_SHA = "13fda4189b3cff306642c41c47524dc3648bf1f4"
API_URL = "https://api.openai.com/v1/responses"
MAX_CALLS = 12
MAX_OUTPUT_BASELINE = 900
MAX_OUTPUT_INQUIRY = 600
MAX_ESTIMATED_DOLLARS = 2.00
RATES_USD_PER_MILLION = {
    "gpt-5": {"input": 1.25, "output": 10.0},
    "gpt-6-astra": {"input": 10.0, "output": 50.0},
}
# Exactly the same input observations for both model arms (no previous model
# answer is injected into the next turn, preventing cross-model history drift).
TURNS = (
    "Fictieve onderwijsproef, dag 1: 24 leerlingen maken oefeningen met "
    "een AI-hulpmiddel. 80% van de antwoorden is juist. Er is geen "
    "zelfstandige toets afgenomen. Welke conclusie volgt wel en niet?",
    "Fictieve onderwijsproef, dag 7: dezelfde leerlingen lossen met het "
    "AI-hulpmiddel nieuwe vragen op en werken sneller. We hebben geen "
    "controlegroep of zelfstandige nameting. Wat verandert aan de conclusie?",
    "Fictieve onderwijsproef, dag 14: zonder AI scoort de oefengroep 60% "
    "en een andere groep 65%. De beginsituatie verschilt mogelijk en "
    "retentie of transfer is niet onderzocht. Wat laat dit zien en welke "
    "vraag is nog open?",
)
BASELINE_INSTRUCTION = (
    "Beantwoord de huidige vraag in het Nederlands, maximaal 110 woorden. "
    "Gebruik alleen de fictieve, gegeven gegevens. Scheid observatie "
    "van conclusie en formuleer geen ongefundeerde leerwinstclaim."
)
DETECTION_INSTRUCTION = (
    "Je bent een onderzoeksmodule voor Shadow Seed Learning. "
    "Kijk naar één vraag en het bijbehorende conceptantwoord. "
    "Formuleer precies ÉÉN specifieke, atomaire onderzoeksvraag over een "
    "mogelijke verwante interpretatie, onzekerheid of samenhang die óók "
    "had kunnen worden onderzocht, maar niet al letterlijk wordt opgelost. "
    "Het is GEEN checklist van wat ontbreekt; noem geen geconstateerde fout. "
    "Beoordeel geen waarheid, belang of nut. Verzin geen personen, getallen "
    "of bronnen. Schrijf uitsluitend één Nederlandse vraagzin met '?' "
    "of schrijf exact NONE wanneer geen specifieke zinvolle "
    "mogelijkheid te formuleren is."
)


def _safe_error_code(payload: bytes) -> str:
    """Only expose the error class/code, never a provider error body."""
    try:
        error = json.loads(payload.decode("utf-8", errors="ignore")).get("error", {})
        candidate = str(error.get("code") or error.get("type") or "provider_error")
        return candidate if re.fullmatch(r"[a-zA-Z0-9_.-]{1,80}", candidate) else "provider_error"
    except (ValueError, TypeError, AttributeError):
        return "provider_error"


class ProviderProblem(Exception):
    def __init__(self, status: str, code: str) -> None:
        self.status = status
        self.code = code
        super().__init__(f"{status}:{code}")


def _response_text(data: dict[str, Any]) -> str:
    chunks: list[str] = []
    for item in data.get("output", []):
        if item.get("type") != "message":
            continue
        for block in item.get("content", []):
            if block.get("type") == "output_text" and isinstance(block.get("text"), str):
                chunks.append(block["text"])
    return "\n".join(chunks).strip()


def _cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    rate = RATES_USD_PER_MILLION[model]
    return (input_tokens * rate["input"] + output_tokens * rate["output"]) / 1_000_000


class MeteredOpenAI:
    def __init__(self, key: str) -> None:
        if not key.startswith("sk-") or len(key) < 30:
            raise ValueError("No suitable OpenAI API credential configured")
        self._key = key
        self.calls = 0
        self.estimated_cost = 0.0

    def ask(self, model: str, instruction: str, prompt: str, *, output_cap: int) -> dict:
        if model not in MODEL_IDS:
            raise ValueError("Only the user-requested GPT-5 and GPT-6 models are allowed")
        if self.calls >= MAX_CALLS:
            raise RuntimeError("Experiment call cap reached; no more requests")
        if self.estimated_cost >= MAX_ESTIMATED_DOLLARS:
            raise RuntimeError("Experiment estimated-cost cap reached")
        if not 1 <= output_cap <= MAX_OUTPUT_BASELINE:
            raise ValueError("Invalid per-request output cap")
        if len(instruction) + len(prompt) > 9000:
            raise ValueError("Bounded research prompt exceeded")

        payload = {
            "model": model,
            "instructions": instruction,
            "input": prompt,
            "reasoning": {"effort": "low"},
            "max_output_tokens": output_cap,
            "store": False,
        }
        req = urllib.request.Request(
            API_URL,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + self._key,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        # An unsuccessful request might still be billed. Count all attempts.
        self.calls += 1
        try:
            with urllib.request.urlopen(req, timeout=150) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise ProviderProblem("http_" + str(exc.code), _safe_error_code(exc.read())) from None
        except (urllib.error.URLError, TimeoutError) as exc:
            raise ProviderProblem("network_error", type(exc).__name__) from None

        if not isinstance(data, dict):
            raise ProviderProblem("invalid_response", "expected_object")
        usage = data.get("usage") or {}
        # Reported usage is exact accounting input; if missing, charge our
        # internal budget conservatively. Never claim it is a provider invoice.
        itok = int(usage.get("input_tokens") or 3600)
        otok = int(usage.get("output_tokens") or output_cap)
        if itok < 0 or otok < 0:
            raise ProviderProblem("invalid_usage", "negative_tokens")
        estimate = _cost_usd(model, itok, otok)
        self.estimated_cost += estimate
        result = {
            "requested_model": model,
            "actual_model": str(data.get("model") or ""),
            "response_id": str(data.get("id") or ""),
            "status": str(data.get("status") or "unknown"),
            "output": _response_text(data),
            "usage": {
                "input_tokens": itok,
                "output_tokens": otok,
                "output_reasoning_tokens": int(
                    ((usage.get("output_tokens_details") or {}).get("reasoning_tokens") or 0)
                ),
            },
            "estimated_usd": round(estimate, 6),
            "incomplete_reason": (data.get("incomplete_details") or {}).get("reason"),
        }
        if result["status"] != "completed" or not result["output"]:
            raise ProviderProblem("incomplete_or_blank", result["status"])
        return result


def _embed(text: str) -> np.ndarray:
    """Deterministic, deliberately lexical fixture for *mechanical* SSL only."""
    vector = np.zeros(96, dtype=np.float64)
    for term in re.findall(r"[^\W_]+", text.casefold(), flags=re.UNICODE):
        part = hashlib.sha256(term.encode("utf-8")).digest()
        i = int.from_bytes(part[:4], "big") % vector.size
        vector[i] += 1.0
    if not vector.any():
        vector[0] = 1.0
    return vector


def _candidate(raw: str) -> str | None:
    stripped = raw.strip()
    if stripped.upper() == "NONE":
        return None
    lines = [x.strip().strip("-• ").strip() for x in stripped.splitlines() if x.strip()]
    if len(lines) != 1 or len(lines[0]) > 300:
        return None
    val = re.sub(r"^\d+[.):]\s*", "", lines[0]).strip()
    if val.count("?") != 1 or not val.endswith("?"):
        return None
    if len(re.findall(r"[^\W_]+", val)) < 4:
        return None
    return val


def _actual_ssl_manager():
    # CI checks out precisely the merged/current production core commit.
    from shadowseed.manager import SSLManager
    return SSLManager(embedding_fn=_embed)


def _prompt_for_turn(t: int) -> str:
    assert 0 <= t < len(TURNS)
    history = "\n".join(
        f"Eerdere vaste gebruikerswaarneming {i+1}: {q}"
        for i, q in enumerate(TURNS[:t])
    )
    return (history + "\n\n" if history else "") + (
        f"HUIDIGE VRAAG {t+1}:\n{TURNS[t]}"
    )


def _snapshot(manager) -> list[dict[str, Any]]:
    return [
        {
            "id": sid, "text": seed.text, "status": seed.status.value,
            "trace": round(float(seed.trace), 6),
            "weight": round(float(seed.weight), 6),
            "occurrence_count": int(seed.occurrence_count),
            "evidence_count": int(seed.evidence_count),
        }
        for sid, seed in sorted(manager.seeds.items())
    ]


def run_model_arm(api: MeteredOpenAI, model: str) -> dict:
    from shadowseed.gate.signals import recurrence_signal

    manager = _actual_ssl_manager()
    arm = {
        "model": model,
        "turns": [],
        "status": "started",
        "core_sha": CORE_SHA,
        "prompt_contract": "one-atomic-unspoken-possibility-not-omission-checklist-v1",
        "embedder": "synthetic_hash_lexical_not_semantic_quality",
        "gate_policy": "evidence_backed",
        "original_answers_never_receive_seed_text": True,
        "third_party_evidence": False,
    }
    for idx in range(len(TURNS)):
        if idx:
            manager.decay_traces(turns_passed=1)
        reactivated = manager.scan_trtl_triggers(TURNS[idx])
        baseline_prompt = _prompt_for_turn(idx)
        baseline = api.ask(
            model, BASELINE_INSTRUCTION, baseline_prompt,
            output_cap=MAX_OUTPUT_BASELINE,
        )
        detector_prompt = (
            "ACTUELE VRAAG:\n" + TURNS[idx] +
            "\n\nORIGINEEL ANTWOORD (zonder Shadowseed):\n" +
            baseline["output"]
        )
        detected = api.ask(
            model, DETECTION_INSTRUCTION, detector_prompt,
            output_cap=MAX_OUTPUT_INQUIRY,
        )
        proposal = _candidate(detected["output"])
        ingest = {"accepted": [], "rejected": []}
        gate_events = []
        if proposal is not None:
            trigger_terms = tuple(
                x for x in re.findall(r"[^\W_]+", proposal.casefold()) if len(x) >= 5
            )[:5]
            ingest = manager.ingest_detection_candidates(
                [proposal],
                trigger_keywords=trigger_terms,
                expand_short_fragments=False,
                split_broad=False,
            )
            for item in ingest.get("accepted", []):
                seed = manager.seeds[item["seed_id"]]
                if seed.occurrence_count < 2:
                    continue
                signal = recurrence_signal(
                    seed.occurrence_count, threshold=2,
                    source_ref=f"synthetic:model:{model}:turn:{idx+1}",
                )
                assert not signal.is_external_evidence
                event = manager.submit_signals(
                    item["seed_id"], [signal], policy_id="evidence_backed"
                )
                gate_events.append({
                    "seed_id": item["seed_id"],
                    "decision": event.decision.value,
                    "policy_id": event.policy_id,
                })
        state = _snapshot(manager)
        if any(seed["weight"] != 0 or seed["evidence_count"] != 0 for seed in state):
            raise AssertionError("Weightless/evidence boundary violated")
        arm["turns"].append({
            "turn": idx + 1,
            "user_question": TURNS[idx],
            "baseline": baseline,
            "detector": detected,
            "parsed_candidate": proposal,
            "intake": {
                "accepted": ingest.get("accepted", []),
                "rejected": ingest.get("rejected", []),
            },
            "reactivated_seed_ids": reactivated,
            "gate_events": gate_events,
            "seed_state_after_turn": state,
            "point_of_use_authority": False,
        })
        print(
            f"RECORDED {model} turn={idx+1} "
            f"baseline_id={baseline['response_id']} "
            f"candidate_id={detected['response_id']} "
            f"candidate={'yes' if proposal else 'none'} "
            f"seeds={len(state)} weight_max=0", flush=True
        )
    arm["status"] = "completed"
    arm["final_seed_count"] = len(manager.seeds)
    arm["born_weightless"] = all(
        row["weight"] == 0
        for turn in arm["turns"]
        for row in turn["seed_state_after_turn"]
    )
    return arm


def check_structure() -> None:
    assert MODEL_IDS == ("gpt-5", "gpt-6-astra")
    assert len(TURNS) == 3
    assert MAX_CALLS == len(MODEL_IDS) * len(TURNS) * 2
    assert MAX_ESTIMATED_DOLLARS <= 2.0
    assert _candidate("Hoe verschilt zelfstandig leren van het voltooien van taken?")
    assert _candidate("NONE") is None
    assert _candidate("What? What?") is None
    assert _embed("leren").shape == (96,)
    from shadowseed.manager import SSLManager
    m = SSLManager(embedding_fn=_embed)
    ingestion = m.ingest_detection_candidates(
        ["Hoe hangen leeractiviteit en zelfstandige uitvoering samen?"],
        expand_short_fragments=False, split_broad=False,
    )
    assert len(ingestion["accepted"]) == 1
    sid = ingestion["accepted"][0]["seed_id"]
    assert m.seeds[sid].weight == 0.0 and m.seeds[sid].trace > 0.0
    m.decay_traces(turns_passed=0)
    assert m.seeds[sid].weight == 0.0
    print("SELF_TEST_OK: no OpenAI calls, core=" + CORE_SHA, flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--execute", action="store_true")
    opts = parser.parse_args()
    if opts.self_test:
        check_structure()
        return 0
    if not opts.execute:
        parser.error("Use --execute to make the authorized, billable calls")
    check_structure()

    key = os.environ.get("OPENAI_API_KEY", "").strip()
    # IMPORTANT: only the pre-existing Actions Secret is supported.
    # Never load committed .env files from any repository.
    if not key:
        print("NOT_EXECUTED: OPENAI_API_KEY Actions Secret unavailable", flush=True)
        return 3
    try:
        api = MeteredOpenAI(key)
    except ValueError:
        print("NOT_EXECUTED: configured API credential is unusable", flush=True)
        return 3
    started = datetime.now(timezone.utc).isoformat()
    output = {
        "experiment": "ssl-core-gpt5-vs-gpt6-astra-first-live-pilot",
        "status": "running",
        "started_utc": started,
        "model_ids": list(MODEL_IDS),
        "source_core_sha": CORE_SHA,
        "criteria": [
            "genuine_provider_response_and_usage",
            "atomic_unspoken_candidate_grounded_in_draft",
            "weight_zero_at_birth",
            "recurrence_is_not_external_evidence",
            "no_authorized_answer_steering_without_verified_support",
        ],
        "method_limits": [
            "3 synthetic user-turns only",
            "No independent blind reviewer labels; no quality claim",
            "No SSL vs baseline efficacy claim: weightless seeds cannot influence outputs",
            "Lexical embeddings are a mechanical fixture, not semantically validated",
            "No H-neuron or knowledge-state inference",
            "GPT-5 and GPT-6 answers may differ even with identical fixed user context",
        ],
        "bounds": {
            "max_requests": MAX_CALLS,
            "max_output_tokens_answer": MAX_OUTPUT_BASELINE,
            "max_output_tokens_detector": MAX_OUTPUT_INQUIRY,
            "estimated_usd_safety_limit": MAX_ESTIMATED_DOLLARS,
        },
        "arms": [],
        "errors": [],
    }
    results = Path("results") / "ssl-gpt5-gpt6-astra-2026-10-23.json"
    results.parent.mkdir(parents=True, exist_ok=True)
    for model in MODEL_IDS:
        before = api.calls
        try:
            arm = run_model_arm(api, model)
            output["arms"].append(arm)
        except ProviderProblem as exc:
            output["errors"].append({
                "model": model, "status": exc.status, "code": exc.code,
                "attempts_on_model": api.calls - before,
            })
            print(f"MODEL_FAILED {model}: {exc.status} {exc.code}", flush=True)
        except Exception as exc:
            output["errors"].append({
                "model": model,
                "status": "instrument_error",
                "code": type(exc).__name__,
                "attempts_on_model": api.calls - before,
            })
            print(f"INSTRUMENT_FAILED {model}: {type(exc).__name__}", flush=True)
    output["ended_utc"] = datetime.now(timezone.utc).isoformat()
    output["total_calls_attempted"] = api.calls
    output["estimated_total_usd"] = round(api.estimated_cost, 6)
    successful_models = [a["model"] for a in output["arms"] if a["status"] == "completed"]
    output["status"] = (
        "completed" if len(successful_models) == 2
        else "partial" if len(successful_models) == 1 else "failed"
    )
    results.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("SUMMARY_JSON_BEGIN", flush=True)
    print(json.dumps({
        "status": output["status"],
        "models_completed": successful_models,
        "errors": output["errors"],
        "calls_attempted": api.calls,
        "estimated_usd": round(api.estimated_cost, 6),
        "result_file": str(results),
        "seed_counts": {a["model"]: a.get("final_seed_count", 0) for a in output["arms"]},
    }, sort_keys=True), flush=True)
    print("SUMMARY_JSON_END", flush=True)
    return 0 if output["status"] == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())
