# Open-set round 007 — out-of-sample replication under prompt v0.3g

> **Status: dispatched.** Two batches, both `microsoft/Phi-3.5-mini-instruct`
> with the v0.3g prompt (gap-label noun phrase canonical), on **fresh items**
> never used in earlier rounds. Goal: test whether the round 006 signals
> (news 0.50, science 0.458, AI-reviewed) replicate out of sample.

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
