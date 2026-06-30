# SSL Evaluatiematrix

> Status: current
> Date: 2026-06-30
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
| A — Regressie | Blijft de kernmechaniek werken? | **Sterk** | Behouden |
| B — Kleine benchmarkvalidatie | Werkt SSL op vaste, controleerbare casussen? | **Bruikbaar** | Behouden als beperkte benchmarklaag |
| C — Open-set seedkwaliteit | Kan SSL goede seeds maken zonder vaste ground truth? | **Eerste evidence, gemengd** | Sterker en breder meten |
| D — Adversarial ruiscontrole | Weert de Gate echte misleidende gaps? | **Eerste echte evidence** | Grotere stresssets |
| E — Probe utility / payoff | Leveren promoted seeds betere vervolgstappen of antwoordruimte op? | **W9f-mechanisme vuurt; payoff-kwaliteit reviewer-afhankelijk (round 022, 1/8)** | Use-time seed-discipline + transfer |
| F — Domein- en taaktransfer | Werkt dezelfde doctrine buiten de bekende scenario's? | **Volgende stap** | W10: doctrine-transfer |
| G — Modelinterne validatie | Is er steun in interne activaties? | **Afwezig / later onderzoek** | Aparte onderzoekslijn |

## 1. Laag A — Regressie

### Vraag

Blijft de mechanische SSL-kern werken na codewijzigingen?

### Voorbeelden

- manager tests;
- lifecycle-tests voor `trace`, `weight`, TTL, TrTL en EXPIRED;
- atomiciteitsregels;
- Gap-Test Suite;
- false-positive suite;
- blind benchmark smoke;
- retrieval en SSOT smokes.

### Primaire metrics

- test pass/fail;
- stabiele outputschema's;
- geen regressies in kernstatussen, Gate-gedrag en benchmarkpaden.

### Huidige status

Sterk.

### Doel

Behouden als snelle CI-ruggengraat.

## 2. Laag B — Kleine benchmarkvalidatie

### Vraag

Werkt SSL op kleine, vaste en controleerbare cases?

### Voorbeelden

- Gap-Test Suite;
- benefit-suite;
- model benefit fixture route;
- vaste payoff-casussen voor regressie.

### Primaire metrics

- scenario score;
- atomische hits;
- gap coverage;
- semantic coverage waar relevant;
- unsupported additions;
- do-no-harm controles.

### Huidige status

Bruikbaar, maar te smal als eindbewijs.

### Doel

Behouden, maar expliciet framen als beperkte benchmarklaag en regressieanker.

## 3. Laag C — Open-set seedkwaliteit

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
- percentage triviale seeds;
- percentage niet-toetsbare seeds.

### Vereiste artifacts

- seed-output per run;
- reviewformulieren of review-packets;
- disagreement-log;
- samenvatting per beoordelaar en per domein.

### Huidige status

Eerste echte evidence, maar gemengd.

Open-set reviews tonen dat de detector vaak on-topic en relevant blijft, maar dat seeds nog te vaak triviaal, te vaag of onvoldoende toetsbaar kunnen zijn. Dit is een kwaliteitswaarschuwing, geen leeg resultaat.

### Doel

Verbreden en herhalen, maar niet verwarren met W9f. Open-set seedkwaliteit blijft een aparte laag naast cross-turn payoff.

## 4. Laag D — Adversarial ruiscontrole

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

Eerste echte evidence.

De huidige Gate discrimineert goed op de bestaande adversarial fixture, maar de set is nog klein. Slechte seeds kunnen antwoordruis veroorzaken als ze toch de revisie halen; dat bevestigt dat `weight = 0` tot Gate-promotie noodzakelijk is.

### Doel

Grotere en minder lexicaal afhankelijke stresssets.

## 5. Laag E — Probe utility, payoff en cross-turn antwoordruimte

### Vraag

Doen promoted of surfaced seeds iets aantoonbaar nuttigs?

### Subvragen

- worden vervolgvraagstukken beter;
- wordt retrieval scherper;
- daalt unsupported uitbreiding;
- helpt falsificatie tegen te snelle promotie;
- opent cross-turn surfacing antwoordruimte die zonder SSL niet als optie bestond;
- wanneer veroorzaakt seed-gebruik vernauwing of ruis?

