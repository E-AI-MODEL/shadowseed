# Shadow Seed Learning 4.5

[![checks](https://github.com/E-AI-MODEL/shadowseed/actions/workflows/tests.yml/badge.svg)](https://github.com/E-AI-MODEL/shadowseed/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Status](https://img.shields.io/badge/status-research%20prototype-orange)

Shadow Seed Learning (SSL) is een research-harness voor een simpele maar strenge vraag:

> kan een model beter antwoorden als het niet alleen kijkt naar wat er staat, maar ook naar wat structureel ontbreekt?

SSL noemt zo'n ontbrekend punt een shadow seed.
Een seed begint gewichtloos. Pas na validatie via de Validation Gate mag die invloed krijgen op vervolgvragen, retrieval of falsificatie.

## Voor nieuwe bezoekers

Begin hier als je de repo of wiki voor het eerst ziet:

1. [GitHub Wiki Home](https://github.com/E-AI-MODEL/shadowseed/wiki)
2. [Latest Test Results](https://github.com/E-AI-MODEL/shadowseed/wiki/Latest-Test-Results)
3. [SSL 4.5 Analysis](https://github.com/E-AI-MODEL/shadowseed/wiki/SSL-45-Analysis)
4. [GitHub Pages dashboard](https://e-ai-model.github.io/shadowseed/)

Die vier ingangen beantwoorden samen:

- wat SSL is;
- welke resultaten je nu bekijkt;
- wat die resultaten wel laten zien;
- wat nog geen brede eindclaim is.

## Wat deze repo vandaag is

De repo is het best te lezen als:

- een werkende SSL 4.5 benchmark-harness;
- met een canonieke inhoudelijke koers richting `docs/00_shadow_seed_learning_4_6.md`;
- en met groeiende aanvullende evidencelagen voor open-set seedkwaliteit, adversarial Gate-gedrag en probe utility.

Kort gezegd:

- de mechanische kern is aanwezig;
- de standaard meetketen draait;
- de hoofdclaim wordt nog steeds bewust klein gehouden.

## Wat de standaardresultaten zijn

De standaard workflow heet `Checks en benchmark-resultaten`.

De standaardpublicatie laat vooral vijf soorten signalen zien:

| Laag | Betekenis |
|---|---|
| regressie | blijft de Python- en benchmarkmechaniek werken? |
| technische smoke | werkt een route technisch zonder grote externe afhankelijkheden? |
| methodologische smoke | blijven detectie en scoring eerlijk gescheiden? |
| kleine benchmark | zie je winst op een kleine vaste suite? |
| aanvullende evidencelaag | zie je al extra bewijs buiten alleen fixture- en scenario-smokes? |

De huidige standaardworkflow publiceert daarom niet alleen de oude kernsuites, maar ook aanvullende evidencelagen voor:

- adversarial Gate-gedrag;
- probe utility.

Die extra lagen horen bij de standaardpublicatie, maar moeten nog steeds gelezen worden als aanvullend bewijs en niet als definitieve eindvalidatie.

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

- `docs/00_shadow_seed_learning_4_6.md`
- `docs/ARCHITECTURE_MAP.md`
- `docs/CLI_COMMAND_MAP.md`
- `docs/research/current-status.md`
- `docs/research/evaluation-matrix.md`
- `docs/research/next-phase-implementation.md`
- `docs/wiki/Home.md`
- `docs/wiki/Benchmarks.md`

## Kernregel

> Een seed bevat precies een klein, toetsbaar ontbrekend punt.

Dat is de reden dat SSL complex kan worden zonder vaag te worden: het systeem probeert niet "meer context" toe te voegen, maar een heel specifiek gemis veilig vast te leggen, te toetsen en pas daarna mee te laten wegen.
