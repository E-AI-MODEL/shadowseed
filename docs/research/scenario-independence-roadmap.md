# Plan Naar Scenario-onafhankelijke SSL-validatie

## Doel van dit document

Dit document zet op papier hoe Shadow Seed Learning kan doorgroeien van een scenario-gedreven benchmarkrepo naar een schonere repo en een sterkere, scenario-onafhankelijke validatiestrategie.

De kernvraag is niet of scenario's nu nuttig zijn. Dat zijn ze. De kernvraag is wanneer scenario's nog een tijdelijke steiger zijn, en wanneer ze het bewijsmodel beginnen te beperken.

Dit plan beschrijft:

1. de huidige afhankelijkheid van scenario's;
2. waarom die afhankelijkheid op termijn een beperking wordt;
3. welk doelbeeld beter past bij SSL als algemeen mechanisme;
4. hoe de repo daarheen kan migreren zonder de huidige resultaten te verliezen;
5. welke acceptatiecriteria bepalen of scenario's echt losgelaten mogen worden.

## Samenvatting

De huidige repo bewijst vooral dat de SSL-mechaniek werkt binnen een kleine, vaste en goed begrepen set scenario's. Dat is nuttig voor fase 0 en delen van fase 1 en 2. Het is nog geen voldoende bewijs dat SSL als algemeen mechanisme domein-onafhankelijk, prompt-onafhankelijk en context-onafhankelijk werkt.

De afhankelijkheid van scenario's zit nu op vier plekken:

- in de benchmarkdata;
- in de detectorlogica via domein-priors;
- in de scoringslogica via vaste ground-truth seeds;
- in de interpretatie van succes via suite-specifieke metrics.

Als SSL uiteindelijk een algemeen mechanisme voor afwezigheidsdetectie moet zijn, moet de evaluatie opschuiven van "vindt het systeem de gaps die wij vooraf hebben opgeschreven?" naar "produceert het systeem herhaalbaar kleine, relevante, valideerbare gaps in onbekende contexten, met betere vervolgstappen en beperkte ruis?"

De overgang moet gefaseerd gebeuren. Scenario's kunnen niet in een sprong verdwijnen. Ze moeten eerst van primaire bewijslaag verschuiven naar regressielaag.

## 1. Huidige situatie

## 1.1 Wat de repo nu goed doet

De huidige repo heeft een duidelijke kern:

- een formeel SSL-model met `trace`, `weight`, statusovergangen en Validation Gate;
- een kleine Gap-Test Suite met drie scenario's;
- false-positive controls;
- benefit-suites voor antwoordverbetering;
- een blinde benchmarklaag met gescheiden labels;
- retrieval- en SSOT-smokes;
- CI en publicatie rond benchmarkresultaten.

Dat is sterk genoeg om een eerste technische these te ondersteunen:

> de SSL-harness kan kleine gaps representeren, volgen, scoren en in beperkte vorm gebruiken.

## 1.2 Waar scenario-afhankelijkheid nu precies zit

De repo is op dit moment nog scenario-gedreven op de volgende manieren.

### A. Vaste scenario's als epistemische ankers

De Gap-Test Suite en verwante suites bouwen op een kleine set handgemaakte casussen. Daardoor is de benchmark sterk controleerbaar, maar ook smal.

### B. Vaste ground-truth seeds als waarheid

Succes is nu vaak gedefinieerd als overlap met vooraf uitgeschreven seeds. Dat is bruikbaar voor startvalidatie, maar minder geschikt zodra SSL nieuwe of onverwachte maar geldige gaps moet mogen vinden.

### C. Domein-priors in detectie

De huidige gratis detector gebruikt domein-priors. Dat maakt de benchmark goedkoop en reproduceerbaar, maar verbindt detectiekwaliteit nog aan bekende testvormen.

### D. Suite-specifieke claims

Metrics zoals `mean_scenario_score` en suite coverage zeggen nu vooral iets over prestatie binnen de suite, niet automatisch over prestatie buiten de suite.

## 1.3 Waarom dit voorlopig nog legitiem is

