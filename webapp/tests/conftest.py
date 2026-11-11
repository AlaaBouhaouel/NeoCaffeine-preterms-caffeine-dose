# Purpose: Shared pytest fixtures for webapp tests; pytest-django runs every test on a temporary test database, never on db.sqlite3.

from __future__ import annotations

import json

import pytest
from django.test import Client


BIRTH_TIME_UTC_TEXT = "2026-01-15T08:30:00+00:00"


@pytest.fixture(autouse=True)
def use_test_database(db) -> None:
    """Give every test access to the temporary test database."""


@pytest.fixture
def patient_payload() -> dict:
    """Return the patient part of a landing form submission."""
    return {
        "gestational_age_weeks": 28,
        "gestational_age_days_extra": 3,
        "birth_weight_g": 980,
        "sex": "male",
        "birth_time": BIRTH_TIME_UTC_TEXT,
    }


@pytest.fixture
def initial_context_payload() -> dict:
    """Return the initial care part of a landing form submission."""
    return {
        "fiO2_fraction": 0.3,
        "breathing_support": "cpap",
        "monitoring_on": True,
    }


@pytest.fixture
def create_run_payload(patient_payload: dict, initial_context_payload: dict) -> dict:
    """Return a full landing form submission."""
    return {
        "patient": patient_payload,
        "initial_context": initial_context_payload,
        "random_seed": 12345,
    }


@pytest.fixture
def created_run(client: Client, create_run_payload: dict) -> dict:
    """Create a run through the API and return its envelope."""
    response = client.post("/api/v1/runs", data=json.dumps(create_run_payload), content_type="application/json")
    assert response.status_code == 200
    return response.json()
