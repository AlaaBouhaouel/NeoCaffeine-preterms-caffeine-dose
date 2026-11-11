# Purpose: Persistence helpers for creating and reading patient records; records are never deleted.

from __future__ import annotations

from uuid import UUID

from neocaffeine.patient.covariates import Covariates
from patients.models import PatientRecord


def create_patient_record(covariates: Covariates) -> PatientRecord:
    """Store the covariates of a new patient and return its record."""
    return PatientRecord.objects.create(
        patient_id=UUID(covariates.patient_id),
        gestational_age_days=covariates.gestational_age_days,
        birth_time=covariates.birth_time,
        birth_weight_grams=covariates.birth_weight_grams,
        sex=str(covariates.sex),
    )


def get_patient_record(patient_id: UUID) -> PatientRecord:
    """Return the record of one patient by its identifier."""
    return PatientRecord.objects.get(patient_id=patient_id)
