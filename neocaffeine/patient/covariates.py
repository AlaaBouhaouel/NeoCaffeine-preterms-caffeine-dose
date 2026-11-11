# The immutable covariates of one infant, and the weeks-plus-days helper for gestational age.

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from neocaffeine.clock.utc_check import require_utc
from neocaffeine.patient.definitional_checks import require_member, require_positive, require_present
from neocaffeine.patient.patient_errors import DefinitionalError
from neocaffeine.patient.vocabularies import Sex

DAYS_PER_WEEK = 7


def gestational_age_days_from(weeks: int, days: int) -> int:
    """Return gestational age in days from completed weeks and extra days (0 to 6)."""
    if not isinstance(weeks, int) or isinstance(weeks, bool) or weeks < 0:
        raise DefinitionalError(f"weeks must be a whole number of at least zero, got {weeks!r}.")
    if not isinstance(days, int) or isinstance(days, bool) or not 0 <= days < DAYS_PER_WEEK:
        raise DefinitionalError(f"days must be a whole number from 0 to 6, got {days!r}.")
    return weeks * DAYS_PER_WEEK + days


def new_patient_id() -> str:
    """Return a new random pseudonymous patient identifier."""
    return str(uuid.uuid4())


@dataclass(frozen=True)
class Covariates:
    """Gestational age, birth time, birth weight and sex of one infant; fixed after creation."""

    gestational_age_days: float
    birth_time: datetime
    birth_weight_grams: float
    sex: Sex
    patient_id: str = field(default_factory=new_patient_id)

    def __post_init__(self) -> None:
        """Reject empty or impossible covariates and keep the birth time in UTC at whole seconds."""
        for name in ("gestational_age_days", "birth_time", "birth_weight_grams", "sex", "patient_id"):
            require_present(name, getattr(self, name))
        require_positive("gestational_age_days", self.gestational_age_days)
        require_positive("birth_weight_grams", self.birth_weight_grams)
        require_member("sex", self.sex, Sex)
        object.__setattr__(self, "birth_time", require_utc(self.birth_time))
