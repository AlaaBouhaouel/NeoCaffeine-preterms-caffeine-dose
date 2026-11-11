# Purpose: Database model for persisted run snapshots, each linked to its patient and holding that run's patient document.

import uuid

from django.db import models


class RunSnapshot(models.Model):
    run_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    patient = models.ForeignKey(
        "patients.PatientRecord",
        on_delete=models.PROTECT,
        related_name="runs",
        null=True,
    )
    patient_document = models.JSONField(null=True)
    state_version = models.PositiveBigIntegerField(default=1)
    state_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "run_snapshots"
