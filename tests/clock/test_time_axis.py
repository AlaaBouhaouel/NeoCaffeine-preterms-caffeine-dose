# Tests for conversion between UTC timestamps and hours since birth, and hour bins.

from datetime import datetime, timedelta, timezone

import pytest

from neocaffeine.clock.clock_errors import BeforeBirthError
from neocaffeine.clock.time_axis import hour_bounds, hour_index, hours_since_birth, timestamp_from_hours

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
