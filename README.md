# Shadow Seed Learning 4.5

Deze repo bevat een minimale en reproduceerbare basis voor Shadow Seed Learning.

## Installatie

### Licht (aanbevolen)

```bash
pip install -e ".[test]"
pytest
```

### Met model (optioneel)

```bash
pip install -e ".[test,models]"
```

## CI

De CI draait standaard zonder modeldownload. Dat houdt tests snel en stabiel.

Er is een aparte job die optioneel een echte embedding test uitvoert met caching.

## Snel starten

```bash
pytest
```

## Benchmark

De benchmarkroute (`AbsenceBench`) is momenteel een voorbereidingsflow.

```bash
python scripts/run_absencebench.py
```

Dit genereert alleen een reproduceerbare status. Geen echte externe run.

## Structuur

- `src/` kernlogica
- `tests/` unit tests (geen model nodig)
- `tests/test_model_optional.py` optionele modeltest
- `scripts/` benchmark voorbereiding

## Belangrijk

- model is optioneel
- tests werken zonder internet
- CI is snel en reproduceerbaar

## Status

- unit tests: stabiel
- CI: actief
- benchmark: voorbereiding
