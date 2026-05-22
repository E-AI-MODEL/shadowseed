"""Open-set taalmodel-detector v0.3 — satisfies the SSL 4.6 one-sentence claim.

Per `docs/00_shadow_seed_learning_4_6.md` the open-set detection step has to
come from a taalmodel. v0.1 (regex templates) and v0.2 (text-grounded
templates) are baselines that do not satisfy that claim. This module is the
first detector that does: given an input item, it prompts a language model
with a Dutch detection prompt derived from `docs/05_prompts.md` and parses
the numbered output into candidate seeds.

Two backends, mirroring the model-benefit-suite pattern:

- ``fixture``: deterministic, no model download, no network. Returns
  text-grounded seeds with a clearly distinctive ``[FIXTURE]`` prefix so
  tests and reviewers can never mistake them for real model output. Used
  in CI and for offline development.
- ``hf-transformers``: real local model via the ``transformers`` stack.
  Opt-in, requires the optional ``models`` extra and a model id, and
  requires network access to download the model (or a pre-warmed HF cache).

The seeds are still hypotheses for human review, not labels. The same
atomicity, normalization and zero-weight storage rules in SSLManager apply
around whatever this detector returns.
"""

from __future__ import annotations

import re
from typing import Any, Protocol


OPEN_SET_MODEL_DETECTOR_ID = "ssl46_open_set_model_detector_v0.3"
OPEN_SET_MODEL_DETECTOR_SOURCE = "open_set_model_detector"


OPEN_SET_DETECTION_PROMPT = """
Je bent een epistemische analist.

Je krijgt een korte inputtekst. Je taak is NIET om de tekst samen te vatten,
te citeren of te paraphraseren. Je taak is om kleine structurele
afwezigheden te vinden: welke kleine concepten, relaties of randvoorwaarden
ONTBREKEN in deze tekst terwijl ze nodig zouden zijn voor een volledig
begrip van dit specifieke onderwerp?

Regels:
- Geef maximaal {max_seeds} seeds.
- Elke seed bevat precies één gap, geformuleerd als hele Nederlandse zin.
- Elke seed benoemt iets dat NIET in de tekst staat maar wel zou moeten.
- Elke seed verwijst concreet naar iets in deze tekst (een entiteit, een
  beslissing, een claim), niet naar een willekeurige tekst van dit type.
- Geen citaten of fragmenten uit de inputtekst.
- Geen losse woorden, namen of acroniemen zonder relatie.
- Geen samengestelde analysekaders of lijsten binnen één seed.
- Geen meta-categorieën zoals "Onderbouwing van de centrale bewering" of
  "Tijdlijn van de gebeurtenis".

Niet goed (citaat / fragment / leeg):
1. Sven Jaschan
2. Apple Computer Inc.
3. AAPL.O&gt
4. Bron van de centrale bewering.

Wel goed (concrete ontbrekende relatie):
1. Motivatie van Sven Jaschan om de Netsky-worm te schrijven.
2. Effect van de Apple-licentievoorwaarden op derde-partij ontwikkelaars.
3. Verantwoordelijke toezichthouder bij grensoverschrijdende virusinfecties.

Inputtekst:
{text}

Geef nu maximaal {max_seeds} echte gap-seeds in dit formaat. Begin direct met "1.".

Output:
1.
""".strip()


class DetectorBackend(Protocol):
    name: str

    def detect_seeds(self, item: dict[str, Any], max_seeds: int = 5) -> list[str]:
        ...


_NUMBERED_LINE = re.compile(r"^\s*\d+[.)]\s*(.+?)\s*$")
_HTML_ENTITY = re.compile(r"&(?:[a-zA-Z]+|#\d+);?")
_ACRONYM_ONLY = re.compile(r"^[A-Z][A-Z0-9.&;<>\-]{1,8}$")


def _looks_like_citation_fragment(seed: str, source_text: str) -> bool:
    """Heuristic filter for clearly non-seed output from small models.

    Drops candidates that are too short, that are obvious HTML/garbage, that
    are bare acronyms, or that appear as a literal long substring of the
    source text. These all indicate the model copied from the input rather
    than naming a gap.
    """
    stripped = seed.strip()
    if not stripped:
        return True
    if _HTML_ENTITY.search(stripped):
        return True
    word_count = len(stripped.split())
    if word_count <= 2:
        return True
    if _ACRONYM_ONLY.match(stripped):
        return True
    # Long literal substring of input → almost certainly a citation
    if source_text and word_count <= 16:
        normalized_seed = re.sub(r"\s+", " ", stripped).strip(" .,:;-").lower()
        normalized_source = re.sub(r"\s+", " ", source_text).lower()
        if len(normalized_seed) >= 20 and normalized_seed in normalized_source:
            return True
    return False


