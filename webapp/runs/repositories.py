# Purpose: Persistence helpers for reading and writing run snapshots; runs are never deleted.

from __future__ import annotations

from typing import Any
from uuid import UUID

from django.db import transaction

from patients.models import PatientRecord
from runs.models import RunSnapshot


def get_run_snapshot(run_id: UUID) -> RunSnapshot:
    """Return the snapshot of one run by its identifier."""
    return RunSnapshot.objects.select_related("patient").get(run_id=run_id)


def create_run_snapshot(state_json: dict, patient: PatientRecord, patient_document: dict[str, Any]) -> RunSnapshot:
    """Store a new run for a patient, with the run's own patient document."""
    return RunSnapshot.objects.create(state_json=state_json, patient=patient, patient_document=patient_document)


@transaction.atomic
def save_run_state(run_id: UUID, state_version: int, state_json: dict) -> RunSnapshot:
    """Replace the state of a run and set its state version."""
    snapshot = get_run_snapshot(run_id)
    snapshot.state_version = state_version
    snapshot.state_json = state_json
    snapshot.save(update_fields=["state_version", "state_json", "updated_at"])
    return snapshot
