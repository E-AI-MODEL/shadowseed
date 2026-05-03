# Tussentijdse rapportage SSL 4.5

## 1. Samenvatting

Shadow Seed Learning 4.5 is in deze repo uitgewerkt van idee naar een testbare research-pipeline. De huidige stand is dat SSL intern reproduceerbaar werkt, dat de positieve en negatieve benchmarklagen draaien, dat resultaten automatisch worden geanalyseerd, en dat een eerste SLM-run via GitHub Actions kan worden uitgevoerd en gerapporteerd.

De belangrijkste tussentijdse conclusie is:

> SSL 4.5 is nu toetsbaar als methode. De repo kan meten of gevalideerde afwezigheden leiden tot betere antwoorden bij hetzelfde model. De eerste claims moeten beperkt blijven tot de huidige suite, de gebruikte prompts en het gekozen model.

Wat nu sterk staat:

- de lifecycle van seeds is geïmplementeerd;
- trace en weight zijn gescheiden;
- promotie loopt via de Validation Gate;
- positieve gaps worden getest;
- false positives worden getest;
- model benefit wordt getest met dezelfde baseline- en SSL-conditie;
- analyse, grafieken en Wiki-publicatie zijn geautomatiseerd.

Wat nog niet sterk genoeg is voor een brede wetenschappelijke claim:

- de suite is nog klein;
- er is nog weinig variatie in domeinen;
- blind review moet nog structureel worden ingevuld;
- meerdere SLM's moeten worden getest;
- de resultaten moeten worden herhaald over meer scenario's.

## 2. Onderzoeksvraag

De centrale vraag is:

> Functioneert een LLM of SLM beter wanneer Shadow Seed Learning gevalideerde ontbrekende elementen gebruikt om een antwoord te verbeteren?

Deze vraag is opgesplitst in kleinere toetsbare vragen:

1. Kan SSL ontbrekende structurele elementen atomisch detecteren?
2. Blijven die seeds gewichtloos totdat ze zijn gevalideerd?
3. Promoot SSL alleen seeds die aan de Gate-condities voldoen?
4. Laat SSL volledige antwoorden met rust?
5. Verbetert SSL de gap coverage van een antwoord?
6. Verbetert hetzelfde model met SSL-guided rewrite ten opzichte van hetzelfde model zonder SSL?

## 3. Begrippen

### Shadow seed

Een shadow seed is een klein, specifiek en toetsbaar ontbrekend element.

Voorbeeld:

```text
Rechtsbevoegdheid bij een geschil tussen een Nederlandse consument en een Amerikaanse webwinkel.
```

Niet goed:

```text
De juridische context mist.
```

Dat is te breed.

### Trace

`trace` meet of een seed aanwezig blijft of opnieuw wordt herkend.

Een seed start met:

```text
trace = 2.0
```

### Weight

`weight` meet of een seed invloed mag hebben.

Een seed start met:

```text
weight = 0.0
```

Daarmee wordt voorkomen dat elke detectie meteen het antwoord gaat sturen.

### Validation Gate

Een seed krijgt pas gewicht als deze voorwaarden gelden:

```text
occurrence_count >= 3
evidence_count >= 2
geen contradictie
```

Daarna stijgt `weight`. Bij voldoende gewicht wordt de seed `PROMOTED`.

## 4. Implementatie

De belangrijkste bron van waarheid is:

```text
src/shadowseed/manager.py
```

Daarin zitten de regels voor:

- seed-status;
- trace;
- weight;
- decay;
- deduplicatie;
- Validation Gate;
- promotie;
- falsificatie.

Belangrijke benchmarkbestanden:

```text
src/shadowseed/benchmark/ssl45_gap_suite.py
src/shadowseed/benchmark/ssl45_false_positive_suite.py
src/shadowseed/benchmark/ssl45_benefit_suite.py
src/shadowseed/benchmark/ssl45_model_benefit_suite.py
src/shadowseed/analysis/ssl45_result_analyzer.py
```

