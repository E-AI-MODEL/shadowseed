# Resultaten

Deze pagina beschrijft de actuele output van de SSL 4.5 Gap-Test Suite.

## Run

| Veld | Waarde |
|---|---|
| Suite | SSL 4.5 Gap-Test Suite |
| Versie | 4.5 |
| Scenario's | 3 |
| Outputbestand | `ssl45_gap_suite.json` |

## Samenvatting

| Metric | Waarde |
|---|---:|
| Mean scenario score | 1.33 |
| Atomische hits | 6 |
| Promoted hits | 6 |

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
| B | Grensoverschrijdende juridische casus | 0 | 0 | 0 | Faalt. De huidige gratis detector vindt geen juridische seeds. |
| C | Software Architectuur | 2 | 4 | 4 | Werkt sterk. De detector vindt privacy-, security- en API-gerelateerde gaps. |

## Gepromoveerde seeds

### Scenario A

- Koloniaal kapitaal als financieringsbron voor Britse fabrieksinvesteringen.
- Goedkope koloniale grondstoffen als voorwaarde voor schaalvergroting van productie.

### Scenario B

Geen promoted seeds.

### Scenario C

- AVG-compliance bij verwerking van medische hartslagdata.
- Authenticatiestrategie voor toegang tot gezondheidsdata.
- Encryptie van medische data in rust en tijdens transport.
- Rate-limiting op API's die gezondheidsdata verwerken.

## Interpretatie

De huidige run laat zien dat de pipeline drie dingen goed doet:

1. atomische detectie in scenario A en C;
2. correcte scheiding tussen detectie en promotie;
3. promotie via de Validation Gate zodra de Gate-condities zijn gehaald.

De run laat ook een duidelijke zwakte zien:

- scenario B wordt niet geraakt door de huidige gratis detector.

Dat betekent dat het huidige resultaat geen bewijs is dat SSL 4.5 algemeen sterk is. Het bewijst wel dat de implementatie de ontworpen lifecycle uitvoert en dat de testset echte zwakke plekken zichtbaar maakt.

## Volgende stap

De eerstvolgende inhoudelijke verbetering is scenario B. De juridische detector moet ten minste deze twee seeds kunnen raken:

- Rechtsbevoegdheid bij een geschil tussen een Nederlandse consument en een Amerikaanse webwinkel.
- Toepasselijk recht bij een grensoverschrijdend consumentencontract.

Daarna moet dezelfde run opnieuw worden gedraaid en vergeleken met deze baseline.
