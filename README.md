# Shadow Seed Learning

[![checks](https://github.com/E-AI-MODEL/shadowseed/actions/workflows/tests.yml/badge.svg)](https://github.com/E-AI-MODEL/shadowseed/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Status](https://img.shields.io/badge/status-research%20prototype-orange)

Shadow Seed Learning (SSL) is een research-harness voor een simpele maar strenge vraag:

> kan een model beter antwoorden als het niet alleen kijkt naar wat er staat, maar ook naar wat structureel ontbreekt?

SSL noemt zo'n ontbrekend punt een shadow seed.
Een seed begint gewichtloos. Pas na validatie via de Validation Gate mag die invloed krijgen op vervolgvragen, retrieval of falsificatie.

## In 30 seconden

- **Wat:** SSL laat een model opsporen wat structureel *ontbreekt* in een antwoord, bewaart dat als een gewichtloze "shadow seed", en laat alleen gevalideerde seeds meesturen in vervolgvraag, retrieval of falsificatie.
- **Hoe:** elke seed heeft twee velden — `trace` (aanwezigheid, vervalt vanzelf) en `weight` (invloed, start op `0.0` en stijgt alléén via de Validation Gate). Gewichtloos tot bewezen.
- **Status:** werkende research-harness met een sterke regressielaag; de brede claim wordt bewust klein gehouden (zie de laagstatus hieronder).

> Kernregel: één seed = één klein, toetsbaar ontbrekend punt.

## Canonieke en historische bron

Gebruik deze regel voor documentatie:

- `docs/00_shadow_seed_learning_4_6.md` is de huidige canonieke bron voor theorie, evaluatiekoers en repo-alignment
- `docs/legacy/00_shadow_seed_learning_4_5.md` blijft beschikbaar als historische technische referentie voor de eerdere 4.5-specificatie

Dat betekent:

- 4.6 vertelt waar de repo inhoudelijk heen moet;
- 4.5 blijft leesbaar, maar is niet meer de primaire bron voor huidige alignment-beslissingen.

## Wat de repo vandaag bewijst (lagen A–G)

SSL hanteert één laag-taal voor bewijs, gelijk aan `docs/00_shadow_seed_learning_4_6.md` en `src/shadowseed/benchmark/evidence_layers.py`. De lagen worden bewust gescheiden gehouden — er is géén totaalscore.

| Laag | Vraag | Status vandaag |
|---|---|---|
| **A** Regressie | Blijft de kernmechaniek werken? | **Sterk** — snelle CI-ruggengraat |
| **B** Kleine benchmark | Werkt SSL op vaste, controleerbare casussen? | **Bruikbaar** (bewust smal) |
| **C** Open-set seedkwaliteit | Goede seeds op onbekende tekst, zonder ground truth? | **Infra compleet; evidence pending** op menselijke review |
| **D** Adversarial Gate | Weert de Gate misleidende gaps? | **Eerste echte evidence** (nog klein) |
| **E** Probe utility | Leveren promoted seeds betere vervolgstappen op? | **Eerste echte evidence** |
| **F** Domeintransfer | Werkt SSL buiten de bekende domeinen? | **Nog leeg** |
| **G** Modelintern | Steun in interne activaties (H-Neurons)? | **Onderzoekslaag**, niet operationeel |

De standaard workflow (`Checks en benchmark-resultaten`) publiceert de regressie- en kleine-benchmarklagen plus de aanvullende evidencelagen D (adversarial Gate) en E (probe utility). Die aanvullende lagen zijn echt bewijs, maar nog geen volledige eindvalidatie.

## Wat de resultaten wel en niet betekenen

Wat je voorzichtig wel mag zeggen:

- SSL heeft een reproduceerbare mechanische kern.
- De repo kan meten of bekende gaps gevonden worden.
- De repo kan meten of het systeem geen evidente promoted false positives doorlaat.
- De repo kan laten zien of aanvullende evidencelagen iets extra's zichtbaar maken.

Wat je nog niet breed moet zeggen:

- dat SSL algemeen bewezen beter presteert op open-ended modeltaken;
- dat fixture-smokes gelijk staan aan echte modelvalidatie;
- dat open-set, adversarial en probe utility al volledige eindvalidatie vormen;
- dat de repo nu al het hele SSL-onderzoeksprogramma heeft afgedekt.

## Snelstart

```bash
pip install -e ".[test]"
pytest
shadowseed run-gap-suite
shadowseed run-false-positive-suite
shadowseed run-benefit-suite
shadowseed run-blind-benchmark --labels benchmarks/private/blind_suite_labels.json
shadowseed run-adversarial-gate-benchmark
shadowseed run-probe-utility-benchmark
shadowseed analyze-results
```

## Hugging Face token

Voor publieke HF dataset-intake is niet altijd een token nodig.
Voor gated of strengere HF-routes gebruikt de repo nu een optioneel secretpatroon via environment variables.

Lokaal:

1. kopieer `.env.example` naar `.env`
2. zet daar je echte token in
3. exporteer `HUGGINGFACE_TOKEN` in je shell of laad `.env` lokaal

In GitHub Actions:

- gebruik de repository secret `HUGGINGFACE_TOKEN`
- start daarna handmatig de workflow `Open-set HF review batch` voor intake en review-packets

Belangrijk:

- commit nooit een echte token;
- zet geen tokens in JSON-bestanden of code;
- gebruik in GitHub Actions een repository secret met de naam `HUGGINGFACE_TOKEN`.

## Belangrijkste documenten

Huidige bron- en researchstack:

- `docs/00_shadow_seed_learning_4_6.md`
- `docs/research/current-status.md`
- `docs/research/work-categories.md`
- `docs/research/roadmap-shadowseed-stabilization.md`
- `docs/research/evaluation-matrix.md`
- `docs/research/artifact-contracts.md`
- `docs/research/workflow-map.md`

Technische repo-oriëntatie:

- `docs/ARCHITECTURE_MAP.md`
- `docs/CLI_COMMAND_MAP.md`
- `docs/README.md`

Historische referentie:

- `docs/legacy/00_shadow_seed_learning_4_5.md`

## Meer lezen

- [GitHub Wiki Home](https://github.com/E-AI-MODEL/shadowseed/wiki) — uitgebreide uitleg en achtergrond
- [GitHub Pages dashboard](https://e-ai-model.github.io/shadowseed/) — actuele resultaten per laag
- [Latest Test Results](https://github.com/E-AI-MODEL/shadowseed/wiki/Latest-Test-Results)
- [SSL 4.5 Analysis](https://github.com/E-AI-MODEL/shadowseed/wiki/SSL-45-Analysis)

## Kernregel

> Een seed bevat precies een klein, toetsbaar ontbrekend punt.

Dat is de reden dat SSL complex kan worden zonder vaag te worden: het systeem probeert niet "meer context" toe te voegen, maar een heel specifiek gemis veilig vast te leggen, te toetsen en pas daarna mee te laten wegen.
