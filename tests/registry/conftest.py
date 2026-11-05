# Shared fixtures for registry tests: copies of the real empty templates, optionally filled with placeholder values.

import copy
import shutil
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML

from neocaffeine.registry.loader import DEFAULT_DATA_DIRECTORY
from neocaffeine.registry.registry import ModelSelection

FIXTURE_TEXT = "test fixture placeholder"
FIXTURE_NUMBER = 1.0
FIXTURE_YEAR = 2000
FIXTURE_UNIT = "dimensionless"
FIXTURE_TIER = "C"
NUMERIC_KEYS = frozenset({
    "value", "minimum", "maximum", "min", "max", "threshold", "min_duration", "max_duration",
    "rate", "reported_maturity", "merge_window",
})
BOOLEAN_KEYS = frozenset({"enabled", "counts_toward_N"})
FIXTURE_CHOICES = {"dosing_weight_rule": "birth_weight", "event_overlap_rule": "separate"}
GROUPS_NEEDING_ONE_ITEM = frozenset({"coefficients", "signal_artifact"})
SELECTION = ModelSelection(pk_model="falcao_1997", effect_model="hill", baseline_model="maturity_exponential")


def filled_value(key: str, parent_key: str | None) -> Any:
    """Return a placeholder test value for an empty field, chosen from its key."""
    if key == "value" and parent_key in FIXTURE_CHOICES:
        return FIXTURE_CHOICES[parent_key]
    if key in NUMERIC_KEYS:
        return FIXTURE_NUMBER
    if key in BOOLEAN_KEYS:
        return True
    if key == "year":
        return FIXTURE_YEAR
    if key == "evidence_tier":
        return FIXTURE_TIER
    if key == "unit" or key.endswith("_unit"):
        return FIXTURE_UNIT
    return FIXTURE_TEXT


def fill_template(node: Any, parent_key: str | None = None) -> Any:
    """Return a copy of a registry template with every empty field filled with a placeholder."""
    if isinstance(node, dict):
        if not node and parent_key in GROUPS_NEEDING_ONE_ITEM:
            return {"fixture_item": fill_template(SCALAR_TEMPLATE, "fixture_item")}
        return {
            key: filled_value(key, parent_key) if value is None else fill_template(value, key)
            for key, value in node.items()
        }
    if isinstance(node, list):
        return [fill_template(item, parent_key) for item in node]
    return node


def read_template(path: Path) -> Any:
    """Read a YAML template as plain Python data."""
    return YAML(typ="safe").load(path.read_text(encoding="utf-8"))


def write_yaml(path: Path, content: Any) -> None:
    """Write plain Python data as YAML."""
    yaml = YAML(typ="safe")
    yaml.default_flow_style = False
    with path.open("w", encoding="utf-8") as stream:
        yaml.dump(content, stream)


SCALAR_TEMPLATE = read_template(DEFAULT_DATA_DIRECTORY / "dosing.yaml")["citrate_to_base_factor"]


@pytest.fixture
def empty_registry_directory(tmp_path: Path) -> Path:
    """Return a temporary copy of the real, empty registry data folder."""
    target = tmp_path / "data"
    shutil.copytree(DEFAULT_DATA_DIRECTORY, target)
    return target


@pytest.fixture
def filled_registry_directory(tmp_path: Path) -> Path:
    """Return a temporary registry folder whose every field holds a placeholder test value."""
    target = tmp_path / "filled"
    target.mkdir()
    for template_path in DEFAULT_DATA_DIRECTORY.glob("*.yaml"):
        write_yaml(target / template_path.name, fill_template(read_template(template_path) or {}))
    return target


def edit_yaml(path: Path, edit) -> None:
    """Apply an edit function to the data of a YAML file and write it back."""
    content = read_template(path)
    edit(content)
    write_yaml(path, content)


@pytest.fixture
def edit_registry_file():
    """Return the function that edits one registry YAML file in place."""
    return edit_yaml


@pytest.fixture
def scalar_template() -> dict[str, Any]:
    """Return a fresh copy of the empty scalar entry template."""
    return copy.deepcopy(SCALAR_TEMPLATE)


@pytest.fixture
def filled_scalar_template() -> dict[str, Any]:
    """Return a scalar entry template with every field filled with a placeholder."""
    return fill_template(copy.deepcopy(SCALAR_TEMPLATE))


@pytest.fixture
def selection() -> ModelSelection:
    """Return the model selection used by registry tests."""
    return SELECTION
