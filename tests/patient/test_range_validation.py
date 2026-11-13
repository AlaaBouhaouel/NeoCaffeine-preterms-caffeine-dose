# Tests for flags raised against the registry validation ranges.

import pytest

from neocaffeine.patient.blood_level_entry import BloodLevelEntry
from neocaffeine.patient.covariates import Covariates
from neocaffeine.patient.dose_entry import DoseEntry
from neocaffeine.patient.daily_record import DailyRecord
from neocaffeine.patient.log_entry import Correction
from neocaffeine.patient.patient import Patient
from neocaffeine.patient.range_validation import ValidationRanges
from neocaffeine.patient.validation_flag import FlagKind
from neocaffeine.patient.vocabularies import Route, SaltForm, SampleType, Sex
from neocaffeine.patient.weight_entry import WeightEntry
from neocaffeine.registry.entry_parser import parse_node
from neocaffeine.registry.registry_errors import UnitError


def blood_level(time_hours, concentration, correction=None):
    """Return a measured blood level."""
    return BloodLevelEntry(
        sampling_time_hours=time_hours, concentration_mg_per_l=concentration, below_detection_limit=False,
        detection_limit_mg_per_l=None, sample_type=SampleType.PLASMA, measurement_method="test method",
        correction=correction,
    )


def test_empty_ranges_flag_range_unchecked_without_blocking(covariates, empty_ranges):
    """With an empty registry, entries are still added and flagged range_unchecked."""
    patient = Patient(covariates, empty_ranges)
    flags = patient.add_weight(WeightEntry(time_hours=1.0, weight_grams=1000))
    assert [flag.kind for flag in flags] == [FlagKind.RANGE_UNCHECKED]
    assert {flag.kind for flag in patient.validation_flags()} == {FlagKind.RANGE_UNCHECKED}
    assert patient.excluded_days() == frozenset()


def test_registry_ranges_are_usable_for_every_patient_field(registry_ranges):
    """Every validation range in the real registry has limits and a unit, so values are checked."""
    for range_name in ("gestational_age", "weight", "dose_amount", "blood_level",
                       "apnea_count", "bradycardia_count", "desaturation_count", "fio2"):
        assert registry_ranges.check(range_name, 0.5).checked


def test_value_inside_range_raises_no_flag(patient):
    """An in-range value is not flagged."""
    assert patient.add_blood_level(blood_level(10.0, 5.0)) == []


def test_out_of_range_observation_flags_and_excludes_its_day(patient):
    """An out-of-range blood level at 30.5 h flags observation day 1 and excludes that day."""
    flags = patient.add_blood_level(blood_level(30.5, 500.0))
    assert [(flag.kind, flag.day_index) for flag in flags] == [(FlagKind.OUT_OF_VALIDATION_RANGE, 1)]
    assert patient.excluded_days() == frozenset({1})


def test_corrected_observation_is_no_longer_excluded(patient):
    """Once an out-of-range level is corrected, its day is no longer excluded."""
    wrong = blood_level(30.5, 500.0)
    patient.add_blood_level(wrong)
    correction = Correction(supersedes=wrong.entry_id, recorded_at=patient.covariates.birth_time, reason="test")
    patient.add_blood_level(blood_level(30.5, 5.0, correction=correction))
    assert patient.excluded_days() == frozenset()
    assert len(patient.entry_flags(wrong.entry_id)) == 1


def test_out_of_range_dose_is_flagged_not_excluded(patient):
    """A dose outside its range is flagged but does not exclude a day."""
    flags = patient.add_dose(DoseEntry(time_hours=2.0, amount_mg_per_kg=500, route=Route.IV, salt_form=SaltForm.BASE))
    assert [flag.range_name for flag in flags] == ["dose_amount"]
    assert patient.excluded_days() == frozenset()


def test_each_event_count_has_its_own_range(covariates, filled_ranges):
    """Apnea, bradycardia and desaturation counts are checked against their own ranges."""
    ranges = dict(filled_ranges.ranges)
    ranges["bradycardia_count"] = parse_node(
        "validation_ranges.bradycardia_count", {"minimum": 0, "maximum": 2, "unit": "dimensionless"}
    )
    patient = Patient(covariates, ValidationRanges(ranges=ranges))
    record = DailyRecord(
        day_index=4, apnea_count=5, bradycardia_count=5, desaturation_count=5,
        valid_hours=24.0, quality_score=1.0, event_definition_version=1,
    )
    flags = patient.add_daily_record(record)
    assert [flag.range_name for flag in flags] == ["bradycardia_count"]
    assert patient.excluded_days() == frozenset({4})


def test_range_is_converted_to_the_field_unit(patient):
    """A weight range written in kg is compared with weights in grams."""
    assert patient.add_weight(WeightEntry(time_hours=1.0, weight_grams=2000)) == []
    assert len(patient.add_weight(WeightEntry(time_hours=2.0, weight_grams=20000))) == 1


def test_range_with_wrong_dimension_raises_a_registry_error(covariates, filled_ranges):
    """A range whose unit cannot convert to the field's unit is a registry problem."""
    ranges = dict(filled_ranges.ranges)
    ranges["weight"] = parse_node("validation_ranges.weight", {"minimum": 0, "maximum": 1, "unit": "mg/L"})
    with pytest.raises(UnitError):
        Patient(covariates, ValidationRanges(ranges=ranges))


def test_covariate_outside_range_is_flagged(filled_ranges, birth_time):
    """A covariate outside the model's validity is flagged, not rejected."""
    covariates = Covariates(gestational_age_days=50, birth_time=birth_time, birth_weight_grams=1000, sex=Sex.UNKNOWN)
    patient = Patient(covariates, filled_ranges)
    flags = patient.entry_flags(covariates.patient_id)
    assert [(flag.range_name, flag.kind) for flag in flags] == [("gestational_age", FlagKind.OUT_OF_VALIDATION_RANGE)]
