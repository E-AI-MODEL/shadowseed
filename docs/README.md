# Documentatie

Deze map bevat de inhoudelijke en praktische documentatie voor Shadow Seed Learning 4.5.

## Leesvolgorde

1. [Framework](01_framework.md)
2. [Atomische seeds](02_atomic_seeds.md)
3. [Gap-Test Suite](03_gap_test_suite.md)
4. [Testplan fase 0-4](04_testplan_fase_0_4.md)
5. [Prompts](05_prompts.md)
6. [Handleiding voor beoordelaars](06_handleiding_beoordelaars.md)
7. [Reproduceerbaarheid](07_reproduceerbaarheid.md)
8. [Referenties](08_referenties.md)
9. [Experimentopzet](EXPERIMENT.md)

## Kernregel

> Een seed bevat precies één gap.

## Praktisch

- De canonieke dataset staat in `src/shadowseed/data/gap_test_suite_4_5.json`.
- De CLI staat in `src/shadowseed/cli.py`.
- De evaluator staat in `src/shadowseed/benchmark/ssl45_gap_suite.py`.
