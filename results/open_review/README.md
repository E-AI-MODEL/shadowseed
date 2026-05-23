# Open-set HF review batch

Deze artifactset komt uit een handmatige workflow met Hugging Face intake.

Run-parameters:

- source_id: `ag_news_test`
- limit: `12`
- offset: `0`
- detector: `model`
- model_backend: `hf-transformers`
- model_id: `Qwen/Qwen2.5-1.5B-Instruct`

Inhoud:

- `open_set_seed_output.json`: de seed-output per item
- `open_set_review_packets.json`: review-packets voor menselijke beoordeling
- `open_set_seed_review_summary.json`: geaggregeerde summary (pending tot review klaar)
- `open_set_disagreements.json`: seeds met gemengde reviewverdicts
- `open_set_review_report.md`: leesbaar Markdown-rapport

Interpretatie:

- dit is een aparte evidencelaag (evidence_layer: open_set_seed_quality)
- dit is geen standaard regressierun
- status is `review_in_progress` totdat menselijke reviewers packets hebben ingevuld
- lees deze laag niet als vervanging van de fixture-regressies
- alleen `detector=model` met `model_backend=hf-transformers` voldoet aan de 4.6 een-zinsclaim;
  adapter_v1, adapter_v2 en de fixture model-backend zijn baseline-infrastructuur, geen Laag-C bewijs
