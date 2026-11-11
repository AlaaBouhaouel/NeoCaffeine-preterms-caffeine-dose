# Tests for patient-level views: weight carry-forward, ages and baseline records.

import pytest

from neocaffeine.patient.baseline_record import BaselineRecord
from neocaffeine.patient.patient_errors import DefinitionalError
from neocaffeine.patient.weight_entry import WeightEntry


def baseline(version, rate=1.0):
    """Return a baseline record of one event-definition version."""
    return BaselineRecord(
        measured_rate_per_hour=rate, valid_hours=6.0, event_count=6, window_maturity_weeks=30.0,
        standard_error_per_hour=0.4, event_definition_version=version,
    )


def test_weight_before_first_measurement_is_birth_weight(patient):
    """The weight log starts empty; birth weight applies until the first measurement."""
    assert patient.weights() == ()
    assert patient.weight_grams_at(10.0) == 1000


def test_weight_is_carried_forward(patient):
    """Between measurements the last value applies, with no interpolation."""
    patient.add_weight(WeightEntry(time_hours=24.0, weight_grams=1050))
    patient.add_weight(WeightEntry(time_hours=48.0, weight_grams=1100))
    assert patient.weight_grams_at(23.9) == 1000
    assert patient.weight_grams_at(24.0) == 1050
    assert patient.weight_grams_at(47.0) == 1050
    assert patient.weight_grams_at(100.0) == 1100


def test_ages_come_from_the_clock(patient):
    """Ages are derived from gestational age and hours since birth."""
    assert patient.day_of_life(30.0) == 2
    assert patient.postnatal_age_days(36.0) == 1.5
    assert patient.postmenstrual_age_days(48.0) == 202.0
    assert patient.postmenstrual_age_weeks(48.0) == pytest.approx(202.0 / 7)


def test_baseline_record_per_version(patient):
    """Each event-definition version has its own baseline record."""
    patient.add_baseline_record(baseline(1, rate=1.0))
    patient.add_baseline_record(baseline(2, rate=2.0))
    assert patient.baseline_record(1).measured_rate_per_hour == 1.0
    assert patient.baseline_record(2).measured_rate_per_hour == 2.0


def test_missing_baseline_window_is_reported(patient):
    """Without a baseline record, outputs must carry no_baseline_window."""
    assert not patient.has_baseline_window(1)
    patient.add_baseline_record(baseline(1))
    assert patient.has_baseline_window(1)


def test_entry_of_the_wrong_type_is_rejected(patient):
    """Each log accepts only its own entry type."""
    with pytest.raises(DefinitionalError):
        patient.add_dose(WeightEntry(time_hours=1.0, weight_grams=1000))
