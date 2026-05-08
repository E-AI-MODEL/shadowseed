# Shadow Seed Learning 4.5

Welkom bij de Wiki voor **Shadow Seed Learning (SSL) 4.5**.

SSL 4.5 onderzoekt of een model beter kan antwoorden door ontbrekende structurele elementen te herkennen als **shadow seeds**. Een seed begint gewichtloos, wordt gevolgd via `trace`, en krijgt pas invloed na validatie via de Validation Gate.

De wiki heeft twee functies tegelijk:

- snel toegang geven tot de laatste resultaten;
- uitleggen wat die resultaten wel en niet betekenen.

## Begin hier

De meest stabiele ingangen zijn nu:

- [Latest Test Results](Latest-Test-Results)
- [SSL 4.5 Analysis](SSL-45-Analysis)
- [Dashboard](Dashboard)
- [Benchmarks](Benchmarks)
- [GitHub Pages dashboard](https://e-ai-model.github.io/shadowseed/)

Gebruik deze volgorde als je snel overzicht wilt:

1. Latest Test Results voor de laatste gepubliceerde artifacts.
2. SSL 4.5 Analysis voor de samengevatte uitkomst.
3. Dashboard voor de bredere handmatige checks.
4. Benchmarks voor uitleg per run en per bewijssoort.

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

## Stabiele hoofdpagina's

- [Latest Test Results](Latest-Test-Results) - ingang naar de laatste standaardpublicatie
- [SSL 4.5 Analysis](SSL-45-Analysis) - centrale analysepagina
- [Dashboard](Dashboard) - bredere status over handmatige en aanvullende checks
- [Start hier](Start-Hier) - eenvoudige instap en leesroute
- [Benchmarks](Benchmarks) - uitleg per suite en bewijssoort

## Aanvullende technische checks

- [SSOT Falsification](SSOT-Falsification)
- [Retrieval Model HF](Retrieval-Model-HF)
- [Full Validation Sweep](Full-Validation-Sweep)
- [Blind Benchmark](Blind-Benchmark)
- [Architectuur](Architectuur)
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
