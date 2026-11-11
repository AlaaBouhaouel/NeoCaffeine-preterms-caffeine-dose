# A measured weight of the infant.

from dataclasses import dataclass, field

from neocaffeine.clock.time_axis import require_not_before_birth
from neocaffeine.patient.definitional_checks import require_number, require_positive
from neocaffeine.patient.log_entry import Correction, new_entry_id


@dataclass(frozen=True)
class WeightEntry:
    """A weight in grams measured at a time in hours since birth."""

    time_hours: float
    weight_grams: float
    correction: Correction | None = None
    entry_id: str = field(default_factory=new_entry_id)

    def __post_init__(self) -> None:
        """Reject impossible times and weights."""
        require_number("time_hours", self.time_hours)
        require_not_before_birth(self.time_hours)
        require_positive("weight_grams", self.weight_grams)
