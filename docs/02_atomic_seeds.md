# Atomische seeds

## 1. Hoofdregel

Een seed bevat precies één gap.

Dat maakt een seed toetsbaar. Een beoordelaar moet kunnen zeggen: deze seed klopt, klopt deels of klopt niet.

## 2. Eisen aan een seed

| Eis | Vraag |
|---|---|
| Eén gap | Staat er maar één ontbrekende relatie of randvoorwaarde in? |
| Specifiek | Is duidelijk waar de seed over gaat? |
| Toetsbaar | Kan een beoordelaar of bron dit controleren? |
| Relevant | Zou de seed het antwoord verbeteren? |
| Niet-triviaal | Verandert de seed het begrip, niet alleen een detail? |

## 3. Niet opslaan als seed

Sla dit niet op als seed:

- volledige analysekaders
- lijsten met meerdere ontbrekende onderdelen
- algemene opmerkingen zoals “meer nuance”
- categorieën zoals “economische context” zonder concrete relatie
- verzonnen of oncontroleerbare concepten
- stijlverbeteringen
- simpele details zoals jaartallen of extra voorbeelden

## 4. Voorbeelden

### Geschiedenis

Te breed:

> De tekst mist oorzaken, sociale gevolgen, koloniale verbanden en milieugevolgen.

Atomisch:

> Koloniaal kapitaal als financieringsbron voor Britse fabrieksinvesteringen.

Atomisch:

> Koloniale katoen als grondstof voor de Britse textielindustrie.

### Recht

Te breed:

> De internationale juridische context ontbreekt.

Atomisch:

> Rechtsbevoegdheid bij een geschil tussen een Nederlandse consument en een Amerikaanse webwinkel.

Atomisch:

> Toepasselijk recht bij een grensoverschrijdend consumentencontract.

### Software

Te breed:

> Security, privacy en schaalbaarheid ontbreken.

Atomisch:

> AVG-compliance bij verwerking van medische hartslagdata.

Atomisch:

> Rate-limiting op API's die gezondheidsdata verwerken.

## 5. Seed-normalisatie

Wanneer een model een brede detectie geeft, volgt een normalisatiestap.

Input:

> Voeg een volledig analysekader toe met aandacht voor oorzaken, chronologie, geografische verspreiding, arbeid, kapitaal, koloniale verbanden, ongelijkheid en milieugevolgen.

Output:

1. Oorzaken van de Industriële Revolutie buiten technische uitvindingen.
2. Chronologische overgang van vroege naar latere industrialisatie.
3. Geografische verspreiding van industrialisatie buiten Groot-Brittannië.
4. Arbeidsomstandigheden in vroege fabrieken.
5. Kapitaalvorming als voorwaarde voor fabrieksinvesteringen.
6. Koloniale verbanden als bron van kapitaal en grondstoffen.
7. Sociale ongelijkheid door fabrieksarbeid en urbanisatie.
8. Milieugevolgen van kolenverbruik en fabrieksgroei.

Daarna beoordeelt de test welke van deze seeds werkelijk de ground truth raakt.

## 6. Scoring van brede detecties

Een brede detectie krijgt maximaal score 1.

Score 2 is alleen mogelijk wanneer de output:

- één gap bevat
- de juiste structurele relatie benoemt
- niet alleen het domein noemt
- controleerbaar is

Voorbeeld:

| Output | Score | Reden |
|---|---:|---|
| Kolonialisme ontbreekt. | 1 | Relevante richting, maar te vaag. |
| Koloniaal kapitaal als financieringsbron voor Britse fabrieksinvesteringen. | 2 | Klein, specifiek en toetsbaar. |

## 7. Praktische heuristiek

Een seed is meestal te breed als hij:

- meer dan 18 woorden bevat
- meerdere komma's bevat
- “en” of “of” gebruikt om domeinen te stapelen
- begint met “volledig analysekader”
- woorden gebruikt als “context”, “perspectieven”, “factoren” zonder concrete relatie

Deze heuristiek is een filter, geen bewijs. Menselijke beoordeling blijft nodig.
