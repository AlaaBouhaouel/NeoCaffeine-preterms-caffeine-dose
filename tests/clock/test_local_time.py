# Tests for display conversion from UTC to local time.

from datetime import datetime, timezone

import pytest

from neocaffeine.clock.clock_errors import NaiveTimestampError, UnknownTimezoneError
from neocaffeine.clock.local_time import to_local_time


def test_utc_converts_to_named_zone():
    """12:00 UTC is 15:00 in Asia/Riyadh, the same instant."""
    timestamp = datetime(2026, 11, 5, 12, 0, 0, tzinfo=timezone.utc)
    local = to_local_time(timestamp, "Asia/Riyadh")
    assert (local.hour, local.minute) == (15, 0)
    assert local == timestamp


def test_unknown_zone_name_is_rejected():
    """An unknown zone name raises UnknownTimezoneError."""
    with pytest.raises(UnknownTimezoneError):
        to_local_time(datetime(2026, 11, 5, 12, 0, 0, tzinfo=timezone.utc), "Not/AZone")


def test_naive_timestamp_is_rejected():
    """Only UTC timestamps can be converted for display."""
    with pytest.raises(NaiveTimestampError):
        to_local_time(datetime(2026, 11, 5, 12, 0, 0), "Asia/Riyadh")
