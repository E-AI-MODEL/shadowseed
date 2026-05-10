# Open-set HF review batch

Deze artifactset komt uit een handmatige workflow met Hugging Face intake.

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
