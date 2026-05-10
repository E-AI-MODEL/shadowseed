# Behavioral evaluation layer

Deze map markeert de gedragslaag voor probe utility.

Doel:

- meten of promoted seeds betere vervolgstappen opleveren;
- Socratische, retrieval- en dialectische probes apart beoordelen;
- niet alleen seed-detectie meten, maar ook bruikbaarheid na promotie.

Hoort hierbij, voorlopig nog via `src/shadowseed/benchmark/`:

- `run-probe-utility-benchmark`
- later retrieval-probe vergelijkingen

Werkregel:

> Deze laag meet vervolgactie-waarde. Een positieve regressie- of coverage-score is hiervoor niet genoeg.

Geen gedrag wordt door deze map gewijzigd. Ze legt alleen de bedoelde eigenaar van deze evaluatielogica vast.
