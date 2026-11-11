# patients

## Purpose
Persists one record per infant: the pseudonymous `patient_id` and the immutable covariates (gestational age, birth time, birth weight, sex). The covariates are shared by every run of the patient. Records are never deleted.

## Contents
- `models.py`: `PatientRecord`, table `patients`.
- `repositories.py`: create and read operations.
- `migrations/`: schema migrations.

## Inputs/Outputs
- Inputs: `Covariates` built by `neocaffeine.patient`.
- Outputs: persisted patient records, read by `patient_id`.

## Depends on
- Django ORM and the configured database (SQLite locally, PostgreSQL on Railway).
- `neocaffeine.patient.covariates`.

## Used by
- `backend/patient_bridge.py` and backend implementations when a run is created.
- `runs/models.py` (each run points to its patient).
