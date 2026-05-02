# Benchmark-pipeline

Dit document beschrijft de vaste benchmark-pipeline voor deze Shadow Seed Learning 4.5-repo.

## Pipeline-doel

Benchmarkwerk moet reproduceerbaar, brontrouw en operationeel helder zijn.

## Vaste benchmark-pipeline

1. **SSL-inputbasis bepalen**
   - gebruik `shadow_seed_learning_4_5_clean.md` als canonieke SSL SSOT
   - gebruik `ssl_4_5_public_release/` als operationele 4.5-uitwerking
   - benoem welk SSL-onderdeel wordt gebenchmarkt

2. **Benchmark kiezen**
   - kies benchmarkdoel
   - kies startbenchmark
   - default naar `AbsenceBench` tenzij het doel duidelijk anders is

3. **Bron en host verifiëren**
   - controleer dataset, paper, repo of benchmarksite
   - noteer expliciet waar de benchmark wordt gehost
   - onderscheid discovery van echte runbaarheid

4. **Executionstatus bepalen**
   - classificeer het werk als precies één van:
     - `benchmarkscan`
     - `benchmarkvoorbereiding`
     - `echte benchmarkrun`

5. **Benchmark-opzet definiëren**
   - formuleer benchmarkdoel
   - definieer inputset of subset
   - leg beoordelingscriterium vast
   - beschrijf risico's en failure modes

6. **Run- of analysepakket opstellen**
   - noteer gebruikte SSL-documenten
   - leg baseline- en SSL-conditie vast
   - leg vast of een execution-gap aanwezig is

7. **Scoreduiding uitvoeren**
   - scheid ruwe score van interpretatie
   - benoem alternatieve verklaringen
   - claim geen SSL-validatie op basis van één benchmark alleen

8. **Rapport en exitticket opleveren**
   - lever benchmarkrapport
   - lever handoffadvies
   - benoem welke component nog ontbreekt voor een echte run

## Huidige repo-status

Voor deze eerste repo-opzet geldt:

- actieve benchmark: `AbsenceBench`
- executionstatus: `benchmarkvoorbereiding`
- execution-gap aanwezig: `ja`

## Minimale succescriteria voor een echte benchmarkrun

Een benchmark geldt pas als operationeel voorbereid voor live-uitvoering wanneer minimaal duidelijk is:

1. welke benchmark draait
2. waar data en code gehost worden
3. welke SSL-input wordt gebruikt
4. hoe baseline en SSL-conditie worden gestart
5. hoe score-output wordt teruggelezen
6. dat de gekozen runnerroute actueel is
