# Handleiding voor beoordelaars

## Doel

Je beoordeelt of een AI-systeem zinvolle kleine afwezigheden kan vinden in een antwoord. Zo'n afwezigheid heet in dit onderzoek een seed.

Je beoordeelt niet of het antwoord mooi geschreven is. Je beoordeelt of de gedetecteerde seed echt een kleine, relevante gap benoemt.

## Wat je krijgt

Per item krijg je:

- een inputtekst
- eventueel een AI-antwoord
- een gedetecteerde seed
- de ground truth seeds

## Hoofdscore

| Score | Betekenis |
|---:|---|
| 0 | Geen relevante gap |
| 1 | Relevante richting, maar te vaag of te breed |
| 2 | Kleine en structureel juiste gap |

Score 2 kan alleen als de seed atomisch is.

## Vijf dimensies

### 1. Atomiciteit

Vraag: bevat de seed precies één gap?

Score laag bij:

- lijsten
- meerdere domeinen in één zin
- volledige analysekaders

Score hoog bij:

- één concrete ontbrekende relatie
- één randvoorwaarde
- één procedureel punt

### 2. Specificiteit

Vraag: is de seed concreet?

Laag:

> Meer context ontbreekt.

Hoog:

> AVG-compliance bij verwerking van medische hartslagdata.

### 3. Relevantie

Vraag: zou deze seed het antwoord echt verbeteren?

Laag:

> Een los detail dat niet nodig is.

Hoog:

> Een structureel punt dat het begrip verandert.

### 4. Verifieerbaarheid

Vraag: kun je controleren of de seed klopt?

Laag:

> Een verzonnen term of oncontroleerbare claim.

Hoog:

> Een onderwerp dat via vakliteratuur, wetgeving, bronmateriaal of technische documentatie te controleren is.

### 5. Niet-trivialiteit

Vraag: is dit meer dan een detail?

Laag:

> Het antwoord noemt geen jaartallen.

Hoog:

> Het antwoord mist de rechtsbevoegdheid in een grensoverschrijdende casus.

## Voorbeelden

| Seed | Score | Reden |
|---|---:|---|
| Kolonialisme ontbreekt. | 1 | Richting klopt, maar te vaag. |
| Koloniaal kapitaal als financieringsbron voor Britse fabrieksinvesteringen. | 2 | Klein, specifiek en relevant. |
| Beveiliging en schaalbaarheid ontbreken. | 1 | Te breed, twee domeinen. |
| Rate-limiting op API's die gezondheidsdata verwerken. | 2 | Kleine technische gap. |

## Werkwijze

1. Lees de inputtekst.
2. Lees de gedetecteerde seed.
3. Vergelijk met de ground truth.
4. Geef score 0, 1 of 2.
5. Noteer kort waarom.

## Belangrijk

Eerlijke lage scores zijn nuttig. Als een seed breed, vaag of decoratief is, geef geen score 2.
