# Adversarial evaluation layer

Deze map markeert de adversarial Gate-laag.

Doel:

- testen of de huidige Validation Gate misleidende of irrelevante seeds beter blokkeert dan zwakkere promotieregels;
- vergelijken met baselines zoals `trace_only` en `trace_no_contradiction_check`;
- casebook-output gebruiken om fouten en blokkades inspecteerbaar te maken.

Hoort hierbij, voorlopig nog via `src/shadowseed/benchmark/`:

- `run-adversarial-gate-benchmark`

Werkregel:

> Deze laag mag pas zwaardere claims dragen als baselinevergelijking en casebook elkaar ondersteunen.

Geen gedrag wordt door deze map gewijzigd. Ze legt alleen de bedoelde eigenaar van deze evaluatielogica vast.
