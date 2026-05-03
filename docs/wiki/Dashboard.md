# Dashboard

Dit is de snelle statuspagina voor Shadow Seed Learning 4.5.

Gebruik deze pagina als je niet alle workflows wilt bekijken, maar alleen wilt weten:

```text
werkt het systeem?
werkt het met een echt model?
blijft het veilig?
kan het leren uit papers?
```

## Hoofdstatus

| Blok | Run | Betekenis | Waar kijk je? |
|---|---|---|---|
| 1 | Full System Check | Test de volledige lichte keten | [Full Validation Sweep](Full-Validation-Sweep) |
| 2 | Model Reality Check | Test met een echt HF/SLM-model | [Retrieval Model HF](Retrieval-Model-HF) |
| 3 | Safety Check | Test of SSOT niet naïef bronnen accepteert | [SSOT Falsification](SSOT-Falsification) |
| 4 | Paper Scenario Benchmark | Test scenario’s die uit papers komen | `Paper Scenario Benchmark` artifact |

## 1. Full System Check

Dit is de belangrijkste standaardrun.

Hij controleert:

- unit tests;
- SSL gap suites;
- false-positive gedrag;
- vectorstore smoke;
- SSOT smoke;
- retrieval benchmark;
- retrieval → model benchmark;
- memory, FAISS en Chroma.

Gebruik deze run om te beantwoorden:

> Werkt het hele systeem nog?

Als deze run rood is, kijk eerst hier.

## 2. Model Reality Check

Deze run gebruikt een echt HF/SLM-model.

Hij vergelijkt:

```text
antwoord zonder SSOT-context
vs
antwoord met opgehaalde SSOT-context
```

Gebruik deze run om te beantwoorden:

> Helpt retrieval + SSOT ook bij echte modeloutput?

Deze run is zwaarder en blijft daarom handmatig.

## 3. Safety Check

Deze run test of het systeem niet naïef is.

Hij controleert:

- fout of irrelevant document promoot geen seed;
- `llm_proposed` telt niet als bewijs;
- `rejected` chunks tellen nooit mee;
- alleen `verified` chunks mogen de Gate in.

Gebruik deze run om te beantwoorden:

> Slikt SSL niet zomaar elke bron?

## 4. Paper Scenario Benchmark

Deze optionele run gebruikt scenario’s die door de paper-pipeline zijn gemaakt.

Flow:

```text
paper → claims → candidate seeds → scenario’s → benchmark
```

Gebruik deze run om te beantwoorden:

> Kunnen papers nieuwe testscenario’s leveren?

Belangrijk: deze paper-scenario’s worden niet automatisch gemengd met de core suites. Ze liggen ernaast als extra bewijslaag.

## Simpele prioriteit

Als je weinig tijd hebt:

1. kijk naar **Full System Check**;
2. kijk naar **Safety Check**;
3. kijk naar **Model Reality Check**;
4. kijk naar **Paper Scenario Benchmark**.

## Wat betekent groen?

Groen betekent:

```text
de implementatie werkt binnen de huidige tests
```

Groen betekent niet automatisch:

```text
wetenschappelijk definitief bewezen
```

Voor sterk bewijs blijven nodig:

- meer papers;
- meer scenario’s;
- meerdere echte modellen;
- herhaalde runs;
- blind review.

## Korte conclusie

De vier blokken samen geven het snelste beeld:

```text
systeem werkt
+ modelcheck werkt
+ safety werkt
+ paperuitbreiding werkt
```

Als die vier groen zijn, is SSL 4.5 technisch gezond en klaar voor verdere validatie.