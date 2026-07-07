# SSL integrale evaluatie — de hele stack, eerlijk gewogen (lagen A–G)

> Status: current
> Date: 2026-07-07
> Evidence layer: integrale synthese over lagen A–G (geen nieuwe meting)
> Current source: yes
> Refs: `docs/00_shadow_seed_learning_4_6.md` (canon), `positioning-synthese.md`,
> `current-status.md`, `evaluation-matrix.md`, rounds 005–029

## Doel

Dit document weegt SSL **als geheel**: wat elke stap in het onderzoek heeft
opgeleverd, van de mechanische kern tot de modelinterne verkenning, en wat het
samen wél en niet draagt. Het is een synthese, geen nieuwe meting.

Twee dingen vooraf, eerlijk:

1. **De lagentaxonomie loopt A–G** (`docs/00_shadow_seed_learning_4_6.md`), waarbij
   **Laag G = modelinterne research** — dat is de laag waar het H-neuron-spoor
   (Gao et al. 2025) en de activatie-sonde in zitten. Er is geen aparte "laag H";
   "t/m laag H" = de volledige stack inclusief dat H-neuron-werk.
2. **Geen totaalscore.** De lagen blijven gescheiden; een sterke laag A maakt een
   zwakke laag C niet goed. Dat is de kern van de 4.6-evidence-discipline.

## Per laag: wat is er bereikt

### Laag A — Regressie · **Sterk**
CI-ruggengraat: 354 tests (4 skipped), coverage ~82%, manager-/lifecycle-tests,
benchmark-smokes. De minimale SSL-definitie is technisch aanwezig en bewaakt:
atomische seeds, `trace`≠`weight`, `weight` start op 0.0, TTL-verval,
TrTL-reactivatie, EXPIRED terminaal, promotie alleen via de Validation Gate.
Dit is het verschil tussen een los benchmarkidee en een reproduceerbare
kernarchitectuur.

### Laag B — Kleine benchmarkvalidatie · **Bruikbaar (bewust smal)**
Vaste, controleerbare casussen als regressie en beperkte benchmark. Geschikt om
de basis betrouwbaar te houden, niet als eindclaim.

### Laag C — Open-set seedkwaliteit · **Eerste echte evidence, gemengd**
Mens- en AI-reviews (rounds 005–007, κ≈0.63) tonen dat SSL relevante seeds
maakt op onbekende tekst, maar ook dat die vaak **triviaal of weinig toetsbaar**
zijn. De waarschuwing is niet "SSL vindt niets", maar "gevonden ≠ waardevol".

### Laag D — Adversarial ruiscontrole · **Eerste echte evidence**
De Gate is sterker dan trace-only-achtige baselines op de adversarial fixture.
Kernles: een capabel model is een redelijke backstop tegen valse feiten, maar
niet tegen irrelevante seed-injectie — daarom blijft `weight=0` tot
Gate-promotie de veiligheidslaag, geen formaliteit.

### Laag E — Probe utility / payoff · **Mechanisme bevestigd; kwaliteit reviewer-afhankelijk**
De rijkste en meest bevochten laag. Het traject:

- **W9c/d (round 019):** eerste positief — cross-turn seeds maken latere
  antwoorden rijker; 2 blinde reviewers **92% en 98%** eens met de AI-jury.
  Grens: onder-doctrine drempels, n=10, gekozen thema's.
- **W9e/f (rounds 020–021):** cluster-recurrence + representative-only promotie
  laten het mechanisme op **veilige** doctrine-drempels vuren (0.85 dedup,
  Gate-bar 3) — het verzoent round-014-veiligheid met round-019-payoff.
- **Round 022:** eerste blinde review op veilige drempels kwam **gespleten**
  terug (2 reviewers oneens op 7/8; overeenstemming ~0.125). De ruis zat in
  *gevalideerde, promoted* seeds → een use-time-disciplinevraag.
- **Round 023:** use-time discipline (`surface_top_k=2` + potentieel-niet-must)
  dempte de ruis vrijwel (~3%), overeenstemming naar **~0.67**, seed-effect
  "sturen bij aanscherping, stil bij irrelevantie". Win-rate ≤0.5; maar op de
  seed-effect-as: **20/30 labels "helpt"** (3 reviewers × 10 items), 10 neutraal,
  **0× ruis/vernauwt** — tegenover round 022 (vóór discipline): 12/16 helpt,
  3× ruis.

Netto, op twee assen (zie "Twee assen" hieronder): op de **winnaar-as** wint
SSL de head-to-head niet (win-rate ≤0.5 tegen een sterke baseline); op de
**seed-effect-as** zeggen reviewers in de meerderheid van de beoordelingen dat
de seed naar een beter antwoord *helpt*, en verdwijnt ruis vrijwel volledig
zodra de use-time discipline aanstaat.

