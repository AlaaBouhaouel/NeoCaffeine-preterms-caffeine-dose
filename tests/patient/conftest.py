# Shared fixtures for patient tests. Range limits here are arbitrary test placeholders, not physiological values.

from datetime import datetime, timezone

import pytest

from neocaffeine.patient.covariates import Covariates
from neocaffeine.patient.patient import Patient
from neocaffeine.patient.range_validation import ValidationRanges
from neocaffeine.patient.vocabularies import Sex
from neocaffeine.registry.entry_parser import parse_node
from neocaffeine.registry.loader import DEFAULT_DATA_DIRECTORY, load_registry

FIXTURE_BIRTH_TIME = datetime(2026, 1, 15, 8, 30, 0, tzinfo=timezone.utc)
FIXTURE_RANGES = {
    "gestational_age": (100, 300, "day"),
    "weight": (0.1, 10, "kg"),
    "dose_amount": (1, 50, "mg/kg"),
    "blood_level": (0, 100, "mg/L"),
    "apnea_count": (0, 100, "dimensionless"),
    "bradycardia_count": (0, 100, "dimensionless"),
    "desaturation_count": (0, 100, "dimensionless"),
    "fio2": (0.21, 1.0, "dimensionless"),
}


def fixture_range(name: str, minimum: float, maximum: float, unit: str):
    """Return a registry range entry holding test placeholder limits."""
    return parse_node(f"validation_ranges.{name}", {"minimum": minimum, "maximum": maximum, "unit": unit})


@pytest.fixture
def filled_ranges() -> ValidationRanges:
    """Return validation ranges filled with test placeholder limits."""
    return ValidationRanges(ranges={name: fixture_range(name, *limits) for name, limits in FIXTURE_RANGES.items()})


@pytest.fixture
def empty_ranges() -> ValidationRanges:
    """Return validation ranges with every range empty, as in an unfilled registry."""
    return ValidationRanges(ranges={})


@pytest.fixture
def registry_ranges() -> ValidationRanges:
    """Return the validation ranges of the real registry."""
    return ValidationRanges.from_registry(load_registry(DEFAULT_DATA_DIRECTORY))


@pytest.fixture
def covariates() -> Covariates:
    """Return covariates of a test infant."""
    return Covariates(gestational_age_days=200, birth_time=FIXTURE_BIRTH_TIME, birth_weight_grams=1000, sex=Sex.FEMALE)


@pytest.fixture
def patient(covariates, filled_ranges) -> Patient:
    """Return a test infant validated against the placeholder ranges."""
    return Patient(covariates, filled_ranges)


@pytest.fixture
def birth_time() -> datetime:
    """Return the birth time of the test infant."""
    return FIXTURE_BIRTH_TIME
