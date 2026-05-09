# Workflows

Dit is de kortste uitleg van wat de workflows in deze repo doen.

## 1. Checks en benchmark-resultaten

Dit is de **standaard workflow**.

Doet:

- unit tests
- gap suite
- false-positive suite
- benefit suite
- model smoke
- blind smoke
- adversarial Gate
- probe utility
- analyse-rapport
- AbsenceBench smoke
- herhalingstest

Gebruik deze workflow als je wilt weten of de repo mechanisch gezond is en of de standaard benchmarklaag nog klopt.

## 2. Publiceer testresultaten naar Wiki en Pages

Dit is de **publicatieworkflow**.

Doet:

- downloadt artifacts uit de laatste geslaagde standaardrun op `main`
- bouwt `results/latest` en een manifest
- maakt de centrale analysis-pagina opnieuw
- publiceert naar Wiki en GitHub Pages

Gebruik deze workflow als de resultaten wel bestaan, maar nog niet netjes op Wiki of Pages staan.

## 3. Publiceer alleen statische Wiki-pagina's

Dit is de **docs-only wiki-sync**.

Doet:

- kopieert alleen `docs/wiki/*.md` naar de GitHub Wiki

Gebruik deze workflow als je alleen wiki-tekst of navigatie hebt aangepast.

## 4. Full Validation Sweep

Dit is een **bredere handmatige sweep**.

Doet:

- standaard kernruns
- vectorstore- en SSOT-checks op meerdere backends
- retrieval en retrieval-model vergelijkingen
- compacte samenvatting naar de wiki

Gebruik deze workflow niet als dagelijkse check, maar voor bredere backend- en retrievaloriëntatie.

## 5. SSOT Falsification Run

Dit is een **gerichte veiligheidscheck**.

Doet:

- test of de SSOT-laag niet te makkelijk fout bewijs accepteert
- publiceert een losse falsification-pagina naar de wiki

Gebruik deze workflow als je aan SSOT-validatie, chunkverificatie of bronbetrouwbaarheid hebt gewerkt.

## Snelle beslisregel

| Vraag | Workflow |
|---|---|
| Is de repo standaard nog gezond? | `Checks en benchmark-resultaten` |
| Waarom zie ik nog geen nieuwe resultaten op wiki/pages? | `Publiceer testresultaten naar Wiki en Pages` |
| Ik heb alleen wiki-tekst aangepast | `Publiceer alleen statische Wiki-pagina's` |
| Ik wil bredere backend/retrieval-checks | `Full Validation Sweep` |
| Ik heb aan SSOT-validatie gewerkt | `SSOT Falsification Run` |
