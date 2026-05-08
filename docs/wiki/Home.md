# Shadow Seed Learning 4.5

Welkom bij de Wiki voor **Shadow Seed Learning (SSL) 4.5**.

SSL 4.5 onderzoekt of een model beter kan antwoorden door ontbrekende structurele elementen te herkennen als **shadow seeds**. Een seed begint gewichtloos, wordt gevolgd via `trace`, en krijgt pas invloed na validatie via de Validation Gate.

De wiki heeft twee functies tegelijk:

- snel toegang geven tot de laatste resultaten;
- uitleggen wat die resultaten wel en niet betekenen.

## Begin hier

De snelste ingang:

- [Dashboard](Dashboard)
- [Latest Test Results](Latest-Test-Results)
- [Benchmarks](Benchmarks)
- [Start hier](Start-Hier)

Gebruik deze volgorde als je snel overzicht wilt:

1. Dashboard voor de huidige status.
2. Latest Test Results voor de laatste gepubliceerde artifacts.
3. Benchmarks voor uitleg per run en per bewijssoort.
4. Start hier voor de inhoudelijke uitleg.

## Welke run doet wat?

| Naam in Actions | Gewone betekenis | Bewijssoort |
|---|---|---|
| 01 Codecheck | Werkt de Python-code? | regressie |
| 02 Gap Finder | Vindt SSL ontbrekende punten? | kleine benchmark |
| 03 Rustig blijven | Voegt SSL geen onzin toe? | regressie / beperkte ruiscontrole |
| 04 Antwoordwinst | Wordt een antwoord completer met SSL? | kleine benchmark |
| 05 Model smoke | Werkt de modelroute technisch? | technische smoke |
| 06 Blind test | Blijven labels verborgen tot scoring? | methodologische smoke |
| 07 Rapport | Vat de resultaten samen. | rapportage |
| 08 AbsenceBench rooktest | Werkt de lokale dataset-run? | technische smoke |
| 09 Herhalingstest | Wat gebeurt er bij meer SSL-rondes? | gevoeligheid / regressie |

## Hoofddossiers

- [Dashboard](Dashboard) - snelle status
- [Latest Test Results](Latest-Test-Results) - laatste gepubliceerde artifacts
- [Start hier](Start-Hier) - eenvoudige instap en leesroute
- [Eindconclusie SSL 4.5](Eindconclusie-SSL-4-5) - volledig dossier, printbaar
- [Tussentijdse rapportage SSL 4.5](Tussentijdse-Rapportage) - tussenstand
- [Visueel verhaal SSL 4.5](Visueel-Verhaal) - compacte uitleg met diagrammen
- [Waarom SSL niet naïef is](Waarom-SSL-niet-naief-is) - veiligheid, Gate en falsificatie

## Technische verdieping

- [Quick Start](Quick-Start)
- [Conceptueel overzicht](Conceptueel-Overzicht)
- [Architectuur](Architectuur)
- [Benchmarks](Benchmarks)
- [Blind Benchmark](Blind-Benchmark)
- [Vectorstore en gewichtloze seeds](Vectorstore-en-Gewichtloze-Seeds)
- [SSOT en documentvalidatie](SSOT-en-Documentvalidatie)
- [Fase 2: SLM-runs](SLM-Runs)
- [Blind review protocol](Blind-Review-Protocol)
- [Roadmap](Roadmap)

## Automatische resultaten

De centrale route is:

```text
Checks en benchmark-resultaten
  -> Publiceer testresultaten naar Wiki en Pages
  -> Wiki + Pages
```

De stap `07 Rapport` verzamelt de analyse-input conflictveilig uit artifacts. De originele artifactstructuur blijft traceerbaar, en de gepubliceerde snapshots verwijzen via een manifest terug naar de bronbestanden.

De belangrijkste automatische pagina's:

- [Latest Test Results](Latest-Test-Results)
- [SSL 4.5 Analysis](SSL-45-Analysis)
- [SSL 4.5 Analysis Summary JSON](SSL-45-Analysis-Summary)
- [Retrieval Model HF](Retrieval-Model-HF)

Oudere of specifieke pagina's kunnen nog bestaan voor losse experimenten, maar de laatste standaardresultaten staan onder `Latest Test Results`.

## Belangrijke grens

De standaardresultaten laten vooral zien dat de meetketen werkt en dat de huidige kleine benchmarklaag bruikbaar is.

Ze bewijzen niet automatisch:

- open-set seedkwaliteit;
- sterke adversarial Gate-robustheid;
- brede modelprestatie buiten de kleine suites;
- domeintransfer;
- modelinterne validatie.

Voor zulke claims zijn grotere suites, menselijke review en aparte evaluatielagen nodig.

## Belangrijkste principe

> Een seed bevat precies één gap.

SSL is geen prompttruc en geen modeltraining. Het is een laag die gevalideerde afwezigheden gebruikt als toetsbare navigatiesignalen.
