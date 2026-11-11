# A reference to a raw signal file; the signal itself is never stored in the patient.

from dataclasses import dataclass, field

from neocaffeine.clock.time_axis import require_not_before_birth
from neocaffeine.patient.definitional_checks import require_member, require_number, require_text
from neocaffeine.patient.log_entry import Correction, new_entry_id
from neocaffeine.patient.patient_errors import DefinitionalError
from neocaffeine.patient.vocabularies import SignalType


@dataclass(frozen=True)
class SignalReference:
    """Where a raw signal lives, which signal it is, and the hours since birth it covers."""

    file_path: str
    signal_type: SignalType
    start_hours: float
    end_hours: float
    correction: Correction | None = None
    entry_id: str = field(default_factory=new_entry_id)

    def __post_init__(self) -> None:
        """Reject empty paths, unknown signal types and impossible time spans."""
        require_text("file_path", self.file_path)
        require_member("signal_type", self.signal_type, SignalType)
        require_number("start_hours", self.start_hours)
        require_number("end_hours", self.end_hours)
        require_not_before_birth(self.start_hours)
        if self.end_hours < self.start_hours:
            raise DefinitionalError(f"end_hours {self.end_hours} is before start_hours {self.start_hours}.")
