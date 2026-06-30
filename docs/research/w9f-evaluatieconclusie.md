# W9f evaluatieconclusie

> Status: current
> Date: 2026-06-30
> Evidence layer: cross-turn payoff / lifecycle doctrine / blind review
> Current source: ja

## Doel van dit document

Dit document zet de W9f-stand vast na de follow-up baseline, de blind A/B-review en de review-artifacts.

De kern is dat W9f niet als los experiment naast SSL moet worden gelezen. W9f operationaliseert de bestaande SSL-doctrine in een multi-turn setting:

- `trace` bewaart aanwezigheid zonder invloed;
- `weight` bepaalt pas na Gate-promotie invloed;
- TrTL houdt een seed levend wanneer nieuwe context hem herkent;
- TTL laat seeds verdwijnen wanneer herkenning uitblijft;
- de Validation Gate voorkomt dat een losse herkenning meteen antwoordgedrag stuurt.

W9f toont dat deze levenscyclus in een echte sessie antwoordruimte kan openen die de baseline zonder SSL niet als optie had gehad.

## Kernconclusie

W9f wordt geaccepteerd als werkende technische baseline voor cross-turn context-discovery en memory-surfacing.

Dat betekent:

- de pipeline detecteert terugkerende of latente context;
- cluster-recurrence kan parafrastische herhaling samenbrengen zonder de veilige opslag-dedup los te laten;
- representatives, niet hele clusters, horen door de Gate te gaan;
- representatives blijven levend wanneer recurrence via non-representative members binnenkomt;
- surfaced context kan later antwoordruimte openen;
- blind review laat zien dat die extra antwoordruimte in meerdere gevallen als rijker, scherper of bruikbaarder wordt herkend.

Dit is voldoende om W9f als technische baseline te sluiten. Verdere recurrence- of promotion-tuning is niet nodig om opnieuw te bewijzen dat het mechanisme bestaat.

## Wat de blind A/B-review wel meet

De blind A/B-review meet niet simpelweg of GPT-4.1 door SSL algemeen wordt verslagen.

De juiste lezing is:

```text
vraag + sessiehistorie -> SSL seed discovery -> recurrence/surfacing -> GPT-4.1 met extra context -> alternatief antwoord
```

De review beoordeelt dus of de door SSL geopende antwoordruimte bruikbaar is.

Zonder SSL zouden deze specifieke antwoordvarianten niet als testoptie hebben bestaan. Het experiment is daarom geen klassieke model-vs-model benchmark, maar een kwaliteitscontrole op SSL-gegenereerde antwoordruimte.

## Wat de review niet bewijst

De review bewijst niet:

- dat SSL elk antwoord beter maakt;
- dat SSL GPT-4.1 algemeen verslaat;
- dat elke promoted seed waardevol is;
- dat seed-gebruik automatisch veilig is;
- dat de claim al scenario- of domein-onafhankelijk is.

Dat hoeft ook niet de W9f-claim te zijn.

## Wat W9f wel bewijst

W9f ondersteunt de smallere en sterkere claim:

> SSL kan latente sessiecontext gewichtloos vasthouden, later valideren of surfacen, en daardoor bruikbare aanvullende antwoordruimte openen.

Deze claim sluit aan op de 4.6-doctrine: wat een model mist wordt geen direct antwoordgewicht, maar eerst een trace. Pas na herhaalde herkenning en Gate-promotie mag de seed invloed krijgen.

## Review-uitkomst in woorden

De revieweruitkomsten zijn gemengd maar betekenisvol:

- sommige reviewers kiezen vaak voor de SSL-gestuurde variant;
- andere reviewers markeren seed-vernauwing of ruis;
- `CONV_CITY` blijft het sterkste signaal;
- `CONV_STARTUP` toont dat brede sociale seeds het antwoord soms kunnen vernauwen.

Dat patroon is precies informatief op de juiste laag:

- positief voor discovery en surfacing;
- waarschuwend voor automatisch seed-gebruik;
- geen reden om de levenscyclusmechaniek opnieuw open te trekken.

## Besluit

W9f is afgerond als baseline.

Vanaf hier moet de repo niet blijven vragen:

> werkt SSL eigenlijk wel?

maar:

> draagt dezelfde SSL-levenscyclus over naar andere domeinen, taken en modellen, en onder welke gebruiksdiscipline mag een surfaced seed het antwoord sturen?

## Volgende fase

De volgende fase is W10: doctrine-transfer.

Niet groter in dezelfde A/B-opzet, maar transfer van de bestaande levenscyclus:

- trace/weight-scheiding;
- TTL/TrTL;
- Gate-promotie;
- cluster-recurrence;
- cross-turn surfaced seeds;
- payoff of nuttige vervolgactie;
- seed-ruis en seed-vernauwing als expliciete foutklasse.

De hoofdvraag voor W10:

> blijft de cross-turn SSL-doctrine werken buiten de huidige startup/city-scenario's?

Mogelijke transferassen:

1. domeintransfer: onderwijs, onderzoek, beleid, productontwerp;
2. taaktransfer: Q&A, planning, kritiek, samenvatting, besluitondersteuning;
3. modeltransfer: gpt-4.1, kleinere OpenAI-modellen, lokale modellen;
4. reviewtransfer: één reviewprotocol voor wins, ties, ruis en seed-vernauwing.

## Repo-gevolg

De statusdocs moeten W9f niet langer framen als open bewijsronde. De juiste status is:

- W9f: geaccepteerde technische baseline;
- blind A/B: kwaliteitscontrole, geen absolute benchmark;
- volgende stap: transfer en gebruiksdiscipline;
- geen nieuwe W9f-validatie tenzij een regressie of nieuw domeinresultaat dat nodig maakt.
