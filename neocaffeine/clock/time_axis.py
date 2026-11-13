# The model time axis: conversion between UTC timestamps and hours since birth, hour bins, and the 24 h observation days.

import math
from datetime import datetime, timedelta, timezone

from neocaffeine.clock.clock_errors import BeforeBirthError
from neocaffeine.clock.utc_check import require_utc

SECONDS_PER_HOUR = 3600
HOURS_PER_DAY = 24


def require_not_before_birth(hours: float) -> float:
    """Return hours unchanged, or raise BeforeBirthError if they are negative."""
    if hours < 0:
        raise BeforeBirthError(f"{hours} hours since birth is before birth.")
    return hours


def hours_since_birth(timestamp: datetime, birth_time: datetime) -> float:
    """Return the hours elapsed from birth to the timestamp, both UTC, at whole-second precision."""
    elapsed = require_utc(timestamp) - require_utc(birth_time)
    elapsed_seconds = elapsed // timedelta(seconds=1)
    if elapsed_seconds < 0:
        raise BeforeBirthError(f"Timestamp {timestamp.isoformat()} is before birth at {birth_time.isoformat()}.")
    return elapsed_seconds / SECONDS_PER_HOUR


def timestamp_from_hours(hours: float, birth_time: datetime) -> datetime:
    """Return the UTC timestamp at the given hours since birth, rounded to the nearest whole second."""
    require_not_before_birth(hours)
    elapsed = timedelta(seconds=round(hours * SECONDS_PER_HOUR))
    return (require_utc(birth_time) + elapsed).astimezone(timezone.utc)


def hour_index(hours: float) -> int:
    """Return k such that the time lies in hour k, the half-open interval [k, k + 1)."""
    return math.floor(require_not_before_birth(hours))


def hour_bounds(hour: int) -> tuple[float, float]:
    """Return the start (included) and end (excluded) of hour k, in hours since birth."""
    require_not_before_birth(hour)
    return float(hour), float(hour + 1)


def day_index(hours: float) -> int:
    """Return d such that the time lies in observation day d, the half-open interval [24d, 24d + 24)."""
    return math.floor(require_not_before_birth(hours) / HOURS_PER_DAY)


def day_bounds(day: int) -> tuple[float, float]:
    """Return the start (included) and end (excluded) of observation day d, in hours since birth."""
    require_not_before_birth(day)
    return float(day * HOURS_PER_DAY), float((day + 1) * HOURS_PER_DAY)
