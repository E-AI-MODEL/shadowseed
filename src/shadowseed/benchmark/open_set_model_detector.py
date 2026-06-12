"""Open-set taalmodel-detector v0.3 — satisfies the SSL 4.6 one-sentence claim.

Per `docs/00_shadow_seed_learning_4_6.md` the open-set detection step has to
come from a taalmodel. v0.1 (regex templates) and v0.2 (text-grounded
templates) are baselines that do not satisfy that claim. This module is the
first detector that does: given an input item, it prompts a language model
with a Dutch detection prompt derived from `docs/05_prompts.md` and parses
the numbered output into candidate seeds.

Three backends, mirroring the model-benefit-suite pattern:

- ``fixture``: deterministic, no model download, no network. Returns
  text-grounded seeds with a clearly distinctive ``[FIXTURE]`` prefix so
  tests and reviewers can never mistake them for real model output. Used
  in CI and for offline development.
- ``hf-transformers``: real local model via the ``transformers`` stack.
  Opt-in, requires the optional ``models`` extra and a model id, and
  requires network access to download the model (or a pre-warmed HF cache).
- ``ollama``: real model served by a local Ollama server over HTTP. Opt-in,
  needs no Python model deps (stdlib only); install Ollama, ``ollama pull``
  the model, and pass its id. Lightweight enough for a standard CI runner.

The seeds are still hypotheses for human review, not labels. The same
atomicity, normalization and zero-weight storage rules in SSLManager apply
around whatever this detector returns.
"""

from __future__ import annotations

import re
from typing import Any, Protocol


OPEN_SET_MODEL_DETECTOR_ID = "ssl46_open_set_model_detector_v0.3"
OPEN_SET_MODEL_DETECTOR_SOURCE = "open_set_model_detector"


# Few-shot examples deliberately come from domains that are NOT the open-set
# news corpus (history, software, law, medicine). When the model leaks an
# example verbatim into a news item it is then obviously off-topic and is also
# caught by the verbatim leakage filter below. Using news-domain entities here
# (the v0.3b mistake) let the model blend "Sven Jaschan" / "Apple" into
# unrelated news items because they pattern-matched the input.
_FEWSHOT_BAD = (
    "Onderbouwing van de centrale bewering.",
    "Tijdlijn van de gebeurtenis.",
    "Security, privacy en schaalbaarheid.",
    "&lt;tag&gt;",
)
_FEWSHOT_GOOD = (
    "Koloniaal kapitaal als financieringsbron voor Britse fabrieksinvesteringen.",
    "AVG-compliance bij verwerking van medische hartslagdata.",
    "Rechtsbevoegdheid bij een grensoverschrijdend consumentengeschil.",
)


def _numbered(lines: tuple[str, ...]) -> str:
    return "\n".join(f"{i}. {line}" for i, line in enumerate(lines, start=1))


