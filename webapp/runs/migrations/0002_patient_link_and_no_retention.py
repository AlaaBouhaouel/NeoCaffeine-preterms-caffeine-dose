# Purpose: Links each run to its patient, stores the run's patient document, and removes retention metadata.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("runs", "0001_initial"),
        ("patients", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="runsnapshot",
            name="patient",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="runs",
                to="patients.patientrecord",
            ),
        ),
        migrations.AddField(
            model_name="runsnapshot",
            name="patient_document",
            field=models.JSONField(null=True),
        ),
        migrations.RemoveField(
            model_name="runsnapshot",
            name="delete_after",
        ),
    ]
