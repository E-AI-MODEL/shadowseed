# Round 033 — verdict: NIET gerepliceerd; Laag G spoor 2 sluit voor deze schaal

> **Status: VERDICT (instrument-niveau, gepreregistreerd).** De replicatie
> van het round-032-signaalkandidaat is uitgevoerd (2026-07-18/19) op een
> níeuwe brontekst. Op de vier vooraf vastgelegde toetsen (lagen 2 en 5 ×
> beide detectoren, Bonferroni-lat 0.0125): **0 van de 4 haalt de lat.**
> Het round-032-kandidaat repliceert niet — het was toeval. Conform de
> vooraf vastgelegde leesregel sluit spoor 2 hiermee definitief voor deze
> schaal (≤0.5B). Signaal ≠ verdict; dit raakt lagen A–F niet.

## Runverwijzing

```text
workflow: Research · Laag G sonde met echte verdictbron
run 1 (vers oordeel): 29490380118   # gpt-4.1 vers, main @ 9ced9a7, success
re-probe (faithful) : 29665325310   # gepinde verdicten, branch-ref, success
artifact (re-probe) : activation-probe-real-verdict (id 8435812870)
digest              : sha256:6c373e4e8ddc8e4179f4494c06bf94e1c66139666b83581235684bee2cb62a7d
probe_model: Qwen/Qwen2.5-0.5B (multilingual, read_location=neuron)
verdict_model: gpt-4.1 (extern, ontkoppeld) — 12 HOUDT_STAND / 12 WEERLEGD
input: dialectic_falsification_transfer_v3.json (24 cases, nieuwe brontekst WONEN/ZORG/CULTUUR)
sparse_permutations: 500 (vloer 1/501 ≈ 0.0020)
```

De re-probe pinde de geverifieerde round-1-verdicten
(`verdicts_run_29490380118.json`), zodat gpt-4.1 niet opnieuw hoefde te
oordelen en de meting een faithful reproductie is van run 29490380118. HF
Hub is in de sandbox org-geblokkeerd (403), dus dit is de manier om de
gepreregistreerde lagen expliciet af te lezen.

## De vier gepreregistreerde toetsen (lat 0.05/4 = 0.0125)

| Toets | round 032 (ontdekking) | round 033 (replicatie) | onder 0.0125? |
|---|---|---|---|
| `layers.2.mlp.down_proj` — centroïde-p | 0.014 | **0.0319** | nee |
| `layers.2.mlp.down_proj` — sparse-p | — | **0.5968** (LOOCV 0.458) | nee |
| `layers.5.mlp.down_proj` — centroïde-p | — | **0.0459** | nee |
| `layers.5.mlp.down_proj` — sparse-p | 0.018 (LOOCV 0.88) | **0.5649** (LOOCV 0.500) | nee |

**0 van de 4. Niet gerepliceerd.**

## Waarom dit beslissend is

1. **De sparse detector klapt in tot toeval.** Het round-032-"signaal" zat
   vooral in de sparse L1-classifier op laag 5 (LOOCV 0.88). Op een nieuwe
   brontekst geeft diezelfde laag met dezelfde detector LOOCV **0.50** —
   zuiver muntworp-niveau, p 0.56. Er was niets stabiels om te vinden.
2. **Het "sterkste" signaal wandelt per run.** Sterkste lagen: round 032
   → 2 (centroïde) / 5 (sparse); round-033-run-1 → 11 / 10; round-033
   re-probe → 11 / 19. Een echte, gelokaliseerde interne codering blijft
   op zijn plek; een die per run verspringt is de vingerafdruk van
   dataset-specifieke ruis. Juist dáárvoor diende de preregistratie: zonder
   de vooraf vastgelegde lagen had de losse "sparse p 0.004 op laag 19"
   verleidelijk als vondst gelezen kunnen worden.
3. **Het instrument werkt — het zegt correct néé.** De permutatiecontrole
   en de LOOCV hielden hier een ceiling-scorende classifier (LOOCV 1.0 op
   laag 19) tegen als niet-repliceerbaar. Dat is precies de bescherming
   waarvoor de sparse-detector-with-permutation is gebouwd.

## Wat dit betekent (en niet)

- **Spoor 2 (activatie-sonde) sluit voor deze schaal (≤0.5B).** Vijf
  iteraties met echte modelruns, nu ook met de H-Neurons-methodiek
  (leespunt `neuron`, sparse detector) en een gepreregistreerde
  replicatie: geen aantoonbare interne codering van het externe
  houdbaarheidsoordeel in kleine modellen. Dat is een eerlijk, definitief
  antwoord op dít niveau.
- **Niet uitgesloten**, maar expliciet toekomstwerk zonder belofte: het
  H-Neurons-precedent (Gao et al. 2025) meet op 24B–70B — een orde van
  grootte die geen GitHub-Actions-werk is. Een heropening vraagt die schaal
  én een nieuwe preregistratie.
- **Spoor 1 (dialectische falsificatie) blijft de actieve Laag G-route** en
  levert vandaag Gate-waarde: het draaide ook hier zonder mankement (12/12
  houdbaarheidsoordelen over de nieuwe caseset).
- **Lagen A–F onaangetast.** De kernclaims van SSL steunen niet op interne
  steun; dit was verkenning van de bovenkant van de stack.

## Claimgrens

Exploratieve Laag G. "Sluit voor deze schaal" betekent: geen nieuwe runs op
dit spoor onder ~1B zonder een nieuw, vooraf geregistreerd plan. De
methodische winst blijft staan — het instrument rapporteert correct néé,
ook toen een positief resultaat aantrekkelijker was geweest.
