# Shadow Seed Learning 4.5

Deze wiki is bedoeld als **ingang**, niet als tweede README.

## Begin met deze drie pagina's

1. [Latest Test Results](Latest-Test-Results)
2. [SSL 4.5 Analysis](SSL-45-Analysis)
3. [Workflows](Workflows)

## De vier bewijsblokken

### 1. Interne logica

Vraag:

- werkt de mechaniek nog?
- blijft de Gate gedisciplineerd?
- loopt de meetketen nog goed?

### 2. Open-set seedkwaliteit

Vraag:

- kan SSL op onbekende teksten bruikbare seeds maken zonder vaste scenario-seeds?

### 3. Output-effect

Vraag:

- wordt de output echt beter, completer of bruikbaarder?

### 4. Robustheid over configuraties

Vraag:

- blijft het effect overeind over meerdere modellen en vectorbackends?

Kernregel:

> een sterke interne stresstest is nog geen bewijs van effect op vrije LLM-output

## Wanneer gebruik je welke pagina?

| Pagina | Gebruik deze voor |
|---|---|
| [Latest Test Results](Latest-Test-Results) | de laatste gepubliceerde standaardrun |
| [SSL 4.5 Analysis](SSL-45-Analysis) | de samengevatte uitkomst van die run |
| [Workflows](Workflows) | uitleg welke workflow welk bewijsblok raakt |
| [Benchmarks](Benchmarks) | uitleg wat elke suite inhoudelijk meet |
| [Blind Benchmark](Blind-Benchmark) | alleen de methodologische blinde laag |
| [Full Validation Sweep](Full-Validation-Sweep) | bredere backend- en retrievalrobustheid |
| [SSOT Falsification](SSOT-Falsification) | gerichte SSOT-veiligheidscheck |

## Wat je hier niet moet aannemen

De standaardresultaten laten vooral zien dat de meetketen werkt en dat de kleine benchmarklaag stabiel blijft.

Ze bewijzen niet automatisch:

- open-set seedkwaliteit
- brede modelprestatie
- domeintransfer
- menselijke agreement over seedkwaliteit
- robuustheid over meerdere modellen en vectorbackends

Voor inhoudelijk doelbeeld en repo-structuur blijf je het beste in de repo zelf:

- `README.md`
- `docs/00_shadow_seed_learning_4_6.md`
- `docs/ARCHITECTURE_MAP.md`