### Primaire metrics

- informatiewinst per Socratische probe;
- retrieval improvement versus baseline-query;
- dekkingstoename zonder evenredige ruisgroei;
- menselijke voorkeur in blind vergelijking;
- seed-effect na keuze: helpt duidelijk, helpt een beetje, geen verschil, veroorzaakt ruis;
- cross-turn payoff events per sessie.

### Vereiste artifacts

- payoff-run JSON;
- blind A/B review-items;
- hidden answer key;
- reviewer scores;
- seed-effect labels;
- samenvatting per conversation.

### Huidige status

Het W9f-mechanisme vuurt op veilige drempels; de payoff-kwaliteit is reviewer-afhankelijk gebleken en daarmee nog open.

W9f toont dat de bestaande doctrine (`trace`, `weight`, TTL, TrTL, Gate) in multi-turn sessies extra antwoordruimte opent die de history-baseline niet zelf opwerpt. De blind A/B-review is kwaliteitscontrole op die geopende antwoordruimte, geen klassieke model-vs-model benchmark — maar de eerste review op veilige drempels kwam **gespleten** terug (round 022: twee reviewers oneens op 7/8, ruis in *promoted* seeds). Dat reframe verandert de lat, het verwijdert hem niet.

### Doel

Niet opnieuw W9f bewijzen, maar transfer en gebruiksdiscipline meten:

- wanneer mag een seed licht worden genoemd;
- wanneer mag hij het hoofdframe sturen;
- wanneer moet hij genegeerd worden;
- wanneer veroorzaakt hij ruis of vernauwing?

## 6. Laag F — Domein- en taaktransfer

### Vraag

Blijft de SSL-doctrine overeind in nieuwe domeinen, promptvormen, modellen en taken?

### Benodigde evaluatie

- extra domeinen buiten de huidige suites;
- cross-domain holdouts;
- meerdere tekstgenres en taakvormen;
- expliciete scheiding tussen domeintransfer en domein-prior tuning;
- hergebruik van dezelfde lifecycle: `trace`, `weight`, TTL, TrTL, Gate en surfacing.

### Primaire metrics

- seed acceptance rate per domein;
- false-positive drift;
- probe utility per domein;
- stabiliteit van atomiciteit;
- cross-turn payoff events per domein;
- reviewerlabels voor seed-ruis en seed-vernauwing.

### Huidige status

Volgende stap.

### Doel

W10: doctrine-transfer. De vraag is niet meer of W9f in de huidige setting werkt, maar of dezelfde levenscyclus overdraagt naar andere domeinen, taken en modellen.

## 7. Laag G — Modelinterne validatie

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

Behandelen als aparte onderzoekslijn, niet als standaard engineeringdoel.

## Praktisch gebruik van deze matrix

Deze matrix moet voor repo-beslissingen als volgt worden gelezen:

- regressie en kleine benchmarkvalidatie houden de repo stabiel;
- open-set, adversarial en probe utility blijven gescheiden evidence-lagen;
- het W9f cross-turn mechanisme is bevestigd op veilige drempels; de payoff-kwaliteit is reviewer-afhankelijk gebleken (round 022) en blijft open;
- de volgende stap is use-time seed-discipline (potentieel-vs-must) plus W10 doctrine-transfer;
- modelinterne validatie blijft later onderzoek.

## Wat niet moet gebeuren

Vermijd:

- één totaalscore waarin regressie, open-set, payoff en transfer verdwijnen;
- publicatie waarin fixture-smokes dezelfde status krijgen als menselijke review;
- een klassieke A/B-test gebruiken alsof SSL alleen waarde heeft wanneer het GPT-4.1 op elk item verslaat;
- domeintransferclaims op basis van alleen scenario-stabiele regressies;
- W9f blijven heropenen als er eigenlijk een transfer- of productvraag ligt.

## Korte prioriteitsvolgorde

1. behoud regressie- en lifecyclelaag;
2. houd W9f vast als baseline;
3. documenteer blind A/B als kwaliteitscontrole, niet als absolute benchmark;
4. bouw W10 doctrine-transfer;
5. meet seed-ruis en seed-vernauwing expliciet;
6. behandel modelinterne validatie als aparte onderzoekslijn.
