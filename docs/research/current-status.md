# Huidige Status van SSL-validatie

## Doel van dit document

Dit document maakt expliciet wat de repository vandaag werkelijk aantoont, wat slechts gedeeltelijk is afgedekt, en wat nog gepland of conceptueel is.

De kernregel is eenvoudig:

> wat mechanisch werkt is nog niet automatisch wetenschappelijk bewezen.

Dit document scheidt daarom vier dingen:

- wat in code en workflows aantoonbaar aanwezig is;
- wat als redelijke tussenstap geldt;
- wat nog niet sluitend is gevalideerd;
- wat nog onderzoekswerk is.

## Samenvatting

De repo staat er sterk voor als benchmark-harness voor SSL-mechaniek. De kernlogica rond atomische seeds, `trace`, `weight`, Validation Gate, blinde labelscheiding, retrieval-smokes en rapportage is aanwezig en functioneel.

De repo staat er nog niet sterk genoeg voor als volledig bewijs van het hele SSL 4.5 onderzoeksprogramma. Vooral fase 1, fase 2, fase 3 en fase 4 zijn nog niet volledig afgedekt zoals de documentatie en specificatie ze formuleren.

Korte totaalscore per laag:

- mechanische regressie: sterk
- kleine benchmarkvalidatie: bruikbaar
- open-world validatie: zwak of afwezig
- gedragsvalidatie van probes: beperkt
- modelinterne validatie: afwezig

## Statusoverzicht per fase

| Fase | Status | Korte duiding |
|---|---|---|
| Fase 0: detectie | Partially implemented | Goede kleine benchmarklaag, maar nog niet alle beloofde metrics en nog niet open-world |
| Fase 1: multi-turn state | Partially implemented | Antwoordwinst is meetbaar, maar de volledige conditievergelijking uit het testplan ontbreekt |
| Fase 2: Validation Gate en probes | Partially implemented | Gate-mechaniek bestaat, maar de evaluatie is nog te vriendelijk en probekwaliteit wordt nog beperkt gemeten |
| Fase 3: constellations | Planned / infrastructural | De bouwstenen bestaan, maar er is nog geen echte constellation-benchmark |
| Fase 4: modelinterne test | Planned | Geen operationele evaluatielaag aanwezig |

## Wat de repo vandaag hard aantoont

### 1. De minimale SSL-definitie is technisch aanwezig

De repo toont overtuigend aan dat de volgende mechanische kern bestaat:

- een seed moet atomisch zijn;
- brede seeds kunnen worden geweigerd;
- `trace` en `weight` zijn formeel gescheiden;
- `weight` start op `0.0`;
- promotie loopt via een Validation Gate;
- promoted seeds kunnen vervolglogica sturen.

Dat is belangrijk, omdat dit het verschil markeert tussen een los benchmarkidee en een reproduceerbare kernarchitectuur.

### 2. Er is een bruikbare regressielaag rond scenario-gedreven detectie

De repo heeft een kleine maar nette regressielaag:

- Gap-Test Suite;
- false-positive suite;
- benefit-suite;
- blind benchmark smoke;
- retrieval- en SSOT-smokes.

Deze laag is goed genoeg om regressies snel zichtbaar te maken en om de kernlogica van SSL stabiel te houden tijdens refactors.

### 3. Blinde labelscheiding is serieus genomen

De repo doet meer dan alleen scores uitrekenen. Ze bewaakt ook dat private labels niet in de detectielaag terechtkomen. Dat is methodologisch een sterk signaal.

### 4. Reproduceerbare, goedkope CI-runs zijn bewust ontworpen

De fixture-backends en deterministische paden maken de repo snel, goedkoop en redelijk stabiel. Voor engineeringkwaliteit is dat een pluspunt.

## Wat gedeeltelijk staat, maar nog geen hard bewijs is

## Fase 0: detectie

### Wat staat

- een vaste Gap-Test Suite met drie scenario's;
- score 0, 1, 2;
- atomische seedregels;
- samenvattende metrics zoals scenario score en atomische hits.

### Wat nog ontbreekt ten opzichte van de docs

- expliciete precision;
- expliciete recall;
- expliciete F1 of `ΔF1` als primaire metric;
- overtuigend bewijs buiten de kleine vaste suite;
- loskoppeling van domein-priors in de detectielaag.

### Statusoordeel

Goed als kleine benchmark. Nog niet volledig als algemene detectievalidatie.

## Fase 1: multi-turn state

### Wat staat

- benefit-suite voor antwoordverbetering;
- model benefit-suite met fixture en optionele `hf-transformers` route;
- gap coverage en unsupported additions;
- blind review items voor menselijke vergelijking van antwoorden.

### Wat nog ontbreekt ten opzichte van de docs

- de volledige A/B/C-opzet uit het testplan:
  - geen state;
  - ruwe context;
  - SSL-state;
