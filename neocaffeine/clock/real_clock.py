# Clock for real data: advanced by the runner to the latest timestamp available in the record.

from datetime import datetime

from neocaffeine.clock.clock_errors import ClockMovedBackwardsError
from neocaffeine.clock.time_axis import hours_since_birth, require_not_before_birth
from neocaffeine.clock.utc_check import require_utc


class RealClock:
    """Clock that follows real data timestamps, starting when the system starts for this infant."""

    def __init__(self, birth_time: datetime, start_hours: float) -> None:
        """Create the clock for an infant born at birth_time (UTC), starting at start_hours."""
        self._birth_time = require_utc(birth_time)
        self._current_hours = require_not_before_birth(start_hours)

    def current_hours(self) -> float:
        """Return the current time in hours since birth."""
        return self._current_hours

    def advance_to(self, hours: float) -> None:
        """Move the clock forward to the given hours since birth; the current time is a no-op."""
        if hours < self._current_hours:
            raise ClockMovedBackwardsError(f"Cannot move from {self._current_hours} to {hours} hours since birth.")
        self._current_hours = hours

    def advance_to_timestamp(self, timestamp: datetime) -> None:
        """Move the clock forward to a UTC timestamp."""
        self.advance_to(hours_since_birth(timestamp, self._birth_time))
