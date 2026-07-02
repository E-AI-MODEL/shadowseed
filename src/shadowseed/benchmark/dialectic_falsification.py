"""Dialectische falsificatie: "valt dit weg te argumenteren?" (vision item 4).

De contradiction-check van de Gate is lexicaal/numeriek; generatieve
"kunnen staan"-seeds vragen een echte dialectische toets: een model probeert de
seed actief weg te argumenteren tegen de brontekst. Dit is de instap van
Laag G (`docs/research/laag-g-scoping.md`); het H-neuron-achtige interne
signaal is het latere fundament.

Doctrine, hard in de uitkomst-mapping:

- WEERLEGD -> contradictie via de Validation Gate: gewicht daalt en het
  agent-contract blokkeert de seed vanaf dat moment;
- HOUDT_STAND -> bounded probe-feedback (``probe_type="dialectic"``): kan
  gewicht beperkt bevestigen maar **nooit promoveren** — promotie blijft
  exclusief aan de Gate;
- ONBESLIST (ook de fail-safe bij onparseerbare modeloutput) -> neutrale
  feedback, geen state-verandering van betekenis.

Dialectiek kan invloed dus alleen wegnemen of beperkt bevestigen, nooit
toekennen.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from shadowseed.benchmark.ssl45_gap_suite import lexical_embedding
from shadowseed.manager import SSLManager

VERDICT_WEERLEGD = "WEERLEGD"
VERDICT_HOUDT_STAND = "HOUDT_STAND"
VERDICT_ONBESLIST = "ONBESLIST"
_VERDICTS = (VERDICT_WEERLEGD, VERDICT_HOUDT_STAND, VERDICT_ONBESLIST)

_VERDICT_LINE_RE = re.compile(r"VERDICT\s*:\s*(.+)", re.IGNORECASE)
_VERDICT_TOKEN_RE = re.compile(r"WEERLEGD|HOUDT[_ ]STAND|ONBESLIST", re.IGNORECASE)
_REASON_RE = re.compile(r"REDEN\s*:\s*(.+)", re.IGNORECASE)


def build_dialectic_prompt(seed_text: str, source_text: str) -> str:
    """Ask the model to actively argue the seed away against the source."""
    return (
        "Je bent een strenge dialectische toetser. Hieronder staan een BRONTEKST "
        "en een STELLING (een kandidaat-ontbrekend punt bij die bron). Probeer de "
        "stelling actief weg te argumenteren: is zij overbodig, al gedekt door de "
        "bron, of strijdig met de bron?\n\n"
        f"BRONTEKST:\n{source_text}\n\n"
        f"STELLING:\n{seed_text}\n\n"
        "Antwoord in exact dit format (niets anders):\n"
        "VERDICT: WEERLEGD | HOUDT_STAND | ONBESLIST\n"
        "REDEN: <één zin>\n\n"
        "WEERLEGD = de stelling valt weg te argumenteren (gedekt, overbodig of "
        "strijdig). HOUDT_STAND = de stelling overleeft de aanval als echt, "
        "toetsbaar ontbrekend punt. ONBESLIST = niet uit te maken op deze bron."
    )


def parse_dialectic_verdict(raw: str) -> dict[str, str]:
    """Parse the model output; anything but one unambiguous verdict fails safe.

    The verdict line must contain exactly one allowed option. A backend that
    echoes the format line ("VERDICT: WEERLEGD | HOUDT_STAND | ONBESLIST"), or
    hedges with multiple options, must land on ONBESLIST — never on a
    contradiction it did not actually assert.
    """
    line_match = _VERDICT_LINE_RE.search(raw or "")
    if not line_match:
        return {"verdict": VERDICT_ONBESLIST, "reason": "onparseerbare modeloutput"}
    tokens = {
        t.upper().replace(" ", "_") for t in _VERDICT_TOKEN_RE.findall(line_match.group(1))
    }
    if len(tokens) != 1:
        return {
            "verdict": VERDICT_ONBESLIST,
            "reason": "ambigu verdict (geen of meerdere opties op de VERDICT-regel)",
        }
    reason_match = _REASON_RE.search(raw)
    reason = reason_match.group(1).strip() if reason_match else ""
    return {"verdict": tokens.pop(), "reason": reason}


class FixtureDialecticBackend:
    """Deterministic CI backend: verdict from lexical overlap with the source.

    A seed sharing no content tokens with the source is treated as arguable
    away (WEERLEGD); a seed sharing tokens holds (HOUDT_STAND). This checks the
    harness mechanics, not dialectic quality.
    """

    name = "fixture"

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {t for t in re.findall(r"[a-zà-ÿ0-9]+", text.lower()) if len(t) > 4}

    def generate(self, prompt: str, scenario: dict, mode: str, ssl_seeds: list[str]) -> str:
        seed_text = scenario.get("seed_text", "")
        source_text = scenario.get("source_text", "")
        overlap = self._tokens(seed_text) & self._tokens(source_text)
        if overlap:
            return "VERDICT: HOUDT_STAND\nREDEN: deelt inhoudswoorden met de bron."
        return "VERDICT: WEERLEGD\nREDEN: geen aanknoping met de bron."


def apply_dialectic_outcome(
    manager: SSLManager, seed_id: str, verdict: str
) -> dict[str, Any]:
    """Map a dialectic verdict onto the sanctioned lifecycle channels."""
    if verdict not in _VERDICTS:
        raise ValueError(f"Onbekend dialectisch verdict: {verdict!r}")
    seed = manager.seeds[seed_id]
    weight_before = float(seed.weight)
    if verdict == VERDICT_WEERLEGD:
        gate = manager.run_validation_gate_detailed(seed_id, contradiction=True)
        channel = "gate_contradiction"
        detail: dict[str, Any] = {"gate_verdict": gate.verdict}
    else:
        outcome = "reward" if verdict == VERDICT_HOUDT_STAND else "neutral"
        fb = manager.apply_probe_feedback(seed_id, outcome, probe_type="dialectic")
        channel = "probe_feedback"
        detail = {"outcome": fb.outcome, "delta_applied": fb.delta_applied, "skipped": fb.skipped}
    return {
        "seed_id": seed_id,
        "verdict": verdict,
        "channel": channel,
        "weight_before": weight_before,
        "weight_after": float(seed.weight),
        "status_after": seed.status.value,
        **detail,
    }


def run_dialectic_probe(
    manager: SSLManager, seed_id: str, source_text: str, model: Any
) -> dict[str, Any]:
    """One full dialectic pass for one seed: prompt -> verdict -> lifecycle."""
    seed = manager.seeds[seed_id]
    prompt = build_dialectic_prompt(seed.text, source_text)
    raw = model.generate(
        prompt, {"seed_text": seed.text, "source_text": source_text}, "dialectic", []
    )
    parsed = parse_dialectic_verdict(raw)
    record = apply_dialectic_outcome(manager, seed_id, parsed["verdict"])
    record["reason"] = parsed["reason"]
    record["raw_output"] = raw
    return record


def _promote_via_gate(manager: SSLManager, seed_id: str) -> None:
    """Drive a fixture seed to PROMOTED through the real Gate (no shortcuts)."""
    seed = manager.seeds[seed_id]
    for _ in range(8):
        if seed.status.value == "PROMOTED":
            return
        seed.occurrence_count += 1
        manager.run_validation_gate(seed_id, external_evidence=True)
    raise RuntimeError(f"Fixture-seed {seed_id} promoveerde niet via de Gate")


def run_dialectic_falsification(
    input_path: str,
    output_path: str = "results/dialectic_falsification.json",
    backend: str = "fixture",
    model_id: str | None = None,
    max_new_tokens: int = 200,
) -> dict[str, Any]:
    """Run the dialectic probe over a case file and write a result artifact.

    Input schema: ``{"source_text": ..., "cases": [{"seed_text": ...,
    "expected_verdict": ...?}, ...]}``. Every seed is ingested weightless and
    promoted through the real Gate first, so the probe attacks exactly the
    seeds that would be allowed to steer — falsification where it matters.
    """
    data = json.loads(Path(input_path).read_text(encoding="utf-8"))
    source_text = data["source_text"]
    if backend == "fixture":
        model: Any = FixtureDialecticBackend()
    else:
        from shadowseed.benchmark.ssl45_model_benefit_suite import make_backend

        model = make_backend(backend=backend, model_id=model_id, max_new_tokens=max_new_tokens)

    manager = SSLManager(embedding_fn=lexical_embedding)
    records: list[dict[str, Any]] = []
    for case in data["cases"]:
        ingest = manager.ingest_detection_candidates([case["seed_text"]])
        accepted = ingest.get("accepted", [])
        if not accepted:
            records.append({"seed_text": case["seed_text"], "skipped": "niet geaccepteerd"})
            continue
        sid = accepted[0]["seed_id"]
        _promote_via_gate(manager, sid)
        record = run_dialectic_probe(manager, sid, source_text, model)
        record["seed_text"] = case["seed_text"]
        expected = case.get("expected_verdict")
        if expected:
            record["expected_verdict"] = expected
            record["matches_expected"] = record["verdict"] == expected
        records.append(record)

    result = {
        "artifact": "dialectic_falsification",
        "backend": getattr(model, "name", backend),
        "doctrine": (
            "dialectiek neemt invloed weg (Gate-contradictie) of bevestigt bounded "
            "(probe-feedback); zij promoveert nooit."
        ),
        "source_text": source_text,
        "records": records,
        "summary": {
            "cases": len(records),
            "weerlegd": sum(1 for r in records if r.get("verdict") == VERDICT_WEERLEGD),
            "houdt_stand": sum(1 for r in records if r.get("verdict") == VERDICT_HOUDT_STAND),
            "onbeslist": sum(1 for r in records if r.get("verdict") == VERDICT_ONBESLIST),
        },
    }
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result
