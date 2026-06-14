# Shadow Seed Learning — visie-aanscherping: van "kunnen staan" naar "moeten staan"

**Status:** richtinggevend visiedocument (voorstel). Geen bewijs, geen
evaluatieclaim. Het scherpt de *bedoeling* van SSL aan en zet het pad uit naar
wat de repo nog niet kan. Bij botsing over mechaniek blijft
`docs/00_shadow_seed_learning_4_6.md` leidend; dit document verfijnt het
doelbeeld dat 00_ beschrijft.

> Ontstaan uit een gesprek (2026-06-14) na de eerste end-to-end payoff-meting
> (round 008). Het legt vast wat shadow seeds *uniek* maakt, omdat de huidige
> canon en evaluatiematrix in de praktijk op iets smallers optimaliseren
> (volledigheid) dan de visie vraagt.

---

## 1. De kern: "wat had hier kunnen staan", niet "wat had hier moeten staan"

De gangbare lezing van een gap is een **omissie**: een verwacht element dat
ontbreekt. Dat is completeness-toetsing — nuttig, maar klein. Het is ook wat de
detector tot v0.3g feitelijk deed, en waarom open-set seedkwaliteit op
"relevant maar triviaal" bleef hangen (round 005–007).

De eigenlijke ambitie is generatief:

> **Wat had hier kunnen staan** — een invalshoek, een kader, een relatie die het
> antwoord had kunnen optillen — en die misschien tot een beter antwoord leidt
> dan een LLM, óók met RAG, ooit zelf zou vinden?

"Moeten staan" is een checklist. "Kunnen staan" is de niet-genomen weg, de
aangrenzende mogelijkheid. Dat onderscheid is geen nuance; het bepaalt of SSL
een volledigheidscontrole is of een navigatie-instrument.

## 2. Waarom dit voorbij RAG reikt

- **RAG haalt op wat bestaat en wat de query activeert** — antwoorden op vragen
  die je al kunt formuleren, uit een corpus dat al geschreven is. Bekende
  onbekenden. Het plafond van RAG is "alles wat vindbaar is".
- **Een shadow seed is de vraag die je niet wíst te stellen.** Hij ontstaat niet
  uit een query tegen een corpus, maar uit de *vorm van dít antwoord in de eigen
  latente ruimte van het model*. Daarmee zit hij **stroomopwaarts van RAG**: een
  seed kan de zoekopdracht genereren die RAG nooit had gevormd (dat is de
  Retrieval Probe — de seed stuurt de retrieval, niet andersom).

Het overschot is intrinsiek én contextueel: niet "wat zegt de encyclopedie dat
mist", maar "wat zegt mijn eigen representatie dat hier opvallend afwezig is,
juist hier". Geen externe index kent de vorm van díé afwezigheid. RAG *stapelt*
feiten; een goed geplaatste seed **herkadert** — en één herkadering kan een
antwoord meer optillen dan duizend opgehaalde feiten.

## 3. De unificatie: gewicht is de as van mogelijkheid → noodzaak

Het beslissende inzicht: "kunnen staan" en "moeten staan" zijn **geen twee
soorten seeds, maar dezelfde seed op verschillende punten van de gewichtsas.**

```
geboorte                                            consolidatie
"had hier KUNNEN staan"  ───── weight stijgt ─────► "moet hier staan"
weight = 0.0                  via de Gate            weight hoog
speculatief, in de schaduw    (herkenning +          gevestigd, mag sturen
kost niets als het niets is    evidentie +
                               overleefde falsificatie)
```

- Een seed wordt geboren als **mogelijkheid** — gewichtloos, in de schaduw.
- Naarmate hij validatie verdient (de Validation Gate), stijgt zijn gewicht.
- Bij genoeg gewicht is de mogelijkheid een **noodzaak** geworden: nu staat vast
  dat dit hoort, het *moet* er zijn.

Dit is precies de geheugenconsolidatie-analogie uit 00_: een fragiel
kandidaat-engram dat via reactivatie en hertoetsing consolideert en daarna
actief nieuwe situaties helpt begrijpen. De `trace`/`weight`/Gate-machinerie die
al in de repo staat **ís** deze mogelijkheid→noodzaak-motor.

