"""Result analyzer for SSL 4.5 benchmark artifacts."""

from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import re
from typing import Any


ResultDict = dict[str, Any]


def load_json(path: str | Path) -> ResultDict | None:
    file_path = Path(path)
    if not file_path.exists():
        return None
    return json.loads(file_path.read_text(encoding="utf-8"))


def load_turn_matrix(source: Path) -> list[ResultDict]:
    rows = []
    for path in sorted(source.glob("ssl45_gap_suite_turns_*.json")):
        payload = load_json(path)
        if not payload:
            continue
        turns_match = re.search(r"turns_(\d+)\.json$", path.name)
        rows.append(
            {
                "turns": int(turns_match.group(1)) if turns_match else None,
                "file": path.name,
                "summary": payload.get("summary", {}),
            }
        )
    return rows


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-zÀ-ÿ0-9_]+", text.lower())


def short_number(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, int):
        return str(value)
    return f"{value:.2f}"


def metric(payload: ResultDict | None, key: str, default: float | int | str | None = None):
    if not payload:
        return default
    return payload.get("summary", {}).get(key, default)


def collect_promoted_seeds(payload: ResultDict | None) -> list[dict[str, str]]:
    if not payload:
        return []
    rows: list[dict[str, str]] = []
    for result in payload.get("results", []):
        scenario_id = result.get("scenario_id", "")
        title = result.get("title", "")
        domain = result.get("domain", "")
        for seed in result.get("promoted_seeds", []):
            if isinstance(seed, dict):
                seed_text = seed.get("text", "")
            else:
                seed_text = str(seed)
            if seed_text:
                rows.append(
                    {
                        "scenario_id": scenario_id,
                        "title": title,
                        "domain": domain,
                        "seed": seed_text,
                    }
                )
    return rows


def semantic_seed_summary(payloads: list[ResultDict | None]) -> dict[str, Any]:
    seeds: list[dict[str, str]] = []
    for payload in payloads:
        seeds.extend(collect_promoted_seeds(payload))

    by_domain: dict[str, list[str]] = defaultdict(list)
    by_scenario: dict[str, list[str]] = defaultdict(list)
    token_counter: Counter[str] = Counter()

    stop = {
        "de", "het", "een", "en", "of", "van", "in", "op", "te", "is", "zijn", "bij",
        "als", "voor", "door", "tot", "met", "data", "recht", "seed", "ssl",
    }

    for row in seeds:
        by_domain[row["domain"]].append(row["seed"])
        by_scenario[row["scenario_id"]].append(row["seed"])
        token_counter.update(token for token in words(row["seed"]) if token not in stop and len(token) > 2)

    return {
        "promoted_seed_mentions": len(seeds),
        "by_domain": dict(by_domain),
        "by_scenario": dict(by_scenario),
        "top_terms": token_counter.most_common(12),
    }


