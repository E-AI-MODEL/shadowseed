# Round 024 — W10 doctrine-transfer

> **Status: eerste live gpt-4.1 transfer-run geslaagd.** De run levert een blind
> A/B-reviewpack op over drie nieuwe domeinen. Menselijke review is nog nodig
> voordat er een kwaliteitsclaim mag staan.

Spoor 2 na round 022/023. De vraag is niet meer of het W9f cross-turn
*mechanisme* bestaat, en ook niet of de use-time discipline de ruis dempt, maar
of dezelfde levenscyclus overdraagt naar andere domeinen en taken.

## Wat W10 toetst

Niet groter binnen dezelfde startup/city-context, maar breedte: draait de
bestaande doctrine — `trace`/`weight`-scheiding, TTL/TrTL, Validation Gate,
cluster-recurrence, representative-promotie, en de round-023 use-time discipline
(`surface_top_k=2` + potentieel-niet-must) — ook buiten de bekende domeinen?

## De transfer-set

`src/shadowseed/data/ssl_session_transfer_suite.json` — 3 conversaties in nieuwe
domeinen én taaktypes (transfer over twee assen tegelijk):

| Conversatie | Domein | Taak | Terugkerend latent thema |
|---|---|---|---|
| `CONV_EDU` | onderwijs | lesontwerp | verschillen in voorkennis / thuissituatie / kansengelijkheid |
| `CONV_HEALTH` | publieke gezondheid | campagne-advies (non-clinical) | gedrag ≠ alleen kennis / sociaaleconomische gezondheidsverschillen |
| `CONV_POLICY` | beleid | beleidsontwerp | verdelingseffecten/rechtvaardigheid / uitvoeringscapaciteit |

Elke conversatie is theme-returning en eindigt op een "wat gaat vaak mis"-beurt,
zodat een vroeg-gezaaide seed later kan opduiken en pay-off kan tonen. Geen
ground truth, geen totaalscore.

## Eerste live run (canoniek, post-#156)

Run:

```text
run_id: 28519306334
branch: main
commit: 7f541e9d531aec74165a26db1695958c4bdf5d38
experiment: ssl-session
model_id: gpt-4.1
recurrence_mode: cluster
input_path: src/shadowseed/data/ssl_session_transfer_suite.json
max_new_tokens: 1000
artifact: ssl-openai-ssl-session-gpt-4.1 (id 8010902341)
artifact_digest: sha256:ca28e5871aa90faa51cc64cc057f94031c301497e2f0c7567c3d170c061d18a5
```

Dit pack is **canoniek**: gegenereerd op `main` ná de artifact-contract-fix
(#156), dus met de neutrale `ssl_session_blind_ab_*` namen + hashes +
truncation-flags. De exacte per-domein tellingen (`conversation_count`,
`cross_turn_payoff_events`, `items_by_conversation`, SSL A/B-distributie) staan in
`ssl_session_blind_ab_summary.json` in dat artifact.

> Noot: een eerdere run (28469553713, commit 560e5bb, digest 85b0b454…) draaide
> **vóór** #156 en leverde een pack met de oude `w9f_blind_ab_*` namen zonder de
> canonieke hashes; die is vervangen door bovenstaande canonieke run. De
> pre-#156-summary rapporteerde ter referentie 8 cross-turn events
> (CONV_EDU 3 / CONV_HEALTH 3 / CONV_POLICY 2, SSL A/B 4/4).

Kwalitatief (leesindruk, geen verdict): de afkap-confound is weg bij
`max_new_tokens=1000` — het CONV_POLICY-t8 antwoord loopt volledig door tot een
"Samenvatting en aanscherping" en weeft de latente seed (sociale ongelijkheid /
verdelingseffecten) coherent in. Interpretatie: het mechanisme vuurt buiten de
oude domeinen — transfer-signaal, geen bewijs van betere antwoordkwaliteit. Dat
vergt de blinde human-review van dit canonieke pack.

## Artifact-contract

Vanaf de artifact-contract-fix hoort het blind A/B-pack neutrale namen te
gebruiken:

```text
ssl_session_blind_ab_review_items.json
ssl_session_blind_ab_answer_key.json
ssl_session_blind_ab_review_form.md
ssl_session_blind_ab_scoring_template.csv
ssl_session_blind_ab_summary.json
```

De generated `*_answer_key.json` is de enige canonieke key voor unblinding.
Eventuele embedded blind velden in `ssl_session_suite.json` zijn legacy/debug en
mogen niet worden gebruikt voor scoring.

De summary moet minimaal bevatten:

```text
schema_version
source_artifact_sha256
shuffle_seed
review_items_sha256
answer_key_sha256
answer_key_is_canonical
truncation.items_with_likely_truncated_answer
```

## Acceptatiecriteria

W10 slaagt niet pas als SSL elk item wint. Realistisch:

- gesurfacete seeds openen in meerdere domeinen bruikbare antwoordruimte;
- ruis/vernauwing blijft laag, expliciet gemeten per domein;
- geen systematische overpromotie per domein;
- `weight = 0` tot Gate-promotie en TTL/TrTL blijven gehandhaafd;
- reviewers kunnen verrijking onderscheiden van alleen lengte.

Rapporteer per domein en per taak, niet als één totaalscore.

## Eerlijke grens

De live run toont dat W10 technisch werkt: input routing, OpenAI-run,
cluster-recurrence, cross-turn surfacing en A/B-pack-generatie komen door. De
kwaliteitsvraag blijft open totdat minimaal twee onafhankelijke reviewers het
blind reviewpack hebben gescoord.

Bekende confound: sommige antwoorden kunnen alsnog afgekapt zijn. Zulke items
moeten in de reviewlaag worden gemarkeerd en zo nodig uit win-rate blijven.
