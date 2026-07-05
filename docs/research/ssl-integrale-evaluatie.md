# SSL integrale evaluatie — de hele stack, eerlijk gewogen (lagen A–G)

> Status: current
> Date: 2026-07-04
> Evidence layer: integrale synthese over lagen A–G (geen nieuwe meting)
> Current source: yes
> Refs: `docs/00_shadow_seed_learning_4_6.md` (canon), `positioning-synthese.md`,
> `current-status.md`, `evaluation-matrix.md`, rounds 005–028

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
  "sturen bij aanscherping, stil bij irrelevantie". Maar **win-rate ≤0.5**.

Netto: het mechanisme vuurt en schaadt met discipline vrijwel niet en scherpt
soms aan — maar het maakt antwoorden niet gemiddeld *beter* (win-rate ≤0.5).

### Laag F — Domein- en taaktransfer (W10) · **Eerste voorzichtig positief verdict**
Round 025 (afkap-vrij pack, 3 nieuwe domeinen, gpt-4.1, 0/14 afgekapt): blinde
consensus (2 protocol-conforme reviewers) voor de SSL-kant op **4/7** items —
waaronder **álle t6-valkuilvragen** —, consensus-baseline 1/7, 2 gespleten;
**ruis 0**; overeenstemming ~0.71 (hoogste tot nu toe). Het round-023-patroon
("sturen bij aanscherping") **repliceert cross-domein**. Grenzen: n=7, één
model, auteur-gekozen thema's. **Replicatie op gpt-4o (round 029) tempert dit:**
eerste reviewer (n=1) gaf win-rate 0.50 en labelde het seed-effect op de vroege
(t04) beurten als "veroorzaakt ruis" (seed-gedreven off-topic-sturing; de
strikte noise-/hallucinatie-kolommen bleven schoon) — de round-025-winst is dus
deels gpt-4.1-specifiek en model-/beurttype-afhankelijk (HEALTH transfereert wél
schoon, EDU/POLICY niet).
Een echt round-029-verdict vraagt ≥2 reviewers; tot dan blijft F "voorzichtig
positief", nu expliciet begrensd.

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

## Wat SSL als geheel (nog) niet draagt

- dat SSL **elk antwoord beter** maakt — win-rate ≤0.5 (E);
- dat elke promoted seed waardevol is — laag C blijft gemengd;
- brede domein-onafhankelijkheid — W10 is n=7 op gpt-4.1; de gpt-4o-replicatie
  (round 029, n=1 reviewer) kwam zwakker terug (win-rate 0.50, seed-gedreven
  off-topic-sturing op t04) → transfer is modelafhankelijk (F);
- **modelinterne steun** — op kleine modellen niet aangetoond (G, correcte null);
- volledige productmatige betrouwbaarheid van automatisch seed-gebruik.

## Overall — één eerlijke zin

> SSL is een sterke, gedisciplineerde researchharness met een bewezen
> lifecycle-kern en, als onderscheidende verdedigbare bijdrage, een
> afdwingbare en auditeerbare geheugendiscipline; het cross-turn mechanisme
> vuurt en draagt voorzichtig-positief over naar nieuwe domeinen, maar de
> payoff-*kwaliteit* blijft begrensd (win-rate ≤0.5, reviewer-afhankelijk) en
> modelinterne steun is op kleine modellen niet aangetoond — precies de
> begrenzing die de doctrine ("gewichtloos tot verdiend, signaal ≠ verdict,
> geen totaalscore") ook van onszelf eist.

## Waar het bewijs het dunst is (eerlijke prioriteit)

1. **F — transfer:** n=7, één model. De gpt-4o-replicatie (loopt) + verse
   blinde review is de meest waardevolle volgende bewijsstap.
2. **E — payoff-kwaliteit:** win-rate ≤0.5; alleen "schaadt niet, scherpt soms"
   is hard. Een taak waar SSL structureel wél wint is nog niet geïsoleerd.
3. **C — seedkwaliteit:** relevant maar triviaal blijft de open zwakte aan de
   detectiekant.
4. **G — modelintern:** vraagt een NL-capabel/groter model vóór enige positieve
   uitspraak; blijft exploratief.

## Claimgrens van dit document

Synthese en weging, geen meting. Het versieren van één getal over alle lagen is
bewust vermeden — dat zou de evidence-discipline breken die SSL juist
onderscheidt.
