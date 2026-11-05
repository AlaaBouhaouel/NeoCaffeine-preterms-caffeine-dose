# Tests for the clock that follows real data timestamps.

from datetime import datetime, timedelta, timezone

import pytest

from neocaffeine.clock.clock import Clock
from neocaffeine.clock.clock_errors import BeforeBirthError, ClockMovedBackwardsError, NonUtcTimestampError
from neocaffeine.clock.real_clock import RealClock

BIRTH_TIME = datetime(2026, 1, 15, 8, 30, 0, tzinfo=timezone.utc)


def test_starts_at_given_hours():
    """The clock starts when the system starts for this infant."""
    assert RealClock(BIRTH_TIME, 12.0).current_hours() == 12.0


def test_advances_forward():
    """The clock moves to a later time."""
    clock = RealClock(BIRTH_TIME, 12.0)
    clock.advance_to(13.5)
    assert clock.current_hours() == 13.5


def test_advance_to_current_time_is_no_op():
    """Advancing to the current time changes nothing."""
    clock = RealClock(BIRTH_TIME, 12.0)
    clock.advance_to(12.0)
    assert clock.current_hours() == 12.0


def test_moving_backwards_is_rejected():
    """Advancing to an earlier time raises ClockMovedBackwardsError."""
    clock = RealClock(BIRTH_TIME, 12.0)
    with pytest.raises(ClockMovedBackwardsError):
        clock.advance_to(11.0)


def test_advance_to_timestamp_converts_to_hours():
    """A UTC timestamp advances the clock to its hours since birth."""
    clock = RealClock(BIRTH_TIME, 0.0)
    clock.advance_to_timestamp(BIRTH_TIME + timedelta(hours=30))
    assert clock.current_hours() == 30.0


def test_negative_start_is_rejected():
    """A start before birth raises BeforeBirthError."""
    with pytest.raises(BeforeBirthError):
        RealClock(BIRTH_TIME, -1.0)


def test_non_utc_birth_time_is_rejected():
    """The birth time must be UTC."""
    with pytest.raises(NonUtcTimestampError):
        RealClock(BIRTH_TIME.astimezone(timezone(timedelta(hours=3))), 0.0)


def test_fits_clock_protocol():
    """RealClock can be used wherever a Clock is expected."""
    clock: Clock = RealClock(BIRTH_TIME, 0.0)
    assert clock.current_hours() == 0.0
