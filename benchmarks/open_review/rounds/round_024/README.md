# Round 024 — W10 doctrine-transfer (opzet)

> **Status: transfer-set + wiring geland (deterministisch); de live gpt-4.1
> transfer-run + blinde review is de pending stap.** Spoor 2 na round 022/023.
> De vraag is niet meer of het W9f cross-turn *mechanisme* bestaat (round 020),
> en ook niet of de use-time discipline de ruis dempt (round 023, grotendeels) —
> maar of **dezelfde levenscyclus overdraagt naar andere domeinen en taken**.

## Wat W10 toetst

Niet groter binnen dezelfde startup/city-context, maar **breedte**: draait de
bestaande, ongewijzigde doctrine — `trace`/`weight`-scheiding, TTL/TrTL, Validation
Gate, cluster-recurrence, representative-promotie, en de round-023 use-time
discipline (`surface_top_k=2` + potentieel-niet-must) — ook buiten de bekende
domeinen?

## De transfer-set

`src/shadowseed/data/ssl_session_transfer_suite.json` — 3 conversaties in nieuwe
domeinen én taaktypes (transfer over twee assen tegelijk):

| Conversatie | Domein | Taak | Terugkerend latent thema (kans op cross-turn) |
|---|---|---|---|
| `CONV_EDU` | onderwijs | lesontwerp | verschillen in voorkennis / thuissituatie / kansengelijkheid |
| `CONV_HEALTH` | publieke gezondheid | campagne-advies (non-clinical) | gedrag ≠ alleen kennis / sociaaleconomische gezondheidsverschillen |
| `CONV_POLICY` | beleid | beleidsontwerp | verdelingseffecten/rechtvaardigheid / uitvoeringscapaciteit |

Elke conversatie is theme-RETURNING (7 beurten) en eindigt op een "wat gaat vaak
mis"-beurt, zodat een vroeg-gezaaide seed later kan opduiken en pay-off kan tonen —
dezelfde structuur die in CONV_CITY werkte. Geen ground truth, geen totaalscore.

## Hoe te draaien

Deterministisch (vorm-check, geen model):

```bash
shadowseed run-ssl-session --input src/shadowseed/data/ssl_session_transfer_suite.json \
  --backend fixture --output results/ssl_session_transfer.json
```

Live transfer-run (gpt-4.1, veilige drempels, round-023 defaults) — via
`Research · SSL Benefit (OpenAI)`, nieuwe input `input_path`:

```text
experiment: ssl-session
model_id: gpt-4.1
recurrence_mode: cluster
input_path: src/shadowseed/data/ssl_session_transfer_suite.json
max_new_tokens: 1000
```

> Zet `max_new_tokens` ruim (~900–1200, hier 1000), niet de default 400 — anders
> rust de win/ruis-review op afgekapte zinnen (zie de afkap-confound onderaan).
> De blind A/B-pack wordt uit déze run gegenereerd, dus de gedocumenteerde run
> moet meteen de evalueerbare zijn.

De workflow genereert daarna automatisch het blind A/B-pack (zelfde tooling als
round 022/023).

## Acceptatiecriteria (uit `scenario-independence-roadmap.md` §5)

W10 slaagt **niet** pas als SSL elk item wint. Realistisch:

- gesurfacete seeds openen in **meerdere domeinen** bruikbare antwoordruimte;
- ruis/vernauwing blijft laag (zoals round 023), expliciet gemeten per domein;
- geen systematische overpromotie per domein;
- `weight = 0` tot Gate-promotie en TTL/TrTL blijven gehandhaafd;
- reviewers kunnen verrijking onderscheiden van alleen lengte.

Rapporteer **per domein en per taak**, niet als één totaalscore.

## Eerlijke grens

Dit round levert nu alleen de **set + wiring + vorm-check** (smoke-test groen op de
fixture-backend). Of de doctrine echt overdraagt is een modelrun + blinde
reviewvraag — net als round 023. Pas met die uitkomst mag over transfer iets
beweerd worden. Bekend confound om mee te nemen: de afkap (`max_new_tokens`) — zet
die voor de transfer-run ruim (~900–1200) zodat win-rate niet op afgekapte zinnen
rust.
