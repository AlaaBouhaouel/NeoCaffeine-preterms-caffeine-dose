# Named exceptions raised by the clock package.


class ClockError(ValueError):
    """Base class for every error raised by the clock package."""


class NaiveTimestampError(ClockError):
    """Raised when a timestamp carries no time zone."""


class NonUtcTimestampError(ClockError):
    """Raised when a timestamp is timezone-aware but not in UTC."""


class BeforeBirthError(ClockError):
    """Raised when a time falls before birth."""


class ClockMovedBackwardsError(ClockError):
    """Raised when a clock is asked to move to an earlier time."""


class UnknownTimezoneError(ClockError):
    """Raised when a display time-zone name is not a known IANA zone."""
