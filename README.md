# Shadow Seed Learning 4.5

Deze repository bevat een reproduceerbare implementatie en evaluatiebasis voor **Shadow Seed Learning 4.5**.

De repo draait twee soorten checks:

1. **SSL 4.5 Gap-Test Suite**  
   De eigen paper-test met drie scenario's, atomische ground-truth seeds, multi-turn seed-opbouw en Validation Gate.

2. **NLP / AbsenceBench smoke test**  
   Een lichte sanity check op absence-detectie, zonder betaalde API's of zware modeldownload.

## Installatie

```bash
pip install -e ".[test]"
```

Optioneel met embeddingmodel:

```bash
pip install -e ".[test,models]"
```

## Snel starten

Run de unit tests:

```bash
pytest
```

Run de SSL 4.5 Gap-Test Suite:

```bash
shadowseed run-gap-suite
```

Run de NLP smoke test:

```bash
shadowseed run-nlp-smoke
```

## CLI-commando's

```bash
shadowseed run-gap-suite
shadowseed run-nlp-smoke
shadowseed fetch-absencebench --limit 10
shadowseed run-local-absencebench --input examples/local_absencebench_sample.json
shadowseed prepare-absencebench
```

## CI

GitHub Actions draait op elke push en pull request:

- unit tests op Python 3.10 en 3.11
- SSL 4.5 Gap-Test Suite
- NLP AbsenceBench smoke test

De CI gebruikt geen betaalde API's en downloadt standaard geen groot model.

## Belangrijke bestanden

```text
src/shadowseed/manager.py                         # SSLManager: trace, weight, Validation Gate
src/shadowseed/data/gap_test_suite_4_5.json       # officiële SSL 4.5 Gap-Test Suite
src/shadowseed/benchmark/ssl45_gap_suite.py       # evaluator voor de eigen paper-test
src/shadowseed/benchmark/absencebench_local.py    # lichte NLP smoke runner
src/shadowseed/benchmark/absencebench_hf.py       # gratis Hugging Face sample fetcher
src/shadowseed/cli.py                             # CLI entrypoint
docs/EXPERIMENT.md                                # experimentopzet
experiments/run_full.py                           # reproduceerbare run helper
```

## Evaluatie

De SSL 4.5 Gap-Test Suite gebruikt de score uit de specificatie:

| Score | Betekenis |
|---:|---|
| 0 | geen relevante gap gevonden |
| 1 | richting klopt, maar output is te vaag of te breed |
| 2 | atomische en structureel juiste gap gevonden |

Ground truth wordt niet gebruikt tijdens detectie. Ground truth wordt alleen gebruikt voor evaluatie en externe validatie in de Validation Gate.

## Status

- `main` is de leidende branch
- CI is groen
- SSL 4.5 Gap-Test Suite draait via CI
- NLP smoke test draait via CI
