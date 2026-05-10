# Current Stack Status

Status: current as of 2026-05-10
Base commit: `087dc7f322a680d6e23b4e657ecc85966c98b3f4`
Related issue: #36

## Purpose

This document records the current technical baseline of `shadowseed` from repository state, not from memory or GitHub UI assumptions.

Use it as a short factual reference before changing tooling, artifact contracts, workflows or evidence layers.

## Project and packaging

- Project name: `shadowseed`
- Project version: `0.2.0`
- Python requirement: `>=3.10`
- Build backend: `setuptools.build_meta`
- Package layout: `src/`
- CLI entry point: `shadowseed = shadowseed.cli:main`

## Core dependency model

The fixed runtime dependency set is intentionally small:

- `numpy>=1.24`

Optional extras carry heavier dependencies:

- `test`: `pytest>=8.0`
- `models`: `sentence-transformers`, `transformers`, `torch`
- `paper`: `pymupdf`
- `vector-faiss`: `faiss-cpu`
- `vector-chroma`: `chromadb`
- `vector`: bundles FAISS and Chroma extras
- `dev`: bundles test, models, vector and paper extras

## Current quality tooling

Current state:

- pytest is configured and used in CI.
- No linter is configured yet.
- No formatter is configured yet.
- No type checker is configured yet.
- No coverage tooling is configured yet.
- No pre-commit config is present.

The next planned quality step is issue #38: add a minimal `ruff check` gate without formatting or typing changes.

## Standard CI baseline

The main CI workflow is `.github/workflows/tests.yml`.

It runs on:

- `push`
- `pull_request`

The pytest job runs on:

- Python 3.10
- Python 3.11

The current codecheck installs `.[test]` and runs:

```bash
python -m pytest -q
```

No lint command is currently part of this workflow.

## Standard benchmark and analysis routes

The standard CI workflow also runs these benchmark or reporting jobs after pytest:

- gap suite: `python -m shadowseed.cli run-gap-suite`
- false-positive suite: `python -m shadowseed.cli run-false-positive-suite`
- benefit suite: `python -m shadowseed.cli run-benefit-suite`
- model-benefit fixture smoke: `python -m shadowseed.cli run-model-benefit-suite --backend fixture`
- blind benchmark smoke: `python -m shadowseed.cli run-blind-benchmark ...`
- adversarial Gate benchmark: `python -m shadowseed.cli run-adversarial-gate-benchmark`
- probe utility benchmark: `python -m shadowseed.cli run-probe-utility-benchmark`
- analysis report: `python -m shadowseed.cli analyze-results`
- AbsenceBench smoke: `python -m shadowseed.cli run-absencebench-smoke --output absencebench_smoke.json`
- repeat-test matrix for different gap-suite turn counts

The analysis job rebuilds a provenance-safe `results/` tree from downloaded artifacts through `shadowseed.analysis.artifact_snapshot` before running `analyze-results`.

## Manual open-set workflow

The manual open-set workflow is `.github/workflows/open-set-hf-review.yml`.

It is triggered with `workflow_dispatch` and uses:

- `HUGGINGFACE_TOKEN`
- `contents: write`

It runs these core steps:

1. fetch an open-set HF batch
2. build open-set review packets
3. generate a pending open-set summary
4. write a short artifact README
5. commit selected open-set summary artifacts back to `main` only when `github.ref == 'refs/heads/main'`
6. upload all open-set review artifacts

The write-back guard is important: branch-based manual runs should not push results to `main`.

## Current open-set artifact contract

Current canonical open-set names and paths are:

- seed output: `results/open_review/open_set_seed_output.json`
- review packets: `results/open_review/open_set_review_packets.json`
- analyzer-facing CLI default summary: `results/open_set_seed_review_summary.json`
- workflow write-back summary: `results/open_review/open_set_seed_review_summary.json`
- disagreements: `results/open_review/open_set_disagreements.json`
- report: `results/open_review/open_set_review_report.md`

The standard analysis workflow includes a passthrough step: if `results/open_review/open_set_seed_review_summary.json` exists in checkout, it is copied into `downloaded-artifacts/open-set-passthrough/` before artifact snapshotting.

This means open-set metrics stay `n/a` until the manual HF workflow has produced and committed a summary.

## Current CLI defaults worth preserving

Important defaults after the recent alignment work:

- `summarize-open-set-seed-review --output`: `results/open_set_seed_review_summary.json`
- `summarize-open-set-seed-review --disagreements-output`: `results/open_review/open_set_disagreements.json`
- `summarize-open-set-seed-review --report-output`: `results/open_review/open_set_review_report.md`
- `run-open-set-seed-review --review-packets`: `results/open_review/open_set_review_packets.json`
- `run-absencebench-smoke --output`: `absencebench_smoke.json`

The AbsenceBench default is intentionally not `results/absencebench_smoke.json`, because the result writer places it under `benchmarks/results/`.

## Backlog status

The repository roadmap is now in:

- `docs/research/roadmap-shadowseed-stabilization.md`

Issue #34 is the parent backlog issue.

Issue #35 was closed after verifying that known acute open-set artifact drift from PR #31 and PR #32 was resolved.

Next planned steps:

1. issue #38: add a minimal `ruff check` quality gate
2. issue #39: make artifact contracts explicit
3. issue #40: create a workflow map

## Known limitations

This document is a snapshot, not a generated inventory.

Do not treat counts such as number of tests, workflow runs or wiki pages as stable unless they are regenerated and dated in a separate report.

## Interpretation

`shadowseed` is currently best understood as a Python research harness with a small runtime core, many benchmark and evidence routes, and a growing need for explicit artifact and workflow contracts.

The next engineering step should be small: add a minimal lint gate without changing benchmark behavior.
