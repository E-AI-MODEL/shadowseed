# Blind Benchmark

De blinde benchmark test of Shadow Seed Learning ontbrekende, toetsbare relaties vindt zonder de evaluator-labels vooraf te kennen.

## Opzet

Er zijn twee soorten input:

```text
src/shadowseed/data/blind_suite_public.json
benchmarks/private/blind_suite_labels.json
```

Het publieke bestand bevat alleen scenario's. Het private bestand bevat `expected_gaps` en `must_not_add` en wordt alleen gebruikt tijdens scoring.

## Waarom gescheiden?

De detector mag alleen publieke scenario's lezen. Labels worden pas aan het einde gebruikt door de scorer. Daardoor meet de benchmark niet of de code het antwoordbestand kent, maar of de SSL-run ontbrekende relaties weet te raken.

## Commando

```bash
shadowseed run-blind-benchmark \
  --input src/shadowseed/data/blind_suite_public.json \
  --labels benchmarks/private/blind_suite_labels.json \
  --output results/blind_benchmark.json \
  --turns 3
```

## Scoring

De output bevat onder meer:

- `mean_baseline_gap_coverage`
- `mean_ssl_gap_coverage`
- `mean_coverage_delta`
- `total_unsupported_additions`
- `total_false_positive_count`
- `mean_net_benefit`

Een sterke run heeft hogere SSL coverage, weinig false positives en geen stijging in unsupported additions.

## Privélabels

`benchmarks/private/` staat in `.gitignore`. Gebruik deze map voor lokale of CI-labels. Commit echte labels niet in de repo.

De smoke workflow maakt een tijdelijk labelbestand aan tijdens GitHub Actions. Dat bestand is bedoeld als technische check, niet als echte blinde benchmark.

## Eerste onderzoeksrun

Een serieuze eerste run kan bestaan uit:

- 20 scenario's
- 5 domeinen
- 4 scenario's per domein
- 5 negatieve controles
- 3 tot 6 verborgen expected gaps per scenario

Gebruik daarna menselijke beoordeling om de automatische scores te controleren.
