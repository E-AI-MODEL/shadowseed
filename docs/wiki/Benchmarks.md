# Benchmarks

Niet elke suite draagt dezelfde bewijslast. Dat is de hoofdregel.

## Snelle indeling

| Laag | Doel | Voorbeelden |
|---|---|---|
| standaard regressie en smoke | mechaniek heel houden | Gap Finder, false-positive, benefit, model smoke, blind smoke |
| handmatige research | sterkere bewijssoorten bouwen | open-set review, adversarial Gate, probe utility |
| extra technische checks | backend en veiligheidscontroles | retrieval, vectorstore, SSOT, full sweep |

## Standaard Actions-runs

| Run | Vraag | Hoofdartifact | Type |
|---|---|---|---|
| 01 Codecheck | Werkt de Python-code? | geen JSON | regressie |
| 02 Gap Finder | Vindt SSL bekende ontbrekende punten? | `ssl45_gap_suite.json` | regressie / kleine benchmark |
| 03 Rustig blijven | Laat SSL volledige antwoorden met rust? | `ssl45_false_positive_suite.json` | regressie |
| 04 Antwoordwinst | Wordt een antwoord completer met SSL? | `ssl45_benefit_suite.json` | kleine benchmark |
| 05 Model smoke | Werkt de modelroute technisch? | `ssl45_model_benefit_suite.json` | technische smoke |
| 06 Blind test | Blijven labels verborgen tot scoring? | `blind_benchmark.json` | methodologische smoke |
| 07 Rapport | Hoe zien de resultaten er samen uit? | `analysis_report.md`, `summary.json` | rapportage |
| 08 AbsenceBench rooktest | Werkt de lokale dataset-run? | `absencebench_smoke.json` | technische smoke |
| 09 Herhalingstest | Wat gebeurt er bij meer rondes? | `ssl45_gap_suite_turns_*.json` | gevoeligheid |

## Handmatige research-routes

| Route | Artifact | Rol |
|---|---|---|
| open-set review | `open_set_seed_review.json`, review-packets | seedkwaliteit zonder vaste seedlijst |
| adversarial Gate | `adversarial_gate_benchmark.json`, casebook | vergelijking met zwakkere promotieregels |
| probe utility | `ssl45_probe_utility_suite.json` | scherpte van vervolgacties |

## Hoe je dit moet lezen

### De standaardlaag zegt vooral

- de mechaniek werkt nog
- kleine benchmarksignalen zijn stabiel
- rapportage en publicatie lopen mee

### De standaardlaag zegt niet automatisch

- dat SSL sterk is in open-set situaties
- dat de Gate breed robuust is
- dat modelprestatie buiten de kleine suites bewezen is
- dat menselijke reviewers seedkwaliteit breed onderschrijven

## Belangrijke aanvullende pagina's

- [Workflows](Workflows)
- [Blind Benchmark](Blind-Benchmark)
- [Latest Test Results](Latest-Test-Results)
- [SSL 4.5 Analysis](SSL-45-Analysis)
