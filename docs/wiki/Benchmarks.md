# Benchmarks

De repo gebruikt meerdere suites. Elke suite test een andere vraag.

Belangrijk: niet elke suite draagt dezelfde bewijslast. De huidige vaste scenario-suites zijn vooral regressie- en kleine benchmarklagen. De algemene SSL-claim moet op termijn sterker leunen op open-set, adversarial en gedragsvalidatie.

## Overzicht in gewone taal

| Naam in Actions | Vraag | CLI | Artifact | Bewijssoort |
|---|---|---|---|---|
| 01 Codecheck | Werkt de Python-code? | `pytest` | geen JSON | regressie |
| 02 Gap Finder | Vindt SSL bekende ontbrekende punten in de regressiesuite? | `shadowseed run-gap-suite` | `ssl45_gap_suite.json` | kleine benchmark / regressie |
| 03 Rustig blijven | Laat SSL volledige antwoorden met rust? | `shadowseed run-false-positive-suite` | `ssl45_false_positive_suite.json` | regressie / beperkte ruiscontrole |
| 04 Antwoordwinst | Wordt een antwoord completer door SSL-seeds? | `shadowseed run-benefit-suite` | `ssl45_benefit_suite.json` | kleine benchmark |
| 05 Model smoke | Werkt dezelfde modelroute met en zonder SSL? | `shadowseed run-model-benefit-suite` | `ssl45_model_benefit_suite.json` | technische smoke |
| 06 Blind test | Ziet de detector de labels niet vooraf? | `shadowseed run-blind-benchmark` | `blind_benchmark.json` | methodologische smoke |
| 07 Rapport | Hoe zien de resultaten er samen uit? | `shadowseed analyze-results` | `analysis_report.md`, `summary.json` | rapportage |
| 08 AbsenceBench rooktest | Werkt de lokale dataset-run? | `shadowseed run-absencebench-smoke` | `absencebench_smoke.json` | technische smoke |
| 09 Herhalingstest | Wat gebeurt er bij meer rondes? | `shadowseed run-gap-suite --turns N` | `ssl45_gap_suite_turns_*.json` | gevoeligheid / regressie |
| handmatig | Kan SSL open-set seeds produceren zonder vaste seedlijst? | `shadowseed run-open-set-seed-review` | `open_set_seed_review.json`, review-packets | open-set scaffold |
| handmatig | Blokkeert de huidige Gate meer misleidende lure-seeds dan zwakkere promotieregels? | `shadowseed run-adversarial-gate-benchmark` | `adversarial_gate_benchmark.json`, casebook | adversarial scaffold |
| handmatig | Levert SSL scherpere vervolgprobes op dan brede baseline-probes? | `shadowseed run-probe-utility-benchmark` | `ssl45_probe_utility_suite.json` | gedragsmatige scaffold |

## Command-audit in het kort

De CLI gebruikt nu drie commandolagen:

- standaard regressie- en smoke-routes;
- handmatige research-routes;
- AbsenceBench-utility routes.

De canonieke AbsenceBench-commands zijn nu:

- `shadowseed prepare-absencebench-bundle`
- `shadowseed fetch-absencebench-sample`
- `shadowseed run-absencebench-local`
- `shadowseed run-absencebench-smoke`

Legacy aliases blijven voorlopig werken:

- `prepare-absencebench`
- `fetch-absencebench`
- `run-local-absencebench`
- `run-nlp-smoke`

Zo wordt de naamgeving consistenter zonder bestaande scripts direct te breken.

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
- false-positive rates;
- Gate-vergelijking tegen zwakkere promotieregels op adversarial lure-candidates.

Deze suite voorkomt dat SSL overal zomaar ontbrekende punten van maakt. De strengere variant laat nu ook zien of de huidige Gate beter blokkeert dan trace-only of lichtere regels.

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

## Open-set en adversarial laag

### Open-set seed review

Data:

```text
src/shadowseed/data/open_set_seed_review_sample.json
```

Output:

