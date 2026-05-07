# Benchmarks

De repo gebruikt meerdere suites. Elke suite test een andere vraag.

Belangrijk: niet elke suite draagt dezelfde bewijslast. De huidige vaste scenario-suites zijn vooral regressie- en kleine benchmarklagen. De algemene SSL-claim moet op termijn sterker leunen op open-set, adversarial en gedragsvalidatie.

## Overzicht in gewone taal

| Naam in Actions | Vraag | CLI | Artifact |
|---|---|---|---|
| 01 Codecheck | Werkt de Python-code? | `pytest` | geen JSON |
| 02 Gap Finder | Vindt SSL bekende ontbrekende punten in de regressiesuite? | `shadowseed run-gap-suite` | `ssl45_gap_suite.json` |
| 03 Rustig blijven | Laat SSL volledige antwoorden met rust? | `shadowseed run-false-positive-suite` | `ssl45_false_positive_suite.json` |
| 04 Antwoordwinst | Wordt een antwoord completer door SSL-seeds? | `shadowseed run-benefit-suite` | `ssl45_benefit_suite.json` |
| 05 Model smoke | Werkt dezelfde modelroute met en zonder SSL? | `shadowseed run-model-benefit-suite` | `ssl45_model_benefit_suite.json` |
| 06 Blind test | Ziet de detector de labels niet vooraf? | `shadowseed run-blind-benchmark` | `blind_benchmark.json` |
| 07 Rapport | Hoe zien de resultaten er samen uit? | `shadowseed analyze-results` | `analysis_report.md`, `summary.json` |
| 08 AbsenceBench rooktest | Werkt de lokale dataset-run? | `shadowseed run-nlp-smoke` | `absencebench_smoke.json` |
| 09 Herhalingstest | Wat gebeurt er bij meer rondes? | `shadowseed run-gap-suite --turns N` | `ssl45_gap_suite_turns_*.json` |

## Regressie- en kleine benchmarklaag

Deze laag is vandaag het sterkst uitgewerkt en draait standaard in CI.

### Gap Finder

Data:

```text
src/shadowseed/data/gap_test_suite_4_5.json
```

Meet:

- scenario score;
- atomische hits;
- promoted hits;
- promoted seeds.

Deze suite laat zien of SSL de ontworpen gaps in de kleine vaste suite vindt. Dat is waardevol als regressie en kleine benchmark, maar nog geen eindbewijs voor open-world prestatie.

### Rustig blijven

Data:

```text
src/shadowseed/data/gap_test_suite_false_positive_4_5.json
```

Meet:

- candidate false positives;
- promoted false positives;
- false-positive rates.

Deze suite voorkomt dat SSL overal zomaar ontbrekende punten van maakt. Voor hardere claims is later nog een strengere adversarial laag nodig.

### Antwoordwinst

Data:

```text
src/shadowseed/data/ssl45_benefit_suite.json
```

Meet:

- baseline gap coverage;
- SSL gap coverage;
- coverage delta;
- unsupported additions.

Dit is fase 1-achtig gedrag binnen een kleine vaste benchmarkopzet. Er wordt nog geen volledig open modelgedrag bewezen.

### Model smoke

Data:

```text
src/shadowseed/data/ssl45_model_benefit_suite.json
```

Meet hetzelfde model in twee condities:

```text
baseline
SSL-guided rewrite
```

Backends:

| Backend | Doel |
|---|---|
| `fixture` | snelle CI-smoke zonder modeldownload |
| `hf-transformers` | echte lokale of handmatige SLM-run |

De standaard CI gebruikt `fixture`. Dat bewijst de meetketen, niet de prestatie van een echt model.

## Blind benchmarklaag

### Blind test

Data:

```text
src/shadowseed/data/blind_suite_public.json
benchmarks/private/blind_suite_labels.json
```

Het publieke bestand bevat scenario's. Het private labelbestand bevat `expected_gaps` en `must_not_add` en wordt pas bij scoring gebruikt.

De standaard CI maakt tijdelijke smoke-labels. Echte labels horen niet in de repo.

Deze laag is belangrijk omdat ze methodologisch bewaakt dat detectie en scoring gescheiden blijven.

## Retrieval en SSOT-laag

| Suite | Vraag | CLI |
|---|---|---|
| Retrieval check | Vindt de vectorstore de juiste bronstukken? | `shadowseed run-retrieval-benchmark` |
| Retrieval modelcheck | Helpt opgehaalde SSOT-context het modelantwoord? | `shadowseed run-retrieval-model-benchmark` |
| SSOT check | Werkt bronstatus en falsificatiebasis? | `shadowseed run-ssot-smoke` |
| Vectorstore check | Werkt opslag en zoeken? | `shadowseed run-vectorstore-smoke` |

Deze runs zijn nuttig voor diagnose en echte modelruns, maar niet elke run zit in de standaard CI.

## Artifacts

De standaard CI uploadt artifacts met leesbare namen:

```text
02-gap-finder-results
03-false-positive-results
04-answer-benefit-results
05-model-smoke-results
06-blind-benchmark-results
07-analysis-report
08-absencebench-smoke-results
09-repeat-test-turns-*
```

Na een geslaagde push naar `main` verzamelt `Publish Test Results` deze artifacts in:

```text
results/latest/
results/artifacts/
```

Gebruik `results/latest/manifest.json` om te zien uit welk artifact elk bestand komt.

## Interpretatie

Een sterke uitkomst vereist minimaal:

- hogere gap coverage met SSL;
- geen stijging in unsupported additions;
- lage false-positive rate;
- hetzelfde model in baseline en SSL-conditie;
- labels gescheiden bij blinde tests;
- geen conclusie alleen op basis van extra lengte.

Een fixture-run is nuttig als technische controle. Een echte modelclaim vraagt om `hf-transformers`, meer scenario's en blind review.

## Wat er nog bij moet komen

Om de repo verder te professionaliseren en minder scenario-afhankelijk te maken, zijn later extra lagen nodig:

- open-set seed quality review;
- adversarial false-positive evaluatie;
- probe utility evaluatie;
- domeintransfer;
- aparte modelinterne onderzoekslijn.
