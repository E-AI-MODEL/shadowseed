# Start hier: Shadow Seed Learning 4.5

Deze pagina is de eenvoudige instap in het hele project. Lees dit als je snel wilt begrijpen wat SSL 4.5 is, wat er gebouwd is, wat er getest wordt en waar de resultaten staan.

## 1. Het idee in één zin

Shadow Seed Learning gebruikt ontbrekende informatie als signaal.

Een model kan een antwoord geven dat goed klinkt, maar toch iets belangrijks mist. SSL noemt zo’n ontbrekend punt een **shadow seed**.

Voorbeeld:

```text
Vraag: Wat moet je juridisch noemen bij een Nederlandse consument en een Amerikaanse webwinkel?

Mogelijk gemist:
- rechtsbevoegdheid
- toepasselijk recht
- afdwingbaarheid van EU-consumentenrecht
```

SSL probeert zulke gemiste punten niet meteen als waarheid te gebruiken. Eerst worden ze vastgelegd als gewichtloze seeds.

## 2. De belangrijkste regel

> Een seed bevat precies één ontbrekend punt.

Goed:

```text
Toepasselijk recht bij internationale online koop.
```

Te breed:

```text
De juridische context ontbreekt.
```

Waarom dit belangrijk is: alleen kleine, duidelijke seeds kun je later goed testen.

## 3. Gewichtloos betekent veilig

Een nieuwe seed krijgt:

```text
trace = aanwezig spoor
weight = 0.0
```

Dat betekent:

- SSL heeft iets opgemerkt;
- maar het mag het antwoord nog niet sturen;
- eerst is bewijs nodig.

Dit voorkomt dat het systeem te snel conclusies trekt.

## 4. Hoe een seed invloed krijgt

Een seed mag pas gewicht krijgen via de Validation Gate.

De Gate kijkt naar:

```text
1. Komt de seed vaker terug?
2. Is er externe bevestiging?
3. Is er geen tegenspraak?
```

Pas daarna kan een seed `PROMOTED` worden.

## 5. De nieuwe laag: vectorruimte

Seeds worden nu ook als vector opgeslagen. Daardoor kan SSL herkennen:

```text
Deze nieuwe vraag lijkt op een eerder onzeker gebied.
```

Belangrijk:

```text
SSLManager.seeds = bron van waarheid
Vectorstore = zoekindex
```

De vectorstore beslist dus niets over waarheid of gewicht. Hij helpt alleen zoeken.

Beschikbare backends:

- memory
- FAISS
- Chroma

## 6. De nieuwe laag: SSOT

SSOT betekent hier: een vertrouwde bron, bijvoorbeeld een document dat de gebruiker toevoegt.

Een document kan:

1. worden geïndexeerd;
2. relevante tekst leveren bij een vraag;
3. open seeds valideren;
4. helpen om blinde vlekken te vinden.

Ook hier geldt:

```text
SSOT levert bewijs
Validation Gate beslist
```

## 7. Wat er nu getest wordt

De repo test meerdere lagen.

| Laag | Vraag |
|---|---|
| Gap-Test Suite | Vindt SSL de juiste ontbrekende punten? |
| False-positive controls | Laat SSL volledige antwoorden met rust? |
| Vectorstore smoke | Werken gewichtloze seeds in vectorruimte? |
| SSOT smoke | Kan een document open seeds valideren? |
| Retrieval benchmark | Welke vectorstore haalt de juiste tekst op? |
| Retrieval → model benchmark | Maakt retrieval het antwoord beter? |
| HF model run | Werkt dit ook met een echt klein taalmodel? |

## 8. De lijn van bewijs

De hele keten ziet er zo uit:

```text
vraag
→ modelantwoord
→ SSL detecteert ontbrekend punt
→ seed wordt gewichtloos opgeslagen
→ vectorstore kan vergelijkbare onzekerheid terugvinden
→ SSOT-document levert bewijs
→ Validation Gate beslist
→ retrieval haalt relevante brontekst op
→ model antwoordt opnieuw
→ benchmark meet of het antwoord completer is
→ Wiki toont resultaat en conclusie
```

Dit is de kern van het project.

## 9. Waar staan de belangrijkste resultaten?

Automatische resultaatpagina’s:

- [SSL 4.5 Analysis](SSL-45-Analysis)
- [SLM Model Benefit](SLM-Model-Benefit)
- [SLM First Conclusion](SLM-First-Conclusion)
- [Vectorstore Smoke](Vectorstore-Smoke)
- [SSOT Smoke](SSOT-Smoke)
- [Backend Comparison](Backend-Comparison)
- [Retrieval-Comparison](Retrieval-Comparison)
- [Retrieval Model Comparison](Retrieval-Model-Comparison)
- [Retrieval Model HF](Retrieval-Model-HF)

Lees vooral deze twee als je snel wilt weten of het werkt:

1. [Retrieval Model Comparison](Retrieval-Model-Comparison)
2. [Retrieval Model HF](Retrieval-Model-HF)

## 10. Wat kun je nu voorzichtig concluderen?

De juiste tussentijdse conclusie is:

> SSL 4.5 is nu een werkende, reproduceerbare testpipeline. De pipeline kan meten of ontbrekende punten worden gevonden, gevalideerd, opgehaald uit een SSOT en gebruikt om antwoorden completer te maken.

Wat je wel mag zeggen:

- de methode is geïmplementeerd;
- de losse onderdelen zijn testbaar;
- de keten is meetbaar;
- vectorstore, SSOT en modeloutput zijn gekoppeld;
- resultaten worden automatisch gerapporteerd.

Wat je nog niet te breed moet zeggen:

- niet dat SSL elk model altijd verbetert;
- niet dat één run genoeg is;
- niet dat dit al productieproof is;
- niet dat retrieval gelijk staat aan waarheid.

## 11. Wat is de volgende stap?

Voor sterker bewijs zijn nodig:

1. meer scenario’s;
2. meerdere modellen;
3. herhaalde runs;
4. blind review;
5. echte documenten in plaats van alleen fixtures;
6. vergelijking tussen positieve, negatieve en gemengde resultaten.

## 12. Leesroute

Voor snel begrip:

1. deze pagina;
2. [Visueel verhaal](Visueel-Verhaal);
3. [Tussentijdse rapportage](Tussentijdse-Rapportage);
4. [Retrieval Model Comparison](Retrieval-Model-Comparison);
5. [Retrieval Model HF](Retrieval-Model-HF).

Voor technisch begrip:

1. [Architectuur](Architectuur);
2. [Vectorstore en gewichtloze seeds](Vectorstore-en-Gewichtloze-Seeds);
3. [SSOT en documentvalidatie](SSOT-en-Documentvalidatie);
4. [Benchmarks](Benchmarks).

## 13. Samenvatting voor print

SSL 4.5 onderzoekt of een model beter kan worden door niet alleen te kijken naar wat er staat, maar ook naar wat structureel ontbreekt. Die ontbrekende punten worden eerst veilig en gewichtloos opgeslagen. Pas wanneer ze herhaald terugkomen en door een vertrouwde bron worden bevestigd, krijgen ze invloed. Met vectorstores worden vergelijkbare onzekerheden teruggevonden. Met SSOT-documenten worden seeds gevalideerd. Met retrieval worden relevante bronnen opgehaald. Met benchmarks wordt gemeten of antwoorden daardoor completer worden.

De repo is daarmee niet alleen een prototype, maar een meetbare onderzoeksopzet.