- `open_set_seed_review.json`
- `open_set_seed_review_packets.json`

Deze runner doet nog geen volledige open-world validatie. Hij bouwt wel de eerste eerlijke structuur daarvoor:

- seed-output zonder vaste ground-truth seedlijst;
- normalisatie en atomiciteitsfiltering;
- review-packets voor menselijke scoring op atomiciteit, relevantie, toetsbaarheid, niet-trivialiteit en follow-up utility.

Dit is de eerste stap weg van alleen scenario-scores.

### Adversarial Gate benchmark

Data:

```text
src/shadowseed/data/adversarial_gate_benchmark.json
```

Output:

- `adversarial_gate_benchmark.json`
- `adversarial_gate_casebook.md`

Deze runner trekt de Gate-stresstest los uit de bredere false-positive suite en maakt de baselinevergelijking zichtbaar:

- `current_gate`
- `trace_only`
- `trace_without_contradiction_check`

De suite bevat drie soorten negatieve gevallen:

- complete antwoorden waarin de lure-seed al gedekt is;
- stijlzwaktes die geen epistemische gap zijn;
- verleidelijke maar irrelevante uitbreidingen.

De JSON-samenvatting laat de deltas per baseline zien. De casebook maakt de concrete blokkades leesbaar per scenario en seed.

### Probe utility

Data:

```text
src/shadowseed/data/ssl45_probe_utility_suite.json
```

Output:

- `ssl45_probe_utility_suite.json`

Deze suite vergelijkt per scenario drie soorten vervolgacties:

- socratische follow-up;
- retrieval-query;
- dialectische tegenvraag.

Per laag vergelijkt de suite een brede baseline met een seed-geleide variant. De score beloont verwachte domeintermen en straft brede stopwoorden of vage termen. Een positieve delta betekent hier dus niet dat de vraag menselijk perfect is, maar wel dat de promoted seed concreter stuurt dan de baseline.

De suite draait nog niet standaard in CI, maar als het resultaatbestand aanwezig is, neemt de analyzer deze laag wel mee in de samenvatting en rapportage.

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

De handmatige verdiepingslagen schrijven standaard naar:

```text
results/open_set_seed_review.json
results/open_set_seed_review_packets.json
results/adversarial_gate_benchmark.json
results/adversarial_gate_casebook.md
results/ssl45_probe_utility_suite.json
```

In `07 Rapport` worden de gedownloade artifacts eerst conflictveilig verzameld. De originele structuur blijft bewaard onder `results/artifacts/`, en `results/manifest.json` legt vast uit welk artifact elk analysebestand afkomstig is.

Na een geslaagde push naar `main` verzamelt `Publiceer testresultaten naar Wiki en Pages` de standaard artifacts in een workflow-snapshot voor Wiki en Pages.

Gebruik `results/latest/manifest.json` om te zien uit welk artifact elk gepubliceerd bestand komt.

## Interpretatie

Een sterke uitkomst vereist minimaal:

- hogere gap coverage met SSL;
- geen stijging in unsupported additions;
- lage false-positive rate;
- hetzelfde model in baseline en SSL-conditie;
- labels gescheiden bij blinde tests;
- geen conclusie alleen op basis van extra lengte.

Een fixture-run is nuttig als technische controle. Een echte modelclaim vraagt om `hf-transformers`, meer scenario's en blind review.

Voor de handmatige open-set, adversarial en probe-lagen geldt extra voorzichtigheid:

- het zijn nog scaffolds, geen eindbewijs;
- de belangrijkste winst is dat de repo eerlijker en toetsbaarder wordt;
- hun artefacts moeten apart gelezen worden, niet als één totaalscore met regressieruns.

## Wat er nog bij moet komen

Om de repo verder te professionaliseren en minder scenario-afhankelijk te maken, zijn later extra lagen nodig:

- volwassen open-set seed quality review;
- zwaardere adversarial false-positive evaluatie met menselijke review;
- probe utility evaluatie met menselijke review;
- domeintransfer;
- aparte modelinterne onderzoekslijn.
