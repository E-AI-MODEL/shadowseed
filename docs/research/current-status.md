# Huidige Status van SSL-validatie

> Status: current
> Date: 2026-05-22 (open-set status refreshed 2026-06-09, na PR #116)
> Evidence layer: status snapshot across layers A-G
> Source: 4.6 evidence model in `docs/00_shadow_seed_learning_4_6.md`

## Doel van dit document

Dit document maakt expliciet wat de repository vandaag werkelijk aantoont, wat slechts gedeeltelijk is afgedekt, en wat nog gepland of conceptueel is.

De kernregel is eenvoudig:

> wat mechanisch werkt is nog niet automatisch wetenschappelijk bewezen.

Dit document scheidt daarom vier dingen:

- wat in code en workflows aantoonbaar aanwezig is;
- wat als redelijke tussenstap geldt;
- wat nog niet sluitend is gevalideerd;
- wat nog onderzoekswerk is.

## Samenvatting

De repo staat er sterk voor als benchmark-harness voor SSL-mechaniek. De kernlogica rond atomische seeds, `trace`, `weight`, Validation Gate, blinde labelscheiding, retrieval-smokes en rapportage is aanwezig en functioneel.

De repo staat er nog niet sterk genoeg voor als volledig bewijs van het hele SSL-onderzoeksprogramma (4.5 als mechaniek, 4.6 als evaluatiekoers). Open-set validatie, domeintransfer en modelinterne validatie zijn nog niet op het niveau dat een brede algemene claim zou dragen. Adversarial Gate-evaluatie en probe-feedback gedrag hebben sinds 2026-05-22 eerste echte evidence (PRs #80 en #82). Open-set seedkwaliteit heeft sinds 2026-06-09 een eerste echt mensgereviewde batch (PR #116, round 005 offset-12) — en die is inhoudelijk een kwaliteitswaarschuwing, geen succes.

Korte totaalscore per laag (per 2026-05-22):

- mechanische regressie: sterk
- kleine benchmarkvalidatie: bruikbaar
- open-set seedkwaliteit: **eerste echte evidence geland, met kwaliteitswaarschuwing** (PR #116). Round 005 offset-12 (Qwen2.5-3B, v0.3e) is volledig mensgereviewd: 41 unieke seeds, acceptance **0.29** (criterium was ≥ 0.60), relevance 0.98 maar non_triviality en follow_up_utility beide 0.29, reviewer agreement unaniem. v0.3e repareerde de vorm (claim-vs-gap 30 → 0 t.o.v. round 004) maar niet de substantie: de detector vindt on-topic maar overwegend triviale of niet-toetsbare afwezigheden. De offset-0 batch en de blinde control zijn inmiddels gesloten als gedelegeerde AI-review (zie hieronder)
- adversarial Gate-evaluatie: eerste echte evidence (PR #80, F1 1.0 op 21 candidates met drie baselines)
- probe utility behavioral: eerste echte evidence (PR #82, 10/10 lifecycle scenarios)
- probe utility prompt-quality: bestaand scaffold in `ssl45_probe_utility_suite`
- open-set/domeintransfer replicatie (round 007, v0.3g, verse items): de model-hefboom houdt out-of-sample stand (nieuws 0.333, wetenschap 0.268 — beide ruim boven Qwen 0.185), maar de round-006 niveaus (0.50/0.458) waren optimistisch en de nieuws-vs-wetenschap-framing onjuist: de daling is niet domein-gebonden (nieuws offset 30 = 0.333 ≈ wetenschap offset 20 = 0.268). Een 'tekstdichtheid'-verklaring hield géén stand bij toetsing: `scripts/analyze_acceptance_vs_density.py` vindt |r| < 0.25 voor vijf deterministische proxies over 48 items; de driver van de daling is dus nog onbekend (kandidaten die deze n=48 single-reviewer-opzet niet kan scheiden: subdomein-moeilijkheid, item-selectie, reviewer-variantie). v0.3g lost de vorm overal op (prescreen clean-rate 0.90/0.95, claim_vs_gap 0). Zie `benchmarks/open_review/rounds/round_007/`
- domeintransfer: **eerste signaal** (2026-06-11, round 006 batch 2): zelfde Phi-3.5-mini + v0.3e op 12 arXiv-abstracts levert AI-gereviewde acceptance **0.458** vs 0.50 op nieuws (zelfde reviewer/model/prompt) — kwaliteit transfereert; het faalprofiel verschuift ("of"-stapeling, LaTeX-truncatie). Eén exploratieve batch, AI-gereviewd: signaal, geen validatie
- human-vs-AI agreement (2026-06-13, eerste sinds round 005): blinde maintainer-review van round 006 batch 1 (54 beoordeeld, 4 abstain) geeft human acceptance **0.593** vs AI **0.519**, raw agreement 0.815, **Cohen's κ 0.627** (substantial). Conclusie: de gedelegeerde AI-reviews zijn een bruikbare proxy, en de 0.50-headline is niet opgeblazen — de mens is zelfs iets milder. De rest-onenigheid zit op de impact/speculatie-grens (de zachtste rubriek). Zie `round_006/batch1/human_review/RESULTS.md`. Nog steeds signaal, geen Laag-C-validatie (n=54, één reviewer, criterium ≥ 0.60)
- rubric-fragiliteit (round 006-007, `scripts/analyze_rubric_sensitivity.py`): de AI-acceptance is gevoelig voor de uitlegregel. Onder één strengere deterministische regel zakt de 0.50-headline-batch naar 0.328 (swing -0.172) en krimpt de cross-batch spread van 0.232 naar 0.146 — een deel van het in-sample/out-of-sample-verschil was reviewer-mildheid, niet alleen items. Zelf-consistentie-grens (zelfde agent), geen onafhankelijke review; de blinde human pass (`round_006/batch1/human_review/`) beslist welke regel dichter bij een mens ligt
- **strategische stand (2026-06-13, zie `docs/research/milestone-open-set-2026-06.md`)**: de vraag 'kan het systeem kleine gaps detecteren/valideren?' is grotendeels met JA beantwoord (detectie ~menskwaliteit op Phi-3.5, methodologie gevalideerd met κ 0.63). De openstaande, beslissende vraag is de payoff: *levert handelen op gevalideerde seeds meetbaar betere antwoorden op?* Detector-iteratie is gestopt bij v0.3g; de volgende stap is de end-to-end payoff-test (round 008), niet meer detectie-tuning
- **payoff-test eerste signaal (2026-06-14, round 008 run 01)**: end-to-end vraag *maken seeds antwoorden beter?* op Phi-3.5-mini, blinde lezer-beoordeling. **SSL-win-rate 0.333 (1 van 3)** — criterium >0.5 niet gehaald, richting negatief (n=3, dus signaal geen verdict). De deterministische coverage-metric bevestigt onafhankelijk: alleen MODEL_B verbeterde (0→0.5). Mechanisme: de seeds zijn niet het probleem, de **revisie-stap derailt** op een klein model (gehallucineerd gedicht; verkeerd product erbij gehaald) — behalve MODEL_B waar de revisie échte juridische substantie injecteerde (de 4.6-belofte werkend). Conclusie: detectie is opgelost, de bottleneck verschuift naar de **seed-injectie/revisie-stap** en modelcapaciteit. Zie `round_008/payoff_run_01/`
- **payoff run 02 (no-harm append)**: zelfde baselines + seeds, maar injectie als gewichtloze toevoeging i.p.v. vrije herschrijving → **SSL-win 1.0 (3/3)** vs 0.333 bij run 01. Bevestigt: de run-01-schade zat in de herschrijf-stap, niet in de seeds; seeds zijn 'potentieel, geen must' en voegen veilig waarde toe wanneer het handelen erop de Gate-filosofie volgt (do-no-harm op antwoordniveau). Kanttekening: de append is per constructie een superset (kan nauwelijks verliezen) en altijd langer — een vloer, geen plafond. Doel blijft: herschrijving die én do-no-harm én vloeiend integreert. Zie `round_008/payoff_run_02/`
- **payoff op capabel model (2026-06-18, round 010, `openai:gpt-4o-mini`)**: de round-008 next-step ('groter model') uitgevoerd via de nieuwe OpenAI-backend (workflow `Research · SSL Benefit (OpenAI)`, secret-only key). Onder dezelfde **vrije** herschrijf-prompt die Phi-3.5 deed derailen: `unsupported_ssl_addition_rate = 0.0` op alle 3 scenario's, geen hallucinatie/topic-bleed. Blinde AI-lezer: **2 ssl-wins / 1 tie / 0 losses** (vs 1/2 bij Phi-3.5); MODEL_C coverage 0→1.0 schoon. Conclusie: de round-008-negatief was een **klein-model-artefact van de revisie-stap**, geen SSL-fout — do-no-harm ontstaat vanzelf bij een capabel model. Metrische kanttekening: MODEL_B's correcte seed is zichtbaar geïntegreerd maar door `coverage()` op 0 gescoord (jaccard/phrasing-artefact). n=3, AI-geoordeeld → sterk signaal, geen Laag-C. Zie `round_010/`
- **gap-3 head-to-head (2026-06-18, round 010, B→B′) — signaal teruggedraaid door echte embeddings**: `run-ssl-vs-rag` op gpt-4o-mini, query=gap (SSL-probe) vs query=vraag (RAG), gelijk contextbudget. Met de **speelgoed-128d hash** (B) leek de SSL-probe te winnen op SSLRAG_LAW (RAG haalde verkeerde chunks → non-antwoord; probe → correct). Met **echte embeddings** (B′, `text-embedding-3-small` 1536d, run 27790952137) verdwijnt dat: gewone RAG op de vraag haalt nu zélf de 3 juiste recht-chunks, `seed_only_chunk_ids = []`. De B-winst was dus een **retriever-artefact**, geen SSL-eigenschap. Op SSLRAG_IR blijft het probe-*mechanisme* echt (`seed_only=[labour]`) maar het ruilt `innovation` weg en het antwoord wordt niet beter. Blinde AI-lezer B′: **0 SSL-wins / 2**. Conclusie: een **fixture/meet-verdict, geen SSL-verdict** — de corpus kan geen gap stellen die orthogonaal is aan de vraag (de seeds zijn parafrases van ophaalbare chunks). Vervolg: een fixture waar de beslissende gap niet uit de vraag ophaalbaar is; en schaal vooral experiment A (payoff, retrieval-onafhankelijk). Zie `round_010/`
- **visie-aanscherping (2026-06-14, `docs/research/vision-generative-seeds.md`)**: het doelbeeld is generatieve "wat had hier KUNNEN staan"-seeds (voorbij het RAG-plafond), niet alleen omissie-detectie. Gewicht is de as mogelijkheid→noodzaak: een "kunnen staan" wordt een "moeten staan" als het gewicht via de Gate stijgt; gewicht 0 maakt ambitie gratis en ruisvrij. Nog niet in de repo: generatieve seed-modus, operationele Retrieval Probe (SSL→RAG-brug), SSL-vs-RAG head-to-head, echte falsificatie, levende cross-turn schaduwlaag
- modelinterne validatie: nog onderzoekswerk per 4.6 doc

## Statusoverzicht per fase

| Fase | Status | Korte duiding |
|---|---|---|
| Fase 0: detectie | First evidence (kwaliteitswaarschuwing) | Drie detectoren op main (v0.1/v0.2/v0.3); fixture-suites groen; round 004 mensgereviewd (acceptance 0.52), round 005 offset-12 mensgereviewd (acceptance 0.29, substantieprobleem); offset-0 + blind control gesloten via gedelegeerde AI-review (offset-0 0.185; control delta +0.219) |
| Fase 1: multi-turn state | Partially implemented | Antwoordwinst is meetbaar op de benefit-suite (delta +0.92 op model-benefit, +0.80 op blind), maar de volledige A/B/C-conditievergelijking uit het testplan ontbreekt nog |
| Fase 2: Validation Gate en probes | First evidence | Gate discrimineert correct op de uitgebreide adversarial fixture (PR #80, F1 1.0); probe-feedback lifecycle gevalideerd op 10 scenarios (PR #82); prompt-quality suite blijft naast de behavioral suite staan |
| Fase 3: constellations | Planned / infrastructural | Bouwstenen bestaan, maar er is nog geen echte constellation-benchmark of clusterwaarde-evaluatie |
| Fase 4: modelinterne test | Planned | Geen operationele evaluatielaag aanwezig |

## Wat de repo vandaag hard aantoont

### 1. De minimale SSL-definitie is technisch aanwezig

De repo toont overtuigend aan dat de volgende mechanische kern bestaat:

- een seed moet atomisch zijn;
- brede seeds kunnen worden geweigerd of gesplitst;
- `trace` en `weight` zijn formeel gescheiden;
- `weight` start op `0.0`;
- promotie loopt via een Validation Gate;
- promoted seeds kunnen vervolglogica sturen.

Dat is belangrijk, omdat dit het verschil markeert tussen een los benchmarkidee en een reproduceerbare kernarchitectuur.

### 2. Er is een bruikbare regressielaag rond scenario-gedreven detectie

De repo heeft een kleine maar nette regressielaag:

- Gap-Test Suite;
- false-positive suite;
- benefit-suite;
- blind benchmark smoke;
- retrieval- en SSOT-smokes.

Deze laag is goed genoeg om regressies snel zichtbaar te maken en om de kernlogica van SSL stabiel te houden tijdens refactors.

### 3. Blinde labelscheiding is serieus genomen

De repo doet meer dan alleen scores uitrekenen. Ze bewaakt ook dat private labels niet in de detectielaag terechtkomen. Dat is methodologisch een sterk signaal.

### 4. Reproduceerbare, goedkope CI-runs zijn bewust ontworpen

De fixture-backends en deterministische paden maken de repo snel, goedkoop en redelijk stabiel. Voor engineeringkwaliteit is dat een pluspunt.

## Wat gedeeltelijk staat, maar nog geen hard bewijs is

## Fase 0: detectie

### Wat staat

- een vaste Gap-Test Suite met drie scenario's;
- score 0, 1, 2;
- atomische seedregels;
- samenvattende metrics zoals scenario score en atomische hits.

### Wat nog ontbreekt ten opzichte van de docs

- expliciete precision;
- expliciete recall;
- expliciete F1 of `ΔF1` als primaire metric;
- overtuigend bewijs buiten de kleine vaste suite;
- loskoppeling van domein-priors in de detectielaag.

### Statusoordeel

Goed als kleine benchmark. Nog niet volledig als algemene detectievalidatie.

## Fase 1: multi-turn state

### Wat staat

- benefit-suite voor antwoordverbetering;
- model benefit-suite met fixture en optionele `hf-transformers` route;
- gap coverage en unsupported additions;
- blind review items voor menselijke vergelijking van antwoorden.

### Wat nog ontbreekt ten opzichte van de docs

- de volledige A/B/C-opzet uit het testplan:
  - geen state;
  - ruwe context;
  - SSL-state;
- expliciete metric voor turn-to-detection;
- expliciete metric voor duplicate seeds;
- bewijs dat SSL-state compacter of scherper werkt dan ruwe context.

### Statusoordeel

Veelbelovend, maar nog geen sluitende fase-1-validatie.

## Fase 2: Validation Gate en probes

### Wat staat

- formele Validation Gate;
- falsificatie- en contradiction-mechaniek;
- SSOT-smoke die laat zien dat externe evidence promotie kan ondersteunen;
- false-positive suite;
- retrieval- en modelgerelateerde evaluatiepaden.

### Wat nog ontbreekt ten opzichte van de docs

- een harde vergelijking tussen de huidige Gate en zwakkere promotieregels;
- echte adversarial false-positive evaluatie;
- zelfstandige meting van Socratische probekwaliteit;
- zelfstandige meting van Retrieval Probe-informatiewinst;
- zelfstandige meting van dialectische kwaliteit als falsificatiemechaniek.

### Belangrijke methodologische beperking

De huidige false-positive suite laat promoted false positives feitelijk op nul eindigen zonder de Gate echt zwaar te belasten. Dat maakt de claim over ruisfiltering zwakker dan de documentatie soms suggereert.

### Statusoordeel

Mechaniek aanwezig, maar bewijs nog te vriendelijk en te smal.

## Fase 3: constellations

### Wat staat

- de manager kan constellations vormen uit promoted seeds;
- retrieval- en vectorstore-infrastructuur bestaat;
- SSOT- en retrieval-benchmarks zijn aanwezig.

### Wat nog ontbreekt

- een echte constellation-benchmark;
- vergelijking tussen losse seed-query en cluster-query;
- metric voor clusterlabelkwaliteit;
- meting van voorspelde nieuwe relevante seeds vanuit clusters.

### Statusoordeel

Architectonisch voorbereid. Nog niet experimenteel bewezen.

## Fase 4: modelinterne test

### Wat staat

- conceptuele documentatie;
- theoretische positionering;
- verwijzing naar latere open-source modelanalyse.

### Wat ontbreekt

- activation extraction;
- sparse classifier-evaluatie;
- intervention testing;
- correlatieanalyse tussen externe `weight` en interne signalen.

### Statusoordeel

Nog onderzoekswerk. Niet operationeel aanwezig in de repo.

## Evaluatielagen buiten de fasen

## Regressielaag

Status: Strong

Dit is de sterkste laag van de repo. Als doel is: regressies voorkomen, mechaniek bewaken, CI betrouwbaar houden, dan is de repo al behoorlijk volwassen.

## Kleine benchmarkvalidatie

Status: Usable

Dit is een bruikbare tussenlaag: goed voor vaste cases, te smal voor brede claims.

## Open-world evaluatie

Status: First evidence (kwaliteitswaarschuwing)

De drie detectiepaden zijn aanwezig op main: `open_set_candidate_adapter` v0.1 (regex baseline, default voor backwards compatibility), v0.2 text-grounded baseline, en v0.3 taalmodel-detector via de hf-transformers backend. De v0.3 detector voldoet aan de 4.6 één-zinsclaim wanneer met een echt model gedraaid. Workflow dispatch ondersteunt alle drie via `--detector` en `--model-backend`.

Round-voortgang: round 001 is een gepauzeerde infrastructure baseline. Round 004 (Qwen2.5-3B, v0.3d) is volledig mensgereviewd door twee beoordelaars (acceptance 0.52, claim-vs-gap dominant). Round 005 offset-12 (v0.3e, Qwen2.5-3B, 12 `ag_news_test` Sci/Tech-items) is sinds PR #116 de **eerste geland Laag-C evidence**: 41 unieke seeds, twee reviewers, unaniem, acceptance **0.29**. Lees dat per criterium: relevance 0.98 (de detector blijft on-topic), maar non_triviality en follow_up_utility beide 0.29 — v0.3e heeft de vorm gerepareerd (claim-vs-gap 30 → 0) maar niet de substantie. Dominante afwijsredenen: `style_not_gap` (20), `not_testable` (18, waarvan 9 mechanisch aanwijsbaar als afgekapte zinnen — zie de prescreen-code `truncated`), `too_vague` (10).

Round 005 is inmiddels gesloten op alle drie de armen. De offset-0 batch en de blinde model-vs-baseline control zijn afgerond als **gedelegeerde AI-review** (één reviewer `reviewer_ai_claude`, expliciet door de maintainer gedelegeerd, 98% accept-agreement met de menselijke offset-12 batch; nadrukkelijk gelabeld als AI, niet als mens — zie `benchmarks/open_review/rounds/round_005/ai_review/`). Uitkomsten: offset-0 acceptance **0.185** (relevance 0.91 maar testability 0.30, non_triviality 0.19 — zelfde patroon als de menselijke batch); blinde control model **0.219** vs baseline `adapter_v1` **0.0** (delta +0.219, model accepted-atomiciteit 1.0). De menselijke offset-12 batch blijft de gezaghebbende Laag-C evidence; de AI-armen zijn de secundaire robuustheidscheck en een eerste gelabelde lezing van offset-0.

Round 006 batch 1 (2026-06-10, Phi-3.5-mini-instruct, v0.3e ongewijzigd, zelfde 12 bronitems als round 005 offset-0) bevestigt de model-hefboom in de zuivere zelfde-reviewer-vergelijking (AI vs AI): acceptance 0.185 → **0.50**, non_triviality 0.19 → **0.50**, atomiciteit 1.00, en nul truncaties/duplicaten/stapelingen in de prescreen. Kanttekeningen: de review is gedelegeerde AI (geen mens, geen Laag-C claim), Phi negeert het absentie-scaffold (vorm-afwijking, handmatig geverifieerd geen feit-beweringen; maintainer-GO op de poort), en de resterende fouten zijn vage impactvragen en false gaps op aanwezige cijfers. De raw run-artifacts (60 kandidaten; manager-poort weigerde er 2, prescreen `not_atomic` bevestigt onafhankelijk dezelfde 2) zijn integraal gecommit. De scaffold-kwestie is na round 006 opgelost in **prompt v0.3g**: de lacune-label-zinsnede (de canonieke 4.5-vorm, die de few-shot voorbeelden al toonden) is nu ook de regel; absentiezinnen blijven toegestaan; de prescreen-`claim_vs_gap` detecteert sindsdien echte beweringen (finiet werkwoord in de hoofdzin) in plaats van een verplichte marker — onder dat contract zijn beide Phi-batches claim-vrij en blijft de round-004 claimsignatuur (24) staan. Zie `benchmarks/open_review/rounds/round_006/batch1/`.

Dit is precies waarvoor de lagenscheiding bestaat: de eerste open-set meting is negatief uitgevallen en dat wordt gerapporteerd als meting, niet weggemiddeld. De juiste vervolgstap is de detector verbeteren (sterker model per #81, afkapprobleem oplossen) en opnieuw meten — niet het criterium verzachten.

## Adversarial Gate-evaluatie

Status: First evidence

PR #80 maakt van de adversarial Gate suite een echte discrimination-test in plaats van een refusal-only suite. De fixture bevat nu 10 scenarios met 21 candidates verdeeld over zes categorieën (volledig antwoord, stijl-zonder-gap, verleidelijke irrelevante, mixed positief-en-lure, near-duplicate paraphrase, plausibele wrong-domain) plus positieve controles met en zonder evidence. Drie baselines worden vergeleken: `current_gate`, `trace_only`, `trace_no_contradiction_check`. Resultaat: 21/21 correct outcomes, precision 1.0, recall 1.0 (op cases met evidence), F1 1.0, baseline-only blocked 16 (wat zwakkere baselines wel zouden doorlaten). Een refusal-only Gate zou nu falen met recall 0.

Beperking: 21 candidates blijft klein en de contradiction-check is lexicaal. Bredere adversarial sets en niet-lexicale contradiction-detectie blijven open werk.

## Probe utility

Status: First evidence (behavioral + prompt-quality)

Twee complementaire suites:

- `ssl45_probe_utility_suite` (bestaand): meet prompt-kwaliteit van SSL-guided follow-up, retrieval en dialectiek versus baseline. Antwoordt op de 4.6 vraag "betere vervolgvragen / retrieval / falsificatie".
- `probe_feedback_behavior_suite` (PR #82): meet of de feedback-loop in `SSLManager.apply_probe_feedback` zich gedraagt zoals de 4.6 spec claimt. 10 scenarios over 8 lifecycle-categorieën (strengthen, weaken, clamp upper, clamp lower, demotion PROMOTED -> ACTIVE, status_block voor DORMANT en EXPIRED, neutral no-op, promotion-block dat reward alleen niet promoteert, mixed). Resultaat: 10/10 correct outcomes, alle 8 categorieën pass. Bevat een expliciete regression-guard test die fixture-mutatie detecteert.

Beperking: de behavioral suite test mechanism, niet usefulness in echte workflows. Dat blijft de taak van de open-set rounds met menselijke review.

## Reproduceerbaarheid

Status: Partial

De intentie is sterk en de documentatie benoemt de juiste artefacten. Tegelijk zie ik nog niet een volledige operationele runlog-laag die het hele faseplan afdekt zoals in `07_reproduceerbaarheid.md` wordt gevraagd.

## Praktische betekenis voor repo-beslissingen

De repo moet vanaf hier twee dingen tegelijk doen:

1. de huidige regressielaag behouden, want die is waardevol;
2. de hoofdclaim verplaatsen naar sterkere evaluatielagen.

Dat betekent concreet:

- scenario-suites niet weggooien;
- scenario-suites herlabelen als regressie en kleine benchmarkvalidatie;
- nieuwe evaluatielagen toevoegen voor open-set kwaliteit, adversarial false positives, probe utility en domeintransfer;
- infrastructuur en rapportage consolideren zonder ongelijke bewijssoorten inhoudelijk samen te trekken.

## Wat nu niet meer impliciet mag blijven

Deze uitspraken moeten in de repo expliciet worden gemaakt:

- de standaard CI bewijst vooral de meetketen, niet algemene SSL-prestatie;
- fixture-runs zijn technische controle, geen eindbewijs;
- fase 3 en 4 zijn nog niet experimenteel afgedekt;
- scenario-scores zijn bruikbaar, maar niet voldoende als eindclaim;
- open-set, adversarial en behavioral evaluatie horen niet te verdwijnen in één totaalscore.

## Aanbevolen volgende documenten

Na dit document horen twee andere documenten leidend te worden:

- `docs/research/scenario-independence-roadmap.md`
- `docs/research/evaluation-matrix.md`

Samen vormen ze:

- huidige status;
- gewenst doelbeeld;
- concrete evaluatiestructuur.

## Korte eindkwalificatie

De repo is vandaag:

> een sterke en serieuze SSL-benchmarkharness met goede mechanische discipline, met eerste echte evidence op de adversarial Gate (D) en probe-feedback (E) lagen, en een eerste echt mensgereviewde open-set batch (C) die een eerlijke kwaliteitswaarschuwing oplevert: de detector vindt relevante maar overwegend triviale afwezigheden (acceptance 0.29). De volgende stap op C is detectorverbetering plus herhaalmeting, niet criteriumversoepeling.
