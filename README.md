# Shadow Seed Learning 4.5

Deze repository is de eerste reproduceerbare, benchmarkklare opzet voor **Shadow Seed Learning 4.5** in de `E-AI-MODEL/shadowseed`-repo.

De inhoud is opgebouwd vanuit drie canonieke bronlagen:

1. `shadow_seed_learning_4_5_clean.md` als SSL SSOT
2. `ssl_4_5_public_release/` als operationele 4.5-uitwerking
3. `benchmark_bibliotheek/` als benchmark- en uitvoeringskader

## Doel

Deze repo levert een eerste Python- en documentatiestructuur voor:

- atomische gap-detectie
- opslag van shadow seeds met `trace` en `weight`
- een minimale manager-implementatie voor SSL 4.5
- een benchmarklane die start bij **AbsenceBench**
- reproduceerbare voorbereiding zonder schijnclaim van een al bevestigde externe runroute

## Huidige benchmarkstatus

- primaire benchmark: `AbsenceBench`
- status: `benchmarkvoorbereiding`
- execution-gap: aanwezig
- reden: dataset-, paper- en hostroute zijn bibliografisch vastgelegd, maar een actuele, hard geverifieerde runnerroute voor een eerste echte benchmarkrun is in deze repo nog niet operationeel vastgezet

De repo claimt dus **geen** voltooide externe benchmarkuitvoer.

## Repositorystructuur

```text
.
├── README.md
├── pyproject.toml
├── requirements.txt
├── benchmarks/
│   ├── README.md
│   ├── register.md
│   ├── pipeline.md
│   └── absencebench/
│       ├── README.md
│       └── runkaart.md
├── docs/
│   ├── architecture/
│   │   └── ssl-foundation.md
│   ├── benchmarking/
│   │   └── absencebench.md
│   └── reproducibility.md
├── scripts/
│   └── run_absencebench.py
├── src/
│   └── shadowseed/
│       ├── __init__.py
│       ├── manager.py
│       ├── prompts.py
│       └── benchmark/
│           ├── __init__.py
│           └── absencebench.py
└── tests/
    ├── test_atomic_seed_rules.py
    └── test_manager_smoke.py
```

## Installatie

Python 3.10+:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Snel starten

Controleer eerst de tests:

```bash
pytest
```

Maak daarna een voorbereidende AbsenceBench-runnotitie:

```bash
python scripts/run_absencebench.py --output runs/absencebench/preparation.json
```

Dit script zet alleen een reproduceerbare voorbereidingsstatus klaar. Het voert geen externe benchmarkrunner uit zolang de runroute niet hard is bevestigd.

## Kernlogica

De kernlogica in `src/shadowseed/manager.py` is overgenomen uit `ssl_4_5_public_release/src/ssl45/manager.py` en voorzichtig aangepast voor:

- package-hernoeming van `ssl45` naar `shadowseed`
- injecteerbare embeddings voor lokale tests
- reproduceerbare smoke-tests zonder verplichte modeldownload

## Benchmarklane

Gebruik deze volgorde:

1. lees `benchmarks/register.md`
2. volg `benchmarks/pipeline.md`
3. open `benchmarks/absencebench/runkaart.md`
4. leg metadata en runnotitie vast via `scripts/run_absencebench.py`

## Reproduceerbaarheid

Zie `docs/reproducibility.md` voor:

- verplichte runmetadata
- loggingvelden
- opslag van mislukte runs
- configuratievelden voor de SSL-manager

## Grenzen

- SSL is geen nieuw foundation model
- `weight` is geen modelparameter
- een seed is een hypothese over afwezigheid, geen bewezen feit
- benchmarkstatus blijft `benchmarkvoorbereiding` tot een actuele runnerroute expliciet is bevestigd
