# Promptbibliotheek SSL 4.6

> Afgeleid werkdocument. Canonieke bron: `docs/00_shadow_seed_learning_4_6.md`. De prompts hieronder horen bij de taalmodel-detectiestap die de 4.6 één-zinsclaim eist.

## 1. Detectie-Pass

Gebruik deze prompt nadat het model een eerste antwoord heeft gegeven.

```text
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
```

## 2. Seed-normalisatie

Gebruik deze prompt wanneer de detectie te breed is.

```text
Splits de volgende brede gap op in atomische shadow seeds.

Regels:
- Elke seed bevat één ontbrekende relatie, factor of randvoorwaarde.
- Geen seed mag meerdere domeinen combineren.
- Formuleer elke seed als korte zin.
- Maximaal 8 seeds.

Brede gap:
"[BREDE_GAP]"
```

## 3. JSON-extractie

Gebruik deze prompt om seeds te structureren.

```text
Zet de volgende seeds om naar JSON.

Regels:
- Bewaar de tekst van elke seed exact.
- Geef 3 tot 5 trigger_keywords per seed.
- Voeg geen nieuwe seeds toe.
- Houd elke rationale kort.

Seeds:
[SEEDS]

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
```

## 4. Dialectische Probe

Gebruik deze prompt in de Validation Gate.

```text
Je hebt de hypothese dat deze gap relevant is:

"[SEED_TEXT]"

Probeer deze hypothese te weerleggen.

Geef een sterk argument waarom deze gap in deze context niet relevant is, of waarom de huidige informatie al voldoende is.

Antwoord alleen met:

FALSIFIED

of

VALIDATED
```

## 5. Socratische Probe

Gebruik deze prompt wanneer een seed promoted is.

```text
Je hebt een gepromoveerde seed:

"[SEED_TEXT]"

Integreer deze seed in het antwoord als één natuurlijke Socratische vraag.

Regels:
- Niet zeggen dat er iets vergeten is.
- Geen lijst maken.
- Geen foutmelding.
- Eén vraag.
- De vraag moet de gebruiker uitnodigen de gap te vullen.
```

## 6. Retrieval Probe

Gebruik deze prompt om een smalle zoekvraag te maken.

```text
Maak één smalle retrieval-query voor deze seed.

Seed:
"[SEED_TEXT]"

Regels:
- Eén query.
- Maximaal 12 woorden.
- Geen brede termen zoals "context" of "analyse".
- Gebruik concrete inhoudswoorden.

Output:
[query]
```

## 7. Judge-prompt

Gebruik deze prompt voor automatische voorbeoordeling. Menselijke beoordeling blijft leidend.

```text
Je beoordeelt een SSL-detectie.

Inputtekst:
[INPUT]

Ground truth seeds:
[GROUND_TRUTH]

Gedetecteerde seed:
[DETECTED_SEED]

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
```

## 8. Anti-patronen

Vermijd prompts die vragen om:

- alle mogelijke ontbrekende dingen
- creatief denken zonder beperking
- algemene perspectieven
- fouten zoeken in plaats van afwezigheden
- vaste gap-typen die het model alleen hoeft af te vinken

Het doel is niet veel output. Het doel is kleine, toetsbare output.
