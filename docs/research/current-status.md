# Huidige Status van SSL-validatie

> Status: current
> Date: 2026-06-30
> Evidence layer: status snapshot across layers A-G
> Source: 4.6 evidence model in `docs/00_shadow_seed_learning_4_6.md`

## Doel van dit document

Dit document maakt expliciet wat de repository vandaag werkelijk aantoont, wat gedeeltelijk is afgedekt, en wat nog onderzoekswerk is.

De kernregel blijft:

> wat mechanisch werkt is nog niet automatisch een brede algemene claim.

Maar de status is sinds de eerdere 2026-05/06-snapshots verschoven. Vooral W9f heeft de cross-turn SSL-levenscyclus uit de sfeer van alleen belofte gehaald en als technische baseline vastgezet.

## Korte samenvatting

De repo staat sterk voor:

- de mechanische SSL-kern (`trace`, `weight`, TTL, TrTL, status lifecycle, Validation Gate);
- regressie en kleine benchmarkvalidatie;
- adversarial Gate-evaluatie als eerste echte ruiscontrole;
- probe-feedback lifecycle als eerste behavioral bewijs;
- cross-turn context-discovery en memory-surfacing via W9f.

De repo staat nog niet sterk genoeg voor:

- een brede claim dat SSL elk antwoord verbetert;
- algemene domein-onafhankelijkheid;
- volledige productmatige betrouwbaarheid van automatisch seed-gebruik;
- modelinterne validatie.

De belangrijkste statuswijziging:

> W9f is geaccepteerd als werkende technische baseline voor cross-turn context-discovery en memory-surfacing. De volgende stap is transfer van de doctrine, niet nog meer bewijs dat het W9f-mechanisme bestaat.

Zie ook `docs/research/w9f-evaluatieconclusie.md`.

## Statusoverzicht per laag

| Laag | Vraag | Status per 2026-06-30 | Korte duiding |
|---|---|---|---|
| A — Regressie | Blijft de kernmechaniek werken? | **Sterk** | CI, manager-tests, lifecycle-tests en benchmark-smokes bewaken de kern. |
| B — Kleine benchmarkvalidatie | Werkt SSL op vaste, controleerbare casussen? | **Bruikbaar** | Geschikt als regressie en beperkte benchmark, niet als eindclaim. |
| C — Open-set seedkwaliteit | Maakt SSL goede seeds zonder vaste ground truth? | **Eerste echte evidence, gemengd** | Menselijke en gedelegeerde reviews tonen relevantie, maar ook trivialiteit/testability-risico. |
| D — Adversarial ruiscontrole | Weert de Gate misleidende gaps? | **Eerste echte evidence** | Gate presteert sterk op kleine adversarial set; bredere stress blijft wenselijk. |
| E — Probe utility / payoff | Leveren promoted seeds nuttige vervolgstappen of antwoorden op? | **Positief voor W9f cross-turn; deels open voor productgebruik** | W9f toont cross-turn payoff; seed-vernauwing blijft foutklasse. |
| F — Domeintransfer | Werkt dezelfde doctrine buiten bekende scenario's? | **Volgende stap** | W10 moet transfer van de levenscyclus meten, niet opnieuw W9f bewijzen. |
| G — Modelintern | Is er interne modelsteun voor extern gemeten afwezigheid? | **Onderzoekslaag** | Niet nodig voor de huidige engineering-baseline. |

## Mechanische kern

De minimale SSL-definitie is technisch aanwezig en wordt bewaakt:

- een seed moet atomisch zijn;
- brede of samengestelde seeds kunnen worden geweigerd of gesplitst;
- `trace` en `weight` zijn formeel gescheiden;
- `trace` bewaart aanwezigheid;
- `weight` start op `0.0` en meet pas na promotie invloed;
- TTL laat onherkende seeds vervallen;
- TrTL houdt seeds levend wanneer nieuwe context ze herkent;
- EXPIRED is terminaal;
- promotie loopt via de Validation Gate.

Dit is het verschil tussen een los benchmarkidee en een reproduceerbare kernarchitectuur.

## Open-set seedkwaliteit

De open-set lijn heeft echte signalen opgeleverd, maar blijft inhoudelijk gemengd.

Belangrijke stand:

- round 005 offset-12 gaf de eerste mensgereviewde Laag-C evidence: relevantie hoog, maar acceptance laag door trivialiteit, vaagheid en toetsbaarheidsproblemen;
- latere gedelegeerde AI-review en modelruns bevestigden dat sterkere modelpaden de vorm kunnen verbeteren, maar niet automatisch de volledige substantieclaim dragen;
- human-vs-AI agreement was bruikbaar genoeg om gedelegeerde reviews als proxy te gebruiken, mits duidelijk gelabeld.

Conclusie:

> Open-set detectie is niet leeg, maar ook niet definitief opgelost. De waarschuwing is niet dat SSL niets vindt, maar dat gevonden seeds vaak relevant maar te triviaal of te weinig toetsbaar kunnen zijn.

## Adversarial Gate en veiligheid

De adversarial Gate-lijn toont dat veiligheid vóór antwoordgeneratie moet zitten.

Belangrijke stand:

- de Gate is sterker dan trace-only-achtige baselines op de huidige adversarial fixture;
- slechte of irrelevante seeds kunnen een sterk model nog steeds richting ruis sturen wanneer ze de revisie halen;
- een capabel model is een redelijke backstop tegen valse feiten, maar niet tegen irrelevante seed-injectie;
- daarom blijft `weight = 0` tot Gate-promotie een kernonderdeel van de doctrine.

Conclusie:

