# Benchmarks

De repo gebruikt meerdere suites. Elke suite test een andere vraag.

## Overzicht

| Suite | Vraag | CLI |
|---|---|---|
| Gap-Test Suite | Vindt SSL de juiste gaps? | `shadowseed run-gap-suite` |
| False-positive controls | Laat SSL volledige antwoorden met rust? | `shadowseed run-false-positive-suite` |
| Benefit Suite | Wordt een antwoord beter door SSL-seeds toe te voegen? | `shadowseed run-benefit-suite` |
| Model Benefit Suite | Wordt hetzelfde model beter met SSL-guided rewrite? | `shadowseed run-model-benefit-suite` |
| Analysis | Hoe zien resultaten er grafisch en semantisch uit? | `shadowseed analyze-results` |

## Positieve Gap-Test Suite

Data:

```text
src/shadowseed/data/gap_test_suite_4_5.json
```

Meet:

- scenario score
- atomische hits
- promoted hits
- promoted seeds

## False-positive controls

Data:

```text
src/shadowseed/data/gap_test_suite_false_positive_4_5.json
```

Meet:

- candidate false positives
- promoted false positives
- false-positive rates

## Benefit Suite

Data:

```text
src/shadowseed/data/ssl45_benefit_suite.json
```

Meet:

- baseline gap coverage
- SSL gap coverage
- coverage delta
- unsupported additions

Dit is fase 1. Er wordt nog geen echt extern model aangeroepen.

## Model Benefit Suite

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

## Artifacts

GitHub Actions uploadt artifacts zoals:

```text
ssl45-gap-suite-results
ssl45-false-positive-results
ssl45-benefit-results
ssl45-model-benefit-results
ssl45-analysis-report
```

## Interpretatie

Een sterke uitkomst vereist minimaal:

- hogere gap coverage met SSL;
- geen stijging in unsupported additions;
- lage false-positive rate;
- hetzelfde model in baseline en SSL-conditie;
- geen conclusie alleen op basis van extra lengte.
