# Open Review Workspace

Deze map is bedoeld voor de eerste echte open-set seedkwaliteitslaag.

## Doel

Beoordelen of SSL op onbekende teksten kleine, relevante, toetsbare en niet-triviale seeds produceert zonder vaste seedlijst.

## Verwachte inputvorm

- kleine batch onbekende teksten
- meerdere domeinen
- meerdere tekstvormen
- geen vooraf uitgeschreven expected seedlijst als primaire waarheid

## Verwachte artifacts

- `open_set_seed_output.json`
- `open_set_review_packets.json`
- `open_set_review_summary.json`
- `open_set_disagreements.json`

## Reviewkern

Iedere seed moet uiteindelijk beoordeeld kunnen worden op:

- atomiciteit
- relevantie
- toetsbaarheid
- niet-trivialiteit
- bruikbaarheid voor vervolgactie

## Grens

Deze map is geen nieuwe scenario-suite.

Het doel is juist de stap weg van:

- vaste scenario seeds

en naar:

- blind beoordeelbare seedkwaliteit in onbekende context
