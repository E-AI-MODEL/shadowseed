# Round 016 — generative payoff (W5): the decisive test of the vision claim

> **Status: convergent NEGATIVE with W1 — with one confound to clear before any
> verdict.** Even SSL's *generative* "wat had hier KUNNEN staan" frames are
> ~88% raised by gpt-4.1 itself. Provenance: run 27896816817, job 82549816835.
> Frames detector-produced (v0.4-gen, openai), topics author-chosen.

## The number

8 reframe-friendly topics, 24 detector-generated frames. Baseline = gpt-4.1
answering the question unaided; we measure how many of the detected frames the
baseline already raised (semantic, real embeddings).

| metric | value |
|---|---:|
| mean baseline **frame** coverage | **0.88** |
| frames the baseline MISSED ("novel") | **3 / 24 (12.5%)** |

The detector's frames are exactly the "obvious non-obvious" lenses a frontier
model produces when asked to answer thoroughly: *macht en zeggenschap*, *sociale/
vermogensongelijkheid*, *speculatie als prijsdrijver*, *vertrouwen in instituties*,
*systeemverandering naast individueel gedrag*. gpt-4.1 raises ~7 of 8 of these
itself. The 3 genuinely novel frames (ecologische gevolgen van vroege
industrialisatie; ruimtelijke ordening/grondbeleid; systeemverandering als kader)
are modestly useful, not transformative.

## Convergence with W1 — the honest synthesis

| test | mode | baseline self-coverage |
|---|---|---:|
| W1 (round 015) | omission ("wat ONTBREEKT") | 0.82 |
| W5 (round 016) | generative ("wat had KUNNEN staan") | 0.88 |

Both interpretations of SSL — omission and generative — converge on the same
finding: **on a frontier model, the detected seeds/frames are largely things the
model produces itself.** Since the detector and the answerer are the same gpt-4.1,
this is almost structural: the model is its own gap/frame generator. SSL's
*external Niveau-1 added value over a frontier model* looks small (~12–18%, partly
metric noise).

## The confound I must flag (before any verdict)

The baseline prompt here explicitly asks for *"de belangrijkste verklarende
invalshoeken"* — it **primes** the model to produce frames. So W5 compares the
detector's specific frames against *the model's own frames when asked for frames*.
That inflates baseline coverage. A fair decider is a **naive baseline** ("just
answer the question", no framing instruction): if even then the frames are already
covered, the negative is unimpeachable; if a naive baseline covers far fewer, SSL
*does* add value over an unprimed model and W5's number is a priming artdefact.

→ **Decider task W7**: re-run W5 with a naive baseline.

## What is and isn't shown

- **Shown (subject to W7):** SSL as an *external detector for a frontier model* on
  single-shot tasks adds little over the model's own thorough answering.
- **NOT shown / still live:**
  1. weaker models (where the model is *not* its own good frame-generator) —
     SSL could lift them;
  2. cross-turn accumulation (gap 5) — value that compounds over a conversation,
     invisible to single-shot tests;
  3. Niveau 2 / model-internal (H-neurons) — a different mechanism entirely;
  4. the payoff-given-a-valid-seed result (rounds 011–013) still stands — acting
     on a good seed helps and does no harm; the issue is that few such seeds exist
     that a frontier model wouldn't raise itself.

## Honest read

This is the result the maintainer anticipated. SSL-as-external-frontier-detector
is in serious doubt (convergent W1+W5). It is **not** a refutation of SSL on weak
models, cross-turn, or Niveau 2 — those are genuinely different claims. The next
move is W7 (clear the confound), then a decision: pursue one of the live claims,
or write the honest "stand van SSL" synthesis.
