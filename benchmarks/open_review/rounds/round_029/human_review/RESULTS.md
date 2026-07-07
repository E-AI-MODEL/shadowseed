# Round 029 — W10 transfer-replicatie op gpt-4o: eerste reviewer (n=1)

> **Status: op de winnaar-as reproduceert gpt-4o het round-025-verdict NIET
> schoon (win-rate 0.50) — dat tempert de head-to-head-transferclaim. Op de
> seed-effect-as ("helpt de seed naar een beter antwoord?") zegt dezelfde
> reviewer 6/9 "helpt", met de 2 ruis-labels geconcentreerd op de vroege
> t04-beurten.** Let op: dit is **één** reviewer; een verdict vraagt ≥2
> (round-025-protocol). Signaal, geen verdict.

## Unblinding (geverifieerd)

Answer key gereproduceerd uit code (`scripts/make_blind_ab_review.py`,
`_balanced_ssl_a_assignments`, seed 45, **count 9**) en **onafhankelijk
bevestigd**: elke reviewer-motivatie noemt de extra invalshoek (ethiek,
psychologische factoren, sociale rechtvaardigheid, financiering) aan precies
de kant die de key als SSL aanwijst.

| Item | SSL-kant | winnaar (r1) | uitkomst | seed-effect |
|---|---|---|---|---|
| CONV_EDU-t04 | A | B | baseline | **veroorzaakt ruis** |
| CONV_EDU-t05 | A | gelijk | tie | geen verschil |
| CONV_EDU-t06 | B | A | baseline | helpt een beetje |
| CONV_HEALTH-t04 | A | A | **SSL** | helpt duidelijk |
| CONV_HEALTH-t05 | B | B | **SSL** | helpt duidelijk |
| CONV_HEALTH-t06 | A | A | **SSL** | helpt duidelijk |
| CONV_POLICY-t04 | A | B | baseline | **veroorzaakt ruis** |
| CONV_POLICY-t05 | B | B | **SSL** | helpt duidelijk |
| CONV_POLICY-t06 | B | A | baseline | helpt een beetje |

## Cijfers (reviewer 1)

- **SSL 4 / baseline 4 / 1 tie → win-rate 4/8 = 0.50.**
- Per domein: **HEALTH 3/3 SSL** (schone winst), **EDU 0/2** (+1 tie),
  **POLICY 1/2**.
- **Seed-effect "veroorzaakt ruis" op 2 items** (EDU-t04, POLICY-t04), béide op
  de SSL-kant. **Let op de bron:** dit is het `seed_effect_after_choice`-label,
  níet de strikte noise-kolommen — die bleven schoon (`no_noise_A/B` = 5/5,
  `noise_or_hallucinated_relevance` leeg). Het gaat dus om **seed-gedreven
  off-topic-sturing/vernauwing**, niet om verzonnen ruis of hallucinatie.

## Twee assen — waarom "win-rate 0.50" niet de hele conclusie is

Het blinde A/B-formaat produceert *logischerwijs* een winnaar-metriek: de
reviewer moet A of B kiezen, ook als beide antwoorden goed zijn. Maar de
doctrine (`positioning-synthese.md`) stelt expliciet dat win-rate **nooit de
hoofdmetriek** is — de review is een kwaliteitscontrole op door SSL geopende
antwoordruimte. De vraag van de repo is niet "verslaat SSL de baseline?", maar
"**helpt SSL naar een beter antwoord?**". Dat zijn twee assen:

1. **Winnaar-as (A/B head-to-head):** SSL 4 / baseline 4 / 1 tie = 0.50.
   Interpretatie-nuance: de baseline is hier óók gpt-4o op z'n best; een
   50/50-uitkomst betekent "de seed-kant is even goed", niet "de seed schaadt".
2. **Seed-effect-as (`seed_effect_after_choice`):** **6/9 "helpt"** (4×
   duidelijk, 2× een beetje), 1× geen verschil, 2× veroorzaakt ruis — beide
   ruis-labels op de vroege t04-beurten, buiten het bereik van de bestaande
   use-time discipline.

Op de tweede as — de as waar de kernclaim op leeft — helpt de seed dus in de
meerderheid van de beoordelingen óók op gpt-4o, en is het probleem specifiek
en adresseerbaar (vroege-beurt-sturing), niet diffuus.

## Wat dit betekent (eerlijk)

1. **Zwakker dan round 025.** Op gpt-4.1 kozen de twee blinde reviewers elk
   ~5/7 (≈0.71) de SSL-kant. Op gpt-4o: win-rate 0.50, en 2 seed-effect-labels
   "veroorzaakt ruis" (waar round 025 er 0 had). De round-025-uitkomst was dus
   deels **gpt-4.1-specifiek** — transfer is modelafhankelijk.
2. **De off-topic-sturing zit op de t04-beurten.** Round 023/025 dempten
   seed-ruis op de latere (t05/t06) beurten met use-time discipline; deze run
   bevat óók t04 (vroege advies-beurten), en juist dáár stuurde de seed het
   antwoord naar een minder relevante invalshoek (ethiek bij EDU-t04,
   financieringsmodellen bij POLICY-t04) — door de reviewer als
   *seed-effect* "veroorzaakt ruis" gelabeld, niet als hallucinatie (de strikte
   noise-kolommen bleven 5/5). De discipline die t05/t06 schoon houdt, dekt de
   vroegste beurt blijkbaar niet — of gpt-4o weeft seeds minder scherp dan
   gpt-4.1.
3. **HEALTH transfereert wél schoon** (3/3, "helpt duidelijk" ×3): de
   psychologische-drijfveren-seed scherpt daar consistent aan. Transfer is dus
   niet alleen model- maar ook domeinafhankelijk.

## Verdict-status

**Laag F blijft "voorzichtig positief".** Op de winnaar-as begrenst deze ronde
de claim (head-to-head-winst draagt niet zonder meer over naar gpt-4o); op de
seed-effect-as bevestigt hij hem conditioneel (6/9 helpt, HEALTH 3/3 schoon).
De open kwestie is specifiek: seed-sturing op de vroegste beurt (t04), waar de
use-time discipline van round 023/025 nog niet dekt.

**Nodig voor een echt round-029-verdict:** ≥1 extra reviewer (bij voorkeur 2)
op ditzelfde blinde pack, zodat consensus (niet één oordeel) de basis is —
exact zoals round 025. Tot dan is dit één eerlijk, temperend datapunt.

## Bestanden

- `r1_scores.csv` — reviewer 1 (blind).
- Answer key: reproduceerbaar uit code (seed 45, count 9); geverifieerd tegen
  de seed-content in de motivaties. Canonieke key in het run-artifact
  (`ssl_session_blind_ab_answer_key.json`, run 28710838639, artifact 8082998649,
  digest `756e672e…`) — te openen ná de scoring.
