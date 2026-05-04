# Documentatie

Deze map bevat de inhoudelijke en praktische documentatie voor Shadow Seed Learning 4.5.

## Start hier

Begin met:

1. [Repo-overzicht](ARCHITECTURE_MAP.md)
2. [Framework](01_framework.md)
3. [Benchmarks in de Wiki](wiki/Benchmarks.md)
4. [Blind Benchmark](wiki/Blind-Benchmark.md)
5. [Resultaten](results.md)

## Leesvolgorde voor inhoud

1. [Framework](01_framework.md)
2. [Atomische seeds](02_atomic_seeds.md)
3. [Gap-Test Suite](03_gap_test_suite.md)
4. [Testplan fase 0-4](04_testplan_fase_0_4.md)
5. [Prompts](05_prompts.md)
6. [Handleiding voor beoordelaars](06_handleiding_beoordelaars.md)
7. [Reproduceerbaarheid](07_reproduceerbaarheid.md)
8. [Referenties](08_referenties.md)
9. [Experimentopzet](EXPERIMENT.md)

## Leesvolgorde voor techniek

| Vraag | Waar kijken? |
|---|---|
| Welke onderdelen heeft de repo? | `ARCHITECTURE_MAP.md` |
| Welke CLI-commando's bestaan? | `src/shadowseed/cli.py` |
| Welke tests draaien standaard? | `.github/workflows/tests.yml` |
| Waar worden resultaten gepubliceerd? | `.github/workflows/publish-test-results.yml` |
| Hoe werkt het dashboard? | `site/` |
| Hoe werkt de analyse? | `src/shadowseed/analysis/ssl45_result_analyzer.py` |

## Kernregel

> Een seed bevat precies één gap.

## Praktisch

- Publieke benchmarkdata staat in `src/shadowseed/data/`.
- Private blinde labels horen in `benchmarks/private/` en worden niet gecommit.
- De CLI staat in `src/shadowseed/cli.py`.
- De benchmarkrunners staan in `src/shadowseed/benchmark/`.
- De laatste gepubliceerde resultaten komen via GitHub Actions in `results/latest/` en `results/artifacts/`.
