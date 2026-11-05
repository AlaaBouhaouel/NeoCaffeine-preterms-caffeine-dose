# Purpose: Django app configuration for simulator pages and APIs.

from django.apps import AppConfig


class SimulatorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "simulator"
