"""Result analyzer for SSL 4.5 benchmark artifacts.

The analyzer reads benchmark JSON files and writes:

- a markdown report;
- a machine-readable summary JSON;
- simple SVG charts;
- a semantic seed summary grouped by scenario and domain;
- a result-based conclusion.

It intentionally avoids heavy plotting dependencies so it can run in CI.
"""

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


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-zÀ-ÿ0-9_]+", text.lower())


def short_number(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, int):
        return str(value)
    return f"{value:.2f}"


def metric(payload: ResultDict | None, key: str, default: float | int | None = None) -> float | int | None:
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
        "promoted_seed_count": len(seeds),
        "by_domain": dict(by_domain),
        "by_scenario": dict(by_scenario),
        "top_terms": token_counter.most_common(12),
    }


def build_conclusion(
    gap_payload: ResultDict | None,
    false_positive_payload: ResultDict | None,
    benefit_payload: ResultDict | None,
    model_benefit_payload: ResultDict | None,
) -> dict[str, Any]:
    """Build a cautious conclusion from the available result summaries."""
    gap_score = float(metric(gap_payload, "mean_scenario_score", 0.0) or 0.0)
    promoted_hits = int(metric(gap_payload, "promoted_hits", 0) or 0)
    fp_rate = float(metric(false_positive_payload, "promoted_false_positive_rate", 0.0) or 0.0)
    benefit_delta = float(metric(benefit_payload, "coverage_delta", 0.0) or 0.0)
    model_delta = float(metric(model_benefit_payload, "coverage_delta", 0.0) or 0.0)
    unsupported_rate = float(metric(model_benefit_payload, "unsupported_ssl_addition_rate", 0.0) or 0.0)
    length_delta = float(metric(model_benefit_payload, "mean_answer_length_delta_words", 0.0) or 0.0)
    backend = str(metric(model_benefit_payload, "backend", "unknown"))
    is_real_model = backend.startswith("hf-transformers:")

    if not model_benefit_payload:
        headline = "Nog geen model-benefit conclusie beschikbaar."
        verdict = "incomplete"
        body = (
            "Er is nog geen model-benefit output gevonden. Draai eerst `shadowseed run-model-benefit-suite` "
            "of de handmatige SLM-workflow."
        )
    elif model_delta > 0 and unsupported_rate == 0.0:
        if is_real_model:
            headline = "SSL verbetert in deze SLM-run de gemeten gap coverage zonder unsupported additions."
            verdict = "positive_slm_run"
            body = (
                "Binnen deze kleine suite presteert hetzelfde SLM beter met SSL-guided rewrite dan zonder SSL. "
                "De verbetering zit in extra dekking van gevalideerde gaps, niet in een ander model. "
                "Dit is positief bewijs voor deze run, maar nog geen algemene claim buiten de geteste scenario's."
            )
        else:
            headline = "De fixture-run bevestigt dat de model-benefit harness werkt."
            verdict = "positive_fixture_smoke"
            body = (
                "De fixture-backend laat zien dat de meetketen werkt: baseline coverage stijgt na SSL-guided rewrite "
                "zonder unsupported additions. Dit is een technische smoke-test, geen echte SLM-claim."
            )
    elif model_delta > 0 and unsupported_rate > 0.0:
        headline = "SSL verhoogt gap coverage, maar introduceert ook unsupported additions."
        verdict = "mixed"
        body = (
            "De run laat verbetering zien, maar niet schoon genoeg. De volgende stap is analyseren welke seeds of revisies "
            "unsupported claims veroorzaken."
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

    if benefit_delta > 0:
        support.append("De benefit-suite laat hogere gap coverage zien na SSL-toevoegingen.")
    else:
        support.append("De benefit-suite laat nog geen coverage-winst zien.")

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
            "benefit_coverage_delta": benefit_delta,
            "model_benefit_coverage_delta": model_delta,
            "model_unsupported_ssl_addition_rate": unsupported_rate,
            "mean_answer_length_delta_words": length_delta,
        },
        "supporting_observations": support,
        "claim_boundary": (
            "Deze conclusie geldt alleen voor de huidige suite, het gebruikte model en de vastgelegde prompts. "
            "Voor een algemene claim zijn meer scenario's, meerdere modellen en blind review nodig."
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


def make_markdown_report(
    gap_payload: ResultDict | None,
    false_positive_payload: ResultDict | None,
    benefit_payload: ResultDict | None,
    model_benefit_payload: ResultDict | None,
    semantic: dict[str, Any],
    conclusion: dict[str, Any],
) -> str:
    lines = [
        "# SSL 4.5 resultaatanalyse",
        "",
        "Deze analyse is automatisch gemaakt uit benchmark-JSON artifacts.",
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
            f"| Gap-Test Suite mean score | {short_number(metric(gap_payload, 'mean_scenario_score'))} |",
            f"| Gap-Test Suite promoted hits | {short_number(metric(gap_payload, 'promoted_hits'))} |",
            f"| False-positive promoted rate | {short_number(metric(false_positive_payload, 'promoted_false_positive_rate'))} |",
            f"| Benefit coverage delta | {short_number(metric(benefit_payload, 'coverage_delta'))} |",
            f"| Model benefit backend | {metric(model_benefit_payload, 'backend', 'n/a')} |",
            f"| Model benefit coverage delta | {short_number(metric(model_benefit_payload, 'coverage_delta'))} |",
            f"| Model benefit unsupported rate | {short_number(metric(model_benefit_payload, 'unsupported_ssl_addition_rate'))} |",
            f"| Mean answer length delta | {short_number(metric(model_benefit_payload, 'mean_answer_length_delta_words'))} |",
            "",
            "## Grafieken",
            "",
            "![Coverage](coverage.svg)",
            "",
            "![False positives](false_positive.svg)",
            "",
            "## Semantische seed-samenvatting",
            "",
            f"Aantal promoted seeds in geanalyseerde positieve outputs: **{semantic['promoted_seed_count']}**.",
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
            "Deze analyse scheidt drie dingen:",
            "",
            "1. of SSL de juiste gaps vindt;",
            "2. of SSL geen false positives promoot;",
            "3. of SSL-guided antwoorden meer gevalideerde gap coverage krijgen dan baseline-antwoorden.",
            "",
            "Een positief resultaat betekent dus niet automatisch dat SSL algemeen werkt. Het betekent dat de gemeten suite beter scoort onder de vastgelegde voorwaarden.",
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

    semantic = semantic_seed_summary([gap, benefit, model_benefit])
    conclusion = build_conclusion(gap, false_positive, benefit, model_benefit)

    coverage_values = {
        "Gap mean score": float(metric(gap, "mean_scenario_score", 0.0) or 0.0),
        "Benefit baseline": float(metric(benefit, "baseline_mean_gap_coverage", 0.0) or 0.0),
        "Benefit SSL": float(metric(benefit, "ssl_mean_gap_coverage", 0.0) or 0.0),
        "Model baseline": float(metric(model_benefit, "baseline_mean_gap_coverage", 0.0) or 0.0),
        "Model SSL": float(metric(model_benefit, "ssl_mean_gap_coverage", 0.0) or 0.0),
    }
    false_positive_values = {
        "Candidate FP rate": float(metric(false_positive, "candidate_false_positive_rate", 0.0) or 0.0),
        "Promoted FP rate": float(metric(false_positive, "promoted_false_positive_rate", 0.0) or 0.0),
        "Model unsupported rate": float(metric(model_benefit, "unsupported_ssl_addition_rate", 0.0) or 0.0),
    }

    svg_bar_chart("Coverage metrics", coverage_values, output / "coverage.svg")
    svg_bar_chart("False-positive and unsupported rates", false_positive_values, output / "false_positive.svg")

    summary = {
        "gap": gap.get("summary") if gap else None,
        "false_positive": false_positive.get("summary") if false_positive else None,
        "benefit": benefit.get("summary") if benefit else None,
        "model_benefit": model_benefit.get("summary") if model_benefit else None,
        "semantic": semantic,
        "conclusion": conclusion,
        "charts": ["coverage.svg", "false_positive.svg"],
    }
    (output / "analysis_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output / "analysis_report.md").write_text(
        make_markdown_report(gap, false_positive, benefit, model_benefit, semantic, conclusion),
        encoding="utf-8",
    )
    return output / "analysis_report.md"
