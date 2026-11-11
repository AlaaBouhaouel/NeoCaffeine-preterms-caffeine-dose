# Checks for values that are impossible by definition; each raises DefinitionalError.

from neocaffeine.patient.patient_errors import DefinitionalError, MissingCovariateError


def is_number(value: object) -> bool:
    """Return True for int or float values, excluding booleans."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def require_present(name: str, value: object) -> None:
    """Raise MissingCovariateError if a required value is empty."""
    if value is None:
        raise MissingCovariateError(f"{name} is required.")


def require_number(name: str, value: object) -> None:
    """Raise DefinitionalError if a value is not a number."""
    if not is_number(value):
        raise DefinitionalError(f"{name} must be a number, got {value!r}.")


def require_positive(name: str, value: object) -> None:
    """Raise DefinitionalError unless a value is a number greater than zero."""
    require_number(name, value)
    if value <= 0:
        raise DefinitionalError(f"{name} must be greater than zero, got {value}.")


def require_non_negative(name: str, value: object) -> None:
    """Raise DefinitionalError unless a value is a number of at least zero."""
    require_number(name, value)
    if value < 0:
        raise DefinitionalError(f"{name} must not be negative, got {value}.")


def require_between(name: str, value: object, lowest: float, highest: float) -> None:
    """Raise DefinitionalError unless a value lies within [lowest, highest]."""
    require_number(name, value)
    if not lowest <= value <= highest:
        raise DefinitionalError(f"{name} must lie between {lowest} and {highest}, got {value}.")


def require_count(name: str, value: object) -> None:
    """Raise DefinitionalError unless a value is a whole number of at least zero."""
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise DefinitionalError(f"{name} must be a whole number of at least zero, got {value!r}.")


def require_text(name: str, value: object) -> None:
    """Raise DefinitionalError unless a value is non-empty text."""
    if not isinstance(value, str) or not value.strip():
        raise DefinitionalError(f"{name} must be non-empty text, got {value!r}.")


def require_member(name: str, value: object, vocabulary: type) -> None:
    """Raise DefinitionalError unless a value belongs to the given enum."""
    if not isinstance(value, vocabulary):
        raise DefinitionalError(f"{name} must be a {vocabulary.__name__}, got {value!r}.")
