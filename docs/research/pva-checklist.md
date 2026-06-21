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

- [ ] **W1. Open-set seeds als payoff-input.** Neem échte open-set-gedetecteerde
  seeds (rounds 004–007, niet zelf verzonnen) en voer ze door de model-benefit /
  revisie-pijplijn op gpt-4.1. *Klaar wanneer:* een run bestaat waarin de
  gehandelde seeds uit de detector komen, niet uit een fixture.
- [ ] **W2. Blinde human-review op de wild-payoff-paren** (hergebruik
  round-013-tooling). *Klaar wanneer:* win-rate + human-vs-AI κ berekend op
  niet-auteur-ontworpen seeds.
- [ ] **W3. Eerlijke koppeling detectie↔payoff vastleggen** als round-note.
  *Klaar wanneer:* één doc die de end-to-end claim (detectie-kwaliteit →
  payoff-effect) met de eerlijke grenzen beschrijft.

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
