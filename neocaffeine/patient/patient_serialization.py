# Conversion of a patient to and from a JSON-ready structure with a schema version.

import dataclasses
from datetime import datetime
from typing import Any

from neocaffeine.patient.covariates import Covariates
from neocaffeine.patient.log_entry import Correction
from neocaffeine.patient.patient import LOG_ENTRY_TYPES, Patient
from neocaffeine.patient.patient_errors import PatientFileError, UnsupportedSchemaVersionError
from neocaffeine.patient.range_validation import ValidationRanges
from neocaffeine.patient.vocabularies import EventType, Route, SaltForm, SampleType, Sex, SignalType, SupportMode

SCHEMA_VERSION = 2
HOURLY_SCHEMA_VERSION = 1
HOURLY_RECORDS_KEY = "hourly_records"
ENUM_FIELDS = {
    "sex": Sex,
    "route": Route,
    "salt_form": SaltForm,
    "sample_type": SampleType,
    "support_mode": SupportMode,
    "signal_type": SignalType,
    "event_type": EventType,
}
RECORDING_SEQUENCE_KEY = "recording_sequence"
CORRECTION_KEY = "correction"


def utc_text(timestamp: datetime) -> str:
    """Return a UTC timestamp as ISO 8601 text."""
    return timestamp.isoformat()


def utc_from_text(path: str, text: object) -> datetime:
    """Return the UTC timestamp written as ISO 8601 text."""
    if not isinstance(text, str):
        raise PatientFileError(f"{path}: expected an ISO 8601 timestamp, got {text!r}.")
    try:
        return datetime.fromisoformat(text)
    except ValueError as error:
        raise PatientFileError(f"{path}: invalid ISO 8601 timestamp {text!r}.") from error


def field_to_json(name: str, value: Any) -> Any:
    """Return one dataclass field value in its JSON form."""
    if isinstance(value, Correction):
        return {"supersedes": value.supersedes, "recorded_at": utc_text(value.recorded_at), "reason": value.reason}
    if isinstance(value, datetime):
        return utc_text(value)
    if name in ENUM_FIELDS and value is not None:
        return str(value)
    return value


def entry_to_json(entry: Any, recording_sequence: int) -> dict[str, Any]:
    """Return one log entry and its recording sequence as a JSON-ready map."""
    content = {field.name: field_to_json(field.name, getattr(entry, field.name)) for field in dataclasses.fields(entry)}
    content[RECORDING_SEQUENCE_KEY] = recording_sequence
    return content


def patient_to_json(patient: Patient) -> dict[str, Any]:
    """Return the whole patient, with every log entry and every flag, as a JSON-ready map."""
    covariates = patient.covariates
    content: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patient_id": covariates.patient_id,
        "covariates": {
            "gestational_age_days": covariates.gestational_age_days,
            "birth_time": utc_text(covariates.birth_time),
            "birth_weight_grams": covariates.birth_weight_grams,
            "sex": str(covariates.sex),
        },
    }
    for log_name in LOG_ENTRY_TYPES:
        content[log_name] = [
            entry_to_json(recorded.entry, recorded.recording_sequence)
            for recorded in patient.log(log_name).recorded_entries()
        ]
    content["validation_flags"] = [
        {**dataclasses.asdict(flag), "kind": str(flag.kind)} for flag in patient.validation_flags()
    ]
    return content


def require_map(path: str, raw: object) -> dict[str, Any]:
    """Return raw if it is a map, or raise PatientFileError."""
    if not isinstance(raw, dict):
        raise PatientFileError(f"{path}: expected a map, got {raw!r}.")
    return raw


def field_from_json(path: str, name: str, value: Any) -> Any:
    """Return one dataclass field value from its JSON form."""
    if name == CORRECTION_KEY and value is not None:
        correction = require_map(path, value)
        return Correction(
            supersedes=correction.get("supersedes"),
            recorded_at=utc_from_text(f"{path}.recorded_at", correction.get("recorded_at")),
            reason=correction.get("reason"),
        )
    if name in ENUM_FIELDS and value is not None:
        try:
            return ENUM_FIELDS[name](value)
        except ValueError as error:
            raise PatientFileError(f"{path}.{name}: unknown value {value!r}.") from error
    return value


def entry_from_json(path: str, entry_type: type, raw: object) -> tuple[Any, int]:
    """Return a log entry and its recording sequence from their JSON form."""
    content = dict(require_map(path, raw))
    recording_sequence = content.pop(RECORDING_SEQUENCE_KEY, None)
    if not isinstance(recording_sequence, int) or isinstance(recording_sequence, bool):
        raise PatientFileError(f"{path}.{RECORDING_SEQUENCE_KEY}: expected a whole number, got {recording_sequence!r}.")
    field_names = {field.name for field in dataclasses.fields(entry_type)}
    unknown = sorted(set(content) - field_names)
    if unknown:
        raise PatientFileError(f"{path}: unknown keys {unknown}.")
    try:
        entry = entry_type(**{name: field_from_json(path, name, value) for name, value in content.items()})
    except TypeError as error:
        raise PatientFileError(f"{path}: {error}") from error
    return entry, recording_sequence


def upgrade_hourly_schema(patient_content: dict[str, Any]) -> dict[str, Any]:
    """Return a schema-1 (hourly) patient as schema 2; only files without hourly records can be upgraded."""
    hourly_records = patient_content.get(HOURLY_RECORDS_KEY, [])
    if hourly_records:
        raise UnsupportedSchemaVersionError(
            "Patient schema version 1 holds hourly records; they cannot be converted to daily records."
        )
    upgraded = {key: value for key, value in patient_content.items() if key != HOURLY_RECORDS_KEY}
    upgraded["schema_version"] = SCHEMA_VERSION
    return upgraded


def patient_from_json(content: object, validation_ranges: ValidationRanges) -> Patient:
    """Rebuild a patient from its JSON form, re-validating every entry against the current ranges."""
    patient_content = require_map("patient", content)
    schema_version = patient_content.get("schema_version")
    if schema_version == HOURLY_SCHEMA_VERSION:
        patient_content = upgrade_hourly_schema(patient_content)
    elif schema_version != SCHEMA_VERSION:
        raise UnsupportedSchemaVersionError(f"Patient schema version {schema_version!r} is not {SCHEMA_VERSION}.")
    raw_covariates = require_map("covariates", patient_content.get("covariates"))
    covariates = Covariates(
        gestational_age_days=raw_covariates.get("gestational_age_days"),
        birth_time=utc_from_text("covariates.birth_time", raw_covariates.get("birth_time")),
        birth_weight_grams=raw_covariates.get("birth_weight_grams"),
        sex=field_from_json("covariates", "sex", raw_covariates.get("sex")),
        patient_id=patient_content.get("patient_id"),
    )
    patient = Patient(covariates, validation_ranges)
    saved_entries = []
    for log_name, entry_type in LOG_ENTRY_TYPES.items():
        raw_entries = patient_content.get(log_name, [])
        if not isinstance(raw_entries, list):
            raise PatientFileError(f"{log_name}: expected a list, got {raw_entries!r}.")
        for index, raw_entry in enumerate(raw_entries):
            entry, recording_sequence = entry_from_json(f"{log_name}[{index}]", entry_type, raw_entry)
            saved_entries.append((recording_sequence, log_name, entry))
    for recording_sequence, log_name, entry in sorted(saved_entries, key=lambda row: row[0]):
        patient.replay(log_name, entry, recording_sequence)
    return patient
