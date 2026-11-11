# A change in exogenous context: FiO2 and breathing support mode.

from dataclasses import dataclass, field

from neocaffeine.clock.time_axis import require_not_before_birth
from neocaffeine.patient.definitional_checks import require_between, require_member, require_number
from neocaffeine.patient.log_entry import Correction, new_entry_id
from neocaffeine.patient.vocabularies import SupportMode

MINIMUM_FIO2_FRACTION = 0.21
MAXIMUM_FIO2_FRACTION = 1.0


@dataclass(frozen=True)
class ContextEntry:
    """FiO2 and support mode in effect from a time in hours since birth until the next entry."""

    time_hours: float
    fio2_fraction: float
    support_mode: SupportMode
    correction: Correction | None = None
    entry_id: str = field(default_factory=new_entry_id)

    def __post_init__(self) -> None:
        """Reject impossible times, FiO2 fractions and support modes."""
        require_number("time_hours", self.time_hours)
        require_not_before_birth(self.time_hours)
        require_between("fio2_fraction", self.fio2_fraction, MINIMUM_FIO2_FRACTION, MAXIMUM_FIO2_FRACTION)
        require_member("support_mode", self.support_mode, SupportMode)
