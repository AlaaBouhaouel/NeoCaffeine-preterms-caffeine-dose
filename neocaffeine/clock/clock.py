# The Clock protocol shared by the real and simulated clocks.

from typing import Protocol


class Clock(Protocol):
    """A clock on the model time axis, in hours since birth, that only moves forward."""

    def current_hours(self) -> float:
        """Return the current time in hours since birth."""
        ...

    def advance_to(self, hours: float) -> None:
        """Move the clock to the given hours since birth."""
        ...