Scenario-afhankelijkheid is in een vroege fase niet fout. Voor SSL is het zelfs nuttig, omdat de eerste vraag niet is of het mechanisme universeel werkt, maar of het mechanisme intern coherent is:

- wordt een brede gap geweigerd of gesplitst;
- start weight echt op nul;
- promoveert een seed niet te vroeg;
- helpt validatie tegen ruis;
- blijft labelinformatie uit de detectielaag.

Daar zijn kleine scenario-suites geschikt voor.

## 2. Waarom scenario-afhankelijkheid op termijn een beperking wordt

Als SSL een algemeen mechanisme wil zijn, ontstaan er vijf problemen zodra de repo te lang op scenario's blijft leunen.

## 2.1 Overfitting aan benchmarkstijl

De detector of scorer kan steeds beter worden in precies die soorten afwezigheden die de suite al bevat. Dan meet de repo optimalisatie op benchmarkvorm in plaats van echte epistemische gevoeligheid.

## 2.2 Te smalle definitie van een "goede seed"

Een systeem kan relevante gaps vinden die niet letterlijk in de ground-truth lijst staan. In een vaste scenario-opzet wordt dat risico snel fout-negatief gescoord.

## 2.3 Onvoldoende bewijs voor domeinrobuustheid

Drie scenario's of een kleine vaste set kan niet hard bewijzen dat SSL werkt buiten geschiedenis, recht en software-architectuur.

## 2.4 Verkeerde stimulans voor repo-evolutie

Zolang de belangrijkste winst uit betere suite-scores komt, verschuift ontwikkeling vanzelf richting benchmarktuning. Dat is niet hetzelfde als mechanismeverbetering.

## 2.5 Onderschatting van menselijke beoordeling

De specificatie benadrukt toetsbaarheid en atomiciteit. Op termijn kan dat niet volledig door vaste seed-overlap worden gevangen. Dan zijn beoordelaars, agreement en blind review geen extra laag meer, maar de hoofdvalidatie.

## 3. Doelbeeld

Het gewenste eindbeeld is:

> SSL wordt beoordeeld als algemeen mechanisme voor detectie, validatie en navigatie van kleine kennislacunes, niet als systeem dat vooraf bekende scenario-antwoorden reproduceert.

Dat doelbeeld heeft zes kenmerken.

## 3.1 Scenario's verschuiven van bewijslaag naar regressielaag

De huidige Gap-Test Suite blijft bestaan, maar alleen als:

- regressietest;
- smoke-test;
- controle op mechanische stabiliteit.

Niet meer als primaire drager van de hoofdclaim.

## 3.2 Detectie moet open-world kunnen werken

De detector mag geen toegang hebben tot vooraf gedefinieerde ground-truth of suite-structuren. Hij moet in onbekende contexten kleine, specifieke en toetsbare gaps kunnen produceren.

## 3.3 Scoring moet deels relationeel en deels menselijk worden

De vraag wordt minder:

> matcht deze seed exact een vooraf bekende lijst?

en meer:

> is deze seed atomisch, relevant, niet-triviaal, controleerbaar en inhoudelijk nuttig?

Daarvoor is een combinatie nodig van:

- heuristische filters;
- blind menselijke beoordeling;
- agreement-meting;
- negatieve controles;
- eventueel retrieval-ondersteunde verificatie.

## 3.4 Validatie moet worden beoordeeld op gedrag, niet op suite-trucjes

De Validation Gate moet niet alleen slagen omdat de benchmark haar spaart. Ze moet aantoonbaar beter zijn dan eenvoudigere promotieregels, zoals:

- pure trace-gestuurde promotie;
- promotie zonder contradictiecheck;
- promotie na slechts een of twee herkenningen.

## 3.5 Probe-kwaliteit moet zelfstandig meetbaar worden

De waarde van SSL zit niet alleen in detectie, maar in wat een promoted seed daarna mogelijk maakt:

- betere vraag aan de gebruiker;
- betere retrieval-query;
- betere falsificatie van een te snelle aanname.

Dat moet apart beoordeeld worden.

## 3.6 Repo-structuur moet deze eerlijkheid expliciet maken

De repo moet zichtbaar scheiden:

