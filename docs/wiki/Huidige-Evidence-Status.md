# Huidige Evidence-Status

> Status: actueel, 2026-05-22. Volgt het 4.6 evidence-model
> (`docs/00_shadow_seed_learning_4_6.md`) en `docs/research/current-status.md`.

De hoofdclaim van SSL rust niet op één totaalscore, maar op gescheiden
evaluatielagen. Per laag: wat is er vandaag, en hoe sterk is het bewijs.

| Laag | Vraag | Status | Bewijs vandaag |
|---|---|---|---|
| **A — Regressie** | blijft de mechaniek werken? | **sterk** | 152 tests groen, ruff schoon |
| **B — Kleine benchmark** | scoort SSL op vaste suites? | **bruikbaar** | gap-, false-positive-, benefit-, blind-suite; benefit-delta +0.8 tot +1.0 zonder ongegronde toevoegingen |
| **C — Open-set seedkwaliteit** | werkt het op onbekende teksten? | **infra klaar, evidence pending** | v0.1/v0.2/v0.3 detectoren op main; taalmodel-detector (v0.3) draait; menselijke review nog niet gedaan |
| **D — Adversarial Gate** | houdt de Gate misleidende seeds tegen? | **eerste echte evidence** | 21 cases, precision 1.0, recall 1.0, F1 1.0; drie baselines vergeleken |
| **E — Probe utility** | doet de feedback-loop echt iets? | **eerste echte evidence** | 10/10 lifecycle-scenarios (reward/penalty/clamp/demotie/status-block); plus prompt-kwaliteit suite |
| **F — Domeintransfer** | blijft kwaliteit overeind buiten bekende domeinen? | **afwezig** | geen module |
| **G — Modelinterne** | steun in interne modelsignalen? | **onderzoekswerk** | conceptueel; per 4.6 bewust uitgesteld |

## Wat je voorzichtig wél mag zeggen

- De mechanische SSL-kern werkt zoals ontworpen.
- Op scenario-data met bekende gaps verbetert SSL het antwoord meetbaar,
  zonder hallucinaties toe te voegen.
- De Gate discrimineert (niet alleen weigeren): hij promoot echte gaps met
  evidence en blokkeert lures.
- De probe-feedback lifecycle gedraagt zich zoals de spec claimt.

## Wat je nog niet mag zeggen

- dat SSL algemeen beter presteert op open data — laag C heeft nog geen
  menselijk gereviewde data
- dat het effect over domeinen transfereert — laag F bestaat nog niet
- dat fixture-resultaten gelijkstaan aan echte modelvalidatie

## De eerlijke één-zin

> Op de gemeten lagen (A, B, D, E) is SSL meetbaar helpend; open-set (C) heeft
> werkende infrastructuur maar wacht op echte review; domeintransfer (F) en
> modelinterne validatie (G) zijn nog open.
