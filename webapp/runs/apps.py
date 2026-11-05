# Purpose: Django app configuration for persisted simulation runs.

from django.apps import AppConfig


class RunsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "runs"
