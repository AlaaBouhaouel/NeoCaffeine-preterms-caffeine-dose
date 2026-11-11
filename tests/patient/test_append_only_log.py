# Tests for append-only logs: chronology, duplicates, corrections and the current view.

from datetime import datetime, timezone

import pytest

from neocaffeine.patient.dose_entry import DoseEntry
from neocaffeine.patient.hourly_record import HourlyRecord
from neocaffeine.patient.log_entry import Correction
from neocaffeine.patient.patient_errors import (
    AlreadySupersededError,
    ChronologyError,
    DuplicateEntryIdError,
    DuplicateTimeError,
    UnknownEntryError,
)
from neocaffeine.patient.vocabularies import Route, SaltForm
from neocaffeine.patient.weight_entry import WeightEntry

CORRECTION_TIME = datetime(2026, 2, 1, 12, 0, 0, tzinfo=timezone.utc)


def dose(time_hours, amount=5.0, correction=None):
    """Return a dose entry."""
    return DoseEntry(
        time_hours=time_hours, amount_mg_per_kg=amount, route=Route.IV, salt_form=SaltForm.CITRATE, correction=correction
    )


def correction_of(entry):
    """Return a correction that supersedes the given entry."""
    return Correction(supersedes=entry.entry_id, recorded_at=CORRECTION_TIME, reason="test correction")


def hourly(hour, version, apneas=1):
    """Return an hourly record."""
    return HourlyRecord(
        hour_index=hour, apnea_count=apneas, bradycardia_count=0, desaturation_count=0,
        valid_hours=1.0, quality_score=1.0, event_definition_version=version,
    )


def test_entries_in_time_order_are_accepted(patient):
    """Original entries added in time order are kept in that order."""
    patient.add_dose(dose(1.0))
    patient.add_dose(dose(25.0))
    assert [entry.time_hours for entry in patient.doses()] == [1.0, 25.0]


def test_original_entry_earlier_than_the_latest_is_rejected(patient):
    """Event-time chronology is enforced on original entries."""
    patient.add_dose(dose(25.0))
    with pytest.raises(ChronologyError):
        patient.add_dose(dose(1.0))


def test_duplicate_time_within_one_log_is_rejected(patient):
    """Two current doses at the same time are an error."""
    patient.add_dose(dose(1.0))
    with pytest.raises(DuplicateTimeError):
        patient.add_dose(dose(1.0))


def test_same_time_across_logs_is_allowed(patient):
    """A dose and a weight may share a time."""
    patient.add_dose(dose(1.0))
    patient.add_weight(WeightEntry(time_hours=1.0, weight_grams=1000))


def test_correction_replaces_entry_in_current_view(patient):
    """The current view shows the correction instead of the original."""
    original = dose(1.0, amount=5.0)
    patient.add_dose(original)
    corrected = dose(1.0, amount=10.0, correction=correction_of(original))
    patient.add_dose(corrected)
    assert patient.doses() == (corrected,)


def test_original_is_kept_unchanged(patient):
    """The superseded original stays in the log, unchanged."""
    original = dose(1.0, amount=5.0)
    patient.add_dose(original)
    patient.add_dose(dose(1.0, amount=10.0, correction=correction_of(original)))
    assert patient.log("dose_log").all_entries()[0] is original
    assert original.amount_mg_per_kg == 5.0


def test_correction_may_carry_an_earlier_event_time(patient):
    """A correction of an old dose may be earlier than the latest entry."""
    first = dose(1.0)
    patient.add_dose(first)
    patient.add_dose(dose(25.0))
    patient.add_dose(dose(2.0, correction=correction_of(first)))
    assert [entry.time_hours for entry in patient.doses()] == [2.0, 25.0]


def test_correction_may_be_corrected(patient):
    """Corrections can form a chain."""
    original = dose(1.0, amount=5.0)
    patient.add_dose(original)
    first_correction = dose(1.0, amount=6.0, correction=correction_of(original))
    patient.add_dose(first_correction)
    second_correction = dose(1.0, amount=7.0, correction=correction_of(first_correction))
    patient.add_dose(second_correction)
    assert patient.doses() == (second_correction,)


def test_two_corrections_of_one_entry_are_rejected(patient):
    """An entry can be superseded only once."""
    original = dose(1.0)
    patient.add_dose(original)
    patient.add_dose(dose(1.0, amount=6.0, correction=correction_of(original)))
    with pytest.raises(AlreadySupersededError):
        patient.add_dose(dose(1.0, amount=7.0, correction=correction_of(original)))


def test_correction_of_unknown_entry_is_rejected(patient):
    """A correction must supersede an entry of the same log."""
    weight = WeightEntry(time_hours=1.0, weight_grams=1000)
    patient.add_weight(weight)
    with pytest.raises(UnknownEntryError):
        patient.add_dose(dose(1.0, correction=correction_of(weight)))


def test_correction_may_not_duplicate_another_current_entry(patient):
    """A correction moved onto the time of another current entry is a duplicate."""
    first = dose(1.0)
    patient.add_dose(first)
    patient.add_dose(dose(2.0))
    with pytest.raises(DuplicateTimeError):
        patient.add_dose(dose(2.0, correction=correction_of(first)))


def test_reused_entry_identifier_is_rejected(patient):
    """Entry identifiers are unique."""
    entry = dose(1.0)
    patient.add_dose(entry)
    with pytest.raises(DuplicateEntryIdError):
        patient.add_dose(entry)


def test_recording_sequence_is_strictly_increasing_across_logs(patient):
    """Every entry, in any log, gets the next recording sequence number."""
    patient.add_dose(dose(1.0))
    patient.add_weight(WeightEntry(time_hours=0.5, weight_grams=1000))
    patient.add_dose(dose(2.0))
    assert [row[0] for row in patient.recording_order()] == [1, 2, 3]
    assert patient.last_recording_sequence == 3


def test_new_definition_version_coexists_with_the_old(patient):
    """A reanalysis adds records under a new version, even for earlier hours."""
    patient.add_hourly_record(hourly(0, version=1))
    patient.add_hourly_record(hourly(1, version=1))
    patient.add_hourly_record(hourly(0, version=2, apneas=3))
    assert [record.hour_index for record in patient.hourly_records(1)] == [0, 1]
    assert [record.apnea_count for record in patient.hourly_records(2)] == [3]


def test_same_hour_twice_in_one_version_is_rejected(patient):
    """One record per hour and version."""
    patient.add_hourly_record(hourly(0, version=1))
    with pytest.raises(DuplicateTimeError):
        patient.add_hourly_record(hourly(0, version=1))
