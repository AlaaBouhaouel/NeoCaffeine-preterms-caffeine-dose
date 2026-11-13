# The daily summary produced by the features layer for one 24 h observation day and one event-definition version.

from dataclasses import dataclass, field

from neocaffeine.clock.time_axis import HOURS_PER_DAY, require_not_before_birth
from neocaffeine.patient.definitional_checks import require_between, require_count, require_number
from neocaffeine.patient.log_entry import Correction, new_entry_id

MINIMUM_FRACTION = 0.0
MAXIMUM_FRACTION = 1.0
MINIMUM_VALID_HOURS = 0.0
MAXIMUM_VALID_HOURS = float(HOURS_PER_DAY)


@dataclass(frozen=True)
class DailyRecord:
    """Event counts, valid observation time and data quality of observation day d, the interval [24d, 24d + 24)."""

    day_index: int
    apnea_count: int
    bradycardia_count: int
    desaturation_count: int
    valid_hours: float
    quality_score: float
    event_definition_version: float
    correction: Correction | None = None
    entry_id: str = field(default_factory=new_entry_id)

    def __post_init__(self) -> None:
        """Reject impossible days, counts, valid times, quality scores and versions."""
        require_count("day_index", self.day_index)
        require_not_before_birth(self.day_index)
        for name in ("apnea_count", "bradycardia_count", "desaturation_count"):
            require_count(name, getattr(self, name))
        require_between("valid_hours", self.valid_hours, MINIMUM_VALID_HOURS, MAXIMUM_VALID_HOURS)
        require_between("quality_score", self.quality_score, MINIMUM_FRACTION, MAXIMUM_FRACTION)
        require_number("event_definition_version", self.event_definition_version)

    @property
    def produces_update(self) -> bool:
        """Return False when the day has no valid observation time."""
        return self.valid_hours > 0