# Prompt iteration v0.3g: resolves the scaffold contradiction that round 006
# exposed. v0.3e's RULE demanded absence sentences ("... wordt niet vermeld")
# while its few-shot EXAMPLES showed bare noun phrases — the canonical 4.5
# seed form ("Koloniaal kapitaal als financieringsbron ..."). Qwen followed
# the rule; Phi followed the examples (and form compliance proved
# domain-dependent: 0/60 scaffolded on news, 18/60 on science). v0.3g aligns
# the rule with the examples: the gap-label noun phrase is canonical, the
# absence sentence stays allowed, and asserting a fact stays forbidden. A
# noun phrase cannot assert a fact (no main-clause verb), so the
# claim-vs-gap failure mode this rule exists for is structurally excluded.
#
# Note (02_atomic_seeds §2): generation enforces only "one gap per seed", "no
# fabricated facts", and "tie the gap to THIS text". Value judgments —
# triviality, specificity, relevance, redundancy — are review/Gate/normalization
# concerns, NOT generation blockades, because pre-judging value at birth breaks
# the weightless-seed principle. Redundant near-duplicates are deduplicated
# downstream (normalization, 4.5 §12.4) and surfaced by the prescreen, not
# suppressed here.
OPEN_SET_DETECTION_PROMPT = """
Je bent een epistemische analist.

Je krijgt een korte inputtekst. Je taak is NIET om de tekst samen te vatten,
te citeren of te paraphraseren. Je taak is om kleine structurele
afwezigheden te vinden: welke kleine concepten, relaties of randvoorwaarden
ONTBREKEN in deze tekst terwijl ze nodig zouden zijn voor een volledig
begrip van dit specifieke onderwerp?

Regels:
- Geef maximaal {max_seeds} kandidaat-lacunes.
- Elke kandidaat-lacune bevat precies één ontbrekend element, geformuleerd als
  hele Nederlandse zin.
- De output is alleen detectoroutput voor latere review. Ken zelf geen seed-,
  evidence- of Round 001-status toe.
- Benoem elke kandidaat-lacune als het ONTBREKENDE element zelf: een korte,
  concrete zinsnede, in de vorm van de goede voorbeelden hieronder. Een
  volledige afwezigheidszin ("... wordt niet vermeld.") mag ook.
  Schrijf NIET een stelling alsof je een nieuw feit beweert.
  * Fout (bewering): "De toezichthouder heeft geen onderzoek gedaan."
  * Goed (lacune-label): "De uitkomst van het onderzoek van de toezichthouder."
  * Ook goed (afwezigheidszin): "Of de toezichthouder onderzoek heeft gedaan,
    wordt niet vermeld."
- Noem alleen iets als ontbrekend wanneer het ECHT niet in de tekst staat.
  Staat het er al (een naam, bedrag, datum), dan is het geen gap; sla het over.
- Elke kandidaat-lacune verwijst concreet naar het onderwerp van DEZE
  inputtekst.
- Verzin geen feiten, namen of cijfers die niet in de tekst staan.
- Behoud vaktermen en eigennamen in hun oorspronkelijke vorm; vertaal ze niet
  als je niet zeker bent van een correcte Nederlandse term. Een onjuiste
  vertaling (bijv. een verzonnen woord) is erger dan de term onvertaald laten.
- Schrijf de kandidaat-lacune verder volledig in het Nederlands; echo geen hele
  Engelse zinsdelen uit de inputtekst.
- Geen citaten of fragmenten uit de inputtekst.
- Geen losse woorden, namen of acroniemen zonder relatie.
- Geen samengestelde analysekaders of lijsten binnen één kandidaat-lacune.
- Geen meta-categorieën zonder concrete relatie.

De volgende voorbeelden komen uit ANDERE teksten (geschiedenis, recht, zorg).
Ze tonen alleen de VORM. Kopieer hun inhoud niet; schrijf kandidaat-lacunes
over het onderwerp van de inputtekst hieronder.

Niet goed (vorm-voorbeelden, niet kopiëren):
{bad_examples}

Wel goed (vorm-voorbeelden uit andere domeinen, niet kopiëren):
{good_examples}

Inputtekst:
{text}

Geef nu maximaal {max_seeds} kandidaat-lacunes over het onderwerp van deze
inputtekst. Begin direct met "1.".

Output:
1.
""".strip()


class DetectorBackend(Protocol):
    name: str

    def detect_seeds(self, item: dict[str, Any], max_seeds: int = 5) -> list[str]:
        ...


_NUMBERED_LINE = re.compile(r"^\s*\d+[.)]\s*(.+?)\s*$")
# Catches both proper entities (&amp; &gt; &#36;) and the bare numeric remnant
# (#36;) that survives when the source already stripped the leading ampersand.
_HTML_ENTITY = re.compile(r"&(?:[a-zA-Z]+|#\d+);?|#\d+;")
_ACRONYM_ONLY = re.compile(r"^[A-Z][A-Z0-9.&;<>\-]{1,8}$")


