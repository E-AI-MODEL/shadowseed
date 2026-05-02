# Shadow Seed Learning 4.5

[![tests](https://github.com/E-AI-MODEL/shadowseed/actions/workflows/tests.yml/badge.svg)](https://github.com/E-AI-MODEL/shadowseed/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Status](https://img.shields.io/badge/status-research%20prototype-orange)
![CI](https://img.shields.io/badge/CI-unit%20%2B%20SSL%20suite%20%2B%20NLP%20smoke-brightgreen)
![License](https://img.shields.io/badge/license-see%20repository-lightgrey)

**Shadow Seed Learning (SSL) 4.5** is een mechanisme voor het detecteren, opslaan en valideren van kleine structurele afwezigheden in een antwoord.

De kern:

> Een seed bevat precies één gap.

Deze repository bevat de implementatie, de officiële SSL 4.5 Gap-Test Suite en een lichte NLP-smoke test. Alles draait gratis in GitHub Actions, zonder betaalde API's en zonder verplichte modeldownload.

---

## Wat wordt getest?

Deze repo test twee dingen:

| Laag | Doel | Commando | CI |
|---|---|---|---|
| Unit tests | Klopt de code? | `pytest` | ja |
| SSL 4.5 Gap-Test Suite | Klopt de paper-pipeline? | `shadowseed run-gap-suite` | ja |
| NLP / AbsenceBench smoke | Breekt de absence-runner niet? | `shadowseed run-nlp-smoke` | ja |

De Gap-Test Suite is de belangrijkste test. Die gebruikt drie scenario's met atomische ground-truth seeds en score 0/1/2.

---

## Architectuur

```mermaid
flowchart TD
    A[Input of modelantwoord] --> B[Detectie-pass]
    B --> C[Seed-normalisatie]
    C --> D[Shadow seed]
    D --> E[trace = 2.0]
    D --> F[weight = 0.0]
    E --> G[Herkenning over turns]
    G --> H[Validation Gate]
    H --> I{Geslaagd?}
    I -- nee --> J[NEW / ACTIVE / DECAYING]
    I -- ja --> K[weight omhoog]
    K --> L{weight >= drempel?}
    L -- nee --> J
    L -- ja --> M[PROMOTED]
    M --> N[Active Probe of retrieval]
```

---

## Twee velden: trace en weight

```mermaid
stateDiagram-v2
    [*] --> NEW
    NEW --> ACTIVE: herkend
    ACTIVE --> DECAYING: geen trigger
    DECAYING --> DORMANT: trace < 0.05
    DORMANT --> NEW: TrTL-trigger
    ACTIVE --> PROMOTED: Validation Gate + weight >= threshold
    PROMOTED --> NEW: falsificatie
    DORMANT --> EXPIRED: te lang dormant
```

| Veld | Betekenis | Startwaarde | Rol |
|---|---|---:|---|
| `trace` | aanwezigheid van de seed | `2.0` | geheugensterkte |
| `weight` | invloed van de seed | `0.0` | pas na validatie actief |

Belangrijk: een nieuwe seed is aanwezig, maar heeft nog geen invloed.

---

## Installatie

```bash
pip install -e ".[test]"
```

Optioneel met embeddingmodel:

```bash
pip install -e ".[test,models]"
```

---

## Quickstart

Run alles lokaal:

```bash
pytest
shadowseed run-gap-suite
shadowseed run-nlp-smoke
```

Run een kleine AbsenceBench-sample:

```bash
shadowseed fetch-absencebench --limit 10
shadowseed run-local-absencebench --input data/absencebench_sample.json
```

---

## CLI

```bash
shadowseed run-gap-suite
shadowseed run-nlp-smoke
shadowseed fetch-absencebench --limit 10
shadowseed run-local-absencebench --input examples/local_absencebench_sample.json
shadowseed prepare-absencebench
```

---

## CI

GitHub Actions draait op elke push en pull request:

```mermaid
flowchart LR
    A[Push / PR] --> B[Unit tests 3.10]
    A --> C[Unit tests 3.11]
    B --> D[SSL 4.5 Gap-Test Suite]
    C --> D
    B --> E[NLP AbsenceBench smoke]
    C --> E
```

De CI gebruikt geen betaalde API's en downloadt standaard geen groot model.

---

## Evaluatie

De SSL 4.5 Gap-Test Suite gebruikt de score uit de specificatie:

| Score | Betekenis |
|---:|---|
| 0 | geen relevante gap gevonden |
| 1 | richting klopt, maar output is te vaag of te breed |
| 2 | atomische en structureel juiste gap gevonden |

Ground truth wordt niet gebruikt tijdens detectie. Ground truth wordt alleen gebruikt voor evaluatie en externe validatie in de Validation Gate.

---

## Belangrijke bestanden

```text
src/shadowseed/manager.py                         # SSLManager: trace, weight, Validation Gate
src/shadowseed/data/gap_test_suite_4_5.json       # officiële SSL 4.5 Gap-Test Suite
src/shadowseed/benchmark/ssl45_gap_suite.py       # evaluator voor de paper-test
src/shadowseed/benchmark/absencebench_local.py    # lichte NLP smoke runner
src/shadowseed/benchmark/absencebench_hf.py       # gratis Hugging Face sample fetcher
src/shadowseed/cli.py                             # CLI entrypoint
docs/EXPERIMENT.md                                # experimentopzet
experiments/run_full.py                           # reproduceerbare run helper
```

---

## Wat dit wel en niet claimt

Wel:

- reproduceerbare SSL 4.5 testopzet
- multi-turn seed-opbouw
- Validation Gate
- scorebare Gap-Test Suite
- gratis CI-run

Niet:

- geen nieuw foundation model
- geen aanpassing van modelgewichten
- geen claim dat SSL al state-of-the-art is
- geen verplichte LLM- of GPU-run

---

## Status

- `main` is de leidende branch
- CI is groen
- SSL 4.5 Gap-Test Suite draait via CI
- NLP smoke test draait via CI

---

## Citeren

Gebruik deze repo als implementatie- en evaluatiebasis voor Shadow Seed Learning 4.5.

```text
Visser, H. (2026). Shadow Seed Learning 4.5: Atomische detectie en epistemische navigatie.
E-AI-MODEL/shadowseed.
```