### Laag F — Domein- en taaktransfer (W10) · **Eerste voorzichtig positief verdict**
Round 025 (afkap-vrij pack, 3 nieuwe domeinen, gpt-4.1, 0/14 afgekapt): blinde
consensus (2 protocol-conforme reviewers) voor de SSL-kant op **4/7** items —
waaronder **álle t6-valkuilvragen** —, consensus-baseline 1/7, 2 gespleten;
**ruis 0**; overeenstemming ~0.71 (hoogste tot nu toe). Het round-023-patroon
("sturen bij aanscherping") **repliceert cross-domein**. Grenzen: n=7, één
model, auteur-gekozen thema's. Op de seed-effect-as was round 025
unaniem: **14/14 labels "helpt"** (r1 7/7, r2 7/7), 0× ruis.
**Replicatie op gpt-4o (round 029) tempert de winnaar-as:** eerste reviewer
(n=1) gaf win-rate 0.50 en labelde het seed-effect op de vroege (t04) beurten
als "veroorzaakt ruis" (seed-gedreven off-topic-sturing; de strikte
noise-/hallucinatie-kolommen bleven schoon) — de head-to-head-winst van round
025 is dus deels gpt-4.1-specifiek en model-/beurttype-afhankelijk. Maar op de
seed-effect-as helpt de seed óók op gpt-4o in de meerderheid: **6/9 "helpt"**,
en HEALTH transfereert schoon (3/3, "helpt duidelijk").
Een echt round-029-verdict vraagt ≥2 reviewers; tot dan blijft F "voorzichtig
positief": begrensd op de winnaar-as, conditioneel bevestigd op de
seed-effect-as.

### Laag G — Modelinterne research (H-neuron-spoor) · **Eerste iteratie doorlopen — schoon nul**
Twee sporen (`laag-g-scoping.md`):
- **Spoor 1 — dialectische falsificatie** (`run-dialectic-falsification`): een
  model argumenteert een promoted seed weg tegen de bron; WEERLEGD → Gate-
  contradictie, HOUDT_STAND → bounded feedback (nooit promotie), ONBESLIST →
  neutraal. Geland, getest.
- **Spoor 2 — activatie-sonde** (`run-activation-probe`): token-scoped pooling +
  permutatie-controle, gemeten op distilgpt2/pythia-14m/-31m (fixture-labels) en
  op distilgpt2 + pythia-14m met **gpt-4.1 als echte oordeelbron** (round 028).
  Resultaat: **geen scheiding boven toeval** — een klein Engels model codeert
  gpt-4.1's Nederlandse houdbaarheidsoordeel niet lineair. Een null is hier het
  **correcte** antwoord, geen falen; signaal ≠ verdict, raakt lagen A–F niet.
  Een positieve uitspraak vraagt een NL-capabel/groter model — open richting.

## Twee assen: winnaar-as vs seed-effect-as

De blinde A/B-reviews produceren *door hun opzet* een winnaar-metriek — de
reviewer móet kiezen, ook als beide antwoorden goed zijn. Die metriek is
eerlijk gerapporteerd, maar hij is **niet de vraag van de repo**
(`positioning-synthese.md`: win-rate is nooit hoofdmetriek). De vraag is:
*helpt SSL naar een beter antwoord?* Daarvoor is het
`seed_effect_after_choice`-label de directe meting. Alle gecommitte labels
(rounds 022–029, 69 beoordelingen):

| Ronde | Labels | Helpt (duidelijk+beetje) | Geen verschil/neutraal | Ruis/vernauwt |
|---|---|---|---|---|
| 022 (vóór discipline) | 16 | 12 | 1 | **3** |
| 023 (met discipline) | 30 | 20 | 10 | 0 |
| 025 (transfer, gpt-4.1) | 14 | **14** | 0 | 0 |
| 029 (transfer, gpt-4o, n=1) | 9 | 6 | 1 | 2 (beide t04) |
| **Totaal** | **69** | **52 (~75%)** | 12 | 5 |

De eerlijke lezing van beide assen samen:

- **Winnaar-as:** SSL wint de head-to-head niet structureel (win-rate ≤0.5 in
  023 en 029; 4/7 consensus in 025). De baseline is hetzelfde frontier-model op
  z'n best — 50/50 betekent "even goed", niet "schaadt".
- **Seed-effect-as:** in **~75% van alle beoordelingen** zegt de reviewer dat de
  seed naar een beter antwoord helpt; ruis is zeldzaam (5/69) en geconcentreerd
  waar de discipline (nog) niet dekt — round 022 vóór use-time discipline, en de
  vroege t04-beurten in round 029.
- **Conditioneel het sterkst:** aanscherpings- en valkuilvragen (round 025: alle
  t6-valkuilvragen consensus-SSL) en het HEALTH-domein (round 029: 3/3).

Dit is geen herinterpretatie achteraf maar het toepassen van de eigen doctrine:
de A/B-review is kwaliteitscontrole op door SSL geopende antwoordruimte; de
seed-effect-as meet de eigenlijke claim.

