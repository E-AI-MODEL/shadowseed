# SSL Evaluatiematrix

> Status: current
> Date: 2026-05-22
> Evidence layer: Evidence-layer matrix
> Current source: yes


## Doel van dit document

Deze matrix vertaalt de SSL-specificatie naar een praktische evaluatiestructuur voor de repository.

De matrix beantwoordt per laag drie vragen:

1. wat willen we aantonen;
2. hoe meten we dat;
3. wat is vandaag de status.

De matrix is geen scorekaart die alles samenvouwt tot één getal. Ze bewaakt juist dat verschillende bewijssoorten zichtbaar gescheiden blijven.

## Overzicht

| Laag | Hoofdvraag | Huidige status | Gewenste status |
|---|---|---|---|
| Regressie | Blijft de kernmechaniek werken? | Sterk | Behouden |
| Kleine benchmarkvalidatie | Werkt SSL op vaste, controleerbare casussen? | Bruikbaar | Aanscherpen |
| Open-set seedkwaliteit | Kan SSL goede seeds maken zonder vaste ground truth? | Zwak | Sterk |
| Adversarial ruiscontrole | Weert de Gate echte misleidende gaps? | Zwak | Sterk |
| Probe utility | Leveren promoted seeds betere vervolgstappen op? | Beperkt | Sterk |
| Domeintransfer | Werkt SSL buiten de bekende benchmarkdomeinen? | Zwak | Sterk |
| Modelinterne validatie | Is er steun in interne activaties? | Afwezig | Onderzoekslaag |

## 1. Regressielaag

### Vraag

Blijft de mechanische SSL-kern werken na codewijzigingen?

### Voorbeelden

- manager tests;
- atomiciteitsregels;
- Gap-Test Suite;
- false-positive suite;
- blind benchmark smoke;
- retrieval en SSOT smokes.

### Primaire metrics

- test pass/fail;
- stabiele outputschema's;
- geen regressies in kernstatussen en benchmarkpaden.

### Huidige status

Sterk.

### Doel

Behouden als snelle CI-ruggengraat.

## 2. Kleine benchmarkvalidatie

### Vraag

Werkt SSL op kleine, vaste en controleerbare cases?

### Voorbeelden

- Gap-Test Suite;
- benefit-suite;
- model benefit fixture route.

### Primaire metrics

- scenario score;
- atomische hits;
- gap coverage;
- unsupported additions.

### Huidige status

Bruikbaar, maar te smal als eindbewijs.

### Doel

Behouden, maar expliciet framen als beperkte benchmarklaag.

## 3. Open-set seedkwaliteit

### Vraag

Kan SSL op onbekende teksten kleine, relevante en toetsbare seeds produceren zonder vaste seedlijst?

### Benodigde evaluatie

- open corpus of sampled real-world teksten;
- seedgeneratie zonder vooraf opgeschreven expected seeds;
- blinde menselijke scoring;
- interbeoordelaarsovereenstemming;
- expliciete afwijscodes voor te brede, triviale, irrelevante en niet-toetsbare seeds.

### Primaire metrics

- acceptance rate;
- atomiciteitsratio;
- relevantieratio;
- agreement;
- percentage triviale seeds.

### Vereiste artifacts

- seed-output per run;
- reviewformulieren of review-packets;
- disagreement-log;
- samenvatting per beoordelaar en per domein.

### Huidige status

Zwak of afwezig.

### Doel

Dit moet een primaire bewijslaag worden.

## 4. Adversarial ruiscontrole

### Vraag

Voorkomt SSL dat zwakke of misleidende gaps promoveren?

### Benodigde evaluatie

- complete of bijna-complete teksten;
- lokkende maar irrelevante uitbreidingskansen;
- vergelijking tussen Gate en zwakkere baselines zoals `trace-only` en `trace + no contradiction check`.

### Primaire metrics

- candidate false-positive rate;
- promoted false-positive rate;
- nettoverbetering van de Gate versus zwakkere promotie;
- zichtbare foutgevallen waarin de Gate terecht blokkeert.

### Vereiste artifacts

- false-positive log;
- promotiebeslissingen per seed;
- vergelijking per baseline-regel;
- voorbeelden van geblokkeerde en doorgelaten seeds.

### Huidige status

Zwak.

### Doel

Echte stresstest van de Gate, niet alleen smokecontrole.

## 5. Probe utility

### Vraag

Doen promoted seeds iets aantoonbaar nuttigs?

### Subvragen

- worden vervolgvraagstukken beter;
- wordt retrieval scherper;
- daalt unsupported uitbreiding;
- helpt falsificatie tegen te snelle promotie.

### Primaire metrics

- informatiewinst per Socratische probe;
- retrieval improvement versus baseline-query;
- dekkingstoename zonder evenredige ruisgroei;
- menselijke voorkeur in blind vergelijking.

### Huidige status

Beperkt.

### Doel

Uitbouwen tot zelfstandige evaluatielaag.

## 6. Domeintransfer

### Vraag

Blijft seedkwaliteit overeind in nieuwe domeinen en promptvormen?

### Benodigde evaluatie

- extra domeinen buiten de huidige suites;
- cross-domain holdouts;
- meerdere tekstgenres en taakvormen;
- expliciete scheiding tussen domeintransfer en domein-prior tuning.

### Primaire metrics

- acceptance rate per domein;
- false-positive drift;
- probe utility per domein;
- stabiliteit van atomiciteit.

### Huidige status

Zwak.

### Doel

Nodig voordat algemene claims geloofwaardig worden.

## 7. Modelinterne validatie

### Vraag

Is er interne modelsteun voor extern gemeten afwezigheid?

### Benodigde evaluatie

- activation extraction;
- sparse classifier;
- intervention testing;
- correlatie tussen externe en interne signalen.

### Primaire metrics

- effect boven random baseline;
- reproduceerbaarheid;
- causale gevoeligheid voor interventie.

### Huidige status

Afwezig in operationele repo-vorm.

### Doel

Behandelen als aparte onderzoekslaag, niet als standaard engineeringdoel.

## Praktisch gebruik van deze matrix

Deze matrix moet voor repo-beslissingen als volgt worden gelezen:

- regressie en kleine benchmarkvalidatie houden de repo stabiel;
- open-set, adversarial en probe utility moeten de hoofdclaim gaan dragen;
- domeintransfer en modelinterne validatie bepalen later hoe breed de claim mag worden.

## Wat niet moet gebeuren

Vermijd:

- één totaalscore waarin regressie, open-set en behavioral metrics verdwijnen;
- publicatie waarin fixture-smokes dezelfde status krijgen als menselijke review;
- domeintransferclaims op basis van alleen scenario-stabiele regressies.

## Korte prioriteitsvolgorde

1. behoud regressielaag;
2. maak huidige status expliciet;
3. bouw open-set seed review;
4. bouw echte adversarial Gate-evaluatie;
5. bouw probe-utility evaluatie;
6. voeg domeintransfer toe;
7. behandel modelinterne validatie als aparte onderzoekslijn.
