# Waarom SSL niet naïef is

Deze pagina legt uit waarom SSL 4.5 niet zomaar elke bron, elk modelantwoord of elke similarity-hit als waarheid accepteert.

## 1. Een seed begint zonder invloed

Een nieuwe shadow seed krijgt wel een spoor, maar geen gewicht:

```text
trace = 2.0
weight = 0.0
```

Dat betekent:

- het systeem heeft een mogelijk gemis gezien;
- het gemis wordt onthouden;
- het mag het antwoord nog niet sturen.

## 2. Similarity is geen waarheid

Een vectorstore kan alleen zeggen:

```text
Deze nieuwe input lijkt op een bestaande seed.
```

De vectorstore mag niet beslissen:

```text
Deze seed is waar.
```

Daarom blijft dit principe leidend:

```text
SSLManager.seeds = bron van waarheid
Vectorstore = zoekindex
```

## 3. SSOT is alleen bewijs als de chunk verified is

De SSOT-laag accepteert niet blind elke tekst.

| Chunkstatus | Mag seed valideren? |
|---|---:|
| `llm_proposed` | nee |
| `rejected` | nee |
| `verified` | ja |

LLM-output kan dus wel worden opgeslagen als voorstel, maar niet meteen als waarheid.

## 4. Menselijke verificatie is de grens

Een LLM kan chunks voorstellen:

```text
LLM output → llm_proposed
```

Pas na verificatie:

```text
verify_chunk() → verified
```

kan een chunk meetellen als externe evidence.

Afwijzing werkt ook expliciet:

```text
reject_chunk() → rejected
```

Rejected chunks blijven zonder invloed.

## 5. De Validation Gate beslist langzaam

Zelfs verified evidence geeft niet meteen volledige invloed.

Met de huidige instelling:

```text
validation_increment = 0.2
promotion_threshold = 0.5
```

moet een seed meerdere geldige Gate-passes halen voordat hij promoted wordt.

Voorbeeld:

```text
pass 1 → weight 0.2
pass 2 → weight 0.4
pass 3 → weight 0.6 → PROMOTED
```

Dit voorkomt dat één document of één correctie meteen te veel macht krijgt.

## 6. Falsification-tests

De repo bevat tests die controleren of SSL niet naïef is:

```text
tests/test_ssot_falsification.py
```

Deze tests bewijzen drie dingen:

1. een fout of irrelevant document promoot geen seed;
2. LLM-output met `llm_proposed` valideert geen seed;
3. rejected chunks valideren nooit een seed.

## 7. Waarom dit belangrijk is

Veel RAG-systemen doen ongeveer dit:

```text
tekst gevonden → tekst gebruiken
```

SSL 4.5 doet iets anders:

```text
tekst gevonden → status checken → Gate checken → pas daarna invloed
```

Dat verschil is belangrijk. Retrieval is niet hetzelfde als waarheid.

## 8. Wat dit wel en niet bewijst

Dit bewijst wel:

- SSL heeft beschermingen tegen te snelle promotie;
- modeloutput wordt niet automatisch waarheid;
- slechte of afgewezen chunks blijven zonder invloed;
- de Gate blijft leidend.

Dit bewijst nog niet:

- dat alle slechte documenten altijd worden herkend;
- dat bronconflicten volledig zijn opgelost;
- dat SSL productieproof is op grote kennisbanken.

## 9. Samenvatting

SSL is niet naïef omdat het drie veiligheidslagen combineert:

```text
gewichtloos starten
+ verified-only SSOT
+ trage Validation Gate
```

Daardoor kan het systeem leren van documenten en feedback, zonder zichzelf meteen te foppen.