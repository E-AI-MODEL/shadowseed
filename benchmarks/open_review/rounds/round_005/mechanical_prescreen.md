# Mechanische prescreen — round_005 (GEEN menselijke review)

> **Status: deterministisch hulpmiddel, geen evidence.** Deterministische prescreen, GEEN menselijke review. Telt NIET als reviewer_a/reviewer_b en niet als open_set_seed_quality (Laag C) evidence, en geeft GEEN accept/reject-verdict. Bedoeld om aandacht te richten en de v0.3e-prompt te toetsen aan haar eigen regels.

Detector: `model` · backend: `hf-transformers:Qwen/Qwen2.5-3B-Instruct`

## Yield (levert het model kandidaten op?)

- items: **12** · met kandidaten: **12** · leeg: **0** (empty-rate **0.0**)
- gemiddeld kandidaten per item: **4.917**

## Kwaliteit van geleverde kandidaten (59 kandidaat-lacunes)

- clean (geen mechanische vlag): **40**
- geflagd: **19**
- clean-rate: **0.678**

## Mechanische faalcodes

- `not_atomic`: 19
- `parse_leak`: 5
- `citation_fragment`: 0
- `claim_vs_gap`: 0
- `entity_bleed`: 0
- `fewshot_leak`: 0
- `language_leak`: 0

## Niet mechanisch te checken (vraagt een lezer)

- `false_gap`, `mistranslation`, `grammar`

