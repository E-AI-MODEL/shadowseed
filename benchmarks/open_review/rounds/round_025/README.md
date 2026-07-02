# Round 025 — W10 transfer, afkap-vrije her-draai (opzet)

> **Status: prompt-hygiëne geland; live run + verse blinde review is de pending
> stap.** Round 024 leverde een onbeslist transfer-verdict op omdat afkap 6/9
> review-items ongeldig maakte (bij `max_new_tokens=1000`); alleen EDU was
> meetbaar (baseline 2 / SSL 1, n=3). Deze ronde herhaalt de transfer-meting
> zonder dat de afkap de meting domineert.

## Wat er verandert t.o.v. round 024

1. **Compactheidsinstructie in de antwoordprompt** (`build_chat_prompt`), in
   **beide armen** zodat het de A/B-vergelijking niet kan biassen: max ~450
   woorden, expliciet afronden met een slotalinea, "midden in een zin stoppen is
   fout". Dit pakt de oorzaak aan (antwoorden gedimensioneerd op het budget)
   i.p.v. alleen het budget te verhogen.
2. **Meta-lek verboden in de weave-prompt**: het antwoord mag nergens
   rechtvaardigen waarom een invalshoek wordt betrokken of weggelaten (round-024
   lek: *"(Deze invalshoek versterkt het antwoord, omdat …)"* kon een item
   de-blinderen).
3. **Ruimer tokenbudget als vangnet**: run met `max_new_tokens: 1600` — de
   compacte instructie hoort het werk te doen; het budget vangt uitschieters.
4. **Quarantaine-regel actief** (uit round 024): key-bewuste diagnostiek wordt
   pas gepubliceerd ná afronding van de scoring, of in een apart
   niet-reviewer-artifact.

## Run-recept

```text
workflow: Research · SSL Benefit (OpenAI)
experiment: ssl-session
model_id: gpt-4.1
recurrence_mode: cluster
input_path: src/shadowseed/data/ssl_session_transfer_suite.json
max_new_tokens: 1600
```

Zelfde transfer-set, zelfde veilige drempels, zelfde use-time discipline
(`surface_top_k=2`, potentieel-niet-must). Het blind A/B-pack
(`ssl_session_blind_ab_*`) wordt automatisch gegenereerd; controleer in de
summary dat `truncation.items_with_likely_truncated_answer` (vrijwel) leeg is
vóór de review start — anders eerst opnieuw draaien.

## Klaar wanneer

- een run waarvan ≤1 review-item afkap-gemarkeerd is;
- verse blinde review (≥2 reviewers, per domein, met seed-effect en
  ruis/vernauwing-labels), unblinding via de canonieke answer key;
- per-domein rapportage (EDU / HEALTH / POLICY), geen totaalscore.

Pas dán is een per-domein transfer-uitspraak mogelijk. Round-024-uitkomst blijft
staan als context: mechanisme vuurt in alle drie domeinen, weave coherent en
ruisvrij; kwaliteitsverdict nog open.
