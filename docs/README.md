# Documentatie

Deze map bevat nu drie verschillende documentrollen die bewust uit elkaar worden gehouden.

## 1. Canonieke bron

Begin voor theorie en doelbeeld hier:

1. [Canonieke bron: SSL 4.6](00_shadow_seed_learning_4_6.md)

Dit document is leidend voor:

- de inhoudelijke definitie van SSL;
- de gewenste evaluatiekoers;
- de richting waarin de repo zich moet ontwikkelen.

Praktische regel:

> als afgeleide docs inhoudelijk botsen met `00_shadow_seed_learning_4_6.md`, dan gaat `00_` voor op theorie en doelbeeld.

## 2. Afgeleide werkdocumenten

Deze documenten zijn afgeleid van de canonieke bron en helpen bij uitleg, benchmarkgebruik en dagelijkse oriëntatie.

1. [Framework](01_framework.md)
2. [Atomische seeds](02_atomic_seeds.md)
3. [Gap-Test Suite](03_gap_test_suite.md)
4. [Testplan fase 0-4](04_testplan_fase_0_4.md)
5. [Handleiding voor beoordelaars](06_handleiding_beoordelaars.md)
6. [Reproduceerbaarheid](07_reproduceerbaarheid.md)
7. [Referenties](08_referenties.md)
8. [CLI command map](CLI_COMMAND_MAP.md)
9. [Repo-overzicht](ARCHITECTURE_MAP.md)
10. [Resultaten](results.md)

Deze documenten zijn bedoeld om delen van het systeem sneller te kunnen lezen zonder telkens de volledige bron te hoeven openen.

## 3. Research- en statusdocumenten

Deze documenten zijn leidend voor de vraag wat de repo vandaag werkelijk bewijst en waar ze inhoudelijk heen wil.

1. [Huidige status](research/current-status.md)
2. [Scenario-onafhankelijk roadmap](research/scenario-independence-roadmap.md)
3. [Evaluatiematrix](research/evaluation-matrix.md)
4. [Open-set en adversarial plan](research/open-set-adversarial-plan.md)

Praktische regel:

> `00_` vertelt wat SSL inhoudelijk wil zijn.
>
> de research-docs vertellen wat vandaag al staat en welke bewijslaag nog gebouwd moet worden.

## Aanbevolen leesroutes

### Route A — Volledige inhoud en doelbeeld

Lees in deze volgorde:

1. [Canonieke bron: SSL 4.6](00_shadow_seed_learning_4_6.md)
2. [Huidige status](research/current-status.md)
3. [Scenario-onafhankelijk roadmap](research/scenario-independence-roadmap.md)
4. [Evaluatiematrix](research/evaluation-matrix.md)

Gebruik deze route als je wilt begrijpen:

- wat SSL inhoudelijk claimt;
- wat de repo vandaag werkelijk aantoont;
- hoe de hoofdclaim moet verschuiven naar sterkere evaluatielagen.

### Route B — Dagelijks repo-gebruik

Lees in deze volgorde:

1. [Repo-overzicht](ARCHITECTURE_MAP.md)
2. [CLI command map](CLI_COMMAND_MAP.md)
3. [Benchmarks in de Wiki](wiki/Benchmarks.md)
4. [Blind Benchmark](wiki/Blind-Benchmark.md)
5. [Resultaten](results.md)

Gebruik deze route als je vooral wilt draaien, vergelijken, publiceren of benchmarkoutput interpreteren.

## Leeswijzer voor waarheidstype

| Vraag | Leidende bron |
|---|---|
| Wat is SSL inhoudelijk en waar moet het heen? | `00_shadow_seed_learning_4_6.md` |
| Wat bewijst de repo vandaag echt? | `research/current-status.md` |
| Welke evaluatielagen moeten de hoofdclaim gaan dragen? | `research/evaluation-matrix.md` |
| Hoe migreert de repo weg van scenario-afhankelijkheid? | `research/scenario-independence-roadmap.md` |
| Welke onderdelen heeft de repo nu? | `ARCHITECTURE_MAP.md` |
| Welke commands en workflows horen bij welke laag? | `CLI_COMMAND_MAP.md` en `.github/workflows/` |

## Kernregels

> Een seed bevat precies één gap.

> Wat mechanisch werkt is nog niet automatisch wetenschappelijk bewezen.

> Regressie, kleine benchmarkvalidatie en hoofdclaim mogen niet door elkaar lopen.

## Praktisch

- Publieke benchmarkdata staat in `src/shadowseed/data/`.
- Private blinde labels horen in `benchmarks/private/` en worden niet gecommit.
- De benchmarkrunners staan in `src/shadowseed/benchmark/`.
- De CLI staat in `src/shadowseed/cli.py`.
- De standaard CI bewaakt vooral regressie en meetketenstabiliteit.
- De volgende inhoudelijke winst moet vooral komen uit open-set review, adversarial Gate-evaluatie, probe utility en domeintransfer.
