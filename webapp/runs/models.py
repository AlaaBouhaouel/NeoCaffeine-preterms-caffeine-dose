# Purpose: Database models for persisted run snapshots and retention cutoff.

import uuid

from django.db import models


class RunSnapshot(models.Model):
    run_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    state_version = models.PositiveBigIntegerField(default=1)
    state_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delete_after = models.DateTimeField()

    class Meta:
        db_table = "run_snapshots"
