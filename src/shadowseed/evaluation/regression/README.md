# Regression evaluation layer

Deze map markeert de bestaande regressie- en smoke-laag.

Doel:

- bewaken dat de SSL-kernmechaniek blijft werken;
- vaste scenario-suites als regressie en kleine benchmark blijven draaien;
- publiceerbare standaard-artifacts blijven leveren zonder de hoofdclaim te vergroten.

Hoort hierbij, voorlopig nog via `src/shadowseed/benchmark/`:

- `run-gap-suite`
- `run-false-positive-suite`
- `run-benefit-suite`
- `run-model-benefit-suite` met fixture-backend
- `run-blind-benchmark`
- `run-absencebench-smoke`

Werkregel:

> Deze laag mag in standaard CI draaien. Output uit deze laag is mechanische stabiliteit of kleine benchmarkvalidatie, geen brede algemene SSL-validatie.

Geen gedrag wordt door deze map gewijzigd. Ze is de eerste stap naar de laagindeling uit de 4.6-koers.