## De laag die niet in A–G staat, maar het onderscheidende draagt

Buiten de bewijslagen, maar wél repo-feit en de **verdedigbare kern** van SSL
(zie `positioning-synthese.md`, issue #46 gesloten):

- **`shadowseed_agent`-contract** — invloed alleen na Gate-promotie én
  hercheck op gebruiksmoment (weight>0, PROMOTED, gelogde promotie, geen
  contradictie); elke poging tot invloed gelogd; replaybare audit faalt hard op
  gewichtloze invloed.
- **`shadowseed chat`** — de levende schaduwlaag operationeel: seed gewichtloos
  geboren → schaduw → Gate → stuurt pas daarna een latere beurt (visie-item 5).
- **SSL→RAG-brug** — promoted seeds proben een corpus; `seed_only_chunk_ids` is
  aanwezigheid, geen sturing (visie-item 2).
- **Retrieval-doctrine** — getest beleid: "gevonden" muteert nooit gewicht,
  status of trace. Gevonden ≠ waar ≠ sturend.

## Wat SSL als geheel wél draagt

1. Een reproduceerbare, bewaakte lifecycle-kern (A) met echte adversarial
   veiligheidsevidence (D).
2. Een **afdwingbare, auditeerbare geheugendiscipline**: gewichtloos tot
   verdiend, contract-gecheckt op gebruik, replaybaar, falsifieerbaar — in code
   en CI, niet alleen op papier. Dít is het onderscheidende dat geen
   frontiermodel-prompt zomaar evenaart.
3. Een bevestigd cross-turn *mechanisme* (E) dat met use-time discipline
   ruisarm is en, blijkens W10 (F), **cross-domein overdraagt** — voorzichtig
   positief.
4. Op de **seed-effect-as**: reviewers oordelen in ~75% van alle gecommitte
   beoordelingen (52/69, rounds 022–029) dat de seed naar een beter antwoord
   *helpt* — het sterkst op aanscherpings-/valkuilvragen en in HEALTH, met
   ruis geconcentreerd waar de discipline (nog) niet dekt.

## Wat SSL als geheel (nog) niet draagt

- dat SSL de **head-to-head wint** van hetzelfde model zonder seeds — win-rate
  ≤0.5 op de winnaar-as (E); de seed helpt vaker dan hij wint;
- dat elke promoted seed waardevol is — laag C blijft gemengd;
- brede domein-onafhankelijkheid — W10 is n=7 op gpt-4.1; de gpt-4o-replicatie
  (round 029, n=1 reviewer) kwam op de winnaar-as zwakker terug (0.50,
  seed-gedreven off-topic-sturing op t04) → head-to-head-transfer is
  modelafhankelijk (F);
- **modelinterne steun** — op kleine modellen niet aangetoond (G, correcte null);
- volledige productmatige betrouwbaarheid van automatisch seed-gebruik.

## Overall — één eerlijke zin

> SSL is een sterke, gedisciplineerde researchharness met een bewezen
> lifecycle-kern en, als onderscheidende verdedigbare bijdrage, een
> afdwingbare en auditeerbare geheugendiscipline; het cross-turn mechanisme
> vuurt, en op de seed-effect-as oordelen reviewers in ~75% van alle
> beoordelingen dat de seed naar een beter antwoord helpt — de seed **helpt
> vaker dan hij de head-to-head wint** (win-rate ≤0.5 tegen hetzelfde
> frontier-model), met de winst conditioneel het duidelijkst op
> aanscherpings-/valkuilvragen en in HEALTH; modelinterne steun is op kleine
> modellen niet aangetoond — precies de begrenzing die de doctrine
> ("gewichtloos tot verdiend, signaal ≠ verdict, geen totaalscore") ook van
> onszelf eist.

## Waar het bewijs het dunst is (eerlijke prioriteit)

1. **F — transfer:** round 029 heeft nog maar n=1 reviewer; ≥1 extra reviewer
   op hetzelfde gpt-4o-pack is de meest waardevolle volgende bewijsstap.
2. **E — payoff-kwaliteit:** de seed-effect-as (helpt ~75%) leunt op
   reviewer-labels met beperkte n per ronde; een taaktype waar SSL ook de
   head-to-head structureel wint is nog niet geïsoleerd, en de vroege-beurt
   (t04) sturing is een open disciplinevraag.
3. **C — seedkwaliteit:** relevant maar triviaal blijft de open zwakte aan de
   detectiekant.
4. **G — modelintern:** vraagt een NL-capabel/groter model vóór enige positieve
   uitspraak; blijft exploratief.

## Claimgrens van dit document

Synthese en weging, geen meting. Het versieren van één getal over alle lagen is
bewust vermeden — dat zou de evidence-discipline breken die SSL juist
onderscheidt.
