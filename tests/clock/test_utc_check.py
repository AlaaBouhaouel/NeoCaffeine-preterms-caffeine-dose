# Tests for the UTC timestamp check.

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from neocaffeine.clock.clock_errors import ClockError, NaiveTimestampError, NonUtcTimestampError
from neocaffeine.clock.utc_check import require_utc


def test_naive_timestamp_is_rejected():
    """A timestamp without a time zone raises NaiveTimestampError."""
    with pytest.raises(NaiveTimestampError):
        require_utc(datetime(2026, 1, 15, 8, 0, 0))


def test_non_utc_zone_is_rejected():
    """A timestamp in a non-UTC zone raises NonUtcTimestampError."""
    with pytest.raises(NonUtcTimestampError):
        require_utc(datetime(2026, 1, 15, 8, 0, 0, tzinfo=ZoneInfo("Asia/Riyadh")))


def test_zone_at_offset_zero_but_not_utc_is_rejected():
    """Europe/London in winter has offset zero but is still rejected."""
    with pytest.raises(NonUtcTimestampError):
        require_utc(datetime(2026, 1, 15, 8, 0, 0, tzinfo=ZoneInfo("Europe/London")))


def test_non_zero_fixed_offset_is_rejected():
    """A fixed non-zero offset is rejected."""
    with pytest.raises(NonUtcTimestampError):
        require_utc(datetime(2026, 1, 15, 8, 0, 0, tzinfo=timezone(timedelta(hours=3))))


@pytest.mark.parametrize("zone", [timezone.utc, ZoneInfo("UTC"), ZoneInfo("Etc/UTC")])
def test_utc_zones_are_accepted(zone):
    """Every accepted spelling of UTC passes."""
    timestamp = datetime(2026, 1, 15, 8, 0, 0, tzinfo=zone)
    assert require_utc(timestamp) == timestamp


def test_microseconds_are_truncated():
    """Sub-second precision is dropped, never rounded up."""
    timestamp = datetime(2026, 1, 15, 8, 0, 0, 999999, tzinfo=timezone.utc)
    assert require_utc(timestamp) == datetime(2026, 1, 15, 8, 0, 0, tzinfo=timezone.utc)


def test_clock_errors_are_value_errors():
    """Every clock error can be caught as ClockError and as ValueError."""
    assert issubclass(NaiveTimestampError, ClockError)
    assert issubclass(ClockError, ValueError)
