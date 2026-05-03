# Roadmap

Deze roadmap houdt de claims van SSL 4.5 eerlijk en toetsbaar.

## Klaar

- SSLManager met trace, weight, decay, Validation Gate en promotie.
- Positieve Gap-Test Suite.
- False-positive controls.
- Benefit Suite fase 1.
- Model Benefit Suite fase 2 met fixture en `hf-transformers` backend.
- CI-artifacts voor suites.
- Analyse-laag met Markdown, JSON en SVG.
- Wiki-publicatie voor analyse en SLM-runs.
- Blind review protocol.

## Eerstvolgende stappen

### 1. Echte SLM-run uitvoeren

Start:

```text
Actions → SLM Model Benefit Run → Run workflow
```

Gebruik eerst:

```text
TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

### 2. SLM-output beoordelen

Gebruik de blind-review velden uit:

```text
SLM-Model-Benefit-Raw.json
```

### 3. Suite uitbreiden

Voeg meer scenario's toe:

- geschiedenis;
- recht;
- software;
- biologie;
- economie;
- beleid;
- onderwijs.

### 4. Gedeeltelijk complete antwoorden

Niet alleen volledige of duidelijk incomplete antwoorden testen, maar ook antwoorden die 1 of 2 gaps al bevatten.

### 5. Meer negatieve controles

Test of SSL rustig blijft bij:

- volledige antwoorden;
- irrelevante signalen;
- tegengestelde evidence;
- brede vaagheden;
- stijlproblemen die geen echte gap zijn.

### 6. Meer modellen

Vergelijk meerdere SLM's, maar altijd binnen hetzelfde patroon:

```text
model X baseline
model X met SSL
```

Niet model X vergelijken met model Y als bewijs voor SSL.

## Claimniveau

### Nu toegestaan

> SSL 4.5 werkt intern op de huidige suite en produceert reproduceerbare benchmark- en analyse-output.

### Pas later toegestaan

> SSL verbetert SLM-antwoorden gemiddeld op meerdere domeinen.

Dat mag pas na echte modelruns, uitbreiding van de suite en blind review.
