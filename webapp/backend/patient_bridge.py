# Purpose: Bridge between webapp payloads and the neocaffeine patient package: builds patients, documents and dashboard patient state.

from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

from neocaffeine.patient.context_entry import ContextEntry
from neocaffeine.patient.covariates import Covariates, gestational_age_days_from
from neocaffeine.patient.patient import Patient
from neocaffeine.patient.patient_serialization import patient_from_json, patient_to_json
from neocaffeine.patient.range_validation import ValidationRanges
from neocaffeine.patient.vocabularies import Sex, SupportMode
from neocaffeine.registry.loader import DEFAULT_DATA_DIRECTORY, load_registry

BIRTH_SIM_TIME_HOURS = 0.0


@lru_cache(maxsize=1)
def validation_ranges() -> ValidationRanges:
    """Return the registry validation ranges, loaded once per process."""
    return ValidationRanges.from_registry(load_registry(DEFAULT_DATA_DIRECTORY))


def birth_time_from_text(text: str) -> datetime | None:
    """Return an ISO 8601 timestamp with a time zone converted to UTC, or None if it is not one."""
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def build_patient(patient_payload: dict[str, Any], initial_context: dict[str, Any]) -> Patient:
    """Return a new patient from the landing form payload, with the initial context recorded at birth."""
    covariates = Covariates(
        gestational_age_days=gestational_age_days_from(
            patient_payload["gestational_age_weeks"], patient_payload["gestational_age_days_extra"]
        ),
        birth_time=birth_time_from_text(patient_payload["birth_time"]),
        birth_weight_grams=patient_payload["birth_weight_g"],
        sex=Sex(patient_payload["sex"]),
    )
    patient = Patient(covariates, validation_ranges())
    patient.add_context(ContextEntry(
        time_hours=BIRTH_SIM_TIME_HOURS,
        fio2_fraction=float(initial_context["fiO2_fraction"]),
        support_mode=SupportMode(initial_context["breathing_support"]),
    ))
    return patient


def patient_document(patient: Patient) -> dict[str, Any]:
    """Return the patient as its versioned JSON document."""
    return patient_to_json(patient)


def patient_from_document(document: dict[str, Any]) -> Patient:
    """Rebuild a patient from its stored JSON document, re-validating it against the current ranges."""
    return patient_from_json(document, validation_ranges())


def patient_state(patient: Patient, sim_time_hours: float) -> dict[str, Any]:
    """Return the dashboard `state.patient` section for a patient at a simulation time."""
    covariates = patient.covariates
    return {
        "patient_id": patient.patient_id,
        "covariates": {
            "gestational_age_days": covariates.gestational_age_days,
            "birth_time": covariates.birth_time.isoformat(),
            "birth_weight_g": covariates.birth_weight_grams,
            "sex": str(covariates.sex),
            "birth_sim_time_hours": BIRTH_SIM_TIME_HOURS,
        },
        "covariates_locked": True,
        "postnatal_age_hours": sim_time_hours,
        "postmenstrual_age_days": patient.postmenstrual_age_days(sim_time_hours),
        "weight_log": [
            {"t_sim_hours": entry.time_hours, "weight_g": entry.weight_grams} for entry in patient.weights()
        ],
        "current_weight_g": patient.weight_grams_at(sim_time_hours),
        "flags": [flag.message for flag in patient.validation_flags()],
    }
