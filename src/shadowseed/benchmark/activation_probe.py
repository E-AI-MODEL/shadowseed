"""Laag G, spoor 2: de activatie-sonde (H-neuron-richting, eerste stap).

Vraag van Laag G: is er *interne* modelsteun voor wat extern als
onhoudbaar/houdbaar wordt geoordeeld? Deze sonde registreert
MLP-activaties tijdens het dialectische verdict (spoor 1,
`dialectic_falsification.py`) en meet per laag hoe goed de activaties de
verdict-klassen WEERLEGD en HOUDT_STAND scheiden — in de geest van
H-Neurons (Gao et al. 2025, arXiv 2512.01797, thunlp/H-Neurons, MIT).

Doctrine, hard in het ontwerp:

- de sonde raakt **geen** seed-state aan: geen manager, geen Gate, geen
  gewicht — zij leest alleen teksten en activaties (signaal != verdict);
- de analysekern is model-vrij en deterministisch (numpy) zodat CI de
  mechaniek bewaakt; de echte modelroute (torch/transformers) is opt-in
  achter de ``models``-extra;
- de uitkomst is een Laag G-*signaal*-artifact, per de laag-taal: het
  voedt geen promotie en geen claim — het meet of verder graven zin heeft.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from shadowseed.benchmark.dialectic_falsification import (
    VERDICT_HOUDT_STAND,
    VERDICT_WEERLEGD,
    FixtureDialecticBackend,
    build_dialectic_prompt,
    parse_dialectic_verdict,
)

# -- analysekern (model-vrij, deterministisch) --------------------------------


def select_focus_positions(
    offsets: list[tuple[int, int]], span_start: int, span_end: int
) -> list[int]:
    """Token-posities waarvan de char-offsets het focus-span overlappen."""
    return [
        i
        for i, (s, e) in enumerate(offsets)
        if e > span_start and s < span_end and e > s
    ]


def class_separation(
    activations: dict[str, list[np.ndarray]],
) -> dict[str, Any]:
    """Meet per laag hoe ver de klasse-gemiddelden uiteen liggen.

    ``activations`` mapt een klasse-label naar een lijst activatievectoren
    (één per case, zelfde laag). Rapporteert cosine-afstand tussen de
    klasse-centroïden en de top-dimensies met het grootste absolute
    verschil — kandidaat-'neuronen', geen bewezen neuronen.
    """
    labels = sorted(activations)
    if len(labels) != 2 or any(len(v) == 0 for v in activations.values()):
        return {"separable": False, "reason": "twee niet-lege klassen vereist"}
    a, b = (np.mean(np.stack(activations[label]), axis=0) for label in labels)
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    cosine = float(np.dot(a, b) / denom) if denom else 1.0
    diff = np.abs(a - b)
    top = np.argsort(diff)[::-1][:5]
    return {
        "separable": True,
        "classes": labels,
        "cosine_between_class_means": cosine,
        "cosine_distance": 1.0 - cosine,
        "candidate_dimensions": [
            {"dim": int(i), "abs_mean_diff": float(diff[i])} for i in top
        ],
        "n_per_class": {label: len(activations[label]) for label in labels},
    }


def probe_report(
    per_layer: dict[str, dict[str, list[np.ndarray]]],
) -> dict[str, Any]:
    """Per-laag scheiding + de laag met het sterkste signaal."""
    layers = {name: class_separation(acts) for name, acts in per_layer.items()}
    scored = {
        name: rep["cosine_distance"]
        for name, rep in layers.items()
        if rep.get("separable")
    }
    best = max(scored, key=scored.get) if scored else None
    return {
        "layers": layers,
        "strongest_layer": best,
        "strongest_cosine_distance": scored.get(best) if best else None,
    }


# -- activatie-backends --------------------------------------------------------


class FakeActivationModel:
    """Deterministische CI-backend: activaties uit een tekst-hash.

    Bewaakt uitsluitend de harnas-mechaniek (hooks->vectoren->analyse);
    zegt níets over echte modelinterne steun. De vector hangt alleen van de
    prompttekst af — geen klasse-informatie wordt ingebakken.
    """

    name = "fake"
    layer_names = ("mlp.0", "mlp.1")

    def __init__(self, dim: int = 16) -> None:
        self.dim = dim

    def activations_for(self, prompt: str, focus: str | None = None) -> dict[str, np.ndarray]:
        # bij token-scoped pooling hangt de vector alleen van het focus-span af
        basis = focus if focus and focus in prompt else prompt
        out: dict[str, np.ndarray] = {}
        for layer in self.layer_names:
            digest = hashlib.sha256(f"{layer}::{basis}".encode()).digest()
            rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
            out[layer] = rng.normal(size=self.dim)
        return out


class HFActivationModel:  # pragma: no cover - vereist torch/transformers (opt-in)
    """Echte sonde: forward-hooks op de MLP-lagen van een klein HF-model."""

    def __init__(self, model_id: str, device: str = "cpu") -> None:
        import torch  # noqa: F401
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.name = f"hf:{model_id}"
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(model_id)
        self.model.eval()
        self.device = device
        self.model.to(device)

    def activations_for(self, prompt: str, focus: str | None = None) -> dict[str, np.ndarray]:
        """Activaties per MLP-laag; met ``focus`` alleen gepoold over de
        tokens van dat tekstspan (round-026-les: full-sequence mean-pooling
        verdunt het stellingsverschil weg omdat de rest van de prompt
        identiek is)."""
        import torch

        positions: list[int] | None = None
        if focus:
            span_start = prompt.find(focus)
            if span_start >= 0:
                encoded = self.tokenizer(
                    prompt,
                    return_offsets_mapping=True,
                    truncation=True,
                    max_length=512,
                )
                positions = select_focus_positions(
                    encoded["offset_mapping"], span_start, span_start + len(focus)
                ) or None

        captured: dict[str, np.ndarray] = {}
        handles = []
        for name, module in self.model.named_modules():
            # dek de gangbare MLP-naamgevingen (GPT-2 'mlp', Llama-stijl 'mlp')
            if name.endswith(".mlp") or name.endswith(".mlp.c_proj"):
                def _hook(mod, inputs, output, _name=name):
                    tensor = output[0] if isinstance(output, tuple) else output
                    tensor = tensor.detach().float()
                    if positions is not None and tensor.dim() == 3:
                        tensor = tensor[:, positions, :]
                    captured[_name] = tensor.mean(dim=(0, 1)).cpu().numpy()
                handles.append(module.register_forward_hook(_hook))
        try:
            tokens = self.tokenizer(
                prompt, return_tensors="pt", truncation=True, max_length=512
            ).to(self.device)
            with torch.no_grad():
                self.model(**tokens)
        finally:
            for h in handles:
                h.remove()
        return captured


# -- de sonde-run ---------------------------------------------------------------


def run_activation_probe(
    input_path: str,
    output_path: str = "results/activation_probe.json",
    backend: str = "fake",
    model_id: str | None = None,
    pooling: str = "stelling",
) -> dict[str, Any]:
    """Sondeer de dialectische cases: activaties per verdict-klasse, per laag.

    Gebruikt dezelfde case-file als ``run-dialectic-falsification``
    (``source_text`` + ``cases``). Het verdict komt in deze eerste sonde uit
    de deterministische fixture-dialectiek (mechaniek-label); een echte
    modelrun combineert later een echt dialectisch verdict met echte
    activaties. Er wordt géén manager en géén seed-state aangeraakt.
    """
    data = json.loads(Path(input_path).read_text(encoding="utf-8"))
    source_text = data["source_text"]
    if backend == "fake":
        model: Any = FakeActivationModel()
    elif backend == "hf":
        if not model_id:
            raise ValueError("--model-id is verplicht voor backend 'hf'")
        model = HFActivationModel(model_id)
    else:
        raise ValueError(f"Onbekende activation-probe backend: {backend!r}")

    verdict_backend = FixtureDialecticBackend()
    per_layer: dict[str, dict[str, list[np.ndarray]]] = {}
    cases_out: list[dict[str, Any]] = []
    for case in data["cases"]:
        seed_text = case["seed_text"]
        prompt = build_dialectic_prompt(seed_text, source_text)
        raw = verdict_backend.generate(
            prompt, {"seed_text": seed_text, "source_text": source_text}, "dialectic", []
        )
        verdict = parse_dialectic_verdict(raw)["verdict"]
        if verdict not in (VERDICT_WEERLEGD, VERDICT_HOUDT_STAND):
            continue  # ONBESLIST draagt geen klasse-signaal
        focus = seed_text if pooling == "stelling" else None
        acts = model.activations_for(prompt, focus=focus)
        for layer, vec in acts.items():
            per_layer.setdefault(layer, {}).setdefault(verdict, []).append(vec)
        cases_out.append({"seed_text": seed_text, "verdict": verdict, "layers": sorted(acts)})

    result = {
        "artifact": "activation_probe",
        "evidence_layer": "G",
        "backend": getattr(model, "name", backend),
        "pooling": pooling,
        "doctrine": (
            "Laag G-signaal: activatie-scheiding tussen dialectische "
            "verdict-klassen. Signaal != verdict; raakt geen seed-state; "
            "voedt geen promotie. Fake-backend bewijst alleen de "
            "harnas-mechaniek."
        ),
        "cases": cases_out,
        "report": probe_report(per_layer),
    }
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result
