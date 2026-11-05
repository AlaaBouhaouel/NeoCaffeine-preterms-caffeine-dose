# Ages derived on demand from hours since birth: day of life, postnatal age, postmenstrual age.

import math

from neocaffeine.clock.time_axis import require_not_before_birth

HOURS_PER_DAY = 24
DAYS_PER_WEEK = 7


def day_of_life(hours: float) -> int:
    """Return the day of life, counting the first day as day 1."""
    return math.floor(require_not_before_birth(hours) / HOURS_PER_DAY) + 1


def postnatal_age_days(hours: float) -> float:
    """Return the continuous postnatal age in days."""
    return require_not_before_birth(hours) / HOURS_PER_DAY


def postmenstrual_age_days(gestational_age_days: float, hours: float) -> float:
    """Return the postmenstrual age in days: gestational age plus continuous postnatal age."""
    return gestational_age_days + postnatal_age_days(hours)


def postmenstrual_age_weeks(gestational_age_days: float, hours: float) -> float:
    """Return the postmenstrual age in weeks."""
    return postmenstrual_age_days(gestational_age_days, hours) / DAYS_PER_WEEK