def build_conclusion(
    gap_payload: ResultDict | None,
    false_positive_payload: ResultDict | None,
    benefit_payload: ResultDict | None,
    model_benefit_payload: ResultDict | None,
    blind_payload: ResultDict | None,
    adversarial_payload: ResultDict | None,
    open_set_payload: ResultDict | None,
) -> dict[str, Any]:
    """Build a cautious conclusion from the available result summaries."""
    gap_score = float(metric(gap_payload, "mean_scenario_score", 0.0) or 0.0)
    promoted_hits = int(metric(gap_payload, "promoted_hits", 0) or 0)
    fp_rate = float(metric(false_positive_payload, "promoted_false_positive_rate", 0.0) or 0.0)
    benefit_delta = float(metric(benefit_payload, "coverage_delta", 0.0) or 0.0)
    model_delta = float(metric(model_benefit_payload, "coverage_delta", 0.0) or 0.0)
    unsupported_rate = float(metric(model_benefit_payload, "unsupported_ssl_addition_rate", 0.0) or 0.0)
    length_delta = float(metric(model_benefit_payload, "mean_answer_length_delta_words", 0.0) or 0.0)
    blind_delta = float(metric(blind_payload, "mean_coverage_delta", 0.0) or 0.0)
    blind_fp = int(metric(blind_payload, "total_false_positive_count", 0) or 0)
    adversarial_gate_fp = float(metric(adversarial_payload, "current_gate_false_promotion_rate", 0.0) or 0.0)
    adversarial_trace_fp = float(metric(adversarial_payload, "trace_only_false_promotion_rate", 0.0) or 0.0)
    adversarial_delta = float(metric(adversarial_payload, "gate_vs_trace_only_delta", 0.0) or 0.0)
    open_set_seed_acceptance_rate = float(metric(open_set_payload, "seed_acceptance_rate", 0.0) or 0.0)
    open_set_unanimous_verdict_rate = float(metric(open_set_payload, "unanimous_verdict_rate", 0.0) or 0.0)
    open_set_pairwise_decision_agreement_rate = float(
        metric(open_set_payload, "pairwise_decision_agreement_rate", 0.0) or 0.0
    )
    backend = str(metric(model_benefit_payload, "backend", "unknown"))
    is_real_model = backend.startswith("hf-transformers:")
    has_open_set = bool(open_set_payload)
    has_adversarial = bool(adversarial_payload)

    if has_open_set and has_adversarial:
        headline = "De standaardpublicatie laat nu meer zien dan alleen regressie en smoke-tests."
        verdict = "supplemented_standard_publication"
        body = (
            "Naast de stabiele basislaag bevat deze publicatie nu ook aanvullende evidencelagen voor open-set seedkwaliteit "
            "en adversarial Gate-gedrag. Dat maakt de repo inhoudelijk sterker en eerlijker, zonder al te doen alsof "
            "het hele SSL-programma volledig gevalideerd is."
        )
    elif has_adversarial:
        headline = "De standaardpublicatie combineert de basislaag nu met een zichtbare adversarial Gate-laag."
        verdict = "supplemented_with_adversarial"
        body = (
            "De repo laat niet alleen zien dat de meetketen werkt, maar ook of de huidige Gate misleidende lure-seeds beter blokkeert "
            "dan zwakkere regels. Dat is aanvullend bewijs, geen volledige eindvalidatie."
        )
    elif has_open_set:
        headline = "De standaardpublicatie combineert de basislaag nu met een zichtbare open-set reviewlaag."
        verdict = "supplemented_with_open_set"
        body = (
            "De repo laat niet alleen vaste scenario-uitkomsten zien, maar ook of open-set seeds reviewbaar overeind blijven. "
            "Dat is inhoudelijk sterker dan alleen kleine suites, maar nog geen volledige eindvalidatie."
        )
    elif not model_benefit_payload:
        headline = "Nog geen model-benefit conclusie beschikbaar."
        verdict = "incomplete"
        body = (
            "Er is nog geen model-benefit output gevonden. Draai eerst `shadowseed run-model-benefit-suite` "
            "of een handmatige modelroute."
        )
    elif model_delta > 0 and unsupported_rate == 0.0:
        if is_real_model:
            headline = "SSL verbetert in deze modelrun de gemeten gap coverage zonder unsupported additions."
            verdict = "positive_slm_run"
            body = (
                "Binnen deze kleine suite presteert hetzelfde model beter met SSL-guided rewrite dan zonder SSL. "
                "Dit is positief bewijs voor deze run, maar geen brede claim buiten de geteste scenario's."
            )
        else:
            headline = "De fixture-run bevestigt dat de model-benefit harness werkt."
            verdict = "positive_fixture_smoke"
            body = (
                "De fixture-backend laat zien dat de meetketen werkt: baseline coverage stijgt na SSL-guided rewrite "
                "zonder unsupported additions. Dit blijft een technische smoke-test."
            )
    elif model_delta > 0 and unsupported_rate > 0.0:
        headline = "SSL verhoogt gap coverage, maar introduceert ook unsupported additions."
        verdict = "mixed"
        body = (
            "De run laat verbetering zien, maar niet schoon genoeg. De volgende stap is analyseren welke seeds of revisies unsupported claims veroorzaken."
        )
    else:
        headline = "Er is in deze run geen meetbare modelverbetering door SSL gevonden."
        verdict = "negative_or_neutral"
        body = (
            "De SSL-conditie scoort niet beter dan baseline op gap coverage. Dit kan liggen aan de detector, de prompts, "
            "het gekozen model of de suitegrootte."
        )

    support = []
    if gap_score >= 2.0 and promoted_hits > 0:
        support.append("De positieve Gap-Test Suite wordt volledig geraakt.")
    elif promoted_hits > 0:
        support.append("De Gap-Test Suite levert promoted seeds op, maar de score is nog niet maximaal.")
    else:
        support.append("De Gap-Test Suite levert nog geen promoted seeds op.")

    if fp_rate == 0.0:
        support.append("De false-positive controls blijven schoon op promoted false positives.")
    else:
        support.append("Er zijn promoted false positives gevonden; conclusies moeten worden beperkt.")

    if has_open_set:
        if open_set_seed_acceptance_rate > 0.0 and open_set_unanimous_verdict_rate > 0.0:
            support.append(
                "De open-set review laat zien dat een deel van de seeds door reviewers wordt geaccepteerd, met expliciete agreement-metrieken voor consensuscontrole."
            )
        elif open_set_seed_acceptance_rate > 0.0:
            support.append(
                "De open-set review levert geaccepteerde seeds op, maar de reviewer-consensus vraagt nog scherpere opvolging."
            )
        else:
            support.append(
                "De open-set review is aanwezig, maar laat nog geen overtuigende geaccepteerde seeds zien."
            )

    if has_adversarial:
        if adversarial_gate_fp == 0.0 and adversarial_delta > 0:
            support.append("De adversarial Gate-laag laat zien dat de huidige Gate lure-promoties blokkeert die trace-only nog zou doorlaten.")
        elif adversarial_trace_fp > adversarial_gate_fp:
            support.append("De adversarial Gate-laag is aanwezig en laat een kleinere false-promotion rate zien dan trace-only, maar nog niet volledig schoon.")
        else:
            support.append("De adversarial Gate-laag vraagt nog scherper verschil met zwakkere baselines.")

    if benefit_delta > 0:
        support.append("De benefit-suite laat hogere gap coverage zien na SSL-toevoegingen.")
    else:
        support.append("De benefit-suite laat nog geen coverage-winst zien.")

    if blind_payload:
        if blind_delta > 0 and blind_fp == 0:
            support.append("De blinde smoke-test vindt verborgen labels zonder extra false positives in deze kleine set.")
        else:
            support.append("De blinde smoke-test is aanwezig, maar vraagt nog controle op coverage en false positives.")

    if length_delta > 0:
        support.append(
            "De SSL-antwoorden zijn langer; daarom moet coverage-winst samen met lengtecorrectie en unsupported additions worden gelezen."
        )

    return {
        "verdict": verdict,
        "headline": headline,
        "body": body,
        "backend": backend,
        "is_real_model": is_real_model,
        "metrics": {
            "gap_mean_scenario_score": gap_score,
            "gap_promoted_hits": promoted_hits,
            "promoted_false_positive_rate": fp_rate,
            "open_set_seed_acceptance_rate": open_set_seed_acceptance_rate,
            "open_set_unanimous_verdict_rate": open_set_unanimous_verdict_rate,
            "open_set_pairwise_decision_agreement_rate": open_set_pairwise_decision_agreement_rate,
            "adversarial_current_gate_false_promotion_rate": adversarial_gate_fp,
            "adversarial_trace_only_false_promotion_rate": adversarial_trace_fp,
            "adversarial_gate_vs_trace_only_delta": adversarial_delta,
            "benefit_coverage_delta": benefit_delta,
            "model_benefit_coverage_delta": model_delta,
            "model_unsupported_ssl_addition_rate": unsupported_rate,
            "blind_coverage_delta": blind_delta,
            "blind_false_positive_count": blind_fp,
            "mean_answer_length_delta_words": length_delta,
        },
        "supporting_observations": support,
        "claim_boundary": (
            "Deze conclusie geldt alleen voor de huidige publicatievorm: regressie, smoke, kleine benchmarks en eventuele aanvullende evidencelagen. "
            "Voor een brede algemene claim zijn meer scenario's, meerdere modellen, sterkere open-set review, transfer en bredere menselijke beoordeling nodig."
        ),
    }


