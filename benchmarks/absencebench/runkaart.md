# AbsenceBench-runkaart

Dit document is de standaard runkaart voor de eerste AbsenceBench-lane in deze repo.

## Benchmarkdoel

Toetsen of een SSL 4.5-conditie betere absence detection oplevert dan een baselineconditie zonder expliciete SSL-sturing.

## Bronbasis

Verplicht gebruiken:

- `shadow_seed_learning_4_5_clean.md`
- `ssl_4_5_public_release/`
- `benchmark_bibliotheek/`

## Bron en host

- dataset-host: `harveyfin/AbsenceBench` op Hugging Face
- paper-host: `2506.11440` op Hugging Face Papers
- code-host: `harvey-fin/absence-bench` op GitHub
- publieke benchmarksite: `absencebench.github.io`

## Executionstatus

- huidige status: `benchmarkvoorbereiding`
- execution-gap aanwezig: `ja`
- repo-status: `te verifiëren`

## Waarom nog geen echte benchmarkrun

De repo legt de benchmarkroute inhoudelijk vast, maar claimt nog geen actuele runnerverificatie. Daardoor zijn de volgende onderdelen nog niet hard bevestigd:

- startcommando baseline
- startcommando SSL-conditie
- actuele uitvoerbaarheid van de gekozen runnerrepo
- score-output schema
- exacte model- en providerkeuze

## Twee-conditie-opzet

### Baseline

- label: `baseline`
- doel: meten hoe een gewone modelopzet zonder SSL-logica presteert
- instructielaag: neutrale benchmarkaansturing zonder seed- of gaplogica

### SSL-conditie

- label: `ssl_condition`
- doel: meten of SSL-sturing betere absence detection oplevert
- instructielaag: Detection-Pass, seed-normalisatie en validatielogica volgens SSL 4.5

## Minimale runnotitie

- benchmark: `AbsenceBench`
- executionstatus: `benchmarkvoorbereiding`
- dataset-host: `harveyfin/AbsenceBench`
- code-host: `harvey-fin/absence-bench`
- paper-host: `2506.11440`
- model: `nog te kiezen`
- provider: `nog te kiezen`
- benchmarksubset: `nog te kiezen`
- baselineprompt-aansturing: `nog te verifiëren`
- ssl-aansturing: `Detection-Pass + seed-normalisatie + validation discipline`
- startcommando baseline: `nog te verifiëren`
- startcommando SSL-conditie: `nog te verifiëren`
- score-output pad of vorm: `nog te verifiëren`
- rapportbestemming: `runs/absencebench/`
- execution-gap: `ja`
- ontbrekende componenten:
  - actuele runnerverificatie
  - bevestigd startcommando
  - model- en providerselectie
  - outputschema

## Handoff

Wanneer de runnerroute actueel is geverifieerd, kan deze runkaart worden opgewaardeerd van `benchmarkvoorbereiding` naar `echte benchmarkrun`.
