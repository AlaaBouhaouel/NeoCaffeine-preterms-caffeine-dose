# Purpose: Persistence helpers for reading and writing run snapshots.

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from django.db import transaction

from runs.models import RunSnapshot


def get_run_snapshot(run_id: UUID) -> RunSnapshot:
    return RunSnapshot.objects.get(run_id=run_id)


def create_run_snapshot(state_json: dict, delete_after: datetime) -> RunSnapshot:
    return RunSnapshot.objects.create(state_json=state_json, delete_after=delete_after)


@transaction.atomic
def save_run_state(run_id: UUID, state_version: int, state_json: dict) -> RunSnapshot:
    snapshot = get_run_snapshot(run_id)
    snapshot.state_version = state_version
    snapshot.state_json = state_json
    snapshot.save(update_fields=["state_version", "state_json", "updated_at"])
    return snapshot


def delete_runs_older_than(cutoff: datetime) -> int:
    deleted, _ = RunSnapshot.objects.filter(delete_after__lt=cutoff).delete()
    return deleted