def svg_bar_chart(title: str, values: dict[str, float], output: Path) -> None:
    width = 760
    bar_height = 32
    gap = 16
    left = 220
    right = 40
    top = 56
    height = top + len(values) * (bar_height + gap) + 30
    max_value = max(values.values()) if values else 1.0
    max_value = max(max_value, 1e-9)
    chart_width = width - left - right

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="20" y="32" font-family="Arial" font-size="22" font-weight="700">{escape_xml(title)}</text>',
    ]
    y = top
    for label, value in values.items():
        bar_width = chart_width * (value / max_value)
        lines.extend(
            [
                f'<text x="20" y="{y + 22}" font-family="Arial" font-size="14">{escape_xml(label)}</text>',
                f'<rect x="{left}" y="{y}" width="{bar_width:.1f}" height="{bar_height}" rx="5" fill="#4f46e5"/>',
                f'<text x="{left + bar_width + 8}" y="{y + 22}" font-family="Arial" font-size="14">{short_number(value)}</text>',
            ]
        )
        y += bar_height + gap
    lines.append("</svg>\n")
    output.write_text("\n".join(lines), encoding="utf-8")


def escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def add_optional_summary_rows(lines: list[str], payload: ResultDict | None, rows: list[tuple[str, str]]) -> None:
    if not payload:
        return
    for label, key in rows:
        lines.append(f"| {label} | {short_number(metric(payload, key))} |")


