# Resultaten

Deze pagina beschrijft de actuele output van de SSL 4.5 Gap-Test Suite.

## Run

| Veld | Waarde |
|---|---|
| Suite | SSL 4.5 Gap-Test Suite |
| Versie | 4.5 |
| Scenario's | 3 |
| Outputbestand | `ssl45_gap_suite.json` |
| Run-tijd in artifact | 2026-05-03T10:30:24 |

## Samenvatting

| Metric | Waarde |
|---|---:|
| Mean scenario score | 2.00 |
| Atomische hits | 10 |
| Promoted hits | 10 |

De score gebruikt de schaal uit de Gap-Test Suite:

| Score | Betekenis |
|---:|---|
| 0 | geen relevante gap gevonden |
| 1 | richting klopt, maar output is te vaag of te breed |
| 2 | atomische en structureel juiste gap gevonden |

## Per scenario

| Scenario | Titel | Score | Atomische hits | Promoted hits | Interpretatie |
|---|---|---:|---:|---:|---|
| A | Industriële Revolutie | 2 | 2 | 2 | Werkt. De detector vindt twee atomische koloniale/economische gaps. |
| B | Grensoverschrijdende juridische casus | 2 | 4 | 4 | Werkt. De detector vindt nu rechtsbevoegdheid, toepasselijk recht, afdwingbaarheid en forumkeuze. |
| C | Software Architectuur | 2 | 4 | 4 | Werkt. De detector vindt privacy-, security- en API-gerelateerde gaps. |

## Gepromoveerde seeds

### Scenario A

- Koloniaal kapitaal als financieringsbron voor Britse fabrieksinvesteringen.
- Goedkope koloniale grondstoffen als voorwaarde voor schaalvergroting van productie.

### Scenario B

- Rechtsbevoegdheid bij een geschil tussen een Nederlandse consument en een Amerikaanse webwinkel.
- Toepasselijk recht bij een grensoverschrijdend consumentencontract.
- Afdwingbaarheid van EU-consumentenrecht tegenover een niet-EU retailer.
- Forumkeuzebeding in internationale online koopvoorwaarden.

### Scenario C

- AVG-compliance bij verwerking van medische hartslagdata.
- Authenticatiestrategie voor toegang tot gezondheidsdata.
- Encryptie van medische data in rust en tijdens transport.
- Rate-limiting op API's die gezondheidsdata verwerken.

## Interpretatie

De huidige run laat zien dat de pipeline vier dingen goed doet:

1. atomische detectie in alle drie scenario's;
2. correcte scheiding tussen detectie en promotie;
3. promotie via de Validation Gate zodra de Gate-condities zijn gehaald;
4. herkenning van juridische procedurele gaps in een grensoverschrijdende consumentencontext.

Alle promoted seeds hebben in de artifact-output:

```text
trace = 3.0
weight = 0.6000000000000001
occurrence_count = 3
evidence_count = 2
status = PROMOTED
```

Dat past bij SSL 4.5: seeds beginnen gewichtloos, worden drie keer herkend, krijgen externe evidence en stijgen pas daarna boven de promotiedrempel.

## Beperking

Deze run gebruikt de gratis deterministische detector. De score toont dat de huidige suite volledig geraakt wordt, maar bewijst nog niet dat SSL 4.5 algemeen sterk is buiten deze drie scenario's. De volgende wetenschappelijke stap is uitbreiding met meer domeinen, meer negatieve controles en menselijke beoordeling via de templates.

## Volgende stap

- Matrix-runs vergelijken voor turns `1`, `2`, `3`, `5` en `8`.
- False-positive scenario's toevoegen.
- Beoordelingsformulier invullen met menselijke scores.
- Daarna pas claims in paper of README sterker maken.
