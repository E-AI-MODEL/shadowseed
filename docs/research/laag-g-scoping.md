# Laag G scoping: van dialectische falsificatie naar modelintern signaal

> Status: current
> Date: 2026-07-04
> Evidence layer: Laag G — scoping + eerste iteratieve metingen (rounds 026–028)
> Current source: yes
> Refs: PvA V2 ("scoping-notitie of eerste sonde"), visie-item 4

## Aanleiding

Met de levende schaduwlaag (PR #164), de SSL→RAG-brug (PR #166) en het
positioneringsbesluit (issue #46) is visie-item 4 het laatste onbebouwde punt
van het pad: **echte falsificatie voor speculatieve seeds**, uiteindelijk
modelintern (Laag G). De maintainer heeft dit spoor geopend (2026-07-02).

De contradiction-check van de Gate is vandaag lexicaal/numeriek. Generatieve
"kunnen staan"-seeds vragen meer: een toets die de seed actief probeert weg te
argumenteren, en op termijn een intern modelsignaal dat die toets fundeert.

## Twee sporen

**Spoor 1 — dialectische falsificatie (nu gebouwd).**
`dialectic_falsification.py` + `run-dialectic-falsification`: een model krijgt
bron en stelling en probeert de stelling weg te argumenteren (gedekt, overbodig
of strijdig?). Verdict-mapping, hard in code:

- `WEERLEGD` → contradictie via de Validation Gate: gewicht daalt, het
  agent-contract blokkeert de seed;
- `HOUDT_STAND` → bounded probe-feedback (`probe_type="dialectic"`): kan
  gewicht beperkt bevestigen maar **nooit promoveren**;
- `ONBESLIST` (ook de fail-safe bij onparseerbare output) → neutraal.

De runner promoveert fixture-seeds eerst via de échte Gate en valt ze dán aan:
falsificatie precies op de seeds die zouden mogen sturen. Deterministisch
getest via een fixture-backend; echte runs volgen dezelfde backend-vlaggen als
de andere routes.

**Spoor 2 — H-neuron-achtige interne sonde (harnas gebouwd, echte run open).**
Gao et al. 2025 (arXiv 2512.01797, code thunlp/H-Neurons, MIT) identificeren
hallucinatie-geassocieerde neuronen in LLM's. De Laag G-vraag voor SSL: is er
*interne* steun voor wat extern als ontbrekend/onhoudbaar wordt gemeten?

Gebouwd (`activation_probe.py` + `run-activation-probe`):

1. model-vrije, deterministische analysekern: per laag de cosine-afstand
   tussen de klasse-centroïden (WEERLEGD vs HOUDT_STAND) plus de
   kandidaat-dimensies met het grootste verschil — kandidaten, geen bewezen
   neuronen;
2. `HFActivationModel` (opt-in, `models`-extra): forward-hooks op de
   MLP-lagen van een klein HF-model tijdens het dialectische verdict;
3. `FakeActivationModel` voor CI: hash-gedreven activaties zonder
   klasse-informatie — bewijst uitsluitend de harnas-mechaniek;
4. artifact `activation_probe.json`, `evidence_layer: "G"`, doctrine-regel in
   het artifact zelf.

**Eerste echte runs (2026-07-03, twee modellen, twee routes):**

- Actions-route: `distilgpt2` (run 28639320528, artifact `activation-probe`
  id 8058091841) — sterkste laag `transformer.h.2.mlp.c_proj`,
  cosine-afstand **0.0054**;
- sandbox-route via de git-model-mirror: `EleutherAI/pythia-14m` (branch
  `model-mirror/EleutherAI-pythia-14m`) — alle 6 GPTNeoX-MLP-lagen gevangen,
  sterkste `gpt_neox.layers.1.mlp`, cosine-afstand **0.0013**.

Lezing, eerlijk: de mechaniek werkt end-to-end op echte gewichten in twee
architecturen, maar de gemeten scheiding is verwaarloosbaar — en dat is
grotendeels **per constructie**: de prompts zijn ~95% identiek (zelfde bron +
instructie, alleen de stelling verschilt) en mean-pooling over de hele
sequentie verdunt het stellingsverschil weg. Bovendien n=3 (2 vs 1) en beide
modellen zijn Engels-getraind op Nederlandse prompts. Dit zegt dus níets over
interne steun, positief noch negatief.

**Iteratie 2 (2026-07-03): token-scoped pooling gebouwd en gemeten.**
`--pooling stelling` (nu default) poolt alleen de stelling-tokens via
char-offset-mapping. Op pythia-14m met dezelfde cases: sterkste laag van
0.0013 → **0.2097** (×160), consistent laagprofiel (vroeg/midden draagt het
verschil). Dit is een instrument-validatie, geen signaalvondst — bij n=3
produceert élk lexicaal verschil scheiding. Zie round 026.

**Iteratie 3 (2026-07-03): permutatie-controle + transfer-cases — schoon
nulresultaat.** `permutation_control` (exact bij klein n, anders Monte Carlo)
zit nu in elk probe-rapport; op 10 transfer-cases (7 echte round-025 seeds +
distractors, mechaniek-labels) scheidt op pythia-14m **geen enkele laag boven
toeval** (p 0.24–0.81, exact over 210 toewijzingen). De ×160-"scheiding" uit
iteratie 2 (n=3) stort onder de shuffle in — lexicaal toeval, geen signaal.
Het instrument rapporteert dus correct néé waar néé hoort. Zie round 027.

**Iteratie 4 (2026-07-03): verdictbron ontkoppeld van gesondeerd model.**
`run-activation-probe --verdicts <dialectic-artifact>` leest echte
verdict-labels uit een `dialectic_falsification`-run in plaats van de
fixture-mechaniek. Daarmee is de zuivere Laag G-vraag stelbaar: **encodeert
een klein model intern het houdbaarheidsoordeel dat een sterk model velt?**
De workflow `activation-probe-real-verdict.yml` ketent het: stap 1 laat
gpt-4.1 oordelen (`--backend openai`), stap 2 sondeert een klein model met
díe labels. Verdictbron en gesondeerd model zijn bewust ontkoppeld; het
artifact draagt `verdict_source: "extern"`.

**Iteratie 5 (2026-07-04): eerste inhoudelijke meting — schoon nulresultaat.**
De `activation-probe-real-verdict`-workflow liep end-to-end: gpt-4.1 oordeelde
de houdbaarheid (7 WEERLEGD / 2 HOUDT_STAND / 1 ONBESLIST over de 10
transfer-stellingen), distilgpt2 werd met díe labels gesondeerd. Sterkste laag
`transformer.h.0.mlp.c_proj` cosine 0.102 maar **permutatie-p 0.833** (vloer
0.028) — geen scheiding boven toeval. distilgpt2 codeert gpt-4.1's oordeel niet
lineair. Een null is hier het correcte antwoord (82M Engels model, NL-oordeel);
signaal ≠ verdict, de null raakt lagen A–F niet. Zie round 028.

**Iteratie 6 (2026-07-07, gebouwd — run open): NL-capabel model + 24 cases.**
Beide open punten uit iteratie 5 zijn nu bebouwd
(`dialectic_falsification_transfer_v2.json`, round 030):

1. **caseset 10 → 24** (zelfde brontekst voor vergelijkbaarheid): de 10
   originele cases plus 14 nieuwe met bewuste ontwerp-intentie — 7 kandidaat
   echt-ontbrekende punten, 5 bron-parafrases ("al gedekt"), 2 strijdige
   stellingen — zodat beide klassen plausibel gevuld raken en de
   permutatievloer daalt van 1/36 naar Monte-Carlo-niveau (~0.002, lokaal
   geverifieerd met de fixture-keten);
2. **NL-capabel gesondeerd model**: `GroNLP/gpt2-small-dutch` (GPT-2-
   architectuur, dus de bestaande `.mlp.c_proj`-hooks passen ongewijzigd) via
   de bestaande `activation-probe-real-verdict.yml` (geparametriseerd op
   `probe_model_id` en `input_path`) — gpt-4.1 blijft de oordeelbron.

De ontwerp-intenties in de notes zijn géén labels: labels komen op runtime
van gpt-4.1, en de sonde meet vervolgens of het NL-model dat oordeel intern
lineair codeert. Ook hier blijft een null een geldig antwoord — maar nu op
een model dat het oordeel plausibel kán encoderen, met een vloer die laag
genoeg is om een echt signaal te kunnen zien.

Pas bij zo'n plausibel model is een positieve uitspraak over interne steun
realistisch — en blijft ook dan een null een eerlijk, geldig antwoord.

## Doctrine-regels (gelden voor beide sporen)

- Een intern of dialectisch signaal is **falsificatie- of evidence-input**,
  nooit directe promotie: promotie blijft exclusief aan de Gate.
- Dialectiek kan invloed alleen **wegnemen** (Gate-contradictie) of **beperkt
  bevestigen** (bounded probe-feedback); de fail-safe bij twijfel is neutraal.
- "Gevonden" blijft nooit "waar" of "sturend"; een seed die de dialectiek
  overleeft is nog steeds potentieel, geen must.
- Laag G rapporteert per de bestaande laag-taal: geen totaalscore, signaal
  gescheiden van oordeel.

## Klaar-criteria

- Spoor 1 (dialectische falsificatie) is geland en in CI; echte modelruns
  leveren leesbare verdict-artifacts. **Klaar als instap.**
- Spoor 2 (activatie-sonde) is als eerste iteratie doorlopen: harnas +
  token-scoped pooling + permutatie-controle, gemeten op twee modellen en met
  gpt-4.1 als echte oordeelbron. **Resultaat: schoon nulresultaat** (rounds
  026–028) — geen bewijs van interne steun, wat het correcte antwoord is voor
  kleine Engelse modellen. Een positieve uitspraak vraagt een NL-capabel,
  groter model + meer cases; dat is open richting, geen must.
- PvA-V2 is afgevinkt (deze scoping + de gelande sonde).

## Claimgrens

Dialectische falsificatie toetst houdbaarheid tegen één bron met één model —
geen waarheidsoordeel. De H-neuron-sonde is verkennend; niets hierin verandert
de bestaande claimgrenzen van lagen A–F.