def make_markdown_report(
    gap_payload: ResultDict | None,
    false_positive_payload: ResultDict | None,
    benefit_payload: ResultDict | None,
    model_benefit_payload: ResultDict | None,
    blind_payload: ResultDict | None,
    adversarial_payload: ResultDict | None,
    open_set_payload: ResultDict | None,
    retrieval_payload: ResultDict | None,
    retrieval_model_payload: ResultDict | None,
    probe_payload: ResultDict | None,
    ssot_payload: ResultDict | None,
    vectorstore_payload: ResultDict | None,
    turn_matrix: list[ResultDict],
    semantic: dict[str, Any],
    conclusion: dict[str, Any],
    publish_mode: str,
) -> str:
    lines = [
        "# SSL 4.5 resultaatanalyse",
        "",
        "Deze analyse is automatisch gemaakt uit benchmark-JSON artifacts.",
        "",
        f"Publicatiemodus: **{publish_mode}**.",
        "",
        "## Wat bekijk je nu?",
        "",
        "Deze publicatie combineert, voor zover aanwezig:",
        "",
        "- regressie-uitvoer",
        "- technische en methodologische smoke-tests",
        "- kleine benchmarklagen",
        "- aanvullende evidencelagen zoals open-set review, adversarial Gate en probe utility",
        "",
        "Lees aanvullende evidencelagen als extra inhoudelijk signaal, niet als volledige eindvalidatie.",
        "",
        "## Conclusie",
        "",
        f"**{conclusion['headline']}**",
        "",
        conclusion["body"],
        "",
        "### Onderbouwing",
        "",
    ]
    for observation in conclusion["supporting_observations"]:
        lines.append(f"- {observation}")
    lines.extend(
        [
            "",
            "### Grens van de claim",
            "",
            conclusion["claim_boundary"],
            "",
            "## Samenvatting",
            "",
            "| Suite | Belangrijkste uitkomst |",
            "|---|---:|",
            f"| Gap Finder mean score | {short_number(metric(gap_payload, 'mean_scenario_score'))} |",
            f"| Gap Finder promoted hits | {short_number(metric(gap_payload, 'promoted_hits'))} |",
            f"| False-positive promoted rate | {short_number(metric(false_positive_payload, 'promoted_false_positive_rate'))} |",
            f"| Open-set seed acceptance rate | {short_number(metric(open_set_payload, 'seed_acceptance_rate'))} |",
            f"| Open-set unanimous verdict rate | {short_number(metric(open_set_payload, 'unanimous_verdict_rate'))} |",
            f"| Open-set pairwise agreement rate | {short_number(metric(open_set_payload, 'pairwise_decision_agreement_rate'))} |",
            f"| Adversarial Gate current FP rate | {short_number(metric(adversarial_payload, 'current_gate_false_promotion_rate'))} |",
            f"| Adversarial Gate trace-only FP rate | {short_number(metric(adversarial_payload, 'trace_only_false_promotion_rate'))} |",
            f"| Adversarial Gate reduction vs trace-only | {short_number(metric(adversarial_payload, 'gate_relative_reduction_vs_trace_only'))} |",
            f"| Antwoordwinst coverage delta | {short_number(metric(benefit_payload, 'coverage_delta'))} |",
            f"| Model smoke backend | {metric(model_benefit_payload, 'backend', 'n/a')} |",
            f"| Model smoke coverage delta | {short_number(metric(model_benefit_payload, 'coverage_delta'))} |",
            f"| Model smoke unsupported rate | {short_number(metric(model_benefit_payload, 'unsupported_ssl_addition_rate'))} |",
            f"| Blinde smoke coverage delta | {short_number(metric(blind_payload, 'mean_coverage_delta'))} |",
            f"| Blinde smoke false positives | {short_number(metric(blind_payload, 'total_false_positive_count'))} |",
            f"| Mean answer length delta | {short_number(metric(model_benefit_payload, 'mean_answer_length_delta_words'))} |",
        ]
    )
    add_optional_summary_rows(
        lines,
        retrieval_model_payload,
        [
            ("Retrieval model baseline coverage", "baseline_mean_gap_coverage"),
            ("Retrieval model with context coverage", "retrieval_mean_gap_coverage"),
            ("Retrieval model coverage delta", "coverage_delta"),
        ],
    )
    add_optional_summary_rows(
        lines,
        probe_payload,
        [
            ("Probe utility follow-up delta", "mean_follow_up_delta"),
            ("Probe utility retrieval delta", "mean_retrieval_delta"),
            ("Probe utility dialectic delta", "mean_dialectic_delta"),
            ("Probe utility overall delta", "overall_probe_utility_delta"),
        ],
    )
    if retrieval_payload:
        metrics = retrieval_payload.get("metrics", {})
        lines.append(f"| Retrieval hit@k | {short_number(metrics.get('hit@k'))} |")
    if ssot_payload:
        lines.append(f"| SSOT smoke passed | {metric(ssot_payload, 'passed', 'n/a')} |")
    if vectorstore_payload:
        lines.append(f"| Vectorstore smoke passed | {metric(vectorstore_payload, 'passed', 'n/a')} |")

    lines.extend(
        [
            "",
            "## Grafieken",
            "",
            "![Coverage](coverage.svg)",
            "",
            "![False positives](false_positive.svg)",
            "",
            "## Herhalingstest",
            "",
        ]
    )
    if turn_matrix:
        lines.extend(["| Rondes | Mean score | Promoted hits |", "|---:|---:|---:|"])
        for row in turn_matrix:
            summary = row.get("summary", {})
            lines.append(
                f"| {row.get('turns', 'n/a')} | {short_number(summary.get('mean_scenario_score'))} | {short_number(summary.get('promoted_hits'))} |"
            )
    else:
        lines.append("Geen turn-matrix artifact gevonden.")

    if open_set_payload:
        lines.extend(
            [
                "",
                "## Open-set review",
                "",
                "| Metric | Waarde |",
                "|---|---:|",
                f"| Review packets | {short_number(metric(open_set_payload, 'packet_count'))} |",
                f"| Unique seeds | {short_number(metric(open_set_payload, 'unique_seed_count'))} |",
                f"| Seed acceptance rate | {short_number(metric(open_set_payload, 'seed_acceptance_rate'))} |",
                f"| Seed rejection rate | {short_number(metric(open_set_payload, 'seed_rejection_rate'))} |",
                f"| Agreement-eligible seeds | {short_number(metric(open_set_payload, 'agreement_eligible_seed_count'))} |",
                f"| Unanimous verdict rate | {short_number(metric(open_set_payload, 'unanimous_verdict_rate'))} |",
                f"| Pairwise decision agreement rate | {short_number(metric(open_set_payload, 'pairwise_decision_agreement_rate'))} |",
                "",
                "Deze laag maakt zichtbaar hoeveel open-set seeds reviewbaar overeind blijven, en hoeveel reviewer-consensus er echt is in plaats van alleen ruwe acceptatie.",
            ]
        )

    if adversarial_payload:
        lines.extend(
            [
                "",
                "## Adversarial Gate-laag",
                "",
                "| Metric | Waarde |",
                "|---|---:|",
                f"| Candidates | {short_number(metric(adversarial_payload, 'candidate_count'))} |",
                f"| Current Gate false-promotion rate | {short_number(metric(adversarial_payload, 'current_gate_false_promotion_rate'))} |",
                f"| Trace-only false-promotion rate | {short_number(metric(adversarial_payload, 'trace_only_false_promotion_rate'))} |",
                f"| Trace zonder contradictie false-promotion rate | {short_number(metric(adversarial_payload, 'trace_without_contradiction_false_promotion_rate'))} |",
                f"| Gate reductie vs trace-only | {short_number(metric(adversarial_payload, 'gate_relative_reduction_vs_trace_only'))} |",
                f"| Gate reductie vs trace zonder contradictiecheck | {short_number(metric(adversarial_payload, 'gate_relative_reduction_vs_trace_without_contradiction'))} |",
                "",
                "Deze laag laat zien hoeveel lure-promoties de Gate voorkomt ten opzichte van zwakkere regels.",
            ]
        )

    lines.extend(
        [
            "",
            "## Semantische seed-samenvatting",
            "",
            f"Aantal promoted seed-vermeldingen in geanalyseerde positieve outputs: **{semantic['promoted_seed_mentions']}**.",
            "",
            "Let op: dit zijn vermeldingen, geen unieke seeds. Dezelfde seed kan in meerdere suites terugkomen.",
            "",
            "### Toptermen",
            "",
            "| Term | Aantal |",
            "|---|---:|",
        ]
    )
    for term, count in semantic["top_terms"]:
        lines.append(f"| {term} | {count} |")

    lines.extend(["", "### Per domein", ""])
    for domain, seeds in semantic["by_domain"].items():
        lines.append(f"#### {domain or 'onbekend'}")
        lines.append("")
        for seed in seeds:
            lines.append(f"- {seed}")
        lines.append("")

    lines.extend(
        [
            "## Interpretatie",
            "",
            "Lees deze analyse in lagen:",
            "",
            "1. werkt de basis nog;",
            "2. zie je winst op kleine benchmarks;",
            "3. zie je aanvullende evidencelagen buiten alleen smoke en scenario-suites;",
            "4. blijft de claimgrens expliciet genoeg."
        ]
    )
    if probe_payload:
        lines.extend(
            [
                "",
                "De probe-utility laag is aanvullend bewijs. Een positieve delta betekent hier alleen dat seed-geleide vervolgacties scherper zijn dan brede baselines binnen deze lokale scaffold.",
            ]
        )
    return "\n".join(lines) + "\n"