Belangrijke datasets:

```text
src/shadowseed/data/gap_test_suite_4_5.json
src/shadowseed/data/gap_test_suite_false_positive_4_5.json
src/shadowseed/data/ssl45_benefit_suite.json
src/shadowseed/data/ssl45_model_benefit_suite.json
```

## 5. Benchmarklagen

### 5.1 Positieve Gap-Test Suite

Doel:

> Testen of SSL de juiste ontbrekende structurele gaps vindt.

Deze suite bevat scenario's waarin een antwoord belangrijke elementen mist. De detector moet daar atomische seeds voor maken.

Belangrijke metrics:

- `mean_scenario_score`
- `atomische_hits`
- `promoted_hits`

### 5.2 False-positive controls

Doel:

> Testen of SSL niets verzint wanneer het antwoord al volledig is.

Deze suite bevat volledige antwoorden waarin de relevante gaps al aanwezig zijn.

Belangrijke metrics:

- `candidate_false_positives`
- `promoted_false_positives`
- `promoted_false_positive_rate`

### 5.3 Benefit Suite fase 1

Doel:

> Testen of SSL-promoted seeds de gap coverage van een antwoord verhogen.

Dit is nog geen echte modelrun. Het is een gecontroleerde test van de meetketen.

Belangrijke metrics:

- `baseline_mean_gap_coverage`
- `ssl_mean_gap_coverage`
- `coverage_delta`
- `unsupported_ssl_additions`

### 5.4 Model Benefit Suite fase 2

Doel:

> Testen of hetzelfde model beter antwoordt met SSL-guided rewrite dan zonder SSL.

Deze laag vergelijkt:

```text
zelfde model zonder SSL
zelfde model met SSL-guided rewrite
```

Belangrijke metrics:

- `baseline_mean_gap_coverage`
- `ssl_mean_gap_coverage`
- `coverage_delta`
- `mean_answer_length_delta_words`
- `coverage_delta_per_100_added_words`
- `unsupported_ssl_addition_rate`

## 6. SLM-run

De repo bevat een handmatige workflow voor echte SLM-runs:

```text
Actions → SLM Model Benefit Run → Run workflow
```

Standaardmodel:

