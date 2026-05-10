# Evaluation Layer Map

Deze map is het doelvak voor de SSL-bewijslagen uit de 4.6-koers.

De huidige repo draait al een sterke regressie- en kleine benchmarklaag in `src/shadowseed/benchmark/`. Die laag blijft bestaan. Deze map maakt zichtbaar welke bewijssoort eigenaar is van nieuwe of bestaande evaluatielogica.

## Lagen

| Map | Doel | Huidige status |
|---|---|---|
| `regression/` | Mechaniek, smoke en kleine vaste benchmarks bewaken | code leeft voorlopig vooral in `benchmark/` |
| `open_review/` | Open-set seedkwaliteit blind beoordelen zonder vaste seedlijst | handmatige route bestaat, menselijke review blijft nodig |
| `adversarial/` | Validation Gate vergelijken met zwakkere promotieregels | benchmark en casebook bestaan |
| `behavioral/` | Probe utility en vervolgstapkwaliteit meten | eerste benchmark bestaat, verdere verdieping volgt |
| `transfer/` | Domeintransfer buiten bekende benchmarkdomeinen testen | gepland |

## Werkregel

Nieuwe evaluatielogica moet expliciet aan één laag worden gekoppeld. Code mag tijdelijk nog in `src/shadowseed/benchmark/` blijven zolang gedrag en imports stabiel blijven.

## Belangrijke grens

Deze map vervangt `src/shadowseed/benchmark/` nog niet.

De hoofdregel blijft:

- `benchmark/` bewaakt de bestaande regressieruggengraat en kleine benchmarkroutes;
- `evaluation/` wordt de plek waar bewijssoort, claimgrens en latere migratie zichtbaar zijn;
- verplaatsen van echte Python-modules gebeurt pas in aparte PR's met tests.

## Geen gedragswijziging

Deze laagindeling verandert geen CLI-command, workflow, benchmarkoutput of publieke claim. Het is alleen de eerste ordeningsstap zodat latere refactors kleiner en veiliger blijven.
