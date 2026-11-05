# Tests for the clock used by virtual infants.

import pytest

from neocaffeine.clock.clock import Clock
from neocaffeine.clock.clock_errors import BeforeBirthError, ClockMovedBackwardsError
from neocaffeine.clock.simulated_clock import SimulatedClock


def test_starts_at_given_hours():
    """The clock starts at the given hours since birth."""
    assert SimulatedClock(0.0).current_hours() == 0.0


def test_jumps_instantly_to_a_later_event():
    """The clock moves straight to any later time."""
    clock = SimulatedClock(0.0)
    clock.advance_to(720.0)
    assert clock.current_hours() == 720.0


def test_advance_to_current_time_is_no_op():
    """Advancing to the current time changes nothing."""
    clock = SimulatedClock(5.0)
    clock.advance_to(5.0)
    assert clock.current_hours() == 5.0


def test_moving_backwards_is_rejected():
    """Advancing to an earlier time raises ClockMovedBackwardsError."""
    clock = SimulatedClock(5.0)
    with pytest.raises(ClockMovedBackwardsError):
        clock.advance_to(4.0)


def test_negative_start_is_rejected():
    """A start before birth raises BeforeBirthError."""
    with pytest.raises(BeforeBirthError):
        SimulatedClock(-0.5)


def test_fits_clock_protocol():
    """SimulatedClock can be used wherever a Clock is expected."""
    clock: Clock = SimulatedClock(0.0)
    assert clock.current_hours() == 0.0