> De Gate/weightless-filtering is geen formaliteit, maar de veiligheidslaag die antwoordruis moet voorkomen.

## Probe utility en payoff

De payoff-lijn heeft drie belangrijke lessen opgeleverd:

1. handelen op geldige seeds kan antwoorden verbeteren;
2. kleine of zwakke modellen kunnen derailen in de revisiestap;
3. capabele modellen kunnen seeds vloeiend gebruiken zonder unsupported additions, mits de prompt en do-no-harm-regel goed staan.

De semantische coverage- en human-review-lijnen tonen dat lexicale coverage te grof was: goed geïntegreerde seeds worden vaak geparafraseerd en moeten semantisch of menselijk beoordeeld worden.

## W9f cross-turn baseline

W9f is de belangrijkste recente statuswijziging.

De eerdere W1/W5 single-shot resultaten lieten zien dat een frontiermodel vaak zelf veel frames of gaps kan noemen. Dat zette SSL als externe single-shot detector onder druk.

W9f verschuift de claim terug naar SSL's eigen sterke mechanisme:

> wat nu nog geen antwoord is, kan later in de sessie antwoordruimte worden.

W9f operationaliseert dit via:

- echte `SSLManager`-lifecycle;
- weightless seeds;
- recurrence;
- Gate-promotie;
- TTL/TrTL;
- cluster-based recurrence voor parafrastische herhaling;
- representative-based promotie in plaats van clusterbrede overpromotie;
- blind A/B-review-pack als kwaliteitscontrole.

### W9f-follow-up baseline

De follow-up baseline na PR #148 corrigeerde twee belangrijke punten:

- centroid-weging en recurrence-telling zijn gescheiden;
- representatives blijven levend wanneer recurrence via non-representative members binnenkomt.

De release `w9f-follow-up-baseline` bevriest deze stand.

De laatste review-artifact met blind A/B-pack bevatte 8 cross-turn payoff items, met gebalanceerde A/B-toewijzing:

- `CONV_STARTUP`: 4 review-items;
- `CONV_CITY`: 4 review-items;
- `CONV_IR_SHORT`: 0 review-items;
- SSL als A: 4;
- SSL als B: 4.

### Interpretatie van de blind review

De blind review moet niet worden gelezen als klassieke model-vs-model benchmark.

Zonder SSL zouden de SSL-gestuurde antwoordvarianten niet als optie hebben bestaan. De review beoordeelt dus of door SSL geopende antwoordruimte bruikbaar is, niet of GPT-4.1 in abstracto wordt verslagen.

De review liet zien:

- meerdere SSL-gestuurde antwoorden werden als rijker, scherper of bruikbaarder beoordeeld;
- `CONV_CITY` bleef het sterkste signaal;
- `CONV_STARTUP` liet risico op seed-vernauwing zien;
- seed-ruis is een foutklasse voor gebruiksdiscipline, geen bewijs dat de levenscyclus niet werkt.

### W9f-besluit

W9f wordt geaccepteerd als werkende technische baseline voor cross-turn context-discovery en memory-surfacing.

Er komt geen nieuwe W9f-validatielus alleen om opnieuw te bewijzen dat het mechanisme bestaat.

## Wat de repo vandaag hard aantoont

De repo toont vandaag overtuigend aan dat:

1. de SSL-levenscyclus technisch aanwezig is;
2. `trace` en `weight` gescheiden blijven;
3. TTL/TrTL reactivatie en verval operationeel maken;
4. de Gate sterker is dan zwakkere promotieregels op de huidige adversarial set;
5. probe-feedback lifecycle-effecten heeft;
6. handelen op geldige seeds bij capabele modellen antwoordruimte kan verbeteren;
7. cross-turn surfaced seeds in W9f bruikbare extra antwoordruimte kunnen openen.

## Wat de repo niet moet claimen

Niet claimen:

- SSL maakt elk antwoord beter;
- SSL verslaat GPT-4.1 algemeen;
- elke promoted seed is waardevol;
- open-set seedkwaliteit is volledig opgelost;
- scenario-onafhankelijkheid is al hard bewezen;
- modelinterne validatie is operationeel.

## Praktische betekenis voor repo-beslissingen

De repo moet vanaf hier drie dingen doen:

1. de regressie- en lifecyclelaag behouden;
2. W9f niet opnieuw openen als bewijsronde tenzij er echte regressie is;
3. de volgende onderzoeksstap richten op transfer van de doctrine.

Dat betekent concreet:

- scenario-suites blijven nuttig als regressie;
- blind A/B blijft nuttig als kwaliteitscontrole op antwoordruimte;
- seed-vernauwing en seed-ruis moeten expliciet als foutklasse blijven staan;
- W10 moet meten of dezelfde lifecycle buiten de huidige scenario's werkt.

## Aanbevolen volgende documenten

Leidend na deze update:

- `docs/00_shadow_seed_learning_4_6.md` — canonieke theorie;
- `docs/research/w9f-evaluatieconclusie.md` — W9f-besluit;
- `docs/research/evaluation-matrix.md` — laagstatus;
- `docs/research/scenario-independence-roadmap.md` — overgang naar transfer.

## Korte eindkwalificatie

De repo is vandaag:

> een sterke SSL-researchharness met bewezen lifecycle-mechaniek, eerste echte open-set en adversarial evidence, en een geaccepteerde W9f-baseline voor cross-turn context-discovery en memory-surfacing. De brede algemene claim blijft begrensd: de volgende stap is transfer van de doctrine naar andere domeinen, taken en modellen, niet nog meer bewijs dat W9f bestaat.
