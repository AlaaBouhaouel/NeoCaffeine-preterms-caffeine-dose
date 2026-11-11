# Purpose: Database model for one infant: its pseudonymous identifier and immutable covariates.

from django.db import models


class PatientRecord(models.Model):
    patient_id = models.UUIDField(unique=True, editable=False)
    gestational_age_days = models.FloatField()
    birth_time = models.DateTimeField()
    birth_weight_grams = models.FloatField()
    sex = models.CharField(max_length=16)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "patients"
