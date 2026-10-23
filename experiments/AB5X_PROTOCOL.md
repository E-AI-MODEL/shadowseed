# Pre-registration: Shadowseed isolated 5x A/B (GPT-5 and GPT-6 Astra)

**Immutable starting context:** Previous real, 3-turn GPT-5/GPT-6 Astra pilot
GitHub Actions run \`39876227564\`, 12 successful real requests and six
weightless seeds. Canonical Shadowseed Pro core from commit
\`13fda4189b3cff306642c41c47524dc3648bf1f4\` (merged PR #205).
Model IDs \`gpt-5\` and \`gpt-6-astra\`; no fallback.

## Exact size and arms

A new 3-case × 5-turn casebook = **15 turns per model per arm**, five
times the earlier **3 turns per model**. Across two models and two arms
this produces **60 answer calls**, plus **30 B-only candidate detector
calls**, a maximum of **90 billable calls**.

Independent four-cell comparison:

- GPT-5 / A: same GPT-5 without Shadowseed or detector.
- GPT-5 / B: GPT-5 with its OWN TTL/TrTL/Gate and candidate memory.
- GPT-6 Astra / A: same GPT-6 without Shadowseed or detector.
- GPT-6 Astra / B: GPT-6 Astra with its OWN TTL/TrTL/Gate and memory.

The fixed facts and question sequence for each case are identical in A
and B, while prior assistant answers belong ONLY to their respective
arm. Each new case starts completely clean, with no A/B or cross-model
history, key, model output, seed or memory imported from any other arm.
No provider \`previous_response_id\`; no server-side response storage.

## Treatment and counterfactual

Only the B arm instantiates a real SSLManager. Each B turn first performs
TTL decay, TrTL reactivation and the canonical use-time eligibility check
\`collect_eligible_promoted_seeds\` with \`enforce_current_gate=True\`.
Only *previous-turn* promoted, relevant seeds may be placed in the
canonical untrusted \`build_candidate_context\` block before generation.

The model is free to ignore that data. After B answers, a separate
same-model detector records up to two genuinely open questions or NONE;
no birth/admission is an epistemic quality or usefulness verdict. To
avoid a positive-feedback loop, candidates detected after B has received
surfaced seed text are **quarantined**, never reinforced or offered to
the Gate. A's turns never instantiate a manager and never receive
detector calls.

**Experimental authority profile:** the existing canonical
\`exploratory\` Gate, *not* the production evidence-backed Gate. This
profile may promote through repeated recognition under recorded
recurrence signals and the existing 0.5 promotion threshold; it must
NEVER report recurrence as verified independent external evidence.
For this limited synthetic test the documented lexical embedder and
dedup threshold 0.65 are explicit research settings (not a semantic
model-quality measure). The point-of-use surface similarity threshold
is 0.20, maximum one seed, with existing resurface costs. Nothing in
the core or production policy is changed.

If B never actually surfaces a seed, the test records \`exposure=0\`.
Model sampling differences between A and B then are **not** SSL benefits.
If B surfaces seeds, compare all 15 paired turns and transparently report
the treated-turn subset. Separately report candidate acceptance,
dedup/repetition, promotions, TTL and TrTL events, post-exposure
quarantine and any blocked influence attempts.

## Independent blinded review, not model grading

30 paired comparison items (15 per model), shuffle item order and A/B
sides using a frozen deterministic randomization. The reviewer pack
contains fictional case facts, the current prompt and response X/Y;
it contains no model names, seed IDs or A/B labels. The separate key
contains model and A/B allocation. Reviewers should rate factual
restraint, task coverage, relevance, unsolicited speculation,
usefulness and unintended overclaiming; include ties and dissent.
Neither GPT-5 nor GPT-6 is the blinded quality judge.

**Primary outcome pending review:** paired human preference and
harm/overclaim rate on **treated B turns**. If none were treated, mark
causal result *not estimable*, rather than \`0\` efficacy. All-arm
intent-to-treat differences are descriptive and include model
stochasticity and divergent arm-specific conversation histories.
No knowledge state, education benefit or H-neuron inference follows.

## Pre-fixed call/cost/operational boundaries

- 90 requests maximum (2 models × 3 cases × 5 turns ×
  [A answer + B answer + B detector]).
- Baseline and treated answers <= 1050 output tokens, detector <= 650;
  \`reasoning.effort=low\`, \`store=false\`, no automatic retries and
  150s HTTP request timeout.
- Hard stop on **estimated accumulated API spending $6.00**;
  conservative pre-request reserve per model. It is an *internal*
  estimate from reported tokens and listed standard prices and cannot
  guarantee billing charges (e.g. failed requests). No paid fallback.
- Uses the EXISTING \`OPENAI_API_KEY\` GitHub Actions Secret in
  \`E-AI-MODEL/shadowseed\` only. Never read a committed .env or print a key.
- Run staged on branch. An additional, explicit marker-file push
  triggers **only one scheduled paid run**. Changes to code or workflow
  do not trigger repeated API runs. Offline preflight job must pass
  first. No human-interactive form required.
- Save each completed response with model ID/snapshot,
  response ID, actual input/output/reasoning token usage and cost
  estimate, plus per-turn seed states, provenance, selected Gate policy,
  decisions and observed exposure. Preserve partial output if an
  exception occurs. Full raw response and blinded packs are artifacts,
  not commits; casebook and code are commits.
- Sources: https://developers.openai.com/api/docs/models/gpt-5 ,
  https://developers.openai.com/api/docs/models/gpt-6-astra .
- Any quota, model access, API, or test failure is an explicit failed
  or partial result; no undocumented model substitution.

**Decision criterion:** the study counts as executed only with actual
response IDs and token usage for both models and both arms. A green
workflow alone cannot establish causality or outcome superiority.
