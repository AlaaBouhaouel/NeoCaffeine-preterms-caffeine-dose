# runs

## Purpose
Persists simulation run snapshots with state versioning. Each run points to its patient and holds its own patient document (covariates plus that run's logs), so runs of the same patient never mix. Runs are never deleted.

## Contents
- `models.py`: `RunSnapshot`, table `run_snapshots` (run_id, patient, patient_document, state_version, state_json, timestamps).
- `repositories.py`: create, read and save-state operations.
- `migrations/`: schema migrations.

## Inputs/Outputs
- Inputs: run IDs, patient records, patient documents (`neocaffeine.patient` JSON format), state versions and full state JSON objects.
- Outputs: persisted snapshots.

## Depends on
- Django ORM and the configured database (SQLite locally, PostgreSQL on Railway).
- `patients` app.

## Used by
- Backend implementations, the backend runtime, and API action handlers.
