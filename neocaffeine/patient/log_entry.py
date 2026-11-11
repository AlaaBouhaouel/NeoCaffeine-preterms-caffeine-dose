# The correction record and entry identifier shared by every patient log entry.

import uuid
from dataclasses import dataclass
from datetime import datetime

from neocaffeine.clock.utc_check import require_utc
from neocaffeine.patient.definitional_checks import require_text


def new_entry_id() -> str:
    """Return a new random identifier for a log entry."""
    return str(uuid.uuid4())


@dataclass(frozen=True)
class Correction:
    """Marks an entry as replacing an earlier one: which entry, when the correction was made, and why."""

    supersedes: str
    recorded_at: datetime
    reason: str

    def __post_init__(self) -> None:
        """Require the replaced entry, a UTC recording time and a reason."""
        require_text("supersedes", self.supersedes)
        require_text("reason", self.reason)
        object.__setattr__(self, "recorded_at", require_utc(self.recorded_at))
