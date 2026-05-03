# Shadow Seed Learning 4.5

Welkom bij de Wiki voor **Shadow Seed Learning (SSL) 4.5**.

SSL 4.5 onderzoekt of een model beter kan antwoorden door ontbrekende structurele elementen te herkennen als **shadow seeds**. Een seed begint gewichtloos, wordt gevolgd via `trace`, en krijgt pas invloed na validatie via de Validation Gate.

## Hoofddossier

Start hier als je de Wiki als één volledig rapport wilt lezen of printen:

- [Tussentijdse rapportage SSL 4.5](Tussentijdse-Rapportage)

Lees daarna het visuele verhaal als compacte, geïllustreerde samenvatting:

- [Visueel verhaal SSL 4.5](Visueel-Verhaal)

## Leesvolgorde

1. [Tussentijdse rapportage](Tussentijdse-Rapportage)
2. [Visueel verhaal](Visueel-Verhaal)
3. [Quick Start](Quick-Start)
4. [Conceptueel overzicht](Conceptueel-Overzicht)
5. [Architectuur](Architectuur)
6. [Benchmarks](Benchmarks)
7. [Vectorstore en gewichtloze seeds](Vectorstore-en-Gewichtloze-Seeds)
8. [Fase 2: SLM-runs](SLM-Runs)
9. [Resultaten en analyse](Resultaten-en-Analyse)
10. [Blind review protocol](Blind-Review-Protocol)
11. [Roadmap](Roadmap)

## Automatische pagina's

Deze Wiki wordt deels automatisch bijgewerkt door GitHub Actions.

Automatisch gegenereerd:

- [SSL 4.5 Analysis](SSL-45-Analysis)
- [SLM Model Benefit](SLM-Model-Benefit)
- [SLM First Conclusion](SLM-First-Conclusion)
- [Vectorstore Smoke](Vectorstore-Smoke)

## Belangrijkste principe

> Een seed bevat precies één gap.

SSL is geen prompttruc en geen modeltraining. Het is een laag die gevalideerde afwezigheden gebruikt als toetsbare navigatiesignalen.
