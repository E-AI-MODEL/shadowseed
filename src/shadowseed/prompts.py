"""Promptbibliotheek voor Shadow Seed Learning 4.6."""

DETECTION_PASS = """
Je bent een epistemische analist.

Je taak is niet om het antwoord te verbeteren.
Je taak is om kleine structurele afwezigheden te vinden.

Kijk naar het antwoord dat je zojuist gaf.

Welke kleine concepten, relaties of randvoorwaarden ontbreken, terwijl ze nodig zijn voor een volledig begrip van dit specifieke onderwerp?

Regels:
- Geef maximaal 5 seeds.
- Elke seed bevat precies één gap.
- Geen samengestelde analysekaders.
- Geen lijsten binnen één seed.
- Formuleer concreet en toetsbaar.
- Geen uitleg.

Output:
1. [seed]
2. [seed]
3. [seed]
""".strip()

SEED_NORMALIZATION = """
Splits de volgende brede gap op in atomische shadow seeds.

Regels:
- Elke seed bevat één ontbrekende relatie, factor of randvoorwaarde.
- Geen seed mag meerdere domeinen combineren.
- Formuleer elke seed als korte zin.
- Maximaal 8 seeds.

Brede gap:
"{broad_gap}"
""".strip()

JSON_EXTRACTION = """
Zet de volgende seeds om naar JSON.

Regels:
- Bewaar de tekst van elke seed exact.
- Geef 3 tot 5 trigger_keywords per seed.
- Voeg geen nieuwe seeds toe.
- Houd elke rationale kort.

Seeds:
{seeds}

Output als JSON:
{
  "shadow_seeds": [
    {
      "text": "...",
      "trigger_keywords": ["...", "..."],
      "rationale": "..."
    }
  ]
}
""".strip()

DIALECTICAL_PROBE = """
Je hebt de hypothese dat deze gap relevant is:

"{seed_text}"

Probeer deze hypothese te weerleggen.

Geef een sterk argument waarom deze gap in deze context niet relevant is, of waarom de huidige informatie al voldoende is.

Antwoord alleen met:

FALSIFIED

of

VALIDATED
""".strip()

SOCRATIC_PROBE = """
Je hebt een gepromoveerde seed:

"{seed_text}"

Integreer deze seed in het antwoord als één natuurlijke Socratische vraag.

Regels:
- Niet zeggen dat er iets vergeten is.
- Geen lijst maken.
- Geen foutmelding.
- Eén vraag.
- De vraag moet de gebruiker uitnodigen de gap te vullen.
""".strip()

RETRIEVAL_PROBE = """
Maak één smalle retrieval-query voor deze seed.

Seed:
"{seed_text}"

Regels:
- Eén query.
- Maximaal 12 woorden.
- Geen brede termen zoals "context" of "analyse".
- Gebruik concrete inhoudswoorden.

Output:
[query]
""".strip()

JUDGE_PROMPT = """
Je beoordeelt een SSL-detectie.

Inputtekst:
{input_text}

Ground truth seeds:
{ground_truth}

Gedetecteerde seed:
{detected_seed}

Geef scores:
- atomiciteit: 0 of 1
- relevantie: 0 tot 2
- ground_truth_match: 0 tot 2
- eindscore: 0, 1 of 2

Regels:
- Score 2 kan alleen als de seed atomisch is.
- Een brede lijst krijgt maximaal score 1.
- Noem kort waarom.

Output als JSON.
""".strip()