def _normalize_for_match(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip(" .,:;-").lower()


def _token_set(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-zà-ÿ0-9]+", text.lower()) if len(t) > 2}


_FEWSHOT_NORMALIZED = frozenset(
    _normalize_for_match(example) for example in (_FEWSHOT_GOOD + _FEWSHOT_BAD)
)
_FEWSHOT_TOKEN_SETS = tuple(_token_set(example) for example in (_FEWSHOT_GOOD + _FEWSHOT_BAD))


def _looks_like_fewshot_leak(seed: str, threshold: float = 0.7) -> bool:
    """Drop output that copies a few-shot example verbatim or near-verbatim.

    A small model sometimes echoes the prompt's example seeds. Foreign-domain
    examples make that obvious and rare, but this is the safety net. Mutated
    leakage (same template, swapped entity) is intentionally NOT caught here:
    that needs content-grounding against the input text, which is future work.
    """
    normalized = _normalize_for_match(seed)
    if normalized in _FEWSHOT_NORMALIZED:
        return True
    seed_tokens = _token_set(seed)
    if not seed_tokens:
        return False
    for example_tokens in _FEWSHOT_TOKEN_SETS:
        if not example_tokens:
            continue
        overlap = len(seed_tokens & example_tokens) / len(seed_tokens | example_tokens)
        if overlap >= threshold:
            return True
    return False


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
        if _looks_like_fewshot_leak(seed):
            continue
        if seed in seen:
            continue
        seen.add(seed)
        seeds.append(seed)
        if len(seeds) >= max_seeds:
            break
    return seeds


def build_detection_prompt(text: str, max_seeds: int = 5) -> str:
    return OPEN_SET_DETECTION_PROMPT.format(
        text=text.strip(),
        max_seeds=max_seeds,
        bad_examples=_numbered(_FEWSHOT_BAD),
        good_examples=_numbered(_FEWSHOT_GOOD),
    )


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
        if torch.cuda.is_available():
            model_kwargs: dict[str, Any] = {"torch_dtype": torch.float16, "device_map": "auto"}
        else:
            # CPU: load the checkpoint's native (half) precision instead of
            # upcasting to float32. Halves memory — a 3.8B model loads in
            # ~8 GB instead of ~15 GB, which is what makes Phi-3.5-mini and
            # Qwen3-4B fit on the public-repo ubuntu-latest runner (16 GB).
            model_kwargs = {"torch_dtype": "auto"}
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


class OllamaDetectorBackend:
    """Detector backend backed by a local Ollama server over HTTP.

    Opt-in. Needs no Python model dependencies (stdlib only): install Ollama,
    run ``ollama pull <model_id>``, then point the run at it. Decoding is greedy
    (temperature 0, fixed seed) so the same input produces the same seeds.
    """

    def __init__(
        self,
        model_id: str,
        max_new_tokens: int = 400,
        host: str | None = None,
    ) -> None:
        from shadowseed.benchmark.ollama_client import OllamaClient

        self.name = f"ollama:{model_id}"
        self.model_id = model_id
        self.max_new_tokens = max_new_tokens
        self.client = OllamaClient(model=model_id, host=host)

    def detect_seeds(self, item: dict[str, Any], max_seeds: int = 5) -> list[str]:
        text = str(item.get("text") or item.get("input") or "").strip()
        if not text:
            return []
        prompt = build_detection_prompt(text, max_seeds=max_seeds)
        raw = self.client.generate(prompt, max_new_tokens=self.max_new_tokens)
        # the prompt ends with "1.\n" — re-prepend so the parser sees the first item
        return parse_numbered_seeds(
            "1. " + raw, max_seeds=max_seeds, source_text=text
        )


SUPPORTED_MODEL_BACKENDS: tuple[str, ...] = ("fixture", "hf-transformers", "ollama")


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
    if backend == "ollama":
        if not model_id:
            raise ValueError(
                "--model-id is required for --model-backend ollama"
            )
        return OllamaDetectorBackend(
            model_id=model_id, max_new_tokens=max_new_tokens
        )
    raise ValueError(
        f"Onbekende model-backend {backend!r}. "
        f"Toegestaan: {SUPPORTED_MODEL_BACKENDS}."
    )
