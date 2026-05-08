# CLI Command Map

Deze pagina legt vast hoe de `shadowseed` CLI gelezen moet worden.

Doel:

- duidelijk maken welke commands tot de standaardroute horen;
- zichtbaar maken welke commands handmatig of experimenteel zijn;
- voorkomen dat nieuwe Actions-routes een onduidelijke commandostructuur verharden;
- een tussenstap bieden vóór een eventuele latere subcommand-herbouw.

## Hoofdregel

Niet elke command heeft dezelfde status.

De CLI heeft daarom vier commandolagen:

1. standaard regressie- en smoke-routes
2. handmatige research-routes
3. retrieval- en backend-routes
4. AbsenceBench-utility routes

## 1. Standaard regressie- en smoke-routes

Deze commands horen direct bij de huidige standaard meetketen of bij de standaard CI-ruggengraat.

| Command | Rol | Verwachte status |
|---|---|---|
| `run-gap-suite` | regressie voor bekende SSL-gaps | standaard |
| `run-false-positive-suite` | negatieve controle en Gate-ruisfiltering | standaard |
| `run-benefit-suite` | kleine benchmark voor antwoordwinst | standaard |
| `run-model-benefit-suite` | fixture-smoke en optionele echte modelrun | standaard voor fixture, handmatig voor echte backend |
| `run-blind-benchmark` | labelscheiding en methodologische smoke | standaard |
| `run-absencebench-smoke` | technische smoke voor lokale AbsenceBench-route | standaard |
| `analyze-results` | rapportage uit resultaatbestanden | standaard |

## 2. Handmatige research-routes

Deze commands verdiepen het bewijs, maar zijn nog niet dezelfde soort stabiele regressielaag als de standaardroutes.

| Command | Rol | Verwachte status |
|---|---|---|
| `run-open-set-seed-review` | open-set scaffold met review-packets | handmatig |
| `summarize-open-set-seed-review` | reviewer-uitkomsten aggregeren tot acceptance, agreement en disagreement-artifacts | handmatig |
| `run-adversarial-gate-benchmark` | vergelijk current Gate met zwakkere promotiebaselines | handmatig |
| `run-probe-utility-benchmark` | gedragsmatige scaffold voor follow-up, retrieval en dialectiek | handmatig |

Hoofdregel:

> deze commands mogen pas standaard-CI worden als hun output stabieler, eerlijker en inhoudelijk volwassener is dan nu.

## 3. Retrieval- en backend-routes

Deze commands zijn nuttig voor diagnose, backend-checks en verdiepende runs, maar horen niet automatisch bij de dagelijkse standaardroute.

| Command | Rol | Verwachte status |
|---|---|---|
| `run-retrieval-benchmark` | retrievalkwaliteit van de vectorstore | handmatig |
| `run-retrieval-model-benchmark` | effect van opgehaalde context op modelantwoord | handmatig |
| `run-ssot-smoke` | SSOT en falsificatiebasis smoke-test | handmatig |
| `run-vectorstore-smoke` | vectorstore backend smoke-test | handmatig |

## 4. AbsenceBench-utility routes

Deze commands horen bij het voorbereiden en draaien van de aparte AbsenceBench-lijn.

| Canonieke command | Legacy alias | Rol |
|---|---|---|
| `prepare-absencebench-bundle` | `prepare-absencebench` | bouw een preparation bundle |
| `fetch-absencebench-sample` | `fetch-absencebench` | haal een sample op |
| `run-absencebench-local` | `run-local-absencebench` | draai een lokale AbsenceBench-run |
| `run-absencebench-smoke` | `run-nlp-smoke` | technische smoke voor de lokale route |

## Waarom deze indeling belangrijk is

Zonder deze indeling ziet de CLI eruit alsof alle commands dezelfde bewijslast en dezelfde operationele status hebben.

Dat is niet waar.

De repo is juist sterker als zij expliciet laat zien:

- wat standaard regressie is;
- wat echte research-verdieping is;
- wat backenddiagnose is;
- wat utility- of voorbereidingswerk is.

## Beslisregel voor nieuwe Actions-routes

Voeg een command pas toe aan de standaardworkflow als hij aan alle vier voldoet:

1. de output is stabiel genoeg voor frequente runs;
2. de command vraagt geen menselijke review als kernstap;
3. de command levert een duidelijke regressie- of smoke-signalering op;
4. de command heeft een helder artifact dat niet makkelijk verkeerd gelezen wordt als eindbewijs.

Als één van die vier nog niet geldt, hoort de route voorlopig handmatig te blijven.

## Wanneer een zwaardere CLI-herbouw logisch wordt

Een grotere herbouw, bijvoorbeeld naar subcommands zoals:

```text
shadowseed standard ...
shadowseed research ...
shadowseed retrieval ...
shadowseed absencebench ...
```

wordt pas logisch als:

- de huidige naamlaag stabiel genoeg is;
- scripts en docs op de canonieke namen over zijn;
- de handmatige research-routes inhoudelijk verder uitgekristalliseerd zijn.

Tot die tijd is de huidige aanpak bewust conservatief:

- betere namen;
- duidelijke tiers;
- legacy aliases behouden;
- geen harde breuk.

## Korte beleidszin

> eerst command-tiers expliciet maken, daarna pas nieuwe standaardworkflows of een grotere CLI-herbouw.
