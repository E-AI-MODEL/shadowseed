# Evaluation Layer Map

Deze map is het doelvak voor de volgende SSL-bewijs-lagen.

De huidige repo draait al een sterke regressie- en kleine benchmarklaag in `src/shadowseed/benchmark/`.
De volgende fase vraagt niet om die laag weg te gooien, maar om duidelijker te scheiden wat regressie is en wat de hoofdclaim later moet gaan dragen.

## Bedoelde lagen

- `open_review`
  Doel: open-set seedkwaliteit blind beoordelen zonder vaste seedlijst.
- `adversarial`
  Doel: de huidige Validation Gate vergelijken met zwakkere promotieregels.
- `behavioral`
  Doel: probe utility en vervolgstapkwaliteit meten.
- `transfer`
  Doel: domeintransfer buiten de bekende benchmarkdomeinen testen.

## Werkregel

Nieuwe evaluatielogica die niet puur regressie of kleine benchmark is, hoort vanaf nu conceptueel in deze laag thuis, ook als de code nog tijdelijk elders leeft.

## Belangrijke grens

Deze map is geen vervanging van `src/shadowseed/benchmark/`.

De hoofdregel blijft:

- `benchmark/` bewaakt de bestaande regressieruggengraat
- `evaluation/` wordt de plek voor zwaardere bewijs-lagen
