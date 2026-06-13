# Round 007 batch A — ag_news offset 30 (Phi v0.3g)

> **Status: prescreen only; AI review pending the artifact.** The detector run
> is real and succeeded (Actions run
> [27438917843](https://github.com/E-AI-MODEL/shadowseed/actions/runs/27438917843)),
> and committed its summary to `main`. But the committed summary carries no
> source article texts, and judging relevance / false-gaps needs them. The
> review therefore waits on the run's Actions artifact (input batch + raw
> seed output), like batch B did before its upload.

## What is here

- `open_set_seed_output.json` — the 54 candidate texts, reconstructed verbatim
  from the workflow-committed summary (commit cd7fc24). Titles/domains only;
  no article text.
- `mechanical_prescreen.json/.md` — deterministic triage on those 54.

## Prescreen (the v0.3g form result holds on news too)

- yield 4.5, **clean-rate 1.0** — zero mechanical flags: `claim_vs_gap` 0,
  `truncated` 0, `not_atomic` 0, `near_duplicate` 0. v0.3g produces clean
  noun-phrase gap labels on news exactly as on science.
- Domain spread (not Sci/Tech): World 8, Sports 3, Business 1 — a first look
  at open-set detection outside the Sci/Tech slice all earlier news rounds used.

## To finish this batch

Upload the Actions artifact for run 27438917843
(`open-set-hf-review-batch-model-hf-transformers-microsoft-Phi-3.5-mini-instruct`).
Then: replace this reconstruction with the verbatim input + seed output, run
the delegated AI review against the article texts, and report the news-side
replication number next to round 006 batch 1 (0.50).
