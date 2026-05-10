# Open-set Review Round 001

Status: planned
Related issue: #41
Protocol: `docs/research/open-set-review-protocol.md`
Evidence layer: `open_set_seed_quality`

## Purpose

Run the first small human review round for open-set seed quality.

This round should turn generated review packets from `review_pending` into real two-reviewer evidence. It should not create a new fixed scenario suite and should not be used as broad proof of SSL effectiveness.

## Round size

Target:

- 12 to 20 source items;
- two reviewers;
- every selected seed reviewed by both reviewers where possible;
- no expansion until the first summary and disagreement file have been inspected.

## Reviewer IDs

Use stable IDs:

- `reviewer_a`
- `reviewer_b`

Do not replace these with names or email addresses in committed review packets.

## Input route

Generate a small open-set batch, for example:

```bash
shadowseed fetch-open-set-hf-batch \
  --source-id ag_news_test \
  --limit 20 \
  --output benchmarks/open_review/input/hf_ag_news_test_batch.json
```

Then generate seed output and review packets:

```bash
shadowseed run-open-set-seed-review \
  --input benchmarks/open_review/input/hf_ag_news_test_batch.json \
  --output results/open_review/open_set_seed_output.json \
  --review-packets results/open_review/open_set_review_packets.json
```

## Review packet handling

For each selected packet:

1. duplicate the packet once for `reviewer_a` and once for `reviewer_b` if needed;
2. fill all five booleans;
3. set `review_status` to `accepted` or `rejected`;
4. set `reject_reason` to one fixed code when rejected;
5. keep `reject_reason` as `null` when accepted;
6. add short `reviewer_notes`.

Do not edit another reviewer’s packet to remove disagreement.

## Reject codes

Allowed codes:

- `too_broad`
- `too_vague`
- `trivial`
- `not_relevant`
- `not_testable`
- `duplicate`
- `style_not_gap`

## Summary route

After the round is filled:

```bash
shadowseed summarize-open-set-seed-review \
  --input results/open_review/open_set_review_packets.json \
  --output results/open_set_seed_review_summary.json \
  --disagreements-output results/open_review/open_set_disagreements.json \
  --report-output results/open_review/open_set_review_report.md
```

## Files expected after actual review

These are generated after the human review is complete. They are not included in this planning PR.

- `results/open_review/open_set_review_packets.json`
- `results/open_set_seed_review_summary.json`
- `results/open_review/open_set_disagreements.json`
- `results/open_review/open_set_review_report.md`

## Completion checklist

Round 001 is complete when:

- selected packets have non-empty `reviewer_id`;
- no completed packet has `review_status: pending`;
- every completed packet has all five review booleans filled;
- every rejected packet has one fixed `reject_reason`;
- every accepted packet has `reject_reason: null`;
- summary, disagreements and report artifacts are generated;
- disagreements are preserved;
- the analyzer can read `results/open_set_seed_review_summary.json` when present.

## Claim boundary

Allowed after a valid round:

```text
A first human-reviewed open-set seed-quality sample exists.
```

Not allowed:

```text
SSL is proven to improve all answers on open data.
```
