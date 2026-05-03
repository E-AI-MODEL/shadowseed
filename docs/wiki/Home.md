# Shadow Seed Learning 4.5

Welkom bij de Wiki voor **Shadow Seed Learning (SSL) 4.5**.

SSL 4.5 onderzoekt of een model beter kan antwoorden door ontbrekende structurele elementen te herkennen als **shadow seeds**. Een seed begint gewichtloos, wordt gevolgd via `trace`, en krijgt pas invloed na validatie via de Validation Gate.

## Hoofddossier

Start hier als je de Wiki als één volledig rapport wilt lezen of printen:

- [Tussentijdse rapportage SSL 4.5](Tussentijdse-Rapportage)

## Leesvolgorde

1. [Tussentijdse rapportage](Tussentijdse-Rapportage)
2. [Quick Start](Quick-Start)
3. [Conceptueel overzicht](Conceptueel-Overzicht)
4. [Architectuur](Architectuur)
5. [Benchmarks](Benchmarks)
6. [Fase 2: SLM-runs](SLM-Runs)
7. [Resultaten en analyse](Resultaten-en-Analyse)
8. [Blind review protocol](Blind-Review-Protocol)
9. [Roadmap](Roadmap)

## Automatische pagina's

Deze Wiki wordt deels automatisch bijgewerkt door GitHub Actions.

Automatisch gegenereerd:

- [SSL 4.5 Analysis](SSL-45-Analysis)
- [SLM Model Benefit](SLM-Model-Benefit)
- [SLM First Conclusion](SLM-First-Conclusion)

## Belangrijkste principe

> Een seed bevat precies één gap.

SSL is geen prompttruc en geen modeltraining. Het is een laag die gevalideerde afwezigheden gebruikt als toetsbare navigatiesignalen.