- mechanische regressietests;
- onderzoeksvalidatie;
- open-world evaluatie;
- publicatie en rapportage.

## 4. Nieuwe evaluatielagen

Om van scenario-afhankelijkheid af te komen, zijn extra evaluatielagen nodig.

## 4.1 Laag A: gesloten regressielaag

Doel:
bewaken dat de huidige SSL-mechaniek niet kapotgaat.

Voorbeelden:

- huidige Gap-Test Suite;
- false-positive suite;
- blind benchmark smoke;
- manager tests;
- vectorstore en SSOT smoke.

Rol:
snelle CI, mechanische stabiliteit, geen hoofdclaim.

## 4.2 Laag B: open-set seed quality review

Doel:
beoordelen of de detector in onbekende teksten goede seeds oplevert.

Benodigde aanpak:

- neem echte of semi-echte teksten uit meerdere domeinen;
- laat het systeem seeds genereren zonder vooraf geschreven seedlijst;
- laat twee of meer beoordelaars blind scoren op:
  - atomiciteit;
  - relevantie;
  - toetsbaarheid;
  - niet-trivialiteit;
  - bruikbaarheid voor vervolgactie.

Primaire metrics:

- acceptance rate van seeds;
- interbeoordelaarsovereenstemming;
- percentage te brede seeds;
- percentage triviale of irrelevante seeds.

Dit is de eerste echte stap weg van scenario-afhankelijkheid.

## 4.3 Laag C: adversarial negative controls

Doel:
testen of SSL ook in open omgevingen niet overal gaps hallucineert.

Benodigde aanpak:

- teksten die inhoudelijk al vrij compleet zijn;
- teksten met lokkende maar niet-relevante uitbreidingsmogelijkheden;
- teksten waarin stijlverschil niet als epistemische gap mag tellen.

Primaire metrics:

- candidate false-positive rate;
- promoted false-positive rate;
- verschil tussen Gate en een zwakkere baseline-promotieregel.

Belangrijk:
hier moet de Gate echt mogen falen of slagen. Niet by construction op nul eindigen.

## 4.4 Laag D: behavioral value layer

Doel:
meten of promoted seeds echt betere vervolgstappen opleveren.

Drie sporen:

1. Socratische probe-kwaliteit
2. Retrieval probe-kwaliteit
3. Dialectische probe-kwaliteit

Mogelijke metrics:

- informatiewinst per vervolgvraag;
- retrieval hit improvement ten opzichte van baseline-query;
- reductie van unsupported additions na dialectische check;
- menselijke voorkeur in blind vergelijking van vervolginteractie.

## 4.5 Laag E: domain transfer layer

Doel:
testen of SSL buiten de bekende domeinen nog werkt.

Aanpak:

- domeinen toevoegen zonder domein-priors te herschrijven;
- cross-domain holdout;
- unseen promptvormen;
- verschillende registertypes: uitleg, beleidsadvies, casusanalyse, ontwerpvoorstel.

Primaire metrics:

- seed acceptance rate per domein;
- false-positive drift per domein;
- probe utility per domein;
- stabiliteit van atomiciteit buiten de trainingsstijl van de suite.

## 4.6 Laag F: model-interne research layer

Doel:
pas later toetsen of externe SSL-signalen correleren met modelinterne patronen.

Deze laag blijft onderzoekswerk en hoeft niet in standaard-CI. Maar hij moet wel als aparte laag worden gemarkeerd, niet als impliciete claim.

## 5. Wat dit betekent voor de repo

De repo kan schoner worden als hij expliciet rond deze lagen wordt opgebouwd.

## 5.1 Aanbevolen structuur

```text
docs/
  research/
    current-status.md
    scenario-independence-roadmap.md
    evaluation-matrix.md
  specs/
    framework.md
    validation-gate.md
    probe-types.md

src/shadowseed/
  core/
  evaluation/
    regression/
    open_review/
    adversarial/
    behavioral/
    transfer/
  reporting/

tests/
  unit/
  regression/
  workflow/

benchmarks/
  regression/
  open_review/
  adversarial/
  transfer/
```

