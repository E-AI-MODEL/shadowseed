# Documentatie

Deze map bevat de inhoudelijke, technische en methodologische documentatie voor Shadow Seed Learning 4.5.

Niet elk document heeft dezelfde rol. Sommige pagina's beschrijven het mechanisme, andere leggen uit wat de repo vandaag werkelijk bewijst, en weer andere helpen je bij dagelijks gebruik van de benchmarks en resultaten.

## Start hier

Als je de repo nog niet kent, lees dan in deze volgorde:

1. [Repo-overzicht](ARCHITECTURE_MAP.md)
2. [Framework](01_framework.md)
3. [Huidige status](research/current-status.md)
4. [Scenario-onafhankelijk roadmap](research/scenario-independence-roadmap.md)
5. [Evaluatiematrix](research/evaluation-matrix.md)

Deze vijf documenten geven samen antwoord op:

- wat SSL 4.5 inhoudelijk is;
- hoe de repo is opgebouwd;
- wat de standaardruns vandaag echt aantonen;
- waar de grootste validatiegaten nog zitten.

## Twee leesroutes

## 1. Inhoud en bewijs

Gebruik deze route als je wilt begrijpen wat SSL claimt en hoe sterk die claim vandaag is afgedekt.

1. [Framework](01_framework.md)
2. [Atomische seeds](02_atomic_seeds.md)
3. [Gap-Test Suite](03_gap_test_suite.md)
4. [Testplan fase 0-4](04_testplan_fase_0_4.md)
5. [Handleiding voor beoordelaars](06_handleiding_beoordelaars.md)
6. [Reproduceerbaarheid](07_reproduceerbaarheid.md)
7. [Referenties](08_referenties.md)
8. [Experimentopzet](EXPERIMENT.md)

## 2. Dagelijks gebruik

Gebruik deze route als je de repo wilt draaien, resultaten wilt begrijpen of workflows wilt volgen.

1. [Repo-overzicht](ARCHITECTURE_MAP.md)
2. [Benchmarks in de Wiki](wiki/Benchmarks.md)
3. [Blind Benchmark](wiki/Blind-Benchmark.md)
4. [Resultaten](results.md)

## Onderzoeksstatus

De research-documenten hebben ieder een andere functie:

- [Huidige status](research/current-status.md): wat staat er vandaag echt?
- [Scenario-onafhankelijk roadmap](research/scenario-independence-roadmap.md): waar moet de repo inhoudelijk heen?
- [Evaluatiematrix](research/evaluation-matrix.md): welke evaluatielagen dragen welke claim?

Samen voorkomen ze dat regressies, kleine benchmarkresultaten en algemene SSL-claims door elkaar gaan lopen.

## Leeswijzer voor techniek

| Vraag | Waar kijken? |
|---|---|
| Welke onderdelen heeft de repo? | `ARCHITECTURE_MAP.md` |
| Welke CLI-commando's bestaan? | `src/shadowseed/cli.py` |
| Welke tests draaien standaard? | `.github/workflows/tests.yml` |
| Waar worden resultaten gepubliceerd? | `.github/workflows/publish-test-results.yml` |
| Hoe werkt de analyse? | `src/shadowseed/analysis/ssl45_result_analyzer.py` |
| Hoe werkt het dashboard? | `site/` |

## Kernregels

> Een seed bevat precies één gap.

> Wat mechanisch werkt is nog niet automatisch wetenschappelijk bewezen.

Deze twee regels zijn samen de kortste samenvatting van de repo.

## Praktisch

- Publieke benchmarkdata staat in `src/shadowseed/data/`.
- Private blinde labels horen in `benchmarks/private/` en worden niet gecommit.
- De benchmarkrunners staan in `src/shadowseed/benchmark/`.
- De CLI staat in `src/shadowseed/cli.py`.
- De laatste gepubliceerde resultaten verschijnen via GitHub Actions in Wiki, Pages en het workflow-artifact `published-latest-results-snapshot`.
- De standaard CI is vooral regressie- en meetketencontrole; grotere claims vragen extra evaluatielagen.
