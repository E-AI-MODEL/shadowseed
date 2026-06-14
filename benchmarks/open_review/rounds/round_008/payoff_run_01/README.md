# Round 008 payoff run 01 — does acting on validated seeds improve answers?

> **Status: first end-to-end payoff signal — negative-leaning at n=3.** Real
> model (Actions run 27491407733, `hf-transformers:microsoft/Phi-3.5-mini-instruct`),
> blind reader judgment (`reviewer_ai_claude`, the κ-0.63-validated judge),
> scored with `scripts/answer_pair_winrate.py`. The model-benefit suite has only
> **3 scenarios**, so this is a signal, not a verdict.

## The number

| metric | value |
|---|---:|
| decided pairs | 3 |
| **SSL-guided wins** | **1** |
| baseline wins | 2 |
| **SSL win rate** | **0.333** |
| length-neutral win rate | 0.5 (1 of 2) |

Success criterion was win rate > 0.5. **Not met.** With n=3 nothing is
statistically significant, but the *direction is negative*: the SSL-guided
revision lost two of three blind comparisons.

## Independent corroboration (deterministic, not my judgment)

The suite's own token gap-coverage delta agrees exactly with the blind reader:

| scenario | baseline cov | ssl cov | reader winner |
|---|---:|---:|---|
| MODEL_A (industrial revolution) | 0.0 | 0.0 | baseline |
| MODEL_B (consumer law) | 0.0 | **0.5** | **ssl** |
| MODEL_C (HealthTrack app) | 0.0 | 0.0 | baseline |

Only MODEL_B improved on either metric. Two independent measures (reader + token
coverage) point to the same single success.

## Why SSL lost — the mechanism (this is the useful part)

It is **not** that the seeds were bad. It is the **revision step** derailing on
a small model:

- **MODEL_A**: asked to revise using the (correct) colonial-capital seeds, Phi
  hallucinated an analysis of a non-existent Seamus Heaney poem ("De lucht is
  een grote, onbekende zee") and welded the seeds onto it. Catastrophic derail.
- **MODEL_C**: the SSL revision bled in a different product entirely ("EcoSave
  energy-saving lamp") mid-evaluation of HealthTrack.
- **MODEL_B (the win)**: the revision cleanly injected the genuinely missing
  legal substance — *applicable law for a cross-border contract*, *enforceability
  of EU consumer law against a non-EU retailer* — which the baseline lacked.
  This is exactly the 4.6 promise working.

So the payoff mechanism **can** work (MODEL_B proves it), but on a 3.8B model the
SSL-revision prompt is fragile: it derails into hallucination/topic-bleed more
often than it helps. Trailing artifacts ("Gevalideerde SSL-seeds: …", leaked
"Vraag: …") show the small model also struggles to follow the revision
instruction cleanly.

## Honest verdict

The make-or-break question — *does using validated seeds make answers better?* —
comes back **"not demonstrated; leaning negative at this scale, with a clear and
fixable mechanism and one genuine success."**

- This does **not** sink SSL: detection works (rounds 004–007), and MODEL_B
  shows the use of seeds can add real substance.
- It **relocates the bottleneck** from detection (largely solved) to the
  **seed-injection / revision step** and **model capability**: the revision
  must add seeds without derailing the answer.

## Next steps (redirect)

1. **Harden the revision step**: the `build_ssl_revision_prompt` lets a small
   model rewrite freely. Try a constrained injection (append a focused
   "ontbrekende punten" paragraph rather than a full rewrite) to remove the
   derailment surface.
2. **Bigger n and a stronger model**: 3 scenarios is too few; a 7B+ or
   hosted-API model would separate "revision-step fragility" from "small-model
   incompetence."
3. **Human anchor** on the answer pairs (re-use the round-006 human tooling)
   once n is larger.

## Files

```text
model_benefit_judged.json   # verbatim run output + my blind better_answer verdicts
winrate.json                # scorer output (ssl_win_rate 0.333)
```
