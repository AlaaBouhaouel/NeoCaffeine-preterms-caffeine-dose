# Tests for the definitional checks of each log entry type.

import pytest

from neocaffeine.clock.clock_errors import BeforeBirthError
from neocaffeine.patient.blood_level_entry import BloodLevelEntry
from neocaffeine.patient.context_entry import ContextEntry
from neocaffeine.patient.detected_event import DetectedEvent
from neocaffeine.patient.dose_entry import DoseEntry
from neocaffeine.patient.daily_record import DailyRecord
from neocaffeine.patient.patient_errors import DefinitionalError
from neocaffeine.patient.signal_reference import SignalReference
from neocaffeine.patient.vocabularies import EventType, Route, SaltForm, SampleType, SignalType, SupportMode
from neocaffeine.patient.weight_entry import WeightEntry


def blood_level(**changes):
    """Return a blood level entry with some fields changed."""
    fields = dict(
        sampling_time_hours=10.0,
        concentration_mg_per_l=5.0,
        below_detection_limit=False,
        detection_limit_mg_per_l=None,
        sample_type=SampleType.SERUM,
        measurement_method="test method",
    )
    fields.update(changes)
    return BloodLevelEntry(**fields)


def daily_record(**changes):
    """Return a daily record with some fields changed."""
    fields = dict(
        day_index=3, apnea_count=2, bradycardia_count=1, desaturation_count=0,
        valid_hours=24.0, quality_score=0.5, event_definition_version=1,
    )
    fields.update(changes)
    return DailyRecord(**fields)


@pytest.mark.parametrize("weight", [0, -100])
def test_weight_must_be_positive(weight):
    """A weight of zero or less is impossible."""
    with pytest.raises(DefinitionalError):
        WeightEntry(time_hours=1.0, weight_grams=weight)


def test_entry_before_birth_is_rejected():
    """No entry may be timed before birth."""
    with pytest.raises(BeforeBirthError):
        WeightEntry(time_hours=-1.0, weight_grams=1000)


@pytest.mark.parametrize("amount", [0, -5])
def test_dose_must_be_positive(amount):
    """A dose of zero or less is impossible."""
    with pytest.raises(DefinitionalError):
        DoseEntry(time_hours=1.0, amount_mg_per_kg=amount, route=Route.IV, salt_form=SaltForm.CITRATE)


def test_dose_route_must_be_from_the_vocabulary():
    """Only listed routes are accepted."""
    with pytest.raises(DefinitionalError):
        DoseEntry(time_hours=1.0, amount_mg_per_kg=5, route="oral", salt_form=SaltForm.BASE)


@pytest.mark.parametrize("fio2", [0.21, 0.5, 1.0])
def test_fio2_within_definitional_range_is_accepted(fio2):
    """FiO2 from 0.21 to 1.0 is accepted."""
    assert ContextEntry(time_hours=1.0, fio2_fraction=fio2, support_mode=SupportMode.CPAP).fio2_fraction == fio2


@pytest.mark.parametrize("fio2", [0.2, 1.01, 0])
def test_fio2_outside_definitional_range_is_rejected(fio2):
    """FiO2 below 0.21 or above 1.0 is impossible."""
    with pytest.raises(DefinitionalError):
        ContextEntry(time_hours=1.0, fio2_fraction=fio2, support_mode=SupportMode.ROOM_AIR)


def test_level_below_detection_limit_has_no_value():
    """Below the detection limit, the concentration is empty and flagged."""
    entry = blood_level(concentration_mg_per_l=None, below_detection_limit=True, detection_limit_mg_per_l=1.0)
    assert entry.concentration_mg_per_l is None


def test_level_below_detection_limit_with_a_value_is_rejected():
    """A value and the below-limit flag contradict each other."""
    with pytest.raises(DefinitionalError):
        blood_level(below_detection_limit=True)


@pytest.mark.parametrize("changes", [
    {"concentration_mg_per_l": -1.0},
    {"concentration_mg_per_l": None},
    {"detection_limit_mg_per_l": 0},
    {"measurement_method": ""},
])
def test_impossible_blood_levels_are_rejected(changes):
    """Negative or missing concentrations, a zero detection limit and an empty method are rejected."""
    with pytest.raises(DefinitionalError):
        blood_level(**changes)


@pytest.mark.parametrize("changes", [
    {"valid_hours": 24.5},
    {"valid_hours": -0.1},
    {"quality_score": 1.1},
    {"apnea_count": -1},
    {"apnea_count": 1.5},
    {"day_index": 2.5},
])
def test_impossible_daily_records_are_rejected(changes):
    """Valid hours outside [0, 24], quality outside [0, 1], negative or fractional counts and fractional days are rejected."""
    with pytest.raises(DefinitionalError):
        daily_record(**changes)


def test_day_without_valid_time_produces_no_update():
    """A record with no valid time is stored but gives no update."""
    assert not daily_record(valid_hours=0.0).produces_update
    assert daily_record(valid_hours=12.5).produces_update


def test_full_day_of_valid_time_is_accepted():
    """All 24 hours of a day may be valid observation time."""
    assert daily_record(valid_hours=24.0).valid_hours == 24.0


def test_signal_end_before_start_is_rejected():
    """A signal cannot end before it starts."""
    with pytest.raises(DefinitionalError):
        SignalReference(file_path="test.edf", signal_type=SignalType.SPO2, start_hours=5.0, end_hours=4.0)


def test_negative_event_duration_is_rejected():
    """An event cannot last less than zero seconds."""
    with pytest.raises(DefinitionalError):
        DetectedEvent(onset_hours=1.0, duration_seconds=-1, event_type=EventType.APNEA, event_definition_version=1)
