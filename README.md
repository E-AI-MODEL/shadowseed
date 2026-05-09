# Shadow Seed Learning 4.5

[![checks](https://github.com/E-AI-MODEL/shadowseed/actions/workflows/tests.yml/badge.svg)](https://github.com/E-AI-MODEL/shadowseed/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Status](https://img.shields.io/badge/status-research%20prototype-orange)

Shadow Seed Learning (SSL) 4.5 is een research prototype voor het herkennen van kleine structurele afwezigheden in antwoorden. Een seed begint gewichtloos, wordt gevolgd via `trace`, en krijgt pas invloed na validatie via de Validation Gate.

De repo zelf is nog een **4.5 harness**. Het inhoudelijke doelbeeld staat in [`docs/00_shadow_seed_learning_4_6.md`](docs/00_shadow_seed_learning_4_6.md).

## Wat je hier krijgt

- een standaard benchmark- en rapportageketen voor interne logica en kleine outputchecks
- een aparte open-set researchroute voor handmatige seed review
- automatische publicatie van standaardresultaten naar Wiki en Pages

## Begin hier

Als je maar drie dingen wilt weten:

1. Wat SSL inhoudelijk wil zijn: [`docs/00_shadow_seed_learning_4_6.md`](docs/00_shadow_seed_learning_4_6.md)
2. Wat de repo vandaag echt bewijst: [`docs/research/current-status.md`](docs/research/current-status.md)
3. Hoe de repo praktisch is ingedeeld: [`docs/ARCHITECTURE_MAP.md`](docs/ARCHITECTURE_MAP.md)

Voor de rest van de documentatie:

- [`docs/README.md`](docs/README.md)
- [`docs/CLI_COMMAND_MAP.md`](docs/CLI_COMMAND_MAP.md)
- [`docs/wiki/Home.md`](docs/wiki/Home.md)

## Installatie

```bash
pip install -e ".[test]"
```

Optioneel met extra model- en vectorbackends:

```bash
pip install -e ".[test,models,vector]"
```

## Snelle routes

### Standaard workflow-keten

```bash
pytest
shadowseed run-gap-suite
shadowseed run-false-positive-suite
shadowseed run-benefit-suite
shadowseed run-model-benefit-suite --backend fixture
shadowseed run-blind-benchmark --labels benchmarks/private/blind_suite_labels.json
shadowseed fetch-open-set-hf-batch --source-id ag_news_test --output benchmarks/open_review/input/hf_ag_news_test_batch.json
shadowseed run-open-set-seed-review --input benchmarks/open_review/input/hf_ag_news_test_batch.json
shadowseed summarize-open-set-seed-review
shadowseed run-adversarial-gate-benchmark
shadowseed run-probe-utility-benchmark
shadowseed analyze-results
```

### Open-set researchroute

```bash
shadowseed fetch-open-set-hf-batch \
  --source-id ag_news_test \
  --output benchmarks/open_review/input/hf_ag_news_test_batch.json

shadowseed run-open-set-seed-review \
  --input benchmarks/open_review/input/hf_ag_news_test_batch.json \
  --output results/open_set_seed_output.json \
  --review-packets results/open_set_review_packets.json
```
## Belangrijkste CLI-routes

| Commando | Gewone naam | Wat test het? |
|---|---|---|
| `shadowseed run-gap-suite` | Gap Finder | Vindt SSL bekende ontbrekende punten in de regressiesuite? |
| `shadowseed run-false-positive-suite` | Rustig blijven | Laat SSL volledige antwoorden met rust en blokkeert de Gate misleidende lure-seeds? |
| `shadowseed run-benefit-suite` | Antwoordwinst | Wordt een antwoord completer met SSL-toevoegingen? |
| `shadowseed fetch-open-set-hf-batch` | Open-set intake | Haalt een kleine HF-batch op en normaliseert die naar reviewbare open-set input? |
| `shadowseed run-open-set-seed-review` | Open-set review | Maakt seed-output en review-packets zonder vaste ground-truth seedlijst |
| `shadowseed summarize-open-set-seed-review` | Open-set samenvatting | Agregeert reviewer-uitkomsten naar acceptance, agreement en disagreement-artifacts |
| `shadowseed run-adversarial-gate-benchmark` | Adversarial Gate | Vergelijkt de huidige Gate met zwakkere promotieregels op misleidende lure-candidates |
| `shadowseed run-probe-utility-benchmark` | Probe utility | Laat zien of promoted seeds scherpere follow-up, retrieval en dialectische probes opleveren dan brede baselines? |
| `shadowseed run-model-benefit-suite --backend fixture` | Model smoke | Werkt de modelroute technisch zonder modeldownload? |
| `shadowseed run-blind-benchmark` | Blind test | Blijven labels verborgen tot de scoring? |
| `shadowseed run-retrieval-benchmark` | Retrieval check | Vindt de vectorstore de juiste bronstukken? |
| `shadowseed run-retrieval-model-benchmark` | Retrieval modelcheck | Helpt opgehaalde SSOT-context het modelantwoord? |
| `shadowseed run-ssot-smoke` | SSOT check | Werkt bronstatus en falsificatiebasis? |
| `shadowseed run-vectorstore-smoke` | Vectorstore check | Werkt opslag en zoeken in de gekozen backend? |
| `shadowseed analyze-results` | Rapport | Maakt Markdown, JSON en SVG-grafieken uit resultaten. |

Deze open-set route hoort niet bij de standaard CI. Daarvoor is nog handmatige review nodig.

## Workflows in het kort

| Workflow | Rol |
|---|---|
| `Checks en benchmark-resultaten` | standaard regressie-, benchmark- en rapportageketen |
| `Publiceer testresultaten naar Wiki en Pages` | publiceert de laatste standaardresultaten |
| `Publiceer alleen statische Wiki-pagina's` | synchroniseert alleen `docs/wiki/` |
| `Full Validation Sweep` | handmatige brede backend- en retrievalrun |
| `SSOT Falsification Run` | gerichte veiligheidscheck voor SSOT-validatie |

De compactste workflow-uitleg staat in [`docs/wiki/Workflows.md`](docs/wiki/Workflows.md).

## Wat dit wel en niet betekent

De standaard CI bewijst vooral dat de meetketen werkt en dat de kleine benchmarklaag stabiel blijft.

Die standaardlaag bewijst niet automatisch:

- open-set seedkwaliteit
- brede modelprestatie
- sterke adversarial robuustheid
- domeintransfer

Daarvoor zijn aparte evaluatielagen en menselijke review nodig.

## Belangrijke paden

```text
src/shadowseed/manager.py
src/shadowseed/benchmark/
src/shadowseed/data/
benchmarks/open_review/
docs/ARCHITECTURE_MAP.md
docs/CLI_COMMAND_MAP.md
.github/workflows/
```

## Resultaten

De hoofdpublicatie van standaardruns komt hier uit:

- Wiki: `Latest Test Results`
- Wiki: `SSL 4.5 Analysis`
- GitHub Pages dashboard

Gebruik `results/latest/manifest.json` in de gepubliceerde snapshot om te zien waar elk bestand vandaan komt.