Hiermee blijft de huidige suite bestaan, maar op een lagere en eerlijkere plek.

## 5.2 Wat behouden moet blijven

Deze onderdelen zijn nog steeds waardevol:

- `SSLManager` en de twee-veld logica;
- atomiciteitsregels;
- blind labelscheiding;
- retrieval- en SSOT-keten;
- huidige scenario-suite als regressielaag;
- analyse- en rapportage-infrastructuur.

## 5.3 Wat samengevoegd of afgeslankt kan worden

- dubbele workflowlogica;
- inline benchmarkdata in workflows;
- meerdere publicatiepaden voor vergelijkbare output;
- verspreide benchmarkfuncties die dezelfde coverage- en scoringlogica herhalen;
- documentatie die actuele resultaten en permanente specificatie door elkaar laat lopen.

Belangrijk:
hier moet consolidatie selectief zijn. Niet elke evaluatielaag moet technisch of inhoudelijk in dezelfde mal worden geduwd.

Wat wel geconsolideerd kan worden:

- één gedeelde resultaatsstructuur voor runs, seeds, beoordelingen en metrics;
- één rapportagepad voor publicatie van evaluatie-uitkomsten;
- één plek voor benchmarkloaders, runlogging en artifact-opslag;
- één naam- en mapconventie voor evaluatielagen.

Wat juist gescheiden moet blijven:

- regressiebewijs versus open-world bewijs;
- mechanische stabiliteitsmetrics versus onderzoeksmetrics;
- automatische filters versus menselijke kwaliteitsbeoordeling;
- domeinspecifieke hulplogica versus scenario-onafhankelijke hoofdclaims.

De hoofdregel is:

> consolideer infrastructuur en rapportage, maar niet ten koste van epistemische eerlijkheid.

## 5.4 Wat inhoudelijk nieuw gebouwd moet worden

- open-review evaluatiepad;
- adversarial negative control suite die de Gate echt belast;
- probe quality evaluators;
- domain transfer evaluatie;
- statusdocument dat expliciet onderscheid maakt tussen bewezen, deels bewezen en nog niet bewezen.

## 5.5 Wat expliciet niet moet gebeuren

De repo moet niet "schoner" lijken door ongelijke bewijssoorten in één score samen te trekken.

Vermijd daarom:

- één totaalscore waarin regressie, open-set en behavioral metrics zonder onderscheid verdwijnen;
- workflow-samenvoeging waarbij reviewer-artefacten en CI-smokes dezelfde status krijgen;
- claims over scenario-onafhankelijkheid op basis van alleen scenario-stabiele regressies;
- hergebruik van domein-priors in evaluatielagen die juist domeintransfer moeten toetsen.

## 6. Migratiepad

De overgang moet in vier stappen gebeuren.

## Stap 1: Maak de huidige status expliciet

Doel:
eerlijk opschrijven wat de repo nu wel en niet bewijst.

Op te leveren:

- `docs/research/current-status.md`
- per fase: implemented, partially implemented, planned
- duidelijk onderscheid tussen mechanische smoke en onderzoeksbewijs

Succes:
niemand hoeft meer te raden of fase 3 of 4 echt al bewezen zijn.

## Stap 2: Degradeer scenario-suites naar regressielaag

Doel:
de huidige scenario-suite behouden zonder haar de hoofdclaim te laten dragen.

Op te leveren:

- hernoeming in docs en workflows naar regression suite;
- README-tekst die duidelijk zegt dat vaste scenario's regressie zijn, niet eindbewijs;
- metrics-labels die suite-scope expliciet maken.

Succes:
de repo kan de huidige resultaten blijven draaien, maar claimt er minder mee dan nu impliciet gebeurt.

## Stap 3: Voeg open-review en adversarial evaluatie toe

Doel:
de eerste echte scenario-onafhankelijke laag bouwen.

Op te leveren:

- open corpus sample-loader;
- review packets voor menselijke seedbeoordeling;
- agreement-meting;
- negatieve controles die de Gate echt belasten;
- baselinevergelijkingen tegen minimaal `trace-only` en `trace + no contradiction check`;
- vaste run-artifacts per evaluatie: seedlijst, reviewerscores, disagreements, false-positive log en promotiebeslissingen.