### Gevolg voor de detector

De `weight = 0.0`-geboorte is geen technisch detail maar de vergunning om
ambitieus te zijn: een speculatieve "kunnen"-seed **kost niets zolang hij niets
is, en levert geen ruis op** — hij wacht gewichtloos in de schaduw. Daarom mag
de detector generatief en gedurfd zijn; de gewichts- en Gate-laag sorteert wel
welke mogelijkheden uitharden tot noodzaak.

De timide detector (alleen veilige omissies → triviaal) was dus een
*onderbenutting* van de architectuur, niet een grens ervan. Kracht en
discipline zijn dezelfde munt: hoe generatiever de seed, hoe essentiëler de
gewichtloze geboorte en de falsificatie-toets.

## 4. Wat hiervoor nog niet in de repo staat (het pad)

Geverifieerd tegen de code op 2026-06-14. De repo bouwt de *toevoer en
boekhouding* van seeds goed (detectie, gewichtloze opslag, Gate, levenscyclus,
constellations) plus een losse, gewone RAG-pijplijn. De stukken die SSL *uniek
en voorbij-RAG* maken ontbreken nog, geprioriteerd:

1. **Generatieve seed-modus ("kunnen staan").** De detector is nu volledig
   afwezigheids-/omissie-gericht (`open_set_model_detector.py`). Een modus die
   de niet-genomen weg / het ontbrekende kader genereert ontbreekt. Dit is de
   linchpin — alle volgende stappen hebben deze als input. Doctrine-veilig:
   generatie levert gewichtloze kandidaten; waarde wordt downstream geoordeeld
   (`02_atomic_seeds` §2).
2. **Retrieval Probe operationeel (de brug SSL→RAG).** De manager berekent een
   constellation-centroid en zet `probe_type="retrieval"`, maar niets consumeert
   die centroid om echt te zoeken en het antwoord te verrijken. De twee helften
   (seeds, retrieval) staan los; juist de verbinding laat een seed vinden wat
   RAG niet vindt.
3. **SSL-seed vs RAG head-to-head.** Er is geen test van de claim "beter dan een
   LLM met RAG ooit zelf zou vinden". Nodig: dezelfde vraag/corpus, waarbij de
   seed een richting opent die gewone RAG mist. Dit *bewijst* de unieke waarde.
4. **Echte falsificatie voor speculatieve seeds.** De contradiction-check is nu
   lexicaal/numeriek. Generatieve "kunnen"-seeds liggen dichter bij hallucinatie
   en vragen een echte dialectische "valt dit weg te argumenteren?"-toets, zodat
   ambitie veilig gewicht kan verdienen.
5. **Levende schaduw-geheugenlaag over beurten.** De levenscyclus is unit-getest
   maar nooit end-to-end getoond: seed geboren in beurt 1 → dormant in de
   schaduw → gereactiveerd/gevalideerd in beurt 3 → stuurt dán pas. De "shadow"
   in shadow seed heeft nog geen operationele demonstratie.

## 5. Wat dit betekent voor de evaluatiekoers

De payoff-test (round 008) gaf de scherpste les: SSL hielp alleen waar het
handelen op seeds **geen schade** deed (de gewichtloze, additieve injectie:
3/3) en faalde waar een vrije herschrijving met ongewicht over het antwoord
heerste (1/3). De Gate-filosofie geldt dus niet alleen voor *welke* seeds actief
worden, maar voor *hoe* ze de wereld raken. Dezelfde discipline — gewichtloos
tot verdiend — is de maat voor zowel detectie als gebruik.

De koers verschuift daarmee van "meer/scherper detecteren van omissies" naar:
**genereer gedurfde mogelijkheden, houd ze gewichtloos, laat de Gate ze tot
noodzaak promoveren, en gebruik alleen wat gewicht verdiend heeft — gericht op
het antwoord dat besloten ligt in wat het model níét zei.**

Dit blijft richting, geen bewijs. Elke stap hierboven hoort de 4.6
evidence-discipline te volgen: gescheiden lagen, geen totaalscore, eerlijk over
wat vandaag werkt en wat doelbeeld is.
