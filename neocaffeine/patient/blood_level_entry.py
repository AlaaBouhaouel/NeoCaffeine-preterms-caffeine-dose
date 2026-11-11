# A measured blood caffeine level, possibly below the assay's detection limit.

from dataclasses import dataclass, field

from neocaffeine.clock.time_axis import require_not_before_birth
from neocaffeine.patient.definitional_checks import (
    require_member,
    require_non_negative,
    require_number,
    require_positive,
    require_text,
)
from neocaffeine.patient.log_entry import Correction, new_entry_id
from neocaffeine.patient.patient_errors import DefinitionalError
from neocaffeine.patient.vocabularies import SampleType


@dataclass(frozen=True)
class BloodLevelEntry:
    """A caffeine concentration in mg/L sampled at a time in hours since birth."""

    sampling_time_hours: float
    concentration_mg_per_l: float | None
    below_detection_limit: bool
    detection_limit_mg_per_l: float | None
    sample_type: SampleType
    measurement_method: str
    correction: Correction | None = None
    entry_id: str = field(default_factory=new_entry_id)

    def __post_init__(self) -> None:
        """Reject impossible values; a level below the detection limit carries no concentration."""
        require_number("sampling_time_hours", self.sampling_time_hours)
        require_not_before_birth(self.sampling_time_hours)
        if not isinstance(self.below_detection_limit, bool):
            raise DefinitionalError(f"below_detection_limit must be true or false, got {self.below_detection_limit!r}.")
        if self.below_detection_limit and self.concentration_mg_per_l is not None:
            raise DefinitionalError("A level below the detection limit must have no concentration value.")
        if not self.below_detection_limit:
            require_non_negative("concentration_mg_per_l", self.concentration_mg_per_l)
        if self.detection_limit_mg_per_l is not None:
            require_positive("detection_limit_mg_per_l", self.detection_limit_mg_per_l)
        require_member("sample_type", self.sample_type, SampleType)
        require_text("measurement_method", self.measurement_method)
