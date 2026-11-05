# Conversion of UTC timestamps to local time, for display only.

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from neocaffeine.clock.clock_errors import UnknownTimezoneError
from neocaffeine.clock.utc_check import require_utc


def to_local_time(timestamp: datetime, timezone_name: str) -> datetime:
    """Return the UTC timestamp expressed in the named IANA time zone."""
    try:
        zone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError) as error:
        raise UnknownTimezoneError(f"Unknown time zone name: {timezone_name!r}.") from error
    return require_utc(timestamp).astimezone(zone)
