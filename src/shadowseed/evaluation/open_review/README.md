# Open-review evaluation layer

Deze map markeert de open-set seedkwaliteit-laag.

Doel:

- beoordelen of SSL in onbekende teksten kleine, relevante en toetsbare seeds maakt;
- werken met review packets en menselijke beoordeling;
- acceptance, rejection en reviewer agreement apart zichtbaar maken.

Hoort hierbij, voorlopig nog via `src/shadowseed/benchmark/`:

- `fetch-open-set-hf-batch`
- `run-open-set-seed-review`
- `summarize-open-set-seed-review`

Werkregel:

> Deze laag hoort niet automatisch in standaard CI zolang menselijke review of handmatige intake de kern is.

Geen gedrag wordt door deze map gewijzigd. Ze legt alleen de bedoelde eigenaar van deze evaluatielogica vast.
