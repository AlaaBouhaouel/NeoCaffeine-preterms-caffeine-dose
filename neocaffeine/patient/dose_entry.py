# A caffeine dose given to the infant.

from dataclasses import dataclass, field

from neocaffeine.clock.time_axis import require_not_before_birth
from neocaffeine.patient.definitional_checks import require_member, require_number, require_positive
from neocaffeine.patient.log_entry import Correction, new_entry_id
from neocaffeine.patient.vocabularies import Route, SaltForm


@dataclass(frozen=True)
class DoseEntry:
    """A dose in mg/kg given at a time in hours since birth, with its route and salt form."""

    time_hours: float
    amount_mg_per_kg: float
    route: Route
    salt_form: SaltForm
    correction: Correction | None = None
    entry_id: str = field(default_factory=new_entry_id)

    def __post_init__(self) -> None:
        """Reject impossible times, amounts, routes and salt forms."""
        require_number("time_hours", self.time_hours)
        require_not_before_birth(self.time_hours)
        require_positive("amount_mg_per_kg", self.amount_mg_per_kg)
        require_member("route", self.route, Route)
        require_member("salt_form", self.salt_form, SaltForm)
