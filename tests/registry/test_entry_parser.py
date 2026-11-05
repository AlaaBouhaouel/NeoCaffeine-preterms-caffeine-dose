# Tests for parsing registry entries and rejecting schema violations.

import pytest

from neocaffeine.registry.entry import ChoiceEntry, ScalarEntry, StructuralEntry
from neocaffeine.registry.entry_parser import parse_node
from neocaffeine.registry.registry_errors import RegistrySchemaError, UnitError


def test_empty_scalar_parses(scalar_template):
    """An entry with every field empty is valid for editing."""
    entry = parse_node("bounds.example", scalar_template)
    assert isinstance(entry, ScalarEntry)
    assert entry.value is None


def test_unknown_key_is_rejected(scalar_template):
    """Keys outside the schema raise RegistrySchemaError."""
    scalar_template["typo_field"] = None
    with pytest.raises(RegistrySchemaError):
        parse_node("bounds.example", scalar_template)


def test_text_in_value_is_rejected(scalar_template):
    """A value must be a number or not_reported."""
    scalar_template["value"] = "ten"
    with pytest.raises(RegistrySchemaError):
        parse_node("bounds.example", scalar_template)


def test_boolean_in_value_is_rejected(scalar_template):
    """true is not accepted as a number."""
    scalar_template["value"] = True
    with pytest.raises(RegistrySchemaError):
        parse_node("bounds.example", scalar_template)


def test_invalid_evidence_tier_is_rejected(scalar_template):
    """The evidence tier must be A, B or C."""
    scalar_template["evidence_tier"] = "D"
    with pytest.raises(RegistrySchemaError):
        parse_node("bounds.example", scalar_template)


def test_unknown_unit_is_rejected(scalar_template):
    """Units must be understood by pint."""
    scalar_template["unit"] = "not_a_unit"
    with pytest.raises(UnitError):
        parse_node("bounds.example", scalar_template)


@pytest.mark.parametrize("unit", ["dimensionless", "mg/L", "1/h", "L/h"])
def test_valid_units_are_accepted(scalar_template, unit):
    """Ordinary unit strings, including dimensionless, are accepted."""
    scalar_template["unit"] = unit
    assert parse_node("bounds.example", scalar_template).unit == unit


def test_not_reported_without_note_is_rejected(scalar_template):
    """not_reported must come with a note explaining why."""
    scalar_template["value"] = "not_reported"
    with pytest.raises(RegistrySchemaError):
        parse_node("bounds.example", scalar_template)


def test_not_reported_with_note_is_accepted(scalar_template):
    """not_reported with a note loads."""
    scalar_template.update(value="not_reported", not_reported_note="test fixture note")
    assert parse_node("bounds.example", scalar_template).value == "not_reported"


def test_choice_outside_options_is_rejected(scalar_template):
    """A choice entry only accepts the options the code implements."""
    scalar_template["value"] = "heaviest_weight"
    with pytest.raises(RegistrySchemaError):
        parse_node("dosing.dosing_weight_rule", scalar_template)


def test_choice_inside_options_is_accepted(scalar_template):
    """A listed option is accepted."""
    scalar_template["value"] = "birth_weight"
    assert isinstance(parse_node("dosing.dosing_weight_rule", scalar_template), ChoiceEntry)


def test_structural_entry_holds_only_meaning():
    """A structural entry holds entry_type and meaning only."""
    assert isinstance(parse_node("observation.example", {"entry_type": "structural", "meaning": None}), StructuralEntry)
    with pytest.raises(RegistrySchemaError):
        parse_node("observation.example", {"entry_type": "structural", "meaning": None, "evidence_tier": None})


def test_design_assumption_rejects_an_evidence_tier():
    """The tier of a design assumption is fixed at C and cannot be written."""
    with pytest.raises(RegistrySchemaError):
        parse_node("baseline.example", {"entry_type": "design_assumption", "evidence_tier": "A"})


def test_unknown_entry_type_is_rejected():
    """Only the structural and design_assumption entry types exist."""
    with pytest.raises(RegistrySchemaError):
        parse_node("baseline.example", {"entry_type": "guess"})
