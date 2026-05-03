# Shadow Seed Learning 4.5

Welkom bij de Wiki voor **Shadow Seed Learning (SSL) 4.5**.

SSL 4.5 onderzoekt of een model beter kan antwoorden door ontbrekende structurele elementen te herkennen als **shadow seeds**. Een seed begint gewichtloos, wordt gevolgd via `trace`, en krijgt pas invloed na validatie via de Validation Gate.

## Begin hier

De snelste en duidelijkste ingang:

- [Dashboard](Dashboard)
- [Start hier](Start-Hier)

Deze pagina legt in gewone taal uit:

- wat SSL 4.5 is;
- wat een shadow seed is;
- waarom seeds eerst gewichtloos blijven;
- hoe vectorstores en SSOT erbij horen;
- welke tests er zijn;
- waar de resultaten staan;
- wat je wel en niet kunt concluderen.

## Hoofddossiers

- [Dashboard](Dashboard) — snelle status
- [Start hier](Start-Hier) — eenvoudige instap en leesroute
- [Eindconclusie SSL 4.5](Eindconclusie-SSL-4-5) — volledig dossier, printbaar
- [Tussentijdse rapportage SSL 4.5](Tussentijdse-Rapportage) — tussenstand
- [Visueel verhaal SSL 4.5](Visueel-Verhaal) — compacte uitleg met diagrammen
- [Waarom SSL niet naïef is](Waarom-SSL-niet-naief-is) — veiligheid, Gate en falsificatie

## Technische verdieping

- [Quick Start](Quick-Start)
- [Conceptueel overzicht](Conceptueel-Overzicht)
- [Architectuur](Architectuur)
- [Benchmarks](Benchmarks)
- [Vectorstore en gewichtloze seeds](Vectorstore-en-Gewichtloze-Seeds)
- [SSOT en documentvalidatie](SSOT-en-Documentvalidatie)
- [Fase 2: SLM-runs](SLM-Runs)
- [Blind review protocol](Blind-Review-Protocol)
- [Roadmap](Roadmap)

## Automatische resultaten

Deze pagina's worden deels of volledig door GitHub Actions bijgewerkt:

- [SSL 4.5 Analysis](SSL-45-Analysis)
- [SLM Model Benefit](SLM-Model-Benefit)
- [SLM First Conclusion](SLM-First-Conclusion)
- [Vectorstore Smoke](Vectorstore-Smoke)
- [SSOT Smoke](SSOT-Smoke)
- [SSOT Falsification](SSOT-Falsification)
- [Full Validation Sweep](Full-Validation-Sweep)
- [Backend Comparison](Backend-Comparison)
- [Retrieval-Comparison](Retrieval-Comparison)
- [Retrieval Model Comparison](Retrieval-Model-Comparison)
- [Retrieval Model HF](Retrieval-Model-HF)

## Belangrijkste principe

> Een seed bevat precies één gap.

SSL is geen prompttruc en geen modeltraining. Het is een laag die gevalideerde afwezigheden gebruikt als toetsbare navigatiesignalen.
