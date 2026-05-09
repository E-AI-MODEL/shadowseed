# Benchmarks

Niet elke suite draagt dezelfde bewijslast. Dat is de hoofdregel.

## De vier bewijsblokken

### 1. Interne logica

Vraag:

- werkt de mechaniek nog?
- blijft de Gate gedisciplineerd?
- gaat de meetketen niet stuk?

Voorbeelden:

- gap suite
- false-positive suite
- blind smoke
- adversarial Gate
- SSOT falsification

### 2. Open-set seedkwaliteit

Vraag:

- kan SSL op onbekende teksten bruikbare seeds maken zonder vaste seedlijst?

Voorbeelden:

- HF intake
- open-set review
- review-packets
- agreement en disagreements

### 3. Output-effect

Vraag:

- wordt output echt beter, completer of bruikbaarder?

Voorbeelden:

- benefit suite
- model benefit
- probe utility
- unsupported additions

### 4. Robustheid over configuraties

Vraag:

- blijft het effect overeind over meerdere modellen, modelgroottes en vectorbackends?

Voorbeelden:

- retrieval-model vergelijkingen
- vectorstore backends
- full validation sweep

Kernregel:

> een sterke stresstest van de interne logica is nog geen bewijs van effect op vrije output

## Standaard Actions-runs

| Run | Hoofdvraag | Type |
|---|---|---|
| 01 Codecheck | Werkt de Python-code? | regressie |
| 02 Gap Finder | Werkt de detectie op bekende gaps nog? | interne logica |
| 03 Rustig blijven | Blijft de Gate onzin blokkeren? | interne logica |
| 04 Antwoordwinst | Wordt een antwoord completer met SSL? | output-effect |
| 05 Model smoke | Werkt de modelroute technisch? | technische smoke |
| 06 Blind test | Blijven labels verborgen tot scoring? | interne logica |
| 07 Rapport | Hoe zien de resultaten er samen uit? | rapportage |
| 08 AbsenceBench rooktest | Werkt de lokale dataset-run? | technische smoke |
| 09 Herhalingstest | Blijft gedrag stabiel over meerdere rondes? | interne logica |

## Handmatige research-routes

| Route | Hoofdrol | Bewijsblok |
|---|---|---|
| open-set review | seedkwaliteit zonder vaste seedlijst | open-set seedkwaliteit |
| adversarial Gate | vergelijking met zwakkere promotieregels | interne logica |
| probe utility | scherpte van vervolgacties | output-effect |
| retrieval en full sweep | backend- en modelvergelijkingen | configuratierobustheid |

## Hoe je dit moet lezen

### Als een interne logica-test sterk is

Dan weet je vooral:

- de mechaniek werkt nog
- de Gate lijkt gedisciplineerd
- de benchmarklaag is niet direct stuk

### Dan weet je nog niet automatisch

- dat SSL op onbekende teksten goede seeds maakt
- dat LLM-output breed beter wordt
- dat het effect overeind blijft bij andere modellen of vectorbackends

## Belangrijke aanvullende pagina's

- [Workflows](Workflows)
- [Blind Benchmark](Blind-Benchmark)
- [Latest Test Results](Latest-Test-Results)
- [SSL 4.5 Analysis](SSL-45-Analysis)
- [Full Validation Sweep](Full-Validation-Sweep)
