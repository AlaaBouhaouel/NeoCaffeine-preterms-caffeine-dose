# Named exceptions raised by the parameter registry.


class RegistryError(Exception):
    """Base class for every error raised by the registry package."""


class RegistrySchemaError(RegistryError):
    """Raised when a registry file does not follow the entry schema."""


class UnitError(RegistryError):
    """Raised when a unit string cannot be parsed by pint."""


class UnknownModelError(RegistryError):
    """Raised when a selected model name has no entry in the registry."""


class IncompleteRegistryError(RegistryError):
    """Raised when entries required by a run are empty; lists every missing item."""

    def __init__(self, missing_items: list[str]) -> None:
        """Store every missing item and build a message listing all of them."""
        self.missing_items = list(missing_items)
        super().__init__(f"{len(self.missing_items)} required registry items are empty:\n" + "\n".join(self.missing_items))


class NotReportedValueError(RegistryError):
    """Raised when values required by a run are marked not_reported; lists every one."""

    def __init__(self, item_names: list[str]) -> None:
        """Store every not_reported item and build a message listing all of them."""
        self.item_names = list(item_names)
        super().__init__(
            f"{len(self.item_names)} required registry values are not_reported and need a value or fallback:\n"
            + "\n".join(self.item_names)
        )
