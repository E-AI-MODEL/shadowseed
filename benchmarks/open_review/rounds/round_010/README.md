# Round 010 — real-model payoff (capable model) + gap-3 head-to-head

> **Status: the round-008 bottleneck is resolved on a capable model; first
> gap-3 signal.** Real hosted model (`openai:gpt-4o-mini`), greedy decoding.
> Two experiments, both at tiny n, both reader-judged by an AI judge
> (`reviewer_ai_claude`, the κ-0.63-validated judge) — **signal, not proof.**
> This is the "bigger model" next step that round 008 payoff_run_01 explicitly
> asked for.

## Provenance

| experiment | Actions run | job | artifact |
|---|---|---|---|
| model-benefit (payoff) | 27788963640 | 82232846606 | `ssl-openai-model-benefit-gpt-4o-mini` (id 7735634956) |
| ssl-vs-rag (gap 3) | 27788968553 | 82232863294 | `ssl-openai-ssl-vs-rag-gpt-4o-mini` (id 7735631165) |

Backend wired in this session (`openai_client.py` + factory wiring, PR #141);
run via the `Research · SSL Benefit (OpenAI)` workflow with the `OPENAI_API_KEY`
repo secret. Decoding `temperature=0, seed=0`. The full result JSON is printed
verbatim into each job log (egress to the artifact blob store is not always
reachable from the analysis environment).

---

## Experiment A — does acting on validated seeds improve answers?

Same harness as round 008 (`run-model-benefit-suite`, 3 scenarios, free-rewrite
revision via `build_ssl_revision_prompt`), but `--backend openai --model-id
gpt-4o-mini` instead of CPU Phi-3.5-mini.

### The headline: the derailment is gone

Round 008 on Phi-3.5 lost 2 of 3 because the **revision step derailed**
(hallucinated a Seamus-Heaney poem; bled in a wrong product). On gpt-4o-mini,
under the *same free-rewrite prompt*:

- `unsupported_ssl_addition_rate = 0.0` on **all three** scenarios;
- the baseline answer is preserved and only the validated seeds are folded in;
- where no relevant seed is promoted, the answer is left essentially unchanged
  (no harm).

So the "do no harm" property we previously had to *enforce* with the append-only
strategy (round 008 run 02) emerges naturally from a capable model even under a
free rewrite. The make-or-break risk of round 008 — *acting on seeds corrupts a
good answer* — does not reproduce here.

### Per-scenario (deterministic coverage + my blind reader verdict)

| scenario | baseline cov | ssl cov | promoted seeds (relevant) | blind verdict |
|---|---:|---:|---|---|
| MODEL_A (industrial revolution) | 0.0 | 0.0 | none relevant promoted | **tie** (answer unchanged, no harm) |
| MODEL_B (consumer law) | 0.0 | 0.0\* | 1 (afdwingbaarheid EU-recht, score 2) | **ssl** (correct point cleanly added) |
| MODEL_C (HealthTrack app) | 0.0 | **1.0** | 4 (AVG, auth, encryptie, rate-limit) | **ssl** (security layer added, 0 unsupported) |

Blind AI reader win rate: **2 ssl wins, 1 tie, 0 losses of 3** (vs Phi-3.5's
1 win / 2 losses). AI judgment, not human; n=3 → signal, not a verdict.

\* **Metric caveat (MODEL_B):** the promoted seed scored a structural match
(score 2) **and** is visibly integrated into the SSL answer ("3. Afdwingbaarheid
van EU-consumentenrecht …"), yet the lexical `coverage()` metric credited it 0.0
— a jaccard-threshold/phrasing artifact. The automatic coverage metric
*understates* the real benefit here; the blind answer-pair review is the better
judge. Worth fixing or at least flagging in the suite.

### MODEL_C, the clean win (illustrative)

Baseline was a generic UX review of a health app. The SSL revision kept it
verbatim and appended exactly the validated, domain-correct gaps for an app
handling medical heart-rate data:

> - Zorg voor AVG-compliance bij de verwerking van medische hartslagdata.
> - Implementeer een sterke authenticatiestrategie voor toegang tot gezondheidsdata.
> - Zorg voor encryptie van medische data, zowel in rust als tijdens transport.
> - Pas rate-limiting toe op API's die gezondheidsdata verwerken.

`coverage 0.0 → 1.0`, `unsupported 0`. This is the 4.6 promise working cleanly.

---

## Experiment B — gap 3: retrieve toward the *gap* vs the *question*

`run-ssl-vs-rag`, 2 items, `top_k=3`, equal context budget (Codex #139 fix).
RAG arm queries the **question**; SSL-probe arm queries the **seed/gap**. Same
model answers both; only the retrieved context differs.

> **Hard caveat:** retrieval here uses the toy deterministic 128-d
> `lexical_embedding` (a hash, not a real embedder). Both arms are brittle under
> it. So this shows the *mechanism*, not a production RAG comparison. Real
> embeddings are the obvious next step (`openai_client.embed` now exists).

### SSLRAG_LAW — the demonstration

| arm | retrieved chunks | answer |
|---|---|---|
| RAG (query=question) | 2× industrial-revolution chunks + 1 law chunk | **non-answer**: "De SSOT-context biedt geen specifieke informatie …" |
| SSL-probe (query=gap) | the 3 correct law chunks (enforcement, jurisdiction, eu_rights) | **correct, substantive**: afdwingbaarheid, internationaal privaatrecht, forumkeuze, EU-garantie, niet-EU-caveat |

Retrieving toward the question pulled the *wrong* documents and the model
honestly refused; retrieving toward the gap pulled the right ones and produced a
correct answer. `seed_only_chunk_ids` confirms the probe reached
`law::enforcement` and `law::eu_rights` that the question retrieval missed. This
is "a shadow seed finds a better answer than ordinary RAG would" — visible, with
the toy-retriever caveat.

### SSLRAG_IR — the honest counter-case

The question retrieval was already complete (it got the innovation chunk), so
RAG covered technology **and** colonial factors. The gap-probe narrowed to the
colonial angle and **dropped the technology factor** — less complete for "why
could the Industrial Revolution arise". → **RAG better** here.

Blind AI reader: **1 ssl win (LAW), 1 RAG win (IR) of 2.** The win is dramatic
(non-answer vs correct); the loss is "narrower", not "wrong". The lesson matches
the philosophy: the gap-probe helps most exactly when ordinary retrieval *misses*
the gap, and can over-narrow when the question already covers the ground.

---

## Honest verdict

- **Payoff (A):** the round-008 negative was a *small-model revision-step
  artifact*, not an SSL flaw. On a capable model the revision adds validated
  substance without derailing (2 wins / 1 harmless tie / 0 losses, 0 unsupported
  additions). Still n=3, AI-judged → **strong signal, not Layer-C validation.**
- **Gap 3 (B):** first end-to-end evidence that querying the gap can beat
  querying the question (LAW: non-answer → correct answer), with an honest
  counter-case (IR) and a **toy-retriever caveat** that bounds the claim.

## Next steps

1. **Real embeddings for gap 3** (`openai_client.embed`) to remove the
   toy-retriever confound, then re-run B.
2. **Bigger n** for both — the 3-scenario / 2-item fixtures are too small for a
   win-rate verdict; expand the fixtures.
3. **Human anchor** on the blind answer pairs (reuse round-006 human tooling).
4. **Fix the MODEL_B coverage-metric blind spot** (integrated seed scored 0).
