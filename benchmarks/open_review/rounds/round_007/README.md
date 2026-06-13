# Open-set round 007 — out-of-sample replication under prompt v0.3g

> **Status: batch B complete; batch A prescreen-only (review pending its
> artifact).** Both ran `microsoft/Phi-3.5-mini-instruct` with the **v0.3g**
> prompt on fresh items. Headline so far: v0.3g fixes form everywhere
> (prescreen clean-rate 1.0 on news, 0.95 on science — `claim_vs_gap` 0,
> `truncated` 0), but the science replication **does not hold**: arXiv offset
> 20 scored AI-reviewed acceptance **0.268** vs round 006's 0.458, because the
> offset-20 items are results-dense physics abstracts that state their
> findings (28/56 candidates restate a stated result). The transfer is
> **density-dependent**: form transfers, but the supply of genuine gaps
> depends on how much the source leaves unsaid. See `batchB/README.md`
> (complete) and `batchA/README.md` (news offset 30, prescreen clean-rate 1.0,
> review pending the Actions artifact for run 27438917843).

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
