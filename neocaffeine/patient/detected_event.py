# One event detected by the features layer from raw signals.

from dataclasses import dataclass, field

from neocaffeine.clock.time_axis import require_not_before_birth
from neocaffeine.patient.definitional_checks import require_member, require_non_negative, require_number
from neocaffeine.patient.log_entry import Correction, new_entry_id
from neocaffeine.patient.vocabularies import EventType


@dataclass(frozen=True)
class DetectedEvent:
    """An apnea, bradycardia or desaturation: onset in hours since birth, duration in seconds."""

    onset_hours: float
    duration_seconds: float
    event_type: EventType
    event_definition_version: float
    correction: Correction | None = None
    entry_id: str = field(default_factory=new_entry_id)

    def __post_init__(self) -> None:
        """Reject impossible onsets, durations, types and versions."""
        require_number("onset_hours", self.onset_hours)
        require_not_before_birth(self.onset_hours)
        require_non_negative("duration_seconds", self.duration_seconds)
        require_member("event_type", self.event_type, EventType)
        require_number("event_definition_version", self.event_definition_version)
