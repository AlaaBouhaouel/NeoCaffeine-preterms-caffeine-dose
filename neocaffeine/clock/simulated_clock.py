# Clock for virtual infants: advances instantly from event to event on the hours axis.

from neocaffeine.clock.clock_errors import ClockMovedBackwardsError
from neocaffeine.clock.time_axis import require_not_before_birth


class SimulatedClock:
    """Clock that moves instantly to any later time, with no real timestamps."""

    def __init__(self, start_hours: float) -> None:
        """Create the clock at start_hours since birth."""
        self._current_hours = require_not_before_birth(start_hours)

    def current_hours(self) -> float:
        """Return the current time in hours since birth."""
        return self._current_hours

    def advance_to(self, hours: float) -> None:
        """Move the clock forward to the given hours since birth; the current time is a no-op."""
        if hours < self._current_hours:
            raise ClockMovedBackwardsError(f"Cannot move from {self._current_hours} to {hours} hours since birth.")
        self._current_hours = hours
