# Open-set round 005 — first v0.3e Layer-C round, with blind model-vs-baseline control

> **Status: scaffolding, awaiting run.** This round protocol is ready; it
> fills in once the v0.3e detector run on a capable model lands. It is Layer C
> (open-set seed quality), evidence pending on human review.

## Why this round

Round 005 is the first round that pairs the v0.3e detector prompt (merge #109,
candidate-gap terminology) on a *capable* model with a **blind control** against
the `adapter_v1` template baseline on the same items.

This serves SSL 4.5's Fase 0 question — *"kan het model kleine atomische gaps
vinden, boven baseline?"* (§20, H1, H8) — executed under SSL 4.6's evidence
discipline: open text, no ground-truth seed list, blind human review, no total
score. The baseline arm restores 4.5's explicit "boven baseline" requirement
that the open-set reframing had softened.

## Go / no-go gate (before any human review)

Run the mechanical prescreen on the model run first:

```bash
python scripts/prescreen_open_set_output.py results/open_review/open_set_seed_output.json \
  --input benchmarks/open_review/rounds/round_005/input/hf_batch.json \
  --round round_005 \
  --output benchmarks/open_review/rounds/round_005/mechanical_prescreen.json
```

- **Reference baselines:** round 004 (Qwen-3B, v0.3d) scored clean-rate **0.45**
  with `claim_vs_gap` dominant; SmolLM2-1.7B was a capability floor (yield
  0.17/item).
- **Proceed to human review only if** the model run clearly beats those:
  yield ≥ ~3 candidates/item and clean-rate well above 0.45. If it is still
  `claim_vs_gap`-dominant, fix the prompt before spending reviewer time.

The prescreen is a deterministic triage aid — **not** human review and **not**
Layer C evidence.

## Blind control design

To keep the seed-quality claim from being a forking-paths artefact (Gelman &
Loken 2013; cf. Tang et al. 2024 on band-exemplar vs distributional prompts),
reviewers judge model and baseline candidates **blind and interleaved**:

```bash
# 1. produce both arms on the SAME input batch
shadowseed run-open-set-seed-review --input <batch> --detector model \
  --model-backend <hf-transformers|ollama> --model-id <id> \
  --output results/open_review/model_seed_output.json
shadowseed run-open-set-seed-review --input <batch> --detector adapter_v1 \
  --output results/open_review/baseline_seed_output.json

# 2. build a single blind packet (arm hidden, order shuffled per item)
python scripts/build_blind_control_packets.py build \
  --model results/open_review/model_seed_output.json \
  --baseline results/open_review/baseline_seed_output.json \
  --input <batch> \
  --packets benchmarks/open_review/rounds/round_005/blind_review_packets.json \
  --key benchmarks/open_review/rounds/round_005/blind_key.json

# 3. reviewers fill `judgment` on the packets (they never see blind_key.json)

# 4. un-blind and read per-arm accept / atomic rates and the model-vs-baseline delta
python scripts/build_blind_control_packets.py unblind \
  --packets <filled blind_review_packets.json> \
  --key benchmarks/open_review/rounds/round_005/blind_key.json \
  --output benchmarks/open_review/rounds/round_005/blind_control_summary.json
```

## Review unit and fields (per candidate gap)

| Field | Question |
|---|---|
| `atomic` | Bevat de kandidaat precies één gap? |
| `relevant` | Gaat het echt over een betekenisvol gemis in deze tekst? |
| `testable` | Is de gap in principe verifieerbaar of falsifieerbaar? |
| `non_trivial` | Is het meer dan een vage of banale uitbreiding? |
| `useful_for_followup` | Helpt het een goede vervolgstap maken? |
| `accept` | `true`/`false` — eindoordeel van deze reviewer |
| `reject_reason` | code (zie hieronder) als `accept=false` |

Reject codes: `too_broad`, `too_vague`, `trivial`, `not_relevant`,
`not_testable`, `duplicate`, `style_not_gap`.

## Round size and reviewers

- 12–20 source items, two reviewers (`reviewer_a`, `reviewer_b`);
- both reviewers judge every blinded candidate where possible;
- a small complete round beats a large partial one.

## Success criteria (Layer C, first usable evidence)

- ≥ 60% of model candidates not directly rejected;
- ≥ 70% of accepted candidates judged atomic;
- reviewer disagreement stays explainable;
- reject reasons return real learning signal;
- **model arm beats the `adapter_v1` baseline arm** on accept and atomic rate.

These are acceptance criteria for a first usable open-set evaluation layer, not
paper-level claims.

## Artifact contract

```text
input/hf_batch.json                 # the open-set source items (from the run)
model_seed_output.json              # detector=model (v0.3e) raw + normalized
baseline_seed_output.json           # detector=adapter_v1 raw + normalized
mechanical_prescreen.json / .md     # deterministic gate (triage, not evidence)
blind_review_packets.json           # blinded interleaved packets for review
blind_key.json                      # hidden arm mapping (reviewers must not see)
blind_control_summary.json          # per-arm accept/atomic rates + delta (after un-blinding)
```
