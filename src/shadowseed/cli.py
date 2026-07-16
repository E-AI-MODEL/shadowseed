"""Command line interface for Shadow Seed Learning."""

from __future__ import annotations

import argparse

from shadowseed.benchmark.open_set_candidate_adapter import SUPPORTED_DETECTORS
from shadowseed.benchmark.open_set_model_detector import SUPPORTED_MODEL_BACKENDS
from shadowseed.cli_dispatch import execute_command


VECTOR_BACKENDS = ["memory", "faiss", "chroma"]
MODEL_BACKENDS = ["fixture", "hf-transformers", "ollama", "openai"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shadowseed",
        description=(
            "CLI voor Shadow Seed Learning 4.6.\n"
            "Standaard regressie- en smoke-routes leven naast handmatige research-routes.\n"
            "Legacy command aliases blijven voorlopig ondersteund voor compatibiliteit."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser(
        "prepare-absencebench-bundle",
        aliases=["prepare-absencebench"],
        help="[absencebench] bouw een preparation bundle",
    )
    prepare.set_defaults(command="prepare-absencebench-bundle")
    prepare.add_argument(
        "--output",
        default="absencebench/preparation_result.json",
        help="Relatief pad binnen benchmarks/results.",
    )

    local = subparsers.add_parser(
        "run-absencebench-local",
        aliases=["run-local-absencebench"],
        help="[absencebench] draai een lokale AbsenceBench-run",
    )
    local.set_defaults(command="run-absencebench-local")
    local.add_argument("--input", required=True, help="JSON-bestand met lokale scenario's.")
    local.add_argument(
        "--output",
        default="absencebench/local_result.json",
        help="Relatief pad binnen benchmarks/results.",
    )

    hf = subparsers.add_parser(
        "fetch-absencebench-sample",
        aliases=["fetch-absencebench"],
        help="[absencebench] haal een sample op voor lokale inspectie",
    )
    hf.set_defaults(command="fetch-absencebench-sample")
    hf.add_argument("--output", default="data/absencebench_sample.json")
    hf.add_argument("--limit", type=int, default=10)

    ssl = subparsers.add_parser(
        "run-gap-suite",
        help="[standard] regressiesuite voor bekende SSL-gaps",
    )
    ssl.add_argument("--input", default="src/shadowseed/data/gap_test_suite_4_5.json")
    ssl.add_argument("--output", default="results/ssl45_gap_suite.json")
    ssl.add_argument("--turns", type=int, default=3)

    fp = subparsers.add_parser(
        "run-false-positive-suite",
        help="[standard] negatieve controle en Gate-ruisfiltering",
    )
    fp.add_argument(
        "--input",
        default="src/shadowseed/data/gap_test_suite_false_positive_4_5.json",
    )
    fp.add_argument("--output", default="results/ssl45_false_positive_suite.json")

    benefit = subparsers.add_parser(
        "run-benefit-suite",
        help="[standard] kleine benchmark voor antwoordwinst",
    )
    benefit.add_argument(
        "--input",
        default="src/shadowseed/data/ssl45_benefit_suite.json",
    )
    benefit.add_argument("--output", default="results/ssl45_benefit_suite.json")
    benefit.add_argument("--turns", type=int, default=3)

    model_benefit = subparsers.add_parser(
        "run-model-benefit-suite",
        help="[standard/manual] fixture-smoke of optionele echte modelrun",
    )
    model_benefit.add_argument(
        "--input",
        default="src/shadowseed/data/ssl45_model_benefit_suite.json",
    )
    model_benefit.add_argument("--output", default="results/ssl45_model_benefit_suite.json")
    model_benefit.add_argument("--turns", type=int, default=3)
    model_benefit.add_argument(
        "--backend",
        choices=MODEL_BACKENDS,
        default="fixture",
        help=(
            "Model-backend. fixture = deterministische CI-smoke. "
            "hf-transformers = echt lokaal model via de transformers stack "
            "(vereist --model-id en de models extra). ollama = echt model via "
            "een lokale Ollama-server (vereist --model-id en een draaiende "
            "`ollama serve` met het model gepulld). openai = gehost model via "
            "de OpenAI API (vereist --model-id, de openai extra en "
            "OPENAI_API_KEY in de omgeving)."
        ),
    )
    model_benefit.add_argument("--model-id", default=None)
    model_benefit.add_argument("--max-new-tokens", type=int, default=220)
    model_benefit.add_argument(
        "--semantic-embedding-backend",
        choices=["none", "lexical", "openai"],
        default="none",
        help=(
            "Optionele semantische coverage-metric naast de lexicale. none = uit "
            "(CI-default). lexical = deterministische hash. openai = echte "
            "embeddings (vereist de openai extra en OPENAI_API_KEY) — meet of de "
            "gap inhoudelijk geadresseerd is i.p.v. letterlijk herhaald."
        ),
    )
    model_benefit.add_argument("--embedding-model", default=None)
    model_benefit.add_argument("--semantic-threshold", type=float, default=0.55)

    blind = subparsers.add_parser(
        "run-blind-benchmark",
        help="[standard] methodologische smoke voor labelscheiding",
    )
    blind.add_argument(
        "--input",
        default="src/shadowseed/data/blind_suite_public.json",
        help="Publieke scenario's zonder evaluator-labels.",
    )
    blind.add_argument(
        "--labels",
        required=True,
        help="Privébestand met expected_gaps en must_not_add labels.",
    )
    blind.add_argument("--output", default="results/blind_benchmark.json")
    blind.add_argument("--turns", type=int, default=3)
    blind.add_argument("--max-seeds", type=int, default=5)

    open_set_hf = subparsers.add_parser(
        "fetch-open-set-hf-batch",
        help="[manual] haal een kleine HF-batch op voor open-set seed review",
    )
    open_set_hf.add_argument(
        "--source-id",
        default="ag_news_test",
        help="Bron-id uit de open-set HF source registry.",
    )
    open_set_hf.add_argument(
        "--registry",
        default="src/shadowseed/data/open_set_hf_sources.json",
        help="JSON-bestand met brondefinities voor HF open-set intake.",
    )
    open_set_hf.add_argument(
        "--output",
        default="benchmarks/open_review/input/hf_ag_news_test_batch.json",
        help="Waar de genormaliseerde open-set batch wordt opgeslagen.",
    )
    open_set_hf.add_argument("--limit", type=int, default=12)
    open_set_hf.add_argument("--offset", type=int, default=0)

    open_set = subparsers.add_parser(
        "run-open-set-seed-review",
        help="[manual] open-set scaffold met review-packets",
    )
    open_set.add_argument("--input", default="src/shadowseed/data/open_set_seed_review_sample.json")
    open_set.add_argument("--output", default="results/open_review/open_set_seed_output.json")
    open_set.add_argument(
        "--review-packets",
        default="results/open_review/open_set_review_packets.json",
        help="Waar de review-packets voor menselijke beoordeling worden opgeslagen.",
    )
    open_set.add_argument(
        "--reviewer-id",
        dest="reviewer_ids",
        action="append",
        default=None,
        help=(
            "Reviewer-id waarvoor een pending packetrij wordt gemaakt. "
            "Gebruik deze optie meerdere keren. Default: reviewer_a en reviewer_b."
        ),
    )
    open_set.add_argument(
        "--detector",
        choices=SUPPORTED_DETECTORS,
        default="adapter_v1",
        help=(
            "Welke candidate generator wordt gebruikt wanneer een item geen "
            "expliciete candidate_seeds heeft. adapter_v1 = regex-template "
            "baseline (default, backwards compatible). adapter_v2 = "
            "text-grounded template baseline. model = v0.3 taalmodel-"
            "detector (voldoet aan de 4.6 een-zinsclaim); kies dan ook "
            "--model-backend."
        ),
    )
    open_set.add_argument(
        "--model-backend",
        choices=SUPPORTED_MODEL_BACKENDS,
        default="fixture",
        help=(
            "Welke model-backend de v0.3 detector gebruikt. Alleen relevant "
            "als --detector model. fixture = deterministisch CI-backend "
            "(seeds krijgen een [FIXTURE] prefix). hf-transformers = echt "
            "lokaal taalmodel via de transformers stack; vereist --model-id "
            "en de optionele models extra. ollama = echt model via een lokale "
            "Ollama-server (HTTP, geen Python model-deps); vereist --model-id "
            "en een draaiende `ollama serve` met het model gepulld."
        ),
    )
    open_set.add_argument(
        "--model-id",
        default=None,
        help=(
            "Model-id voor --model-backend. Voor hf-transformers een Hugging "
            "Face id (bijv. een klein instruct-model dat lokaal past); voor "
            "ollama de Ollama-modelnaam (bijv. qwen2.5:0.5b of tinyllama)."
        ),
    )
    open_set.add_argument(
        "--max-new-tokens",
        type=int,
        default=400,
        help="Maximale tokens die de v0.3 model-backend per item genereert.",
    )
    open_set.add_argument(
        "--prompt-variant",
        choices=["absence", "generative"],
        default="absence",
        help=(
            "Detector-prompt. absence = 'wat ONTBREEKT' (omissie, default). "
            "generative = 'wat had hier KUNNEN staan' (de niet-genomen "
            "invalshoek/kader; gat 1 uit vision-generative-seeds.md). Alleen "
            "relevant als --detector model."
        ),
    )

    open_set_summary = subparsers.add_parser(
        "summarize-open-set-seed-review",
        help="[manual/reporting] vat ingevulde open-set review-packets samen",
    )
    open_set_summary.add_argument(
        "--input",
        default="results/open_review/open_set_review_packets.json",
        help="JSON-bestand met ingevulde review-packets.",
    )
    open_set_summary.add_argument(
        "--output",
        default="results/open_set_seed_review_summary.json",
        help="Waar de geaggregeerde review-samenvatting wordt opgeslagen.",
    )
    open_set_summary.add_argument(
        "--disagreements-output",
        default="results/open_review/open_set_disagreements.json",
        help="Waar seed-level disagreements voor handmatige follow-up worden opgeslagen.",
    )
    open_set_summary.add_argument(
        "--report-output",
        default="results/open_review/open_set_review_report.md",
        help="Waar de leesbare open-set samenvatting wordt opgeslagen.",
    )

    list_models = subparsers.add_parser(
        "list-open-set-models",
        help="[info] toon de gecureerde lijst HF-modellen voor de model-detector / SLM-routes",
    )
    list_models.add_argument(
        "--registry",
        default="src/shadowseed/data/open_set_models.json",
        help="JSON-registry met gecureerde modellen.",
    )
    list_models.add_argument(
        "--output",
        default=None,
        help="Optioneel pad om de tabel naar weg te schrijven; standaard naar stdout.",
    )

    adversarial = subparsers.add_parser(
        "run-adversarial-gate-benchmark",
        help="[manual] vergelijk current Gate met zwakkere promotieregels",
    )
    adversarial.add_argument(
        "--input",
        default="src/shadowseed/data/adversarial_gate_benchmark.json",
    )
    adversarial.add_argument(
        "--output",
        default="results/adversarial_gate_benchmark.json",
    )
    adversarial.add_argument(
        "--casebook",
        default="results/adversarial_gate_casebook.md",
        help="Waar de leesbare casebook met baseline-vs-gate blokkades wordt opgeslagen.",
    )

    probe = subparsers.add_parser(
        "run-probe-utility-benchmark",
        help="[manual] gedragsmatige scaffold voor follow-up, retrieval en dialectiek",
    )
    probe.add_argument("--input", default="src/shadowseed/data/ssl45_probe_utility_suite.json")
    probe.add_argument("--output", default="results/ssl45_probe_utility_suite.json")

    probe_behavior = subparsers.add_parser(
        "run-probe-feedback-behavior-suite",
        help="[manual] Laag-E lifecycle-test: reward, penalty, clamping, demotie, status-block",
    )
    probe_behavior.add_argument(
        "--input",
        default="src/shadowseed/data/probe_feedback_behavior_suite.json",
    )
    probe_behavior.add_argument(
        "--output",
        default="results/probe_feedback_behavior_suite.json",
    )
    probe_behavior.add_argument(
        "--casebook",
        default="results/probe_feedback_behavior_casebook.md",
        help="Waar de leesbare casebook met per-scenario verdicten wordt opgeslagen.",
    )

    vectorstore = subparsers.add_parser(
        "run-vectorstore-smoke",
        help="[manual] vectorstore backend smoke-test",
    )
    vectorstore.add_argument("--output", default="results/vectorstore_smoke.json")
    vectorstore.add_argument("--backend", choices=VECTOR_BACKENDS, default="memory")

    ssot = subparsers.add_parser(
        "run-ssot-smoke",
        help="[manual] SSOT en falsificatiebasis smoke-test",
    )
    ssot.add_argument("--output", default="results/ssot_smoke.json")
    ssot.add_argument("--backend", choices=VECTOR_BACKENDS, default="memory")

    retrieval = subparsers.add_parser(
        "run-retrieval-benchmark",
        help="[manual] retrievalkwaliteit van de gekozen vectorstore",
    )
    retrieval.add_argument("--input", default="src/shadowseed/data/retrieval_benchmark.json")
    retrieval.add_argument("--output", default="results/retrieval_benchmark.json")
    retrieval.add_argument("--backend", choices=VECTOR_BACKENDS, default="memory")
    retrieval.add_argument("--k", type=int, default=3)

    retrieval_model = subparsers.add_parser(
        "run-retrieval-model-benchmark",
        help="[manual] effect van opgehaalde context op modelantwoord",
    )
    retrieval_model.add_argument("--input", default="src/shadowseed/data/retrieval_output_benchmark.json")
    retrieval_model.add_argument("--retrieval-input", default="src/shadowseed/data/retrieval_benchmark.json")
    retrieval_model.add_argument("--output", default="results/retrieval_model_benchmark.json")
    retrieval_model.add_argument("--vector-backend", choices=VECTOR_BACKENDS, default="memory")
    retrieval_model.add_argument("--model-backend", choices=MODEL_BACKENDS, default="fixture")
    retrieval_model.add_argument("--model-id", default=None)
    retrieval_model.add_argument("--max-new-tokens", type=int, default=220)
    retrieval_model.add_argument("--top-k", type=int, default=3)

    ssl_vs_rag = subparsers.add_parser(
        "run-ssl-vs-rag",
        help="[manual/research] gap 3: SSL Retrieval Probe (query=gap) vs gewone RAG (query=vraag)",
    )
    ssl_vs_rag.add_argument("--data", default="src/shadowseed/data/ssl_vs_rag_benchmark.json")
    ssl_vs_rag.add_argument("--output", default="results/ssl_vs_rag_benchmark.json")
    # Only the backends make_output_model actually supports — advertising
    # ollama here would crash at runtime (Codex #139). openai is supported.
    ssl_vs_rag.add_argument(
        "--model-backend", choices=["fixture", "hf-transformers", "openai"], default="fixture"
    )
    ssl_vs_rag.add_argument("--model-id", default=None)
    ssl_vs_rag.add_argument("--max-new-tokens", type=int, default=220)
    ssl_vs_rag.add_argument("--top-k", type=int, default=3)
    ssl_vs_rag.add_argument(
        "--use-centroid",
        action="store_true",
        help="Eén centroid-query voor de seed-constellation i.p.v. per-seed union.",
    )
    ssl_vs_rag.add_argument(
        "--embedding-backend",
        choices=["lexical", "openai"],
        default="lexical",
        help=(
            "Retrieval-embedder. lexical = deterministische 128d-hash (CI, "
            "speelgoed; mechanisme niet productie-RAG). openai = echte "
            "embeddings (vereist de openai extra en OPENAI_API_KEY) — haalt de "
            "toy-retriever-confound uit de gap-3 vergelijking."
        ),
    )
    ssl_vs_rag.add_argument(
        "--embedding-model",
        default=None,
        help="Embedding-model-id voor --embedding-backend openai (default text-embedding-3-small).",
    )

    adv_payoff = subparsers.add_parser(
        "run-adversarial-payoff",
        help="[manual/research] discriminatietest: forceer een slechte seed in de revisie",
    )
    adv_payoff.add_argument("--input", default="src/shadowseed/data/adversarial_payoff_suite.json")
    adv_payoff.add_argument("--output", default="results/adversarial_payoff_suite.json")
    adv_payoff.add_argument("--backend", choices=MODEL_BACKENDS, default="fixture")
    adv_payoff.add_argument("--model-id", default=None)
    adv_payoff.add_argument("--max-new-tokens", type=int, default=400)

    wild_payoff = subparsers.add_parser(
        "run-wild-payoff",
        help="[manual/research] P0/W1: echte open-set seeds door de payoff-pijplijn",
    )
    wild_payoff.add_argument("--input", default="src/shadowseed/data/wild_payoff_suite.json")
    wild_payoff.add_argument("--output", default="results/wild_payoff_suite.json")
    wild_payoff.add_argument("--backend", choices=MODEL_BACKENDS, default="fixture")
    wild_payoff.add_argument("--model-id", default=None)
    wild_payoff.add_argument("--max-new-tokens", type=int, default=400)
    wild_payoff.add_argument(
        "--semantic-embedding-backend", choices=["none", "lexical", "openai"], default="none"
    )
    wild_payoff.add_argument("--embedding-model", default=None)

    gen_payoff = subparsers.add_parser(
        "run-generative-payoff",
        help="[manual/research] P0/W5: generatieve 'kunnen staan'-frames door de payoff-pijplijn",
    )
    gen_payoff.add_argument("--input", default="src/shadowseed/data/generative_payoff_suite.json")
    gen_payoff.add_argument("--output", default="results/generative_payoff_suite.json")
    gen_payoff.add_argument("--backend", choices=MODEL_BACKENDS, default="fixture")
    gen_payoff.add_argument("--model-id", default=None)
    gen_payoff.add_argument("--max-new-tokens", type=int, default=400)
    gen_payoff.add_argument(
        "--semantic-embedding-backend", choices=["none", "lexical", "openai"], default="none"
    )
    gen_payoff.add_argument("--embedding-model", default=None)

    dialectic = subparsers.add_parser(
        "run-dialectic-falsification",
        help="[manual/research] Laag G instap: probeer promoted seeds weg te argumenteren tegen de bron "
        "(WEERLEGD -> Gate-contradictie; HOUDT_STAND -> bounded feedback, promoveert nooit)",
    )
    dialectic.add_argument("--input", default="src/shadowseed/data/dialectic_falsification_fixture.json")
    dialectic.add_argument("--output", default="results/dialectic_falsification.json")
    dialectic.add_argument("--backend", choices=MODEL_BACKENDS, default="fixture")
    dialectic.add_argument("--model-id", default=None)
    dialectic.add_argument("--max-new-tokens", type=int, default=200)

    act_probe = subparsers.add_parser(
        "run-activation-probe",
        help="[manual/research] Laag G spoor 2: MLP-activatiescheiding tussen dialectische "
        "verdict-klassen (signaal != verdict; raakt geen seed-state)",
    )
    act_probe.add_argument("--input", default="src/shadowseed/data/dialectic_falsification_fixture.json")
    act_probe.add_argument("--output", default="results/activation_probe.json")
    act_probe.add_argument("--backend", choices=["fake", "hf"], default="fake",
        help="'fake' bewijst alleen de harnas-mechaniek; 'hf' (opt-in, models-extra) sondeert een echt model.")
    act_probe.add_argument("--model-id", default=None)
    act_probe.add_argument("--pooling", choices=["stelling", "full"], default="stelling",
        help="'stelling' poolt alleen de stelling-tokens (round-026-les); 'full' de hele prompt.")
    act_probe.add_argument("--verdicts", default=None,
        help="Pad naar een dialectic_falsification-artifact: gebruik díe verdict-labels "
        "(bv. gpt-4.1 oordeelt) i.p.v. de fixture-mechaniek. De echte Laag G-vraag.")
    act_probe.add_argument("--read-location", choices=["mlp_out", "neuron"], default="mlp_out",
        help="'mlp_out' = MLP-blok-output (rounds 026-030); 'neuron' = input van de "
        "down-projectie (c_proj/down_proj) — het per-neuron-leespunt van H-Neurons "
        "(Gao et al. 2025).")
    act_probe.add_argument("--sparse-permutations", type=int, default=500,
        help="Aantal label-shuffles voor de permutatiecontrole op de sparse "
        "L1-classifier (0 = alleen LOOCV, geen p-waarde). Default 500: vloer "
        "1/501 ~0.002, haalbaar onder de Bonferroni-lat van 24 lagen (round 032).")

    chat = subparsers.add_parser(
        "chat",
        help="[demo] levende schaduwlaag: interactieve SSL-chat (manager, Gate, TTL/TrTL, agent-contract)",
    )
    chat.add_argument("--backend", choices=MODEL_BACKENDS, default="fixture")
    chat.add_argument("--model-id", default=None)
    chat.add_argument("--max-new-tokens", type=int, default=700)
    chat.add_argument("--embedding-backend", choices=["lexical", "openai"], default="lexical")
    chat.add_argument("--embedding-model", default=None)
    chat.add_argument("--surface-threshold", type=float, default=0.30)
    chat.add_argument("--surface-top-k", type=int, default=2,
        help="Use-time discipline: max. gevalideerde seeds per beurt (potentieel, geen must).")
    chat.add_argument("--recurrence-mode", choices=["pairwise", "cluster"], default="cluster")
    chat.add_argument("--script", default=None,
        help="Bestand met vragen (1 per regel) voor een niet-interactieve sessie.")
    chat.add_argument("--transcript", default=None,
        help="Schrijf het sessietranscript incl. audit-trail naar dit JSON-pad.")
    chat.add_argument("--show-shadow", action="store_true",
        help="Toon per beurt de schaduwlaag-diagnostiek.")
    chat.add_argument("--probe-corpus", default=None,
        help="Corpus (JSON chunks of platte tekst) waar promoted seeds live in zoeken; "
        "resultaten zijn aanwezigheid, geen sturing (gevonden != waar).")
    chat.add_argument("--probe-top-k", type=int, default=3,
        help="Aantal hits per retrieval-probe-arm (default 3).")

    ssl_session = subparsers.add_parser(
        "run-ssl-session",
        help="[manual/research] W9: multi-turn SSL door de ECHTE pijplijn (manager, Gate, TTL/TrTL)",
    )
    ssl_session.add_argument("--input", default="src/shadowseed/data/ssl_session_suite.json")
    ssl_session.add_argument("--output", default="results/ssl_session_suite.json")
    ssl_session.add_argument("--backend", choices=MODEL_BACKENDS, default="fixture")
    ssl_session.add_argument("--model-id", default=None)
    ssl_session.add_argument("--max-new-tokens", type=int, default=400)
    ssl_session.add_argument(
        "--embedding-backend", choices=["lexical", "openai"], default="lexical"
    )
    ssl_session.add_argument("--embedding-model", default=None)
    ssl_session.add_argument(
        "--surface-threshold",
        type=float,
        default=0.30,
        help="Relevantiedrempel (cosine) waarboven een promoted seed in een latere beurt mag opduiken.",
    )
    ssl_session.add_argument(
        "--surface-top-k",
        type=int,
        default=2,
        help="Use-time discipline (round 023): max. aantal meest-relevante promoted seeds dat een beurt mag sturen. Promoted = potentieel, geen must; voorkomt diffuse/vernauwde antwoorden. -1 = geen limiet.",
    )
    ssl_session.add_argument(
        "--early-turn-margin",
        type=float,
        default=0.10,
        help="Vroege-beurt-discipline (round 029): extra relevantiemarge bovenop --surface-threshold zolang de beurtindex kleiner is dan --early-turn-history. Selecteert op fit, blokkeert geen beurten. 0 = uit.",
    )
    ssl_session.add_argument(
        "--early-turn-history",
        type=int,
        default=5,
        help="Aantal eerste beurten (0-geïndexeerd: t < N) waarop de vroege-beurt-marge geldt.",
    )
    ssl_session.add_argument(
        "--resurface-margin",
        type=float,
        default=0.15,
        help="Gebruiksdemping (round 031-les, TrTL op use-time): extra relevantiemarge voor een seed die net een antwoord stuurde, halverend per beurt sinds de laatste surfacing. Gebruik verbruikt trace; terugkomen vergt verse fit met de nieuwe vraag. Weight blijft Gate-exclusief. 0 = uit.",
    )
    ssl_session.add_argument(
        "--dedup-threshold",
        type=float,
        default=None,
        help="Per-run dedup-drempel (default 0.85). Lager merge paraphrastische gaps zodat recurrence accumuleert (W9c). Globale doctrine-default blijft.",
    )
    ssl_session.add_argument(
        "--min-occurrences",
        type=int,
        default=None,
        help="Per-run recurrence-drempel voor de Gate (default 3).",
    )
    ssl_session.add_argument(
        "--promotion-threshold",
        type=float,
        default=None,
        help="Per-run promotie-drempel voor weight (default 0.5). Per-topic override kan in de conversatie-fixture.",
    )
    ssl_session.add_argument(
        "--recurrence-mode",
        choices=["pairwise", "cluster"],
        default="pairwise",
        help="cluster (W9e): parafrastische gaps tellen samen als recurrence, zodat promotie bij de veilige Gate-drempel vuurt zonder de strikte 0.85-dedup te verlagen.",
    )
    ssl_session.add_argument("--cluster-threshold", type=float, default=None,
        help="Cosine-drempel voor recurrence-clustering (default 0.6); alleen bij --recurrence-mode cluster.")
    ssl_session.add_argument("--auto-calibrate", action="store_true",
        help="Per-topic auto-kalibratie van de recurrence-bar op gespreksleng­te.")

    analyze = subparsers.add_parser(
        "analyze-results",
        help="[reporting] maak rapport en grafieken uit resultaatbestanden",
    )
    analyze.add_argument("--results-dir", default="results")
    analyze.add_argument("--output-dir", default="results/analysis")

    nlp = subparsers.add_parser(
        "run-absencebench-smoke",
        aliases=["run-nlp-smoke"],
        help="[standard] technische smoke voor de lokale AbsenceBench-route",
    )
    nlp.set_defaults(command="run-absencebench-smoke")
    nlp.add_argument("--input", default="examples/local_absencebench_sample.json")
    nlp.add_argument("--output", default="absencebench_smoke.json")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = execute_command(args)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
