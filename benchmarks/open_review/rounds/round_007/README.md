# Open-set round 007 — out-of-sample replication under prompt v0.3g

> **Status: complete — both batches run, verbatim artifacts, AI-reviewed.**
> Both ran `microsoft/Phi-3.5-mini-instruct` with the **v0.3g** prompt on fresh
> out-of-sample items. Three findings, in order of confidence:
>
> 1. **v0.3g fixes form everywhere** — prescreen clean-rate 0.90 (news) / 0.95
>    (science), `claim_vs_gap` 0, `truncated` 0 on both. Solid.
> 2. **The model lever holds out of sample** — news 0.333, science 0.268, both
>    well above round 005's Qwen baseline (0.185). Phi >> Qwen replicates.
> 3. **Round 006's absolute levels (0.50 / 0.458) were optimistic, and the
>    news/science framing was wrong.** Out of sample both drop to ~0.30, and
>    the driver is not domain but **text density**: news offset 30 (0.333) ≈
>    science offset 20 (0.268), both below the gap-rich offset-0 batches.

## The five-point picture (delegated AI review, one reviewer, one rubric)

| round | detector | source | offset | acceptance |
|---|---|---|---|---:|
| 005 (AI arm) | Qwen2.5-3B | ag_news | 0 | 0.185 |
| 006 batch 1 | Phi-3.5-mini | ag_news | 0 | 0.50 |
| 006 batch 2 | Phi-3.5-mini | arXiv | 0 | 0.458 |
| **007 batch A** | Phi-3.5-mini | ag_news | 30 | **0.333** |
| **007 batch B** | Phi-3.5-mini | arXiv | 20 | **0.268** |

**The unifying variable is how much the source text leaves unsaid.**
Fact-complete short wire items (Indians-beat-Twins box scores) and
results-dense physics abstracts (stated Hopf bifurcations, stated kondo peaks)
both yield few genuine gaps; narrative World stories and discursive abstracts
yield more. A stated finding is not a gap, and the detector is correctly
rejected on it. This is a property of the corpus, not a detector regression —
and it means a fair Layer-C/F number needs a **density-controlled** item
sample, not just more items. (Candidate for round 008: stratify intake by
text density, or measure gap-yield against a density proxy.)

Round 006 was right to flag *single-batch noise*; out-of-sample replication
shows the caveat mattered.

## Why this round

Round 006 established two signals with one batch each: the model lever works
(Layer C) and quality transfers across domains (first Layer-F point). Both
carry the explicit caveat *single-batch noise*. Round 007 attacks exactly that
caveat: same model, same (now self-consistent) prompt, fresh inputs.

Secondary: this is the first live run of prompt v0.3g, which aligned the rule
with the few-shot examples after the scaffold contradiction (see ADR 0001,
round 006 row). Expected effect on Phi is small (it already followed the
examples); the prescreen claim/truncation profile is the check.

## Design

| | Batch A (news) | Batch B (science) |
|---|---|---|
| source | `ag_news_test` | `arxiv_abstracts` |
| offset | **30** (rounds 004–006 used 0–25) | **20** (round 006 used 0–14) |
| limit | 12 | 12 |
| model | Phi-3.5-mini-instruct | Phi-3.5-mini-instruct |
| max_new_tokens | 512 | 512 |

One lever versus round 006: fresh items (plus the v0.3g form fix). No model
change, no domain change, no rubric change.

## Success criteria (replication, no total score)

- Batch A acceptance in the neighborhood of 0.50; batch B in the neighborhood
  of 0.46–0.51 — same reviewer (`reviewer_ai_claude`), same documented rubric
  including the genre reading for abstracts.
- Prescreen: `claim_vs_gap` 0 under the assertion-based check; truncation and
  "of"-stacking profiles reported per domain.
- A material drop on fresh items would mean the round 006 numbers leaned on
  item luck — that is a reportable, course-changing outcome, not a failure of
  the round.

## Review

Delegated AI review (`reviewer_ai_claude`), explicitly labeled, single
reviewer; the runs' own two-reviewer packets are preserved untouched per batch
so a human pass stays possible. AI review is a signal, not Layer-C/F evidence.

## Artifact contract

Per batch under `batchA/` / `batchB/`: same round-local contract as round 006
(`input/hf_batch.json`, `open_set_seed_output.json`,
`run_review_packets_pending.json`, `mechanical_prescreen.json/.md`,
`ai_review/*`).
