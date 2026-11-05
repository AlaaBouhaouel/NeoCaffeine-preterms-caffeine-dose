# Validation that a timestamp is timezone-aware UTC, truncated to whole seconds.

from datetime import datetime, timedelta, timezone, tzinfo
from zoneinfo import ZoneInfo

from neocaffeine.clock.clock_errors import NaiveTimestampError, NonUtcTimestampError

UTC_ZONE_NAMES = frozenset({"UTC", "Etc/UTC"})


def is_utc_zone(zone: tzinfo) -> bool:
    """Return True if the zone is UTC itself, not merely a zone at offset zero."""
    if isinstance(zone, timezone):
        return zone.utcoffset(None) == timedelta(0)
    if isinstance(zone, ZoneInfo):
        return zone.key in UTC_ZONE_NAMES
    return False


def require_utc(timestamp: datetime) -> datetime:
    """Return the timestamp truncated to whole seconds, or raise if it is naive or not UTC."""
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise NaiveTimestampError(f"Timestamp {timestamp.isoformat()} has no time zone; UTC is required.")
    if not is_utc_zone(timestamp.tzinfo):
        raise NonUtcTimestampError(f"Timestamp {timestamp.isoformat()} is in zone {timestamp.tzinfo}; UTC is required.")
    return timestamp.replace(microsecond=0)
