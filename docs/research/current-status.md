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
- open-set/domeintransfer replicatie (round 007, v0.3g, verse items): de model-hefboom houdt out-of-sample stand (nieuws 0.333, wetenschap 0.268 — beide ruim boven Qwen 0.185), maar de round-006 niveaus (0.50/0.458) waren optimistisch en de nieuws-vs-wetenschap-framing onjuist: de driver is **tekstdichtheid**, niet domein (feit-complete wire-items en resultaat-dichte abstracts leveren weinig echte gaps). v0.3g lost de vorm overal op (prescreen clean-rate 0.90/0.95, claim_vs_gap 0). Zie `benchmarks/open_review/rounds/round_007/`
- domeintransfer: **eerste signaal** (2026-06-11, round 006 batch 2): zelfde Phi-3.5-mini + v0.3e op 12 arXiv-abstracts levert AI-gereviewde acceptance **0.458** vs 0.50 op nieuws (zelfde reviewer/model/prompt) — kwaliteit transfereert; het faalprofiel verschuift ("of"-stapeling, LaTeX-truncatie). Eén exploratieve batch, AI-gereviewd: signaal, geen validatie
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
