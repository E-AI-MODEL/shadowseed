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
- [x] **W5. Generatieve "kunnen staan"-frames door payoff** (gap 1, v0.4-gen):
  uitgevoerd (round 016). **Convergent negatief**: gpt-4.1 dekt zelf ~88% van de
  generatieve frames (novel 3/24). Kanttekening: baseline was *geprimed* op
  "verklarende invalshoeken" → confound, zie W7. Zie `round_016/`.
- [!] **W7. (gedegradeerd) naïeve single-shot baseline.** Nuttige sanity-check,
  maar niet meer de decider — scope-correctie hieronder: single-shot mist het
  SSL-mechanisme.
- [~] **W9. DE ECHTE DECIDER — cross-turn payoff (gap 5), via de ECHTE pijplijn.**
  Harness gebouwd: `ssl_session_suite.py` draait een multi-turn gesprek door de
  echte `SSLManager` (weight-0 ingest, recurrence-dedup, Validation Gate over
  beurten, TTL-decay, TrTL-reactivatie, constellations); alleen een
  pijplijn-PROMOTED seed geboren in een eerdere beurt mag een later antwoord
  sturen. Pipeline-getrouwe test bewijst het pad (recurrence→Gate→promote→
  cross-turn surface). **Vervangt de losstaande W1/W5/W14-afgeleiden** (die de
  manager NIET gebruikten — nu gemarkeerd als NIET-PIJPLIJN). Rest: draaien op
  gpt-4.1 + blinde review van de cross-turn paren. Multi-turn gesprek
  waarin een weight-0 seed die vroeg gedetecteerd is meereist (TTL/TrTL) en pas
  later, als de context verschuift, alsnog in het antwoord kan landen. Baseline =
  normale chatbot met dezelfde gespreksgeschiedenis maar zónder shadow-memory.
  *Klaar wanneer:* gemeten is of de meegereisde seed in een latere beurt waarde
  toevoegt die het model niet zelf uit de historie afleidt. Mag falen (sterk
  model leidt zelf af); per het residu-argument telt zelfs een kleine
  betrouwbare winst. **Scope-correctie (2026-06-21):** W1/W5 maten single-shot;
  SSL's eigenlijke claim is dit cross-turn-mechanisme + dat het 3–10%-residu dat
  zelfs een frontier-model mist betrouwbaar/persistent/gratis wordt gevangen — een
  grote LLM-stap, geen marginale. Zie `round_016/`.
- [ ] **W6. Blinde human-review** alleen op een variant die toegevoegde waarde
  laat zien (W4/W7), niet op de redundante sets. *Klaar wanneer:* win-rate + κ.
- [ ] **W8. Andere claim-richtingen** indien W7 ook negatief: (a) zwakker model
  dat SSL-lift krijgt, (b) cross-turn accumulatie (gap 5), (c) Niveau 2. Elk is
  een *andere* claim dan "externe detector verslaat frontier-model".

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
