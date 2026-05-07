# Manager Design

Dit document beschrijft de huidige ontwerpkeuzes van `src/shadowseed/manager.py`.

## Doel van de manager

De manager bewaakt de Niveau-1 SSL 4.5-kern:

- atomische seeds opslaan
- brede detecties normaliseren naar reviewbare kandidaten
- deduplicatie op embeddinggelijkenis
- trace-verval
- Validation Gate
- reactivatie van dormant seeds
- constellations voor promoted seeds
- event logging voor reproduceerbaarheid

## Ontwerpkeuzes

### Centrale 4.5-defaults

De manager gebruikt nu een expliciete `SSLCoreConfig` met canonieke defaultwaarden voor:

- `trace_start`
- `half_life_turns`
- `dedup_threshold`
- `promotion_threshold`
- `dormant_threshold`
- `validation_increment`
- `contradiction_penalty`
- `max_trace`
- `reactivation_increment`
- minimale Gate-voorwaarden

Hiermee staat de technische 4.5-lijn op één plek in plaats van verspreid over losse magic numbers.

### Injecteerbare embeddings

De manager ondersteunt een `embedding_fn` zodat tests en benchmarkvoorbereiding niet afhangen van een live modeldownload.

### Gescheiden aanwezigheid en invloed

- `trace` registreert aanwezigheid
- `weight` registreert invloed

Deze scheiding volgt het canonieke SSL-kader.

### Expliciete normalisatielaag

SSL 4.5 vereist dat brede detecties niet direct worden opgeslagen. Daarom ondersteunt de manager nu een aparte normalisatiestap via `ingest_detection_candidates()`.

Belangrijk:

- normalisatie splitst brede output naar kleinere kandidaten;
- de manager beslist daarna pas wat echt atomisch genoeg is;
- niet elke genormaliseerde kandidaat wordt automatisch geaccepteerd.

### Gedetailleerde Validation Gate-uitvoer

De manager ondersteunt naast de eenvoudige Gate-uitkomst nu ook een gedetailleerde beslisstructuur via `run_validation_gate_detailed()`.

Daarin staat per stap:

- of interne herkenning slaagde;
- of externe evidence voldoende was;
- of contradictie de seed blokkeerde;
- of de seed alleen gevalideerd of echt gepromoveerd werd.

### Event logging

De manager logt nu kerngebeurtenissen zoals:

- seed creatie
- deduplicatie
- trace decay
- validatieblokkade
- validatie en promotie
- contradictie
- reactivatie
- expiratie

Dit maakt state dumps en benchmarkanalyse beter uitlegbaar.

### Benchmarkgerichte uitvoer

`to_dict()` geeft nu terug:

- config
- seeds
- constellations
- validation log
- event log
- vector-constellation state

Daardoor kan benchmark- of analysecode niet alleen de eindtoestand, maar ook het beslisspoor opslaan.

## Grenzen

Deze manager is nog geen volledige benchmarkrunner en ook geen modelinterne SSL-implementatie. Hij is bedoeld als reproduceerbare kernlaag voor:

- benchmarkvoorbereiding
- eerste evaluatie-adapters
- robuuste regressietests
- latere uitbreiding naar sterkere evaluatielagen
