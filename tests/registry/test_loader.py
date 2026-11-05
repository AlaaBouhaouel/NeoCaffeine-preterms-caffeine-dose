# Tests for loading registry files.

import pytest

from neocaffeine.registry.entry import DesignAssumptionEntry, EntryGroup, StructuralEntry
from neocaffeine.registry.loader import CATEGORY_NAMES, DEFAULT_DATA_DIRECTORY, load_registry
from neocaffeine.registry.pk_model import PkModel
from neocaffeine.registry.registry_errors import RegistrySchemaError, UnknownModelError


def test_real_empty_registry_loads():
    """The shipped registry, with every value empty, loads for editing."""
    registry = load_registry(DEFAULT_DATA_DIRECTORY)
    assert registry.category_names() == list(CATEGORY_NAMES)
    assert registry.version is None


def test_every_pk_model_is_present():
    """The five published PK models are stored side by side."""
    registry = load_registry(DEFAULT_DATA_DIRECTORY)
    for name in ("thomson_1996", "falcao_1997", "charles_2008", "gao_2020", "engbers_2021"):
        assert isinstance(registry.pk_model(name), PkModel)


def test_unknown_model_name_is_rejected():
    """Asking for a model that is not in the registry raises UnknownModelError."""
    registry = load_registry(DEFAULT_DATA_DIRECTORY)
    with pytest.raises(UnknownModelError):
        registry.pk_model("not_a_model")


def test_entries_are_found_by_full_name():
    """Nested entries are reachable by their full dotted name."""
    registry = load_registry(DEFAULT_DATA_DIRECTORY)
    assert registry.find("pk_models.models.falcao_1997.clearance_equation").name.endswith("clearance_equation")
    assert isinstance(registry.find("observation.valid_time_exclusions.monitoring_off"), StructuralEntry)
    assert isinstance(registry.find("observation.valid_time_exclusions.signal_artifact"), EntryGroup)
    assert registry.find("bounds.not_an_entry") is None


def test_design_assumptions_are_listed():
    """Every design assumption is listed so runs can report it as a limitation."""
    registry = load_registry(DEFAULT_DATA_DIRECTORY)
    assumptions = registry.design_assumptions()
    assert [entry.name for entry in assumptions] == ["baseline.models.maturity_exponential"]
    assert isinstance(assumptions[0], DesignAssumptionEntry)
    assert assumptions[0].evidence_tier == "C"


def test_reference_maturity_is_absent():
    """The baseline model is relative to the measured window; there is no global reference maturity."""
    registry = load_registry(DEFAULT_DATA_DIRECTORY)
    assert registry.category("maturity") == {}
    assert registry.find("maturity.reference_maturity") is None


def test_missing_category_file_is_rejected(empty_registry_directory):
    """A registry folder without one of its category files cannot be loaded."""
    (empty_registry_directory / "bounds.yaml").unlink()
    with pytest.raises(RegistrySchemaError):
        load_registry(empty_registry_directory)


def test_conflict_with_unknown_entry_is_rejected(empty_registry_directory, edit_registry_file):
    """conflicts_with must name entries that exist."""
    edit_registry_file(
        empty_registry_directory / "bounds.yaml",
        lambda content: content["concentration"].update(conflicts_with=["bounds.not_an_entry"]),
    )
    with pytest.raises(RegistrySchemaError):
        load_registry(empty_registry_directory)


def test_conflict_with_existing_entry_is_accepted(empty_registry_directory, edit_registry_file):
    """conflicts_with may name any existing entry, including nested ones."""
    edit_registry_file(
        empty_registry_directory / "priors.yaml",
        lambda content: content["clearance_variability"]["falcao_1997"].update(
            conflicts_with=["priors.clearance_variability.engbers_2021"]
        ),
    )
    load_registry(empty_registry_directory)
