# Round 025 — blinde review van de afkap-vrije W10 transfer-run (3 reviewers)

> **Status: het W10 doctrine-transfer-verdict is binnen en is positief, met
> grenzen.** Drie onafhankelijke reviewers scoorden het canonieke blinde
> A/B-pack (7 cross-turn items, 3 nieuwe domeinen, gpt-4.1, run 28573062737,
> artifact 8031850899, digest `c6867a23…`; 0/14 afgekapt, 0 meta-lekken).
> De SSL-kant wint per meerderheid **6/7**; alle t6-valkuilvragen zijn
> **unaniem** voor de SSL-kant; ruis- en vernauwingsnotities: **nul** bij alle
> drie reviewers. Eén reviewer (R3) week af van het blinde protocol
> (seed-bewust beoordeeld) en telt als aparte kwaliteitslezing.

## Unblinding

Answer key gereproduceerd uit code (`scripts/make_blind_ab_review.py`,
`_balanced_ssl_a_assignments`, seed 45, 7 items in run-volgorde) en
onafhankelijk bevestigd door de seed-verweving in de antwoordteksten zelf —
beide routes geven identiek:

| Item | SSL-kant |
|---|---|
| CONV_EDU-t04-01 | B |
| CONV_EDU-t05-02 | B |
| CONV_EDU-t06-03 | A |
| CONV_HEALTH-t05-04 | A |
| CONV_HEALTH-t06-05 | A |
| CONV_POLICY-t05-06 | B |
| CONV_POLICY-t06-07 | A |

## Cijfers

SSL-voorkeur (winnaar == SSL-kant), per reviewer:

| Reviewer | SSL-wins / 7 | EDU (3) | HEALTH (2) | POLICY (2) | Protocol |
|---|---|---|---|---|---|
| r1 (CSV + geannoteerde JSON) | **5/7** | 2/3 | 2/2 | 1/2 | blind, conform |
| r2 (compacte CSV) | **5/7** | 1/3 | 2/2 | 2/2 | blind, conform |
| r3 (proza) | 7/7 | 3/3 | 2/2 | 2/2 | **seed-bewust — apart tellen** |

- **Meerderheidswinnaar: SSL op 6/7** (alleen CONV_EDU-t04 gaat per
  meerderheid naar de baseline).
- **Unaniem (3/3): 4 items, alle vier SSL-kant** — EDU-t06, HEALTH-t05,
  HEALTH-t06, POLICY-t06.
- Overeenstemming: pairwise 5/7 bij alle drie paren (**~0.71**; round 022 was
  0.125, round 023 ~0.67).
- Uitgesloten items: **0**; afkap: **0/14** (round 024: 6/9 uitgesloten door
  afkap — de compactheidsfix deed zijn werk).

## Het scherpste patroon: vraagtype, niet domein

- **Valkuil-/reflectievragen (t6, alle drie domeinen): 9/9 reviewer-stemmen
  voor de SSL-kant.** De seeds (instrumenteel-vs-vormingsproces; commerciële
  tegenkracht; korte-vs-lange termijn + sociale ongelijkheid) structureren
  daar aantoonbaar de probleemanalyse — reviewers benoemen precies die punten
  als doorslaggevend ("raakt de kern", "adresseert de olifant in de kamer",
  "twee essentiële valkuilen die in B volledig ontbreken").
- **Praktische adviesvragen (t4/t5): 8/12 stemmen voor SSL** — gemengd. Waar
  de vraag om direct uitvoerbare stappen vraagt (EDU-t04), verkiezen blinde
  reviewers de concretere baseline; de seed-kant wint waar het bredere kader
  de overtuigingskracht verhoogt (EDU-t05 bij 2/3, POLICY-t05 bij 2/3).

Dit is hetzelfde gedrag dat round 023 binnen één domein liet zien ("sturen
bij aanscherping, stil bij irrelevantie") — nu gerepliceerd over drie nieuwe
domeinen: **de use-time discipline draagt over**.

## Ruis en seed-effect

- Ruis-/hallucinatienotities: **0 bij alle drie reviewers** (r1 expliciet
  "geen duidelijke ruis" ×7; r3: "zonder ruis of hallucinaties"; r2 kolom
  leeg). De enige milde kanttekening van r1 (motiverende gespreksvoering
  "iets minder passend", HEALTH-t05) betreft de **baseline**-kant.
- Seed-effect-labels (na keuze): uitsluitend "helpt duidelijk" (4×) of
  "helpt een beetje" (3×) — nergens "ruis" of "vernauwt".

## Transfer-verdict (W10)

**Positief, met grenzen.** In drie domeinen die de suite nooit eerder zag
(onderwijs, publieke gezondheid, gemeentelijk klimaatbeleid):

1. het mechanisme vuurde (7 cross-turn events, 7 promoties, Gate op veilige
   drempels);
2. de gepromoveerde seeds openden antwoordruimte die blinde reviewers per
   meerderheid verkiezen (6/7), met **unanimiteit precies waar de doctrine
   het voorspelt** (reflectie/aanscherping) en eerlijke splitsing waar
   concreetheid wint;
3. ruis — de round-022-foutklasse — bleef op nul;
4. de overeenstemming (~0.71) is het hoogste tot nu toe.

**Grenzen, onverminderd:** n=7 items, één model (gpt-4.1), één run,
auteur-gekozen gespreksthema's, beide armen LLM-gegenereerd, r3
protocol-afwijking (apart geteld), win-rate blijft een kwaliteitscontrole op
door SSL geopende antwoordruimte — geen bewijs dat SSL "elk antwoord beter
maakt".

## Doorwerking

- De herzieningstrigger uit `docs/research/positioning-synthese.md` is
  gevallen: het positieve verdict **verstevigt de tweede positioneringszin**
  (cross-turn kan SSL antwoordruimte openen die reviewers verkiezen, nu ook
  buiten de oorspronkelijke domeinen); het besluit zelf (discipline voorop,
  4.6-lijn, geen versiesprong) verandert niet.
- Laag F (evaluatiematrix/README) gaat van "verdict pending" naar "eerste
  positieve transfer-verdict (round 025), met bovenstaande grenzen".

## Bestanden

- `r1_scores.csv` + `r1_review_items_annotated.json` — reviewer 1 (blind)
- `r2_scores.csv` — reviewer 2 (blind)
- `r3_review.md` — reviewer 3 (seed-bewust; protocol-kanttekening in het
  bestand)
- Answer key: reproduceerbaar uit code (seed 45); origineel in het
  run-artifact (`ssl_session_blind_ab_answer_key.json`, digest-gepind).