def analyze_results(
    results_dir: str,
    output_dir: str,
) -> Path:
    source = Path(results_dir)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    gap = load_json(source / "ssl45_gap_suite.json")
    false_positive = load_json(source / "ssl45_false_positive_suite.json")
    benefit = load_json(source / "ssl45_benefit_suite.json")
    model_benefit = load_json(source / "ssl45_model_benefit_suite.json")
    blind = load_json(source / "blind_benchmark.json")
    adversarial = load_json(source / "adversarial_gate_benchmark.json")
    open_set_review = load_json(source / "open_set_seed_review_summary.json")
    retrieval = load_json(source / "retrieval_benchmark.json")
    retrieval_model = load_json(source / "retrieval_model_benchmark.json")
    probe = load_json(source / "ssl45_probe_utility_suite.json")
    ssot = load_json(source / "ssot_smoke.json")
    vectorstore = load_json(source / "vectorstore_smoke.json")
    manifest = load_json(source / "manifest.json")
    turn_matrix = load_turn_matrix(source)

    semantic = semantic_seed_summary([gap, benefit, model_benefit])
    conclusion = build_conclusion(gap, false_positive, benefit, model_benefit, blind, adversarial, open_set_review)
    publish_mode = "workflow snapshot"
    if manifest and manifest.get("committed_back_to_main") is False:
        publish_mode = "wiki/pages snapshot without main write-back"

    coverage_values = {
        "Gap mean score": float(metric(gap, "mean_scenario_score", 0.0) or 0.0),
        "Benefit baseline": float(metric(benefit, "baseline_mean_gap_coverage", 0.0) or 0.0),
        "Benefit SSL": float(metric(benefit, "ssl_mean_gap_coverage", 0.0) or 0.0),
        "Model baseline": float(metric(model_benefit, "baseline_mean_gap_coverage", 0.0) or 0.0),
        "Model SSL": float(metric(model_benefit, "ssl_mean_gap_coverage", 0.0) or 0.0),
        "Blind SSL": float(metric(blind, "mean_ssl_gap_coverage", 0.0) or 0.0),
    }
    false_positive_values = {
        "Candidate FP rate": float(metric(false_positive, "candidate_false_positive_rate", 0.0) or 0.0),
        "Promoted FP rate": float(metric(false_positive, "promoted_false_positive_rate", 0.0) or 0.0),
        "Adversarial Gate FP rate": float(metric(adversarial, "current_gate_false_promotion_rate", 0.0) or 0.0),
        "Adversarial trace-only FP rate": float(metric(adversarial, "trace_only_false_promotion_rate", 0.0) or 0.0),
        "Model unsupported rate": float(metric(model_benefit, "unsupported_ssl_addition_rate", 0.0) or 0.0),
        "Blind FP count": float(metric(blind, "total_false_positive_count", 0.0) or 0.0),
    }

    svg_bar_chart("Coverage metrics", coverage_values, output / "coverage.svg")
    svg_bar_chart("False-positive and unsupported rates", false_positive_values, output / "false_positive.svg")

    summary = {
        "gap": gap.get("summary") if gap else None,
        "false_positive": false_positive.get("summary") if false_positive else None,
        "benefit": benefit.get("summary") if benefit else None,
        "model_benefit": model_benefit.get("summary") if model_benefit else None,
        "blind": blind.get("summary") if blind else None,
        "adversarial_gate": adversarial.get("summary") if adversarial else None,
        "open_set_review": open_set_review.get("summary") if open_set_review else None,
        "retrieval": retrieval.get("metrics") if retrieval else None,
        "retrieval_model": retrieval_model.get("summary") if retrieval_model else None,
        "probe_utility": probe.get("summary") if probe else None,
        "ssot": ssot.get("summary") if ssot else None,
        "vectorstore": vectorstore.get("summary") if vectorstore else None,
        "turn_matrix": turn_matrix,
        "manifest": manifest,
        "publish_mode": publish_mode,
        "semantic": semantic,
        "conclusion": conclusion,
        "charts": ["coverage.svg", "false_positive.svg"],
    }
    (output / "analysis_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output / "analysis_report.md").write_text(
        make_markdown_report(
            gap,
            false_positive,
            benefit,
            model_benefit,
            blind,
            adversarial,
            open_set_review,
            retrieval,
            retrieval_model,
            probe,
            ssot,
            vectorstore,
            turn_matrix,
            semantic,
            conclusion,
            publish_mode,
        ),
        encoding="utf-8",
    )
    return output / "analysis_report.md"
