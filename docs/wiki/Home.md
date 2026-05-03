# Shadow Seed Learning 4.5

Welkom bij de Wiki voor **Shadow Seed Learning (SSL) 4.5**.

SSL 4.5 onderzoekt of een model beter kan antwoorden door ontbrekende structurele elementen te herkennen als **shadow seeds**. Een seed begint gewichtloos, wordt gevolgd via `trace`, en krijgt pas invloed na validatie via de Validation Gate.

## Leesvolgorde

1. [Quick Start](Quick-Start)
2. [Conceptueel overzicht](Conceptueel-Overzicht)
3. [Architectuur](Architectuur)
4. [Benchmarks](Benchmarks)
5. [Fase 2: SLM-runs](SLM-Runs)
6. [Resultaten en analyse](Resultaten-en-Analyse)
7. [Blind review protocol](Blind-Review-Protocol)
8. [Roadmap](Roadmap)

## Automatische pagina's

Deze Wiki wordt deels automatisch bijgewerkt door GitHub Actions.

Automatisch gegenereerd:

- [SSL 4.5 Analysis](SSL-45-Analysis)
- [SLM Model Benefit](SLM-Model-Benefit)

## Belangrijkste principe

> Een seed bevat precies één gap.

SSL is geen prompttruc en geen modeltraining. Het is een laag die gevalideerde afwezigheden gebruikt als toetsbare navigatiesignalen.
