# Laag G scoping: van dialectische falsificatie naar modelintern signaal

> Status: current
> Date: 2026-07-02
> Evidence layer: scoping-notitie voor Laag G (geen meting)
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

**Nog te doen (de echte sonde):** een run op een klein open model
(`--backend hf --model-id ...`) met een échte dialectische verdictbron in
plaats van de fixture-labels, over de fixture- én transfer-sets; pas daarná
is een uitspraak over interne steun aan de orde.

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

- Spoor 1 is klaar als instap zodra de harness in CI staat (deze PR) en één
  echte modelrun een leesbaar verdict-artifact oplevert.
- Spoor 2 begint met een reproduceerbare activatie-sonde op één klein model;
  pas daarna is een uitspraak over "interne steun" aan de orde.
- Dit document is de PvA-V2 scoping-notitie; de PvA kan V2 afvinken zodra
  spoor 1 gemerged is.

## Claimgrens

Dialectische falsificatie toetst houdbaarheid tegen één bron met één model —
geen waarheidsoordeel. De H-neuron-sonde is verkennend; niets hierin verandert
de bestaande claimgrenzen van lagen A–F.
