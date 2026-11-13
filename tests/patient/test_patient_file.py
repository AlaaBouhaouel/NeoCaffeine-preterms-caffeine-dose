# Tests for patient serialization to and from JSON files.

import json
from datetime import datetime, timezone

import pytest

from neocaffeine.patient.blood_level_entry import BloodLevelEntry
from neocaffeine.patient.context_entry import ContextEntry
from neocaffeine.patient.detected_event import DetectedEvent
from neocaffeine.patient.dose_entry import DoseEntry
from neocaffeine.patient.daily_record import DailyRecord
from neocaffeine.patient.log_entry import Correction
from neocaffeine.patient.patient_errors import PatientFileError, UnsupportedSchemaVersionError
from neocaffeine.patient.patient_file import read_patient_file, write_patient_file
from neocaffeine.patient.signal_reference import SignalReference
from neocaffeine.patient.vocabularies import EventType, Route, SaltForm, SampleType, SignalType, SupportMode
from neocaffeine.patient.weight_entry import WeightEntry


@pytest.fixture
def full_patient(patient):
    """Return a test patient with entries in every log, including a correction."""
    first_dose = DoseEntry(time_hours=1.0, amount_mg_per_kg=5, route=Route.IV, salt_form=SaltForm.CITRATE)
    patient.add_dose(first_dose)
    patient.add_weight(WeightEntry(time_hours=24.0, weight_grams=1050))
    patient.add_dose(DoseEntry(
        time_hours=1.0, amount_mg_per_kg=6, route=Route.IV, salt_form=SaltForm.CITRATE,
        correction=Correction(
            supersedes=first_dose.entry_id,
            recorded_at=datetime(2026, 2, 1, 12, 0, 0, tzinfo=timezone.utc),
            reason="test correction",
        ),
    ))
    patient.add_blood_level(BloodLevelEntry(
        sampling_time_hours=30.0, concentration_mg_per_l=None, below_detection_limit=True,
        detection_limit_mg_per_l=1.0, sample_type=SampleType.DRIED_BLOOD_SPOT, measurement_method="test method",
    ))
    patient.add_context(ContextEntry(time_hours=0.0, fio2_fraction=0.3, support_mode=SupportMode.CPAP))
    patient.add_signal_reference(SignalReference(
        file_path="data/test.edf", signal_type=SignalType.SPO2, start_hours=0.0, end_hours=48.0,
    ))
    patient.add_detected_event(DetectedEvent(
        onset_hours=2.5, duration_seconds=20, event_type=EventType.APNEA, event_definition_version=1,
    ))
    patient.add_daily_record(DailyRecord(
        day_index=2, apnea_count=1, bradycardia_count=0, desaturation_count=0,
        valid_hours=21.6, quality_score=0.8, event_definition_version=1,
    ))
    return patient


def test_round_trip_preserves_every_entry(full_patient, filled_ranges, tmp_path):
    """Writing and reading a patient gives back the same entries, corrections and recording order."""
    path = write_patient_file(full_patient, tmp_path)
    restored = read_patient_file(path, filled_ranges)
    assert restored.covariates == full_patient.covariates
    assert restored.recording_order() == full_patient.recording_order()
    assert restored.doses() == full_patient.doses()
    assert restored.blood_levels()[0].concentration_mg_per_l is None


def test_file_is_named_after_the_patient(full_patient, tmp_path):
    """One file per patient, named <patient_id>.json."""
    assert write_patient_file(full_patient, tmp_path).name == f"{full_patient.patient_id}.json"


def test_real_world_times_are_iso_and_event_times_are_hours(full_patient, tmp_path):
    """Birth time and correction times are ISO 8601 UTC; event times stay in hours since birth."""
    content = json.loads(write_patient_file(full_patient, tmp_path).read_text(encoding="utf-8"))
    assert content["schema_version"] == 2
    assert content["daily_records"][0]["day_index"] == 2
    assert content["covariates"]["birth_time"] == "2026-01-15T08:30:00+00:00"
    assert content["dose_log"][1]["correction"]["recorded_at"] == "2026-02-01T12:00:00+00:00"
    assert content["dose_log"][0]["time_hours"] == 1.0
    assert content["context_log"][0]["support_mode"] == "cpap"


def test_loading_re_validates_against_current_ranges(full_patient, empty_ranges, tmp_path):
    """Flags are recomputed on load from the ranges in use."""
    restored = read_patient_file(write_patient_file(full_patient, tmp_path), empty_ranges)
    assert restored.validation_flags()
    assert all(flag.kind == "range_unchecked" for flag in restored.validation_flags())


def test_hourly_schema_without_hourly_records_is_upgraded(full_patient, filled_ranges, tmp_path):
    """A schema-1 file whose hourly_records list is empty loads as schema 2."""
    path = write_patient_file(full_patient, tmp_path)
    content = json.loads(path.read_text(encoding="utf-8"))
    content["schema_version"] = 1
    content.pop("daily_records")
    content["hourly_records"] = []
    path.write_text(json.dumps(content), encoding="utf-8")
    restored = read_patient_file(path, filled_ranges)
    assert restored.covariates == full_patient.covariates
    assert restored.daily_records(1) == ()


def test_hourly_schema_with_hourly_records_is_rejected(full_patient, filled_ranges, tmp_path):
    """A schema-1 file holding hourly records cannot be read as daily records."""
    path = write_patient_file(full_patient, tmp_path)
    content = json.loads(path.read_text(encoding="utf-8"))
    content["schema_version"] = 1
    content.pop("daily_records")
    content["hourly_records"] = [{"hour_index": 2}]
    path.write_text(json.dumps(content), encoding="utf-8")
    with pytest.raises(UnsupportedSchemaVersionError):
        read_patient_file(path, filled_ranges)


def test_unknown_schema_version_is_rejected(full_patient, filled_ranges, tmp_path):
    """A file with another schema version is not read."""
    path = write_patient_file(full_patient, tmp_path)
    content = json.loads(path.read_text(encoding="utf-8"))
    content["schema_version"] = 99
    path.write_text(json.dumps(content), encoding="utf-8")
    with pytest.raises(UnsupportedSchemaVersionError):
        read_patient_file(path, filled_ranges)


def test_unknown_key_in_an_entry_is_rejected(full_patient, filled_ranges, tmp_path):
    """Entries in the file follow the entry schema exactly."""
    path = write_patient_file(full_patient, tmp_path)
    content = json.loads(path.read_text(encoding="utf-8"))
    content["weight_log"][0]["typo_field"] = 1
    path.write_text(json.dumps(content), encoding="utf-8")
    with pytest.raises(PatientFileError):
        read_patient_file(path, filled_ranges)


def test_missing_file_is_a_patient_file_error(filled_ranges, tmp_path):
    """Reading a file that does not exist raises PatientFileError."""
    with pytest.raises(PatientFileError):
        read_patient_file(tmp_path / "absent.json", filled_ranges)