```text
TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

De run doet drie dingen:

1. hetzelfde model draait de baselineconditie;
2. SSL detecteert en valideert seeds;
3. hetzelfde model herschrijft het antwoord met SSL-guidance.

Daarna worden de resultaten geanalyseerd en op de Wiki gezet.

Automatische Wiki-output:

```text
SLM-Model-Benefit
SLM-Model-Benefit-Analysis
SLM-Model-Benefit-Analysis-Summary
SLM-Model-Benefit-Raw
SLM-First-Conclusion
```

## 7. Analyse en rapportage

De analyse wordt gemaakt door:

```text
shadowseed analyze-results
```

Output:

```text
results/analysis/analysis_report.md
results/analysis/analysis_summary.json
results/analysis/coverage.svg
results/analysis/false_positive.svg
```

De analyse bevat:

- numerieke samenvatting;
- grafieken;
- promoted seeds per domein;
- toptermen;
- automatische conclusie;
- claimgrens.

De Wiki wordt automatisch bijgewerkt met deze analyse.

## 8. Tussentijdse conclusie

Op basis van de huidige stand is de juiste conclusie:

> SSL 4.5 is nu een werkende, reproduceerbare en toetsbare research-pipeline. De methode detecteert atomische afwezigheden, houdt trace en weight gescheiden, promoot seeds pas na validatie en kan modeloutput vergelijken in baseline- en SSL-conditie.

De huidige resultaten ondersteunen deze beperkte claim:

> Binnen de huidige benchmarkopzet kan SSL worden gemeten als verbetering van gap coverage, mits unsupported additions en false positives laag blijven.

De huidige resultaten ondersteunen nog niet deze brede claim:

> SSL verbetert LLM's of SLM's in het algemeen.

Daarvoor is meer nodig:

- meer scenario's;
- meer domeinen;
- meerdere SLM's;
- herhaalde runs;
- blind review;
- rapportage van negatieve en gemengde resultaten.

## 9. Wetenschappelijke waarde tot nu toe

De waarde van de huidige repo zit niet alleen in de scores. De belangrijkste waarde is dat SSL is omgezet in een meetbare methode.

Voorheen was SSL vooral een conceptuele claim:

```text
ontbrekende elementen kunnen modeloutput verbeteren
```

Nu is het een toetsbare pipeline:

```text
detectie → seed → trace → validation gate → promotion → model benefit test → analyse → Wiki
```

Dat maakt de methode controleerbaar.

## 10. Risico's en beperkingen

### Kleine suite

De huidige suite is klein. Goede scores op deze suite zijn nuttig, maar niet genoeg voor een brede claim.

### Detector kan te passend zijn

Omdat de detector nu domeinpriors gebruikt, moet worden getest of hij ook buiten de huidige scenario's goed werkt.

### Lengte-effect

SSL-antwoorden kunnen langer zijn. Daarom meet de pipeline ook:

```text
coverage_delta_per_100_added_words
```

Verbetering door alleen langere antwoorden telt niet als sterke SSL-winst.

### Geen automatische waarheid

Een promoted seed is geen absolute waarheid. Het is een gevalideerd signaal binnen de testopzet.

### SLM-run is modelafhankelijk

Een positief resultaat met één model geldt niet automatisch voor andere modellen.

## 11. Blind review

De fase-2 output bevat blind review items:

```text
blind_review_items
blind_answer_key
```

De beoordelaar krijgt antwoord A en B zonder te weten welke baseline of SSL is.

Te beoordelen:

- welk antwoord is beter;
- gap coverage;
- unsupported claims;
- helderheid;
- toelichting.

Blind review is nodig voordat claims sterker worden gemaakt.

## 12. Volgende stappen

### Stap 1: eerste SLM-conclusie vastleggen

Gebruik:

```text
Actions → Publish Existing SLM Conclusion → Run workflow
```

Deze workflow pakt de bestaande SLM-run en maakt een Wiki-conclusie.

### Stap 2: scenario's uitbreiden

Minimaal uitbreiden naar:

- 10 positieve scenario's;
- 10 negatieve scenario's;
- 10 gedeeltelijk complete scenario's.

### Stap 3: meerdere modellen testen

Altijd per model vergelijken:

```text
model X zonder SSL
model X met SSL
```

Niet model X vergelijken met model Y als bewijs voor SSL.

### Stap 4: blind review uitvoeren

Gebruik de reviewtemplates en de blind review output.

### Stap 5: paperclaims aanpassen

Pas na meer runs en reviews kunnen claims in paper of README sterker worden.

## 13. Printbare conclusie

Als dit dossier wordt uitgeprint, is de kern:

1. SSL 4.5 is geïmplementeerd als testbare methode.
2. De repo bewaakt de interne methode met unit tests en formule-tests.
3. De benchmarklaag test positieve detectie, negatieve controles en benefit.
4. De SLM-laag test hetzelfde model zonder en met SSL.
5. De analyse zet resultaten om in grafieken, semantiek en conclusie.
6. De huidige claim moet beperkt blijven tot de huidige suite en runs.
7. De volgende stap is schaalvergroting en blind review.

## 14. Verwijzingen binnen de Wiki

- [Quick Start](Quick-Start)
- [Conceptueel overzicht](Conceptueel-Overzicht)
- [Architectuur](Architectuur)
- [Benchmarks](Benchmarks)
- [SLM-runs](SLM-Runs)
- [Resultaten en analyse](Resultaten-en-Analyse)
- [Blind review protocol](Blind-Review-Protocol)
- [Roadmap](Roadmap)
- [SSL 4.5 Analysis](SSL-45-Analysis)
- [SLM Model Benefit](SLM-Model-Benefit)
- [SLM First Conclusion](SLM-First-Conclusion)
