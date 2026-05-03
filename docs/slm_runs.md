# SLM-runs

Deze pagina beschrijft hoe je een echte kleine taalmodel-run uitvoert voor SSL 4.5.

## Doel

De SLM-run vergelijkt hetzelfde model in twee condities:

```text
baseline: vraag direct beantwoorden
SSL: baseline-antwoord herzien met gevalideerde SSL-seeds
```

Het model blijft hetzelfde. Alleen SSL-guidance verandert.

## Handmatig starten in GitHub Actions

Ga naar:

```text
Actions → SLM Model Benefit Run → Run workflow
```

Vul in:

| Veld | Voorbeeld |
|---|---|
| `model_id` | `TinyLlama/TinyLlama-1.1B-Chat-v1.0` |
| `turns` | `3` |
| `max_new_tokens` | `220` |

Klik daarna op **Run workflow**.

## Output artifacts

Na afloop krijg je:

```text
ssl45-slm-model-benefit-results
ssl45-slm-analysis-report
```

Het eerste artifact bevat de ruwe modelvergelijking:

```text
results/ssl45_model_benefit_suite.json
```

Het tweede artifact bevat:

```text
analysis_report.md
analysis_summary.json
coverage.svg
false_positive.svg
```

## Belangrijke metrics

| Metric | Betekenis |
|---|---|
| `baseline_mean_gap_coverage` | dekking zonder SSL |
| `ssl_mean_gap_coverage` | dekking met SSL-guided rewrite |
| `coverage_delta` | verbetering door SSL |
| `mean_answer_length_delta_words` | hoeveel langer SSL-antwoorden zijn |
| `coverage_delta_per_100_added_words` | verbetering gecorrigeerd voor extra lengte |
| `unsupported_ssl_addition_rate` | aandeel unsupported SSL-toevoegingen |

## Eerlijke interpretatie

Een goede SLM-run toont niet alleen dat SSL-antwoorden langer zijn.

Een goede run toont:

```text
hogere gap coverage
zonder hogere unsupported addition rate
bij hetzelfde model
```

## Aanbevolen eerste model

```text
TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

Dit model is klein genoeg om als eerste gratis test te proberen. De run kan traag zijn op CPU.

## Let op

GitHub-hosted runners hebben beperkte CPU, RAM en tijd. Als een model-run faalt door geheugen of timeout, gebruik dan lokaal dezelfde CLI:

```bash
pip install -e ".[models]"

shadowseed run-model-benefit-suite \
  --backend hf-transformers \
  --model-id TinyLlama/TinyLlama-1.1B-Chat-v1.0 \
  --turns 3 \
  --max-new-tokens 220

shadowseed analyze-results
```
