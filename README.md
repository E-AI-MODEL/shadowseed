# Shadow Seed Learning

[![checks](https://github.com/E-AI-MODEL/shadowseed/actions/workflows/tests.yml/badge.svg)](https://github.com/E-AI-MODEL/shadowseed/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Status](https://img.shields.io/badge/status-research%20prototype-orange)

Shadow Seed Learning (SSL) is een research-harness voor een simpele maar strenge vraag:

> kan een model beter verder werken als het niet alleen kijkt naar wat er staat, maar ook naar wat structureel ontbreekt?

SSL noemt zo'n ontbrekend punt een shadow seed.
Een seed begint gewichtloos. Pas na validatie via de Validation Gate mag die invloed krijgen op vervolgvragen, retrieval, falsificatie of latere antwoordruimte.

## In 30 seconden

- **Wat:** SSL laat een model opsporen wat structureel *ontbreekt* of onderbelicht blijft, bewaart dat als een gewichtloze shadow seed, en laat alleen gevalideerde seeds meesturen in vervolgactie of antwoordruimte.
- **Hoe:** elke seed heeft twee velden — `trace` (aanwezigheid, vervalt via TTL en leeft op via TrTL) en `weight` (invloed, start op `0.0` en stijgt alléén via de Validation Gate). Gewichtloos tot bewezen.
- **Status:** werkende research-harness met sterke lifecycle- en regressielaag. W9f is geaccepteerd als technische baseline voor cross-turn context-discovery en memory-surfacing; de brede claim blijft bewust begrensd.

> Kernregel: één seed = één klein, toetsbaar ontbrekend punt.

## Canonieke en historische bron

Gebruik deze regel voor documentatie:

- `docs/00_shadow_seed_learning_4_6.md` is de huidige canonieke bron voor theorie, evaluatiekoers en repo-alignment.
- `docs/legacy/00_shadow_seed_learning_4_5.md` blijft beschikbaar als historische technische referentie voor de eerdere 4.5-specificatie.

Dat betekent:

- 4.6 vertelt waar de repo inhoudelijk heen moet;
- 4.5 blijft leesbaar, maar is niet meer de primaire bron voor huidige alignment-beslissingen.

## Wat de repo vandaag bewijst (lagen A–G)

SSL hanteert één laag-taal voor bewijs, gelijk aan `docs/00_shadow_seed_learning_4_6.md` en `src/shadowseed/benchmark/evidence_layers.py`. De lagen worden bewust gescheiden gehouden — er is géén totaalscore.

| Laag | Vraag | Status vandaag |
|---|---|---|
| **A** Regressie | Blijft de kernmechaniek werken? | **Sterk** — snelle CI-ruggengraat |
| **B** Kleine benchmark | Werkt SSL op vaste, controleerbare casussen? | **Bruikbaar** — bewust smal |
| **C** Open-set seedkwaliteit | Goede seeds op onbekende tekst, zonder ground truth? | **Eerste evidence, gemengd** — relevantie hoog, trivialiteit/testability blijft risico |
| **D** Adversarial Gate | Weert de Gate misleidende gaps? | **Eerste echte evidence** — kleine maar duidelijke stresstest |
| **E** Probe utility / payoff | Leveren promoted seeds betere vervolgstappen of antwoordruimte op? | **W9f positief voor cross-turn discovery; productmatige seed-use discipline blijft open** |
| **F** Domein- en taaktransfer | Werkt dezelfde doctrine buiten de bekende domeinen? | **Volgende stap: W10 doctrine-transfer** |
| **G** Modelintern | Steun in interne activaties? | **Onderzoekslaag**, niet operationeel |

De standaard workflow (`Checks en benchmark-resultaten`) publiceert de regressie- en kleine-benchmarklagen plus aanvullende evidencelagen. Manual OpenAI-runs via `Research · SSL Benefit (OpenAI)` kunnen zwaardere payoff- en `ssl-session` artifacts maken, inclusief blind A/B-reviewpack voor cross-turn sessies.

## W9f-status

W9f is de huidige technische baseline voor cross-turn SSL.

De kernclaim is niet dat SSL elk antwoord beter maakt of GPT-4.1 algemeen verslaat. De claim is smaller:

> SSL kan latente sessiecontext gewichtloos vasthouden, later valideren of surfacen, en daardoor bruikbare aanvullende antwoordruimte openen.

De blind A/B-review wordt daarom gelezen als kwaliteitscontrole op door SSL geopende antwoordruimte, niet als klassieke model-vs-model benchmark. Zonder SSL zouden de SSL-gestuurde antwoordvarianten niet als optie hebben bestaan.

Zie `docs/research/w9f-evaluatieconclusie.md`.

## Wat de resultaten wel en niet betekenen

Wat je voorzichtig wel mag zeggen:

- SSL heeft een reproduceerbare mechanische kern.
- De repo bewaakt `trace`, `weight`, TTL, TrTL, status lifecycle en Gate-gedrag.
- De repo kan meten of bekende gaps gevonden worden.
- De Gate heeft eerste echte adversarial evidence.
- Probe-feedback heeft eerste behavioral evidence.
- W9f toont dat cross-turn surfaced seeds bruikbare extra antwoordruimte kunnen openen.

Wat je nog niet breed moet zeggen:

- dat SSL algemeen bewezen beter presteert op open-ended modeltaken;
- dat SSL elk antwoord verbetert;
- dat elke promoted seed waardevol is;
- dat fixture-smokes gelijk staan aan echte modelvalidatie;
- dat open-set, adversarial, probe utility en W9f samen al volledige scenario-onafhankelijke eindvalidatie vormen.

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
- `docs/research/w9f-evaluatieconclusie.md`
- `docs/research/w9f-review-artifacts.md`
- `docs/research/scenario-independence-roadmap.md`
- `docs/research/evaluation-matrix.md`
- `docs/research/work-categories.md`
- `docs/research/roadmap-shadowseed-stabilization.md`
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
