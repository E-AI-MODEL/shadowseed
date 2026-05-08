# Repo-overzicht

Deze pagina is de kaart van de repo. Gebruik hem als startpunt als je niet meer weet welke run waarvoor is.

De repo heeft niet één doel maar meerdere banen die samen moeten blijven kloppen. Juist daarom is het belangrijk om regressie, benchmark, rapportage en publicatie niet met elkaar te verwarren.

## Vier banen

| Baan | Doel | Belangrijkste plekken | Status |
|---|---|---|---|
| Core SSL | Seeds opslaan, laten uitdoven, valideren en eventueel promoten | `src/shadowseed/manager.py`, `src/shadowseed/vectorstore/`, `src/shadowseed/ssot.py` | prototype, getest |
| Benchmarks | Meten of SSL iets vindt, niets verzint en antwoorden helpt | `src/shadowseed/benchmark/`, `src/shadowseed/data/` | CI en handmatig |
| Rapportage | JSON-resultaten samenvatten tot rapport en grafieken | `src/shadowseed/analysis/ssl45_result_analyzer.py`, workflow-snapshot `results/latest/` | automatisch |
| Publicatie | Laatste resultaten tonen op Wiki en Pages | `.github/workflows/publish-test-results.yml`, `site/`, `docs/wiki/` | automatisch na main push |

## De hoofdroute

```text
push naar main
  -> Checks en benchmark-resultaten
  -> artifacts uploaden
  -> Publiceer testresultaten naar Wiki en Pages
  -> results/latest + results/artifacts als workflow-snapshot
  -> Wiki + Pages + workflow-artifact
```

De hoofdroute gebruikt alleen geslaagde `push`-runs op `main`. PR-runs worden niet gepubliceerd. De publish-workflow commit geen resultatensnapshot terug naar `main`.

Binnen `07 Rapport` worden artifacts eerst provenance-safe verzameld: de originele artifactstructuur blijft behouden per artifact, eventuele naamconflicten krijgen een artifactprefix en `results/manifest.json` bewaart de herkomst van de analyse-input.

Binnen de publish-workflow worden daarna ook expliciete guardrails afgedwongen: de run stopt als verplichte kernbestanden ontbreken, als het manifest geen `copied_files` bevat of als de centrale `summary.json` leeg of ongeldig is.

## Welke run doet wat?

| Runnaam in GitHub Actions | Wat doet hij? | Uitkomst | Bewijssoort |
|---|---|---|---|
| 01 Codecheck | Controleert of de Python-code en unit tests werken | pytest-resultaat | regressie |
| 02 Gap Finder | Test of SSL bekende ontbrekende punten vindt | `ssl45_gap_suite.json` | kleine benchmark |
| 03 Rustig blijven | Test of SSL volledige antwoorden met rust laat | `ssl45_false_positive_suite.json` | regressie / kleine benchmark |
| 04 Antwoordwinst | Test of SSL-toevoegingen een antwoord completer maken | `ssl45_benefit_suite.json` | kleine benchmark |
| 05 Model smoke | Test dezelfde modelroute met fixture-backend | `ssl45_model_benefit_suite.json` | technische smoke |
| 06 Blind test | Test labelscheiding: detectie ziet labels niet vooraf | `blind_benchmark.json` | methodologische smoke |
| 07 Rapport | Vat kernresultaten samen | `analysis_report.md`, `summary.json`, grafieken | rapportage |
| 08 AbsenceBench rooktest | Controleert lokale dataset-run | `absencebench_smoke.json` | technische smoke |
| 09 Herhalingstest | Draait Gap Finder met meer of minder rondes | `ssl45_gap_suite_turns_*.json` | regressie / gevoeligheid |

## Handmatige workflows

| Workflow | Wanneer gebruiken? |
|---|---|
| Blind test handmatig | Als je alleen de blinde smoke-test opnieuw wilt draaien |
| Model Reality Check | Als je een echte Hugging Face modelrun wilt doen |
| Publiceer testresultaten naar Wiki en Pages | Als je de laatste geslaagde `main`-run opnieuw wilt publiceren zonder nieuwe test-run |
| Publiceer alleen statische Wiki-pagina's | Alleen om statische wiki-pagina's opnieuw te publiceren |

## Waar staan de resultaten?

| Plek | Betekenis |
|---|---|
| workflow-artifact `published-latest-results-snapshot` | Platte snapshot van de gepubliceerde `results/latest` map |
| `results/latest/summary.json` | Centrale machineleesbare samenvatting binnen de gepubliceerde snapshot |
| `results/latest/analysis_report.md` | Menselijk rapport binnen de gepubliceerde snapshot |
| `results/latest/manifest.json` | Herkomst van elk gepubliceerd artifact |
| `results/artifacts/` | Originele artifactstructuur binnen de gepubliceerde snapshot |
| GitHub Wiki `Latest-Test-Results` | Wiki-ingang naar de laatste gepubliceerde resultaten |
| GitHub Pages | Visueel dashboard |

## Belangrijke grens

De standaard CI gebruikt vooral kleine suites en fixture-runs. Dat bewijst dat de meetketen werkt en dat regressies zichtbaar worden.

De standaard CI bewijst niet automatisch:

- algemene SSL-prestatie buiten de vaste suites;
- open-set seedkwaliteit;
- sterke adversarial Gate-robustheid;
- brede modelclaims op echte backends;
- domeintransfer;
- modelinterne validatie.

Voor dat soort claims zijn handmatige HF-runs, grotere suites, menselijke review en aparte evaluatielagen nodig.

## Hoe deze kaart samenhangt met de research-docs

Gebruik deze combinatie:

- `ARCHITECTURE_MAP.md` voor de vraag: wat draait hier precies?
- `docs/research/current-status.md` voor de vraag: wat bewijst dat vandaag echt?
- `docs/research/scenario-independence-roadmap.md` voor de vraag: waar moet het bewijs heen?
- `docs/research/evaluation-matrix.md` voor de vraag: welke laag draagt welke claim?
