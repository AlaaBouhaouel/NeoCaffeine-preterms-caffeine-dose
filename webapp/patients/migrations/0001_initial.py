# Purpose: Initial migration creating the patients table.

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PatientRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("patient_id", models.UUIDField(editable=False, unique=True)),
                ("gestational_age_days", models.FloatField()),
                ("birth_time", models.DateTimeField()),
                ("birth_weight_grams", models.FloatField()),
                ("sex", models.CharField(max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"db_table": "patients"},
        )
    ]
