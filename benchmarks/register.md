# Benchmark-register

Dit register is de vaste benchmarkbibliotheek voor deze Shadow Seed Learning 4.5-repo.

## Doel

- vastleggen welke benchmarks relevant zijn voor SSL 4.5
- koppelen van benchmarks aan concrete SSL-onderdelen
- status en bronroute expliciet maken
- voorkomen dat benchmarkwerk buiten vaste lablogica om gebeurt

## Gebruik

Lees dit register altijd samen met `benchmarks/pipeline.md` en de benchmarkspecifieke runkaarten.

## Benchmarks

| Benchmark | Primaire SSL-koppeling | Rol in deze repo | Verwachte bron | Status | Opmerking |
|---|---|---|---|---|---|
| AbsenceBench | Detection-Pass / geometrie van afwezigheid | eerste benchmarkvoorbereiding | Hugging Face dataset + GitHub-code | klaar voor intake | default startbenchmark |
| GAIA | structurele gaps / multi-step ambiguity | latere verbreding | Hugging Face leaderboard of repo | in bibliotheek | pas na AbsenceBench-voorbereiding |
| LLM Spark | Validation Gate | latere validatielaag | externe repo of paperbron | te verifiëren | nuttig voor flawed-information tests |
| PTF-ID-Bench | Active Probing / escalatie | latere escalatietest | externe repo of paperbron | te verifiëren | relevant voor mens-escalatiegedrag |
| AMA-Bench | JSON-state / geheugencontinuïteit | latere geheugentest | externe repo of paperbron | te verifiëren | relevant voor state-updates |
| MR-Ben | meta-redeneren | latere interpretatietest | externe repo of paperbron | te verifiëren | relevant voor foutanalyse |

## Statuswaarden

Gebruik in deze repo alleen deze bibliotheekstatussen:

- `in bibliotheek`
- `te verifiëren`
- `klaar voor intake`
- `klaar voor benchmarkrun`
- `in gebruik`
- `gearchiveerd`

## Repo- en runnerregel

Een benchmarkrepo geldt pas als geldige runroute wanneer minimaal aannemelijk is dat:

1. de route actueel genoeg is voor de genoemde benchmarkversie
2. de codebase niet zichtbaar outdated is
3. er een plausibele uitvoerroute aanwezig is
4. de repo meer is dan alleen historische context

Zolang dat niet hard vastligt, blijft de benchmarkstatus in deze repo minimaal `benchmarkvoorbereiding`.

## AbsenceBench-notitie

Voor AbsenceBench is de benchmarkinhoud al als eerste lane opgenomen, maar de actuele runnerroute blijft nog `te verifiëren`. Daarom is de operationele benchmarkstatus in deze repo nog niet `echte benchmarkrun`.
