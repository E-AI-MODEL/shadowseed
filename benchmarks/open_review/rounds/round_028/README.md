# Round 028 — eerste INHOUDELIJKE Laag G-meting (gpt-4.1 oordeelt, distilgpt2 gesondeerd)

> **Status: de volledige keten liep end-to-end op echte oordelen; het
> resultaat is een schoon, eerlijk NULRESULTAAT.** Geen Laag G-claim — een
> null is hier het correcte wetenschappelijke antwoord.

## Opzet

Voor het eerst is de verdictbron ontkoppeld van het gesondeerde model
(PR #175, workflow `activation-probe-real-verdict.yml`):

1. **gpt-4.1 oordeelt** de houdbaarheid van de 10 transfer-stellingen
   (`run-dialectic-falsification --backend openai`, echte dialectiek — geen
   fixture-mechaniek meer);
2. **distilgpt2 wordt gesondeerd** met díe labels, stelling-pooling,
   permutatie-controle.

Run 28701485594 (main @ 05ddd86), artifact `activation-probe-real-verdict`
(id 8080328870): `dialectic_verdicts.json` + `activation_probe_real_verdict.json`.

## Wat gpt-4.1 oordeelde (een resultaat op zich)

Van de 10 stellingen tegen de compacte samengestelde bron: **1 ONBESLIST**
(uit de meting; de sociaal-culturele EDU-seed), **7 WEERLEGD**, **2
HOUDT_STAND** (alleen "Sociale ongelijkheid als lens" en "Kosten-batenanalyse
lange vs korte termijn"). gpt-4.1 argumenteert dus de meeste seeds — inclusief
de meeste round-025 *promoted* seeds — wég tegen déze bron.

Belangrijk: dit is een **andere taak** dan de blinde A/B (round 025). Daar was
de vraag "geeft de seed een rijker antwoord?"; hier "valt de stelling weg te
argumenteren tegen precies deze compacte bron?". Een strikte dialectiek tegen
een korte bron weerlegt sneller. Geen tegenspraak met round 025, wél een
scherpe illustratie dat houdbaarheid bron- en taakafhankelijk is.

## De activatie-meting

| | waarde |
|---|---|
| gesondeerd model | distilgpt2 (hf) |
| verdict-bron | **extern (gpt-4.1)** |
| klassen | 7 WEERLEGD / 2 HOUDT_STAND (9 cases na ONBESLIST-drop) |
| sterkste laag | `transformer.h.0.mlp.c_proj` |
| cosine-afstand | 0.1021 |
| permutatie-p | **0.833** |
| haalbare vloer | 0.028 (1/36) |

**Geen scheiding boven toeval** (p 0.833, ver van de vloer 0.028). distilgpt2's
MLP-gemiddelden encoderen gpt-4.1's houdbaarheidsoordeel niet lineair.

## Lezing (eerlijk)

1. **De keten werkt en de vraag is voor het eerst écht gesteld**: een sterk
   model oordeelt, een klein model wordt gesondeerd, met controle. Dat is de
   mijlpaal — niet het getal.
2. **Het nulresultaat is het correcte antwoord, geen falen.** distilgpt2 (82M,
   Engels, GPT-2-tijdperk) heeft geen reden om een Nederlands
   houdbaarheidsoordeel intern te representeren. Een null zegt "dit kleine
   Engelse model codeert dit oordeel niet lineair in zijn MLP-gemiddelden",
   niet "de doctrine klopt niet". Signaal ≠ verdict; de null raakt lagen A–F
   niet.
3. **Wat een positieve Laag G-meting plausibel zou maken**: een model dat het
   oordeel *plausibel* kan encoderen — capabel én NL-getraind, en groot genoeg
   dat interne representatie realistisch is. Dat is de open richting, geen
   belofte.

## Volgende stap (open, geen must)

- een NL-capabel, groter gesondeerd model (fp16-downcast in de mirror nodig
  voor >31m, of directe HF-load in de Actions-route);
- meer cases zodat de permutatie-vloer lager wordt (nu 1/36 bij 9 items).

Doctrine ongewijzigd: deze route voedt geen promotie en geen claim; ze meet
of interne steun zichtbaar is, en rapporteert eerlijk als dat (nog) niet zo is.
