# Round 007 batch A — ag_news offset 30 (Phi v0.3g)

> **Status: AI review complete.** Detector run is real (Actions run
> [27438917843](https://github.com/E-AI-MODEL/shadowseed/actions/runs/27438917843)),
> artifacts committed **verbatim** (maintainer-uploaded). Review is **delegated
> AI** (`reviewer_ai_claude`, single reviewer) — labeled AI, not human.

## Run provenance

- **Model:** `hf-transformers:microsoft/Phi-3.5-mini-instruct`, **prompt v0.3g**,
  `max_new_tokens=512`.
- **Input:** `ag_news_test` offset **30**, 12 items — fresh, no overlap with the
  offset 0–25 of rounds 004–006. Domain spread: World 8, Sports 3, Business 1
  (the earlier news rounds were all Sci/Tech).

## v0.3g form result (news)

- 60 raw candidates, manager gate rejected 6; **prescreen clean-rate 0.90**,
  `claim_vs_gap` 0, `truncated` 0 (only `not_atomic` 6, matching the gate).
  Form holds on news exactly as on science.

## AI review result

- unique seeds **54** · accepted **18** · acceptance **0.333**
- criterion pass rates: atomicity 1.00, relevance 0.74, testability 0.59,
  non_triviality 0.33, follow_up_utility 0.33
- reject codes: `too_vague` 19, `not_relevant` 11, `trivial` 3,
  `style_not_gap` 3

## The replication result (vs round 006 batch 1, news offset 0)

| news batch | offset | acceptance |
|---|---|---|
| round 006 batch 1 | 0 | 0.50 |
| round 007 batch A | 30 | **0.333** |

News acceptance drops out of sample too — and the cause is the same one batch B
showed for science: **fact-complete short wire items have almost no gaps.**
Item 31 (Indians beat Twins) and item 40 (D-Backs end slide) are 3-line
box-score recaps that state opponent, score, scorers, standing and day — 0/5
and 1/5 accepted, every rejected candidate a stated fact. The gap-rich items
are the narrative World stories (item 37 USERRA provisions-stub 3/5, Najaf 2/5,
Afghan army 2/5).

So the news/science distinction is **not** the driver; text density is. See the
round-level synthesis in `../README.md`.