Succes:
de hoofdclaim verschuift van "seed matcht suite" naar "seed is blind beoordeeld als goed en nuttig".

## Stap 4: Verplaats hoofdclaim naar gedragsvalidatie

Doel:
SSL bewijzen op gedrag, niet op benchmarkherkenning.

Op te leveren:

- meting van probe utility;
- meting van false-positive reductie versus zwakkere promotiebaselines;
- cross-domain transfer;
- heldere rapportage per evaluatielaag.

Succes:
scenario's zijn nog nuttig, maar niet langer noodzakelijk voor de kernclaim.

## 7. Acceptatiecriteria voor het loslaten van scenario's

Scenario's mogen pas van primaire bewijslaag naar secundaire regressielaag verschuiven wanneer alle onderstaande punten voldoende staan.

## 7.1 Seed quality zonder vaste seedlijsten

Er moet een open-set evaluatie bestaan waarin seeds zonder vooraf uitgeschreven ground truth beoordeeld worden op kwaliteit.

Minimaal nodig:

- blind menselijke scoring;
- agreement tussen beoordelaars;
- acceptabele atomiciteitsratio;
- expliciete afwijscodes voor te brede, triviale, irrelevante en niet-toetsbare seeds.

## 7.2 Gate-waarde boven eenvoudige baselines

De Validation Gate moet aantoonbaar beter presteren dan eenvoudigere regels.

Minimaal nodig:

- lagere false-positive promotie dan trace-only;
- betere netto-opbrengst dan promotie zonder contradictiecheck;
- zichtbare foutgevallen waarin de Gate terecht blokkeert ondanks lokkende maar niet-relevante uitbreidingen.

## 7.3 Probe utility moet meetbaar positief zijn

Promoted seeds moeten aantoonbaar iets nuttigs doen.

Minimaal nodig:

- betere retrieval-query's;
- betere vervolgvragen;
- minder unsupported additions of betere coverage.

## 7.4 Domeintransfer moet zichtbaar zijn

De detector mag niet alleen netjes werken in de drie bekende benchmarkdomeinen.

Minimaal nodig:

- minstens enkele extra domeinen;
- stabiele seed quality zonder herschrijven van domein-priors per domein.

## 7.5 Reproduceerbaarheid moet blijven staan

Bij het loslaten van scenario's mag reproduceerbaarheid niet verdwijnen.

Minimaal nodig:

- runlogs;
- beoordelingsdata;
- promptversies;
- seed-output en review-output;
- failure logging;
- stabiele artifactnamen en rapportagevelden zodat lagen onderling vergelijkbaar blijven zonder inhoudelijk te worden vermengd.

## 8. Conclusie

De huidige scenario-suites zijn geen fout ontwerp. Ze zijn een juiste vroege fase voor SSL. Maar ze zijn niet het eindmodel voor bewijs.

Als SSL echt een mechanisme voor algemene epistemische navigatie wil zijn, moet de repo verschuiven van:

> "vindt het systeem de gaps die wij vooraf in kleine scenario's hebben vastgelegd?"

naar:

> "genereert het systeem in onbekende contexten kleine, relevante, toetsbare en bruikbare gaps, en gebruikt het die veiliger en nuttiger dan eenvoudigere alternatieven?"

Dat vraagt niet om het weggooien van de huidige repo, maar om herordening:

- huidige suites behouden als regressielaag;
- hoofdclaim verplaatsen naar open-set, adversarial en behavioral evaluatie;
- repo-structuur opschonen zodat die verschuiving zichtbaar en onderhoudbaar wordt.

## 9. Directe vervolgstappen

De hoogste hefboom is nu:

1. schrijf een expliciete statusmatrix per SSL-fase;
2. herlabel de huidige scenario-suite als regressielaag;
3. ontwerp een open-review evaluatie voor seedkwaliteit zonder vaste ground truth;
4. ontwerp een echte adversarial false-positive evaluatie voor de Validation Gate;
5. consolideer daarna pas reporting, workflows en artifacts rond deze nieuwe lagen.
