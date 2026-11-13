# Tests for conversion between UTC timestamps and hours since birth, hour bins, and 24 h observation days.

from datetime import datetime, timedelta, timezone

import pytest

from neocaffeine.clock.clock_errors import BeforeBirthError
from neocaffeine.clock.time_axis import (
    day_bounds,
    day_index,
    hour_bounds,
    hour_index,
    hours_since_birth,
    timestamp_from_hours,
)

BIRTH_TIME = datetime(2026, 1, 15, 8, 30, 0, tzinfo=timezone.utc)


def test_birth_is_hour_zero():
    """The birth time itself is zero hours since birth."""
    assert hours_since_birth(BIRTH_TIME, BIRTH_TIME) == 0.0


def test_hours_since_birth_is_exact_at_whole_hours():
    """Whole hours after birth convert to exact numbers."""
    assert hours_since_birth(BIRTH_TIME + timedelta(hours=3), BIRTH_TIME) == 3.0


def test_timestamp_before_birth_is_rejected():
    """A timestamp one second before birth raises BeforeBirthError."""
    with pytest.raises(BeforeBirthError):
        hours_since_birth(BIRTH_TIME - timedelta(seconds=1), BIRTH_TIME)


def test_round_trip_timestamp_to_hours_and_back():
    """Converting a whole-second timestamp to hours and back returns the same instant."""
    timestamp = BIRTH_TIME + timedelta(hours=50, minutes=17, seconds=43)
    hours = hours_since_birth(timestamp, BIRTH_TIME)
    assert timestamp_from_hours(hours, BIRTH_TIME) == timestamp


def test_timestamp_from_hours_rounds_to_nearest_second():
    """Floating-point error does not shift the result one second early."""
    assert timestamp_from_hours(0.1, BIRTH_TIME) == BIRTH_TIME + timedelta(seconds=360)


def test_timestamp_from_hours_returns_utc():
    """The result is in UTC."""
    assert timestamp_from_hours(1.0, BIRTH_TIME).tzinfo == timezone.utc


def test_timestamp_from_negative_hours_is_rejected():
    """Negative hours raise BeforeBirthError."""
    with pytest.raises(BeforeBirthError):
        timestamp_from_hours(-0.5, BIRTH_TIME)


def test_time_exactly_at_boundary_belongs_to_that_hour():
    """A time exactly at t = k belongs to hour k."""
    assert hour_index(3.0) == 3


def test_time_one_second_before_boundary_belongs_to_previous_hour():
    """One second before t = k belongs to hour k - 1."""
    hours = hours_since_birth(BIRTH_TIME + timedelta(hours=3) - timedelta(seconds=1), BIRTH_TIME)
    assert hour_index(hours) == 2


def test_first_hour_of_life_is_hour_zero():
    """Any time in the first hour of life is hour 0."""
    assert hour_index(0.0) == 0
    assert hour_index(0.999) == 0


def test_hour_index_rejects_negative_hours():
    """Negative hours raise BeforeBirthError."""
    with pytest.raises(BeforeBirthError):
        hour_index(-0.001)


def test_hour_bounds_are_half_open_interval():
    """Hour k spans k (included) to k + 1 (excluded)."""
    assert hour_bounds(4) == (4.0, 5.0)


def test_hour_bounds_rejects_negative_hour():
    """A negative hour index raises BeforeBirthError."""
    with pytest.raises(BeforeBirthError):
        hour_bounds(-1)


def test_first_24_hours_are_day_zero():
    """Any time in the first 24 hours of life is observation day 0."""
    assert day_index(0.0) == 0
    assert day_index(23.999) == 0


def test_time_exactly_at_day_boundary_belongs_to_that_day():
    """A time exactly at t = 24d belongs to day d."""
    assert day_index(24.0) == 1
    assert day_index(48.0) == 2


def test_day_index_rejects_negative_hours():
    """Negative hours raise BeforeBirthError."""
    with pytest.raises(BeforeBirthError):
        day_index(-0.001)


def test_day_bounds_are_half_open_24_hour_interval():
    """Day d spans 24d (included) to 24d + 24 (excluded)."""
    assert day_bounds(0) == (0.0, 24.0)
    assert day_bounds(2) == (48.0, 72.0)


def test_day_bounds_rejects_negative_day():
    """A negative day index raises BeforeBirthError."""
    with pytest.raises(BeforeBirthError):
        day_bounds(-1)
