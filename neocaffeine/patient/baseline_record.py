# The pre-dose baseline apnea rate measured by the features layer, for one event-definition version.

from dataclasses import dataclass, field

from neocaffeine.patient.definitional_checks import require_count, require_non_negative, require_number, require_positive
from neocaffeine.patient.log_entry import Correction, new_entry_id


@dataclass(frozen=True)
class BaselineRecord:
    """Measured rate, valid hours, event count and maturity of the pre-dose window."""

    measured_rate_per_hour: float
    valid_hours: float
    event_count: int
    window_maturity_weeks: float
    standard_error_per_hour: float
    event_definition_version: float
    correction: Correction | None = None
    entry_id: str = field(default_factory=new_entry_id)

    def __post_init__(self) -> None:
        """Reject impossible rates, times, counts and versions."""
        require_non_negative("measured_rate_per_hour", self.measured_rate_per_hour)
        require_positive("valid_hours", self.valid_hours)
        require_count("event_count", self.event_count)
        require_number("window_maturity_weeks", self.window_maturity_weeks)
        require_non_negative("standard_error_per_hour", self.standard_error_per_hour)
        require_number("event_definition_version", self.event_definition_version)
