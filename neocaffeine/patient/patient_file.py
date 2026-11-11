# Reading and writing one patient file, named <patient_id>.json.

import json
from pathlib import Path

from neocaffeine.patient.patient import Patient
from neocaffeine.patient.patient_errors import PatientFileError
from neocaffeine.patient.patient_serialization import patient_from_json, patient_to_json
from neocaffeine.patient.range_validation import ValidationRanges

PATIENT_FILE_SUFFIX = ".json"


def patient_file_path(directory: Path, patient_id: str) -> Path:
    """Return the path of a patient's file inside a directory."""
    return directory / f"{patient_id}{PATIENT_FILE_SUFFIX}"


def write_patient_file(patient: Patient, directory: Path) -> Path:
    """Write the patient to <patient_id>.json in the directory and return the file path."""
    path = patient_file_path(directory, patient.patient_id)
    path.write_text(json.dumps(patient_to_json(patient), indent=2), encoding="utf-8")
    return path


def read_patient_file(path: Path, validation_ranges: ValidationRanges) -> Patient:
    """Read a patient file and rebuild the patient, re-validating every entry."""
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise PatientFileError(f"Patient file not found: {path}") from error
    except json.JSONDecodeError as error:
        raise PatientFileError(f"Patient file {path} is not valid JSON: {error}") from error
    return patient_from_json(content, validation_ranges)
