# Purpose: Shared pytest fixtures for Django setup, database cleanup, and run bootstrap.

from __future__ import annotations

import os
import sys
import json
from pathlib import Path

import pytest


ROOT_DIR = Path(__file__).resolve().parents[2]
WEBAPP_DIR = ROOT_DIR / "webapp"
if str(WEBAPP_DIR) not in sys.path:
    sys.path.insert(0, str(WEBAPP_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "neocaffeine_web.settings.dev")

import django

django.setup()

from django.core.management import call_command
from django.test import Client

from runs.models import RunSnapshot


@pytest.fixture(scope="session", autouse=True)
def apply_migrations() -> None:
    call_command("migrate", verbosity=0)


@pytest.fixture(autouse=True)
def clean_runs() -> None:
    RunSnapshot.objects.all().delete()


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.fixture
def create_run_payload() -> dict:
    return {
        "patient": {
            "gestational_age_weeks": 28,
            "gestational_age_days_extra": 3,
            "birth_weight_g": 980,
            "sex": "male",
        },
        "initial_context": {
            "fiO2_fraction": 0.3,
            "breathing_support": "cpap",
            "monitoring_on": True,
        },
        "random_seed": 12345,
    }


@pytest.fixture
def created_run(client: Client, create_run_payload: dict) -> dict:
    response = client.post("/api/v1/runs", data=json.dumps(create_run_payload), content_type="application/json")
    assert response.status_code == 200
    return response.json()
