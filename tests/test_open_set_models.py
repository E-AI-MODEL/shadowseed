"""Tests for the curated open-set model registry and its workflow wiring."""

from __future__ import annotations

import yaml

from shadowseed.benchmark.open_set_models import (
    dropdown_ids,
    find_model,
    format_table,
    load_models,
)


def test_registry_loads_and_has_required_fields():
    models = load_models()
    assert models
    for m in models:
        assert m["id"]
        for key in ("params_b", "approx_ram_gb", "license", "gated", "cpu_runner_ok"):
            assert key in m, f"{m['id']} missing {key}"


def test_find_model_strips_whitespace():
    # the trailing-space crash class: lookup must tolerate stray whitespace
    assert find_model("Qwen/Qwen2.5-1.5B-Instruct ") is not None
    assert find_model("  Qwen/Qwen2.5-1.5B-Instruct") is not None
    assert find_model("nope/does-not-exist") is None


def test_dropdown_ids_are_ungated_and_cpu_ok():
    ids = dropdown_ids()
    assert ids
    by_id = {m["id"]: m for m in load_models()}
    for mid in ids:
        assert by_id[mid]["gated"] is False
        assert by_id[mid]["cpu_runner_ok"] is True


def test_format_table_renders():
    table = format_table()
    assert "model_id" in table
    assert "Dropdown" in table
    assert "Qwen/Qwen2.5-1.5B-Instruct" in table


def _workflow_model_choices(path: str) -> list[str]:
    data = yaml.safe_load(open(path, encoding="utf-8"))
    inputs = data[True]["workflow_dispatch"]["inputs"]  # 'on' parses as True
    return list(inputs["model_id"].get("options", []))


def test_open_set_workflow_dropdown_is_subset_of_registry():
    """Drift guard: every model offered in the open-set workflow dropdown must
    exist in the registry and be ungated + cpu_runner_ok."""
    choices = _workflow_model_choices(".github/workflows/open-set-hf-review.yml")
    assert choices
    by_id = {m["id"]: m for m in load_models()}
    for mid in choices:
        assert mid in by_id, f"{mid} not in registry"
        assert by_id[mid]["gated"] is False
        assert by_id[mid]["cpu_runner_ok"] is True


def test_slm_workflow_dropdown_is_subset_of_registry():
    choices = _workflow_model_choices(".github/workflows/slm-model-benefit.yml")
    assert choices
    by_id = {m["id"]: m for m in load_models()}
    for mid in choices:
        assert mid in by_id, f"{mid} not in registry"
        assert by_id[mid]["gated"] is False
        assert by_id[mid]["cpu_runner_ok"] is True
