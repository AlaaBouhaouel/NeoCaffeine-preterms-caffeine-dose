# Tests for ages derived from hours since birth.

import pytest

from neocaffeine.clock.ages import day_of_life, postmenstrual_age_days, postmenstrual_age_weeks, postnatal_age_days
from neocaffeine.clock.clock_errors import BeforeBirthError


def test_first_day_of_life_is_day_one():
    """Birth and the end of the first 24 hours are both day 1."""
    assert day_of_life(0.0) == 1
    assert day_of_life(23.999) == 1


def test_day_of_life_changes_at_24_hours():
    """Exactly 24 hours after birth is day 2."""
    assert day_of_life(24.0) == 2


def test_postnatal_age_is_continuous():
    """Postnatal age in days is hours divided by 24, not rounded."""
    assert postnatal_age_days(36.0) == 1.5


def test_postmenstrual_age_days_adds_postnatal_age():
    """Postmenstrual age in days is gestational age plus continuous postnatal age."""
    assert postmenstrual_age_days(200.0, 48.0) == 202.0


def test_postmenstrual_age_weeks_divides_by_seven():
    """Postmenstrual age in weeks is the age in days divided by 7."""
    assert postmenstrual_age_weeks(200.0, 48.0) == pytest.approx(202.0 / 7)


@pytest.mark.parametrize(
    "age_function",
    [day_of_life, postnatal_age_days, lambda hours: postmenstrual_age_days(200.0, hours), lambda hours: postmenstrual_age_weeks(200.0, hours)],
)
def test_every_age_rejects_times_before_birth(age_function):
    """Every age helper raises BeforeBirthError for negative hours."""
    with pytest.raises(BeforeBirthError):
        age_function(-1.0)
