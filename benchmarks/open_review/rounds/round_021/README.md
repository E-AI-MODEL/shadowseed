# Round 021 — W9f: cluster recurrence promotes a representative, not the whole cluster

> **Status: engineering refinement landed (deterministic test); live re-run +
> fresh human review on safe thresholds is the pending follow-up.** Round 020
> made the cross-turn payoff fire at the SAFE doctrine thresholds via
> cluster-based recurrence, but its v1 credited the cluster size to *every*
> member, so one recurring (paraphrastic) gap promoted the whole cluster (49
> promotions). W9f credits recurrence to a single cluster **representative** (the
> earliest-born member), cutting promotion volume to ~one per qualifying cluster
> without touching identity/storage (strict 0.85 dedup) or the Gate bar (3).

## What changed

`ssl_session_suite` cluster mode previously did:

```text
for every seed in a cluster:
    seed.occurrence_count = max(own, cluster_size)   # all members clear the bar
```

It now does:

```text
representative = earliest-born member of the cluster
representative.occurrence_count = max(own, cluster_size)   # only the rep clears the bar
other members keep their own (low) occurrence_count        # they stay below the bar
```

The cluster *size* is still the recurrence signal; only its **assignment**
changed. Crucially:

- **Identity/storage unchanged** — the strict 0.85 dedup still keeps paraphrases
  as distinct seeds; the cluster only counts recurrence semantically.
- **Gate bar unchanged** — still the SAFE default (`min_occurrences_for_gate = 3`).
- **Cross-turn surfacing unchanged** — surfacing is relevance-gated
  (`surface_threshold`), not volume-gated, so cutting promotion volume does not
  remove cross-turn events. The representative is the earliest-born member, which
  is exactly the seed eligible to surface in a later turn, so the two notions stay
  aligned.

## Why the representative is the earliest-born member

A cross-turn payoff requires a seed *born in an earlier turn* to resurface later.
Anchoring the cluster on its earliest member means the promoted seed is the one
that has the most turns left to resurface — and keeps "the seed that promotes" and
"the seed that can surface" the same object instead of an arbitrary cluster member.

## Evidence in this PR (deterministic, no model)

`tests/test_recurrence_clustering.py::test_cluster_mode_promotes_one_representative_not_all_members`
drives the real `SSLManager` with six paraphrases whose embeddings cluster
together (pairwise cosine ~0.7 ≥ cluster bar 0.6) yet stay distinct under the
strict 0.85 dedup. It asserts:

- the six paraphrases stayed **distinct** in storage (`distinct_seeds_created ≥ 5`);
- the cluster still **accumulated recurrence** past the SAFE bar
  (`max_occurrence_count ≥ 3`);
- but **exactly one** seed promoted (`len(promoted_ever) == 1`), not the whole
  cluster.

This is the engineering claim of W9f, verified without a model. Full suite green
(283 passed, 4 skipped).

## Honest qualifiers

1. **This is the mechanism fix, not a fresh quality measurement.** The "richer"
   quality claim still rests on the round-019 human review (2 independent
   reviewers, 92%/98% agreement) on equivalent content. The next step re-runs the
   real model and human-reviews a fresh batch at safe thresholds.
2. **The 49→cluster-count reduction is shown deterministically here**; the exact
   number on the round-020 conversations will be confirmed by the live re-run.
3. Cross-turn events are expected to be unchanged by construction (relevance-gated
   surfacing), but that too is confirmed by the live re-run, not asserted here.

## Next (pending manual / secrets-gated run)

1. **Re-run** the round-020 conversations on `openai:gpt-4.1` with
   `--recurrence-mode cluster` at the safe defaults (workflow
   `Research · SSL Benefit (OpenAI)`), and record the new promoted count
   (expected ~cluster count, not 49) and the cross-turn event count (expected
   unchanged at 10).
2. **Fresh blind human review** of the re-run's cross-turn pairs to confirm
   quality holds at safe thresholds (round-013/019 tooling).
3. If both hold, carry this configuration forward: strict safety + semantic
   recurrence + representative promotion + per-topic tuning.
