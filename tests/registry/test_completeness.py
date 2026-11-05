# Tests for the completeness check that refuses runs on an incomplete registry.

import pytest

from neocaffeine.registry.completeness import missing_items, require_complete
from neocaffeine.registry.entry_parser import parse_node
from neocaffeine.registry.loader import DEFAULT_DATA_DIRECTORY, load_registry
from neocaffeine.registry.registry import ModelSelection
from neocaffeine.registry.registry_errors import IncompleteRegistryError, NotReportedValueError, UnknownModelError


@pytest.fixture
def missing_from_empty_registry(selection) -> list[str]:
    """Return the missing items reported for the real empty registry."""
    with pytest.raises(IncompleteRegistryError) as raised:
        require_complete(load_registry(DEFAULT_DATA_DIRECTORY), selection)
    return raised.value.missing_items


def test_empty_registry_refuses_to_run(missing_from_empty_registry):
    """The real empty registry lists missing items for every category."""
    for prefix in (
        "registry_meta.version", "pk_models.", "dosing.", "effect.", "baseline.", "priors.",
        "bounds.", "events.", "observation.", "validation_ranges.", "decision.",
    ):
        assert any(item.startswith(prefix) for item in missing_from_empty_registry), prefix


def test_every_missing_item_is_listed_at_once(missing_from_empty_registry):
    """One error lists every missing item, not only the first."""
    assert len(missing_from_empty_registry) > 100


def test_only_selected_models_are_required(missing_from_empty_registry):
    """Unselected PK models and their variabilities may stay empty."""
    assert any("falcao_1997" in item for item in missing_from_empty_registry)
    for unselected in ("thomson_1996", "charles_2008", "gao_2020", "engbers_2021"):
        assert not any(unselected in item for item in missing_from_empty_registry), unselected


def test_selected_variabilities_are_required(missing_from_empty_registry):
    """The selected PK model's CL and V variabilities are required."""
    assert "priors.clearance_variability.falcao_1997.value: empty" in missing_from_empty_registry
    assert "priors.volume_variability.falcao_1997.value: empty" in missing_from_empty_registry


def test_empty_coefficients_count_as_missing(missing_from_empty_registry):
    """An empty coefficients map is reported until the model's coefficients are filled."""
    assert "pk_models.models.falcao_1997.coefficients: empty" in missing_from_empty_registry


def test_structural_entry_needs_only_meaning(missing_from_empty_registry):
    """monitoring_off is reported for its meaning only, never for a tier or citation."""
    items = [item for item in missing_from_empty_registry if ".monitoring_off" in item]
    assert items == ["observation.valid_time_exclusions.monitoring_off.meaning: empty"]


def test_design_assumption_needs_rationale_not_tier(missing_from_empty_registry):
    """The baseline design assumption needs a rationale and citations, but no tier or population."""
    items = [item for item in missing_from_empty_registry if item.startswith("baseline.models.maturity_exponential")]
    assert "baseline.models.maturity_exponential.rationale: empty" in items
    assert not any("evidence_tier" in item or "population" in item for item in items)


def test_unknown_selected_model_is_rejected():
    """Selecting a model name that does not exist raises UnknownModelError."""
    selection = ModelSelection(pk_model="not_a_model", effect_model="hill", baseline_model="maturity_exponential")
    with pytest.raises(UnknownModelError):
        require_complete(load_registry(DEFAULT_DATA_DIRECTORY), selection)


def test_filled_registry_passes(filled_registry_directory, selection):
    """A registry with every field filled passes the check."""
    require_complete(load_registry(filled_registry_directory), selection)


def test_not_reported_required_value_stops_the_run(filled_registry_directory, edit_registry_file, selection):
    """A required value marked not_reported raises NotReportedValueError naming it."""
    edit_registry_file(
        filled_registry_directory / "priors.yaml",
        lambda content: content["clearance_variability"]["falcao_1997"].update(
            value="not_reported", not_reported_note="test fixture note"
        ),
    )
    with pytest.raises(NotReportedValueError) as raised:
        require_complete(load_registry(filled_registry_directory), selection)
    assert raised.value.item_names == ["priors.clearance_variability.falcao_1997.value"]


def test_not_reported_value_of_unselected_model_is_allowed(filled_registry_directory, edit_registry_file, selection):
    """not_reported in a model the run does not select does not stop the run."""
    edit_registry_file(
        filled_registry_directory / "priors.yaml",
        lambda content: content["clearance_variability"]["thomson_1996"].update(
            value="not_reported", not_reported_note="test fixture note"
        ),
    )
    require_complete(load_registry(filled_registry_directory), selection)


def test_merge_window_required_only_for_merge_option(filled_registry_directory, edit_registry_file, selection):
    """merge_within_window needs merge_window and its unit; separate does not."""
    edit_registry_file(
        filled_registry_directory / "events.yaml",
        lambda content: content["event_overlap_rule"].update(
            value="merge_within_window", merge_window=None, merge_window_unit=None
        ),
    )
    with pytest.raises(IncompleteRegistryError) as raised:
        require_complete(load_registry(filled_registry_directory), selection)
    assert len(raised.value.missing_items) == 2
    assert all("merge_window" in item for item in raised.value.missing_items)


def test_citation_needs_one_identifier(filled_scalar_template):
    """A citation without DOI, PMID or URL is incomplete."""
    filled_scalar_template["citations"][0].update(doi=None, pmid=None, url=None)
    assert missing_items(parse_node("bounds.example", filled_scalar_template)) == [
        "bounds.example.citations[0].doi|pmid|url: empty, at least one is required"
    ]


def test_optional_citation_fields_may_stay_empty(filled_scalar_template):
    """volume, issue, pages and notes are optional."""
    filled_scalar_template["citations"][0].update(volume=None, issue=None, pages=None, notes=None)
    assert missing_items(parse_node("bounds.example", filled_scalar_template)) == []


def test_conflict_needs_a_note(filled_scalar_template):
    """A filled conflicts_with without a note is incomplete."""
    filled_scalar_template.update(conflicts_with=["bounds.other"], conflict_note=None)
    assert missing_items(parse_node("bounds.example", filled_scalar_template)) == [
        "bounds.example.conflict_note: empty, required when conflicts_with is filled"
    ]