- expliciete metric voor turn-to-detection;
- expliciete metric voor duplicate seeds;
- bewijs dat SSL-state compacter of scherper werkt dan ruwe context.

### Statusoordeel

Veelbelovend, maar nog geen sluitende fase-1-validatie.

## Fase 2: Validation Gate en probes

### Wat staat

- formele Validation Gate;
- falsificatie- en contradiction-mechaniek;
- SSOT-smoke die laat zien dat externe evidence promotie kan ondersteunen;
- false-positive suite;
- retrieval- en modelgerelateerde evaluatiepaden.

### Wat nog ontbreekt ten opzichte van de docs

- een harde vergelijking tussen de huidige Gate en zwakkere promotieregels;
- echte adversarial false-positive evaluatie;
- zelfstandige meting van Socratische probekwaliteit;
- zelfstandige meting van Retrieval Probe-informatiewinst;
- zelfstandige meting van dialectische kwaliteit als falsificatiemechaniek.

### Belangrijke methodologische beperking

De huidige false-positive suite laat promoted false positives feitelijk op nul eindigen zonder de Gate echt zwaar te belasten. Dat maakt de claim over ruisfiltering zwakker dan de documentatie soms suggereert.

### Statusoordeel

Mechaniek aanwezig, maar bewijs nog te vriendelijk en te smal.

## Fase 3: constellations

### Wat staat

- de manager kan constellations vormen uit promoted seeds;
- retrieval- en vectorstore-infrastructuur bestaat;
- SSOT- en retrieval-benchmarks zijn aanwezig.

### Wat nog ontbreekt

- een echte constellation-benchmark;
- vergelijking tussen losse seed-query en cluster-query;
- metric voor clusterlabelkwaliteit;
- meting van voorspelde nieuwe relevante seeds vanuit clusters.

### Statusoordeel

Architectonisch voorbereid. Nog niet experimenteel bewezen.

## Fase 4: modelinterne test

### Wat staat

- conceptuele documentatie;
- theoretische positionering;
- verwijzing naar latere open-source modelanalyse.

### Wat ontbreekt

- activation extraction;
- sparse classifier-evaluatie;
- intervention testing;
- correlatieanalyse tussen externe `weight` en interne signalen.

### Statusoordeel

Nog onderzoekswerk. Niet operationeel aanwezig in de repo.

## Evaluatielagen buiten de fasen

## Regressielaag

Status: Strong

Dit is de sterkste laag van de repo. Als doel is: regressies voorkomen, mechaniek bewaken, CI betrouwbaar houden, dan is de repo al behoorlijk volwassen.

## Open-world evaluatie

Status: Weak

Er is nog geen volwassen open-set evaluatie waarbij onbekende teksten zonder vaste ground-truth seedlijst blind beoordeeld worden op seedkwaliteit.

## Probe utility

Status: Weak to partial

De repo heeft wel paden die vervolgkwaliteit benaderen, maar nog geen volledige en zelfstandige evaluatielaag voor probe utility.

## Reproduceerbaarheid

Status: Partial

De intentie is sterk en de documentatie benoemt de juiste artefacten. Tegelijk zie ik nog niet een volledige operationele runlog-laag die het hele faseplan afdekt zoals in `07_reproduceerbaarheid.md` wordt gevraagd.

## Praktische betekenis voor repo-beslissingen

De repo moet vanaf hier twee dingen tegelijk doen:

1. de huidige regressielaag behouden, want die is waardevol;
2. de hoofdclaim verplaatsen naar sterkere evaluatielagen.

Dat betekent concreet:

- scenario-suites niet weggooien;
- scenario-suites herlabelen als regressie en kleine benchmarkvalidatie;
- nieuwe evaluatielagen toevoegen voor open-set kwaliteit, adversarial false positives, probe utility en domeintransfer.

## Wat nu niet meer impliciet mag blijven

Deze uitspraken moeten in de repo expliciet worden gemaakt:

- de standaard CI bewijst vooral de meetketen, niet algemene SSL-prestatie;
- fixture-runs zijn technische controle, geen eindbewijs;
- fase 3 en 4 zijn nog niet experimenteel afgedekt;
- scenario-scores zijn bruikbaar, maar niet voldoende als eindclaim.

## Aanbevolen volgende documenten

Na dit document horen twee andere documenten leidend te worden:

- `docs/research/scenario-independence-roadmap.md`
- `docs/research/evaluation-matrix.md`

Samen vormen ze:

- huidige status;
- gewenst doelbeeld;
- concrete evaluatiestructuur.

## Korte eindkwalificatie

De repo is vandaag:

> een sterke en serieuze SSL-benchmarkharness met goede mechanische discipline, maar nog geen volledige validatie van het hele SSL 4.5 onderzoeksprogramma.
