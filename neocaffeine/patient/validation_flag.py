# Flags raised when patient data is outside, or could not be checked against, the registry validation ranges.

from dataclasses import dataclass
from enum import StrEnum


class FlagKind(StrEnum):
    """Why an entry was flagged."""

    OUT_OF_VALIDATION_RANGE = "out_of_validation_range"
    RANGE_UNCHECKED = "range_unchecked"


@dataclass(frozen=True)
class ValidationFlag:
    """One flag on one entry: its kind, the range checked, the observation day it concerns, and a message."""

    entry_id: str
    kind: FlagKind
    range_name: str
    day_index: int | None
    message: str
