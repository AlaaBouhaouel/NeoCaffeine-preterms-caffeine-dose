# Tests for the immutable covariates and the weeks-plus-days helper.

import dataclasses
from datetime import datetime, timedelta, timezone

import pytest

from neocaffeine.clock.clock_errors import NaiveTimestampError, NonUtcTimestampError
from neocaffeine.patient.covariates import Covariates, gestational_age_days_from
from neocaffeine.patient.patient_errors import DefinitionalError, MissingCovariateError
from neocaffeine.patient.vocabularies import Sex


def make_covariates(**changes):
    """Return covariates of a test infant with some fields changed."""
    fields = dict(
        gestational_age_days=200,
        birth_time=datetime(2026, 1, 15, 8, 30, 0, tzinfo=timezone.utc),
        birth_weight_grams=1000,
        sex=Sex.MALE,
    )
    fields.update(changes)
    return Covariates(**fields)


def test_patient_id_is_a_new_random_identifier():
    """Each infant gets its own pseudonymous identifier."""
    assert make_covariates().patient_id != make_covariates().patient_id


@pytest.mark.parametrize("field", ["gestational_age_days", "birth_time", "birth_weight_grams", "sex"])
def test_every_covariate_is_required(field):
    """An empty covariate raises MissingCovariateError."""
    with pytest.raises(MissingCovariateError):
        make_covariates(**{field: None})


@pytest.mark.parametrize("field", ["gestational_age_days", "birth_weight_grams"])
@pytest.mark.parametrize("value", [0, -1])
def test_non_positive_values_are_definitional_errors(field, value):
    """A gestational age or birth weight of zero or less is impossible."""
    with pytest.raises(DefinitionalError):
        make_covariates(**{field: value})


def test_sex_must_be_from_the_vocabulary():
    """Sex must be a Sex value."""
    with pytest.raises(DefinitionalError):
        make_covariates(sex="other")


def test_birth_time_must_be_utc():
    """Birth time must be timezone-aware UTC."""
    with pytest.raises(NaiveTimestampError):
        make_covariates(birth_time=datetime(2026, 1, 15, 8, 30))
    with pytest.raises(NonUtcTimestampError):
        make_covariates(birth_time=datetime(2026, 1, 15, 8, 30, tzinfo=timezone(timedelta(hours=3))))


def test_covariates_cannot_be_changed():
    """Covariates are fixed after creation."""
    with pytest.raises(dataclasses.FrozenInstanceError):
        make_covariates().gestational_age_days = 210


def test_weeks_and_days_convert_to_days():
    """Completed weeks plus extra days give gestational age in days."""
    assert gestational_age_days_from(28, 3) == 199


@pytest.mark.parametrize("days", [7, -1])
def test_extra_days_must_be_0_to_6(days):
    """More than 6 extra days in a week is a definitional error."""
    with pytest.raises(DefinitionalError):
        gestational_age_days_from(28, days)