def parse_numbered_seeds(
    raw_output: str,
    max_seeds: int = 5,
    source_text: str = "",
) -> list[str]:
    """Parse `1. seed` style lines out of a model response.

    Lines without a leading number are ignored. Blank seeds, the literal
    placeholder ``[seed]``, citation fragments (HTML entities, bare
    acronyms, very short stubs, long substrings of the source text) and
    duplicates are dropped. Returns at most ``max_seeds`` items in source
    order.

    `source_text` is the inputtext that was given to the model. When
    provided, candidates that appear as a long literal substring of it are
    dropped as citations.
    """
    seeds: list[str] = []
    seen: set[str] = set()
    for line in raw_output.splitlines():
        match = _NUMBERED_LINE.match(line)
        if not match:
            continue
        seed = match.group(1).strip().strip("-•").strip()
        if not seed or seed.lower() == "[seed]":
            continue
        if _looks_like_citation_fragment(seed, source_text):
            continue
        if seed in seen:
            continue
        seen.add(seed)
        seeds.append(seed)
        if len(seeds) >= max_seeds:
            break
    return seeds


def build_detection_prompt(text: str, max_seeds: int = 5) -> str:
    return OPEN_SET_DETECTION_PROMPT.format(text=text.strip(), max_seeds=max_seeds)


class FixtureDetectorBackend:
    """Deterministic CI backend. Marks every seed with ``[FIXTURE]``."""

    name = "fixture"

    def detect_seeds(self, item: dict[str, Any], max_seeds: int = 5) -> list[str]:
        text = str(item.get("text") or item.get("input") or "").strip()
        if not text:
            return []
        # take up to max_seeds distinct capitalized tokens from the text
        tokens: list[str] = []
        seen: set[str] = set()
        for token in re.findall(r"\b[A-ZÀ-Þ][a-zA-ZÀ-ÿ]{2,}\b", text):
            key = token.lower()
            if key in seen:
                continue
            seen.add(key)
            tokens.append(token)
            if len(tokens) >= max_seeds:
                break
        return [
            f"[FIXTURE] Ontbrekende toelichting bij {token} in deze tekst."
            for token in tokens
        ]


class HFTransformersDetectorBackend:
    """Local Hugging Face transformers backend for real taalmodel detection.

    Opt-in. Requires ``pip install -e '.[models]'`` and network access to
    download the model (or a pre-warmed HF cache). Default decoding is
    greedy and deterministic so the same input produces the same seeds.
    """

    def __init__(self, model_id: str, max_new_tokens: int = 400) -> None:
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "Install optional model dependencies first: "
                "pip install -e '.[models]' transformers torch"
            ) from exc

        self.name = f"hf-transformers:{model_id}"
        self.model_id = model_id
        self.max_new_tokens = max_new_tokens
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        model_kwargs: dict[str, Any] = {}
        if torch.cuda.is_available():
            model_kwargs = {"torch_dtype": torch.float16, "device_map": "auto"}
        model = AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)
        self.generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=self.tokenizer,
            device=0 if torch.cuda.is_available() else -1,
        )

    def detect_seeds(self, item: dict[str, Any], max_seeds: int = 5) -> list[str]:
        text = str(item.get("text") or item.get("input") or "").strip()
        if not text:
            return []
        prompt = build_detection_prompt(text, max_seeds=max_seeds)
        output = self.generator(
            prompt,
            max_new_tokens=self.max_new_tokens,
            do_sample=False,
            return_full_text=False,
        )
        raw = output[0]["generated_text"]
        # the prompt ends with "1.\n" — re-prepend so the parser sees the first item
        return parse_numbered_seeds(
            "1. " + raw, max_seeds=max_seeds, source_text=text
        )


SUPPORTED_MODEL_BACKENDS: tuple[str, ...] = ("fixture", "hf-transformers")


def make_detector_backend(
    backend: str,
    model_id: str | None = None,
    max_new_tokens: int = 400,
) -> DetectorBackend:
    if backend == "fixture":
        return FixtureDetectorBackend()
    if backend == "hf-transformers":
        if not model_id:
            raise ValueError(
                "--model-id is required for --model-backend hf-transformers"
            )
        return HFTransformersDetectorBackend(
            model_id=model_id, max_new_tokens=max_new_tokens
        )
    raise ValueError(
        f"Onbekende model-backend {backend!r}. "
        f"Toegestaan: {SUPPORTED_MODEL_BACKENDS}."
    )
