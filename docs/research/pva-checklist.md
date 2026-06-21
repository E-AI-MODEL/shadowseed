# PvA — open taken richting einddoel

> **Levend document.** Doel: de openstaande stappen richting het einddoel —
> *SSL gevalideerd als scenario-onafhankelijk mechanisme* (hoofdclaim op
> gescheiden evidence-lagen A–G, `docs/00_shadow_seed_learning_4_6.md`) — in
> beeld houden en afvinken terwijl we ze doen.
>
> Bijwerken: vink `[x]` af wanneer "klaar wanneer" is gehaald, met de PR/round
> erbij. Voeg nieuwe taken toe onder de juiste sectie. Geen totaalscore —
> houd de laag-status eerlijk gescheiden.
>
> Status-legenda: `[ ]` open · `[~]` bezig · `[x]` klaar · `[!]` geblokkeerd/keuze nodig
>
> Baseline bij start (2026-06-20): stappen ~55% · repo-kwaliteit ~82% ·
> output-kwaliteit ~58% (detectie zwak / payoff sterk).

---

## P0 — Hoogste hefboom: de wild-detectie → payoff-lus sluiten

*Raakt Laag C + E + output-kwaliteit tegelijk. Tot nu zijn payoff-seeds
auteur-ontworpen; dit koppelt "vinden" aan "gebruiken".*

- [x] **W1. Open-set seeds als payoff-input.** Echte open-set-gedetecteerde seeds
  (round 006 batch1, AI-accepted, κ 0.63) door de payoff-pijplijn op gpt-4.1
  (round 015). **Resultaat: grotendeels negatief/directioneel** — een sterk model
  vindt zélf ~82% van de gedetecteerde gaps (echt nieuw: ~2/29 niche). De
  wild-loop loont dus níét op korte, makkelijke teksten. Zie `round_015/`.
- [~] **W3. Eerlijke koppeling detectie↔payoff vastgelegd** (round 015):
  detectie-kwaliteit op makkelijke teksten → lage payoff omdat het model de
  triviale gaps zelf al ziet. Vervolg hieronder (W4–W6).
- [ ] **W4. Harde/dichte teksten**: draai de wild-payoff op de round-007
  wetenschap-batch / lange of technische teksten, waar het model de gap *niet*
  spontaan ziet. *Klaar wanneer:* baseline-coverage van gedetecteerde gaps
  duidelijk < dan op nieuws (detector voegt aantoonbaar toe).
- [ ] **W5. Generatieve "kunnen staan"-frames door payoff** (gap 1, v0.4-gen):
  niet-omissies maar niet-voor-de-hand-liggende invalshoeken. *Klaar wanneer:*
  wild-payoff met generatieve seeds, baseline-coverage gemeten.
- [ ] **W6. Blinde human-review** op de winnende variant (W4/W5), niet op de
  redundante nieuws-set. *Klaar wanneer:* win-rate + κ op een set waar de
  detector toegevoegde waarde laat zien.

## P1 — Laag C: open-set seedkwaliteit naar criterium (≥ 0.60)

*De make-or-break detectie-claim; plateaut nu op "relevant maar triviaal".*

- [ ] **C1. Substantie-probleem aanpakken**: de generatieve "kunnen staan"-variant
  (gap 1, v0.4-gen) echt A/B draaien vs de absence-detector op verse items.
  *Klaar wanneer:* round 009 uitgevoerd (niet alleen gepland) met acceptance per
  variant.
- [ ] **C2. Tweede onafhankelijke human-reviewer** op een verse batch.
  *Klaar wanneer:* κ op n≥50 met ≥2 reviewers, los van AI-review.
- [ ] **C3. Acceptance ≥ 0.60 op een verse, geblindeerde batch** of een eerlijke
  conclusie waaróm dat (nog) niet haalbaar is. *Klaar wanneer:* criterium gehaald
  óf gefundeerd afgeschreven.

## P1 — Laag F: domeintransfer

- [ ] **F1. Minder afhankelijkheid van domein-priors**: de model-benefit-detectie
  draait nu op `DOMAIN_PRIORS`. Test op domeinen zónder priors. *Klaar wanneer:*
  een transfer-run op holdout-domeinen met eerlijke uitkomst.
- [ ] **F2. Driver van de out-of-sample-daling** (round 007, |r|<0.25 voor
  dichtheid) verder onderzoeken of expliciet open laten. *Klaar wanneer:*
  kandidaat-verklaring getoetst of gemarkeerd als onbeslist.

## P2 — Laag E: probe utility verdiepen

- [ ] **E1. Behavioral metric "betere vervolgvraag/retrieval-query"** verder dan
  smoke. *Klaar wanneer:* een meetbare vergelijking promoted-vs-niet op
  probe-kwaliteit.

## P2 — Repo-kwaliteit (warts opruimen)

- [ ] **Q1. Semantische coverage overal** waar nu nog lexicale `coverage()` de
  primaire maat is (niet alleen model-benefit). *Klaar wanneer:* lexicaal is
  gedegradeerd tot secundaire/echo-indicator.
- [ ] **Q2. Falsehood-flag met negatie-detectie** (round 014 gaf 2/3
  vals-positief). *Klaar wanneer:* de flag een correctie niet meer als bewering
  telt.
- [ ] **Q3. Doc-code-drift sweep**: controleer dat docs/00, manager-design en de
  wiki de huidige lifecycle (TTL/TrTL/EXPIRED) consistent beschrijven.
- [ ] **Q4. Coverage-metric blind spot in de suite-interpretatie** documenteren
  waar resultaten nog de oude lexicale +0.35 noemen.

## P3 — Visie-gaten (gap 4 & 5) en Laag G

- [ ] **V1. Gap 5 — levende cross-turn shadow-laag**: de seed die echt meereist
  over beurten (nu lifecycle-mechaniek aanwezig, maar geen multi-turn demo).
  *Klaar wanneer:* een demo waarin een seed over meerdere beurten leeft, decayt
  of via TrTL herleeft in een echt gesprek.
- [ ] **V2. Gap 4 / Laag G — modelinterne (H-neuron) verkenning**: blijft
  research; alleen oppakken als P0–P2 staan. *Klaar wanneer:* een scoping-notitie
  of eerste sonde.

## Doorlopend

- [ ] **D1. Round-notes + status-doc** bijwerken bij elke afgeronde taak.
- [ ] **D2. Deze PvA bijhouden** (afvinken, nieuwe taken toevoegen).

---

## Changelog

- 2026-06-20 — PvA aangemaakt na merge van PR #142 (rounds 010–014 + lifecycle
  TTL/TrTL). Eerstvolgende focus: P0 (wild-lus).
- 2026-06-21 — W1 gedaan (round 015): wild-loop op nieuws is grotendeels redundant
  (model vindt ~82% zelf). W-taken bijgesteld naar harde teksten (W4) +
  generatieve frames (W5), human-review (W6) pas op de winnende variant.
