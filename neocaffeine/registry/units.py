# The shared pint unit registry and validation of unit strings.

import pint

from neocaffeine.registry.registry_errors import UnitError

unit_registry = pint.UnitRegistry()


def require_valid_unit(unit: object, location: str) -> str | None:
    """Return the unit string unchanged if empty or parseable by pint; raise UnitError otherwise."""
    if unit is None:
        return None
    if not isinstance(unit, str):
        raise UnitError(f"{location}: unit must be text, got {unit!r}.")
    try:
        unit_registry.parse_units(unit)
    except (pint.PintError, AttributeError, TypeError, ValueError, SyntaxError) as error:
        raise UnitError(f"{location}: unknown unit {unit!r}.") from error
    return unit
