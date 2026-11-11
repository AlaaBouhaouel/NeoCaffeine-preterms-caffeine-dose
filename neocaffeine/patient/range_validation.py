# Checks of patient values against the registry validation ranges, converted to each field's unit with pint.

from dataclasses import dataclass

import pint

from neocaffeine.registry.entry import NOT_REPORTED, RangeEntry
from neocaffeine.registry.registry import Registry
from neocaffeine.registry.registry_errors import UnitError
from neocaffeine.registry.units import unit_registry

FIELD_UNITS = {
    "gestational_age": "day",
    "weight": "gram",
    "dose_amount": "mg/kg",
    "blood_level": "mg/L",
    "apnea_count": "dimensionless",
    "bradycardia_count": "dimensionless",
    "desaturation_count": "dimensionless",
    "fio2": "dimensionless",
}
VALIDATION_RANGES_CATEGORY = "validation_ranges"


@dataclass(frozen=True)
class RangeCheck:
    """Result of one range check: whether it could run, and whether the value was inside."""

    checked: bool
    inside: bool


def limit_in_field_unit(range_entry: RangeEntry, limit: float, range_name: str) -> float:
    """Return a registry range limit converted to the unit of the patient field it applies to."""
    try:
        quantity = unit_registry.Quantity(limit, range_entry.unit)
        return quantity.to(FIELD_UNITS[range_name]).magnitude
    except pint.DimensionalityError as error:
        raise UnitError(
            f"{range_entry.name}: unit {range_entry.unit!r} cannot be converted to {FIELD_UNITS[range_name]!r}."
        ) from error


def is_usable(range_entry: RangeEntry | None) -> bool:
    """Return True if a range has both limits and a unit, and neither limit is not_reported."""
    if range_entry is None or range_entry.unit is None:
        return False
    limits = (range_entry.minimum, range_entry.maximum)
    return all(limit is not None and limit != NOT_REPORTED for limit in limits)


@dataclass(frozen=True)
class ValidationRanges:
    """The registry validation ranges the patient checks its data against."""

    ranges: dict[str, RangeEntry]

    @classmethod
    def from_registry(cls, registry: Registry) -> "ValidationRanges":
        """Build the validation ranges from a loaded registry."""
        category = registry.category(VALIDATION_RANGES_CATEGORY)
        return cls(ranges={name: entry for name, entry in category.items() if isinstance(entry, RangeEntry)})

    def check(self, range_name: str, value: float) -> RangeCheck:
        """Check a value, in its field's unit, against the named range; an empty range is not checked."""
        range_entry = self.ranges.get(range_name)
        if not is_usable(range_entry):
            return RangeCheck(checked=False, inside=False)
        minimum = limit_in_field_unit(range_entry, range_entry.minimum, range_name)
        maximum = limit_in_field_unit(range_entry, range_entry.maximum, range_name)
        return RangeCheck(checked=True, inside=minimum <= value <= maximum)
