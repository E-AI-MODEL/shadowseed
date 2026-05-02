# Manager Design

Dit document beschrijft de huidige ontwerpkeuzes van `src/shadowseed/manager.py`.

## Doel van de manager

De manager bewaakt de minimale Niveau-1 SSL-logica:

- atomische seeds opslaan
- deduplicatie op embeddinggelijkenis
- trace-verval
- validation gate
- reactivatie van dormant seeds
- constellations voor promoted seeds

## Ontwerpkeuzes

### Injecteerbare embeddings

De manager ondersteunt een `embedding_fn` zodat tests en benchmarkvoorbereiding niet afhangen van een live modeldownload.

### Gescheiden aanwezigheid en invloed

- `trace` registreert aanwezigheid
- `weight` registreert invloed

Deze scheiding volgt het canonieke SSL-kader.

### Benchmarkgerichte uitvoer

`to_dict()` geeft zowel seeds als constellations terug, zodat benchmark- of analysecode direct een compacte state dump kan opslaan.

### Grenzen

Deze manager is nog geen volledige benchmarkrunner en ook geen modelinterne SSL-implementatie. Hij is bedoeld als reproduceerbare kernlaag voor benchmarkvoorbereiding en eerste evaluatie-adapters.
