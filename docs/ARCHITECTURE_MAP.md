# Repo-overzicht

Deze pagina is de kaart van de repo. Gebruik hem als startpunt als je niet meer weet welke run waarvoor is.

## Vier banen

| Baan | Doel | Belangrijkste plekken | Status |
|---|---|---|---|
| Core SSL | Seeds opslaan, laten uitdoven, valideren en eventueel promoten | `src/shadowseed/manager.py`, `src/shadowseed/vectorstore/`, `src/shadowseed/ssot.py` | prototype, getest |
| Benchmarks | Meten of SSL iets vindt, niets verzint en antwoorden helpt | `src/shadowseed/benchmark/`, `src/shadowseed/data/` | CI en handmatig |
| Rapportage | JSON-resultaten samenvatten tot rapport en grafieken | `src/shadowseed/analysis/ssl45_result_analyzer.py`, `results/latest/` | automatisch |
| Publicatie | Laatste resultaten tonen op Wiki en Pages | `.github/workflows/publish-test-results.yml`, `site/`, `docs/wiki/` | automatisch na main push |

## De hoofdroute

```text
push naar main
  -> Checks en benchmark-resultaten
  -> artifacts uploaden
  -> Publiceer testresultaten naar Wiki en Pages
  -> results/latest + results/artifacts
  -> Wiki + Pages
```

De hoofdroute gebruikt alleen geslaagde `push`-runs op `main`. PR-runs worden niet gepubliceerd.

## Welke run doet wat?

| Runnaam in GitHub Actions | Wat doet hij? | Uitkomst |
|---|---|---|
| 01 Codecheck | Controleert of de Python-code en unit tests werken | pytest-resultaat |
| 02 Gap Finder | Test of SSL bekende ontbrekende punten vindt | `ssl45_gap_suite.json` |
| 03 Rustig blijven | Test of SSL volledige antwoorden met rust laat | `ssl45_false_positive_suite.json` |
| 04 Antwoordwinst | Test of SSL-toevoegingen een antwoord completer maken | `ssl45_benefit_suite.json` |
| 05 Model smoke | Test dezelfde modelroute met fixture-backend | `ssl45_model_benefit_suite.json` |
| 06 Blind test | Test labelscheiding: detectie ziet labels niet vooraf | `blind_benchmark.json` |
| 07 Rapport | Vat kernresultaten samen | `analysis_report.md`, `summary.json`, grafieken |
| 08 AbsenceBench rooktest | Controleert lokale AbsenceBench-run | `absencebench_smoke.json` |
| 09 Herhalingstest | Draait Gap Finder met meer of minder rondes | `ssl45_gap_suite_turns_*.json` |

## Handmatige workflows

| Workflow | Wanneer gebruiken? |
|---|---|
| Blind test handmatig | Als je alleen de blinde smoke-test opnieuw wilt draaien |
| Model Reality Check | Als je een echte Hugging Face modelrun wilt doen |
| Deploy Dashboard handmatig | Alleen als noodroute voor Pages |
| Publish Static Wiki Docs | Alleen om statische wiki-pagina's opnieuw te publiceren |

## Waar staan de resultaten?

| Pad | Betekenis |
|---|---|
| `results/latest/summary.json` | Centrale machineleesbare samenvatting |
| `results/latest/analysis_report.md` | Menselijk rapport |
| `results/latest/manifest.json` | Herkomst van elk gepubliceerd artifact |
| `results/artifacts/` | Originele artifactstructuur uit GitHub Actions |
| GitHub Wiki `Latest-Test-Results` | Wiki-ingang naar de laatste gepubliceerde resultaten |
| GitHub Pages | Visueel dashboard |

## Belangrijke grens

De standaard CI gebruikt vooral kleine suites en fixture-runs. Dat bewijst dat de meetketen werkt. Echte modelclaims horen bij handmatige HF-runs, grotere suites en blind review.
