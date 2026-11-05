# The loaded registry: categories of entries, lookup by full name, model selection and version.

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from neocaffeine.registry.entry import DesignAssumptionEntry, EntryGroup, child_nodes
from neocaffeine.registry.pk_model import PkModel
from neocaffeine.registry.registry_errors import UnknownModelError


@dataclass(frozen=True)
class ModelSelection:
    """The PK, effect and baseline model names a run uses, from the run configuration."""

    pk_model: str
    effect_model: str
    baseline_model: str


class Registry:
    """Read-only view of every registry category, with its version."""

    def __init__(self, version: Any, date: Any, categories: dict[str, dict[str, Any]]) -> None:
        """Create the registry from its version, date and parsed categories."""
        self._version = version
        self._date = date
        self._categories = categories

    @property
    def version(self) -> Any:
        """Return the registry version, or None if empty."""
        return self._version

    @property
    def date(self) -> Any:
        """Return the registry date, or None if empty."""
        return self._date

    def category_names(self) -> list[str]:
        """Return the names of every category, in file order."""
        return list(self._categories)

    def category(self, name: str) -> dict[str, Any]:
        """Return the top-level entries and groups of one category by short name."""
        return dict(self._categories[name])

    def find(self, full_name: str) -> Any | None:
        """Return the entry or group with the given full name, or None if there is none."""
        category_name, _, rest = full_name.partition(".")
        if category_name not in self._categories:
            return None
        node: Any = EntryGroup(name=category_name, entries=self._categories[category_name])
        for part in rest.split(".") if rest else []:
            node = child_nodes(node).get(part)
            if node is None:
                return None
        return node

    def all_nodes(self) -> Iterator[Any]:
        """Yield every entry and group of every category, nested ones included."""
        pending = [node for category in self._categories.values() for node in category.values()]
        while pending:
            node = pending.pop(0)
            yield node
            pending.extend(child_nodes(node).values())

    def model(self, category_name: str, model_name: str) -> Any:
        """Return a model of a category's models section, or raise UnknownModelError."""
        models = self._categories.get(category_name, {}).get("models")
        model = None if models is None else child_nodes(models).get(model_name)
        if model is None:
            raise UnknownModelError(f"No model named {model_name!r} in {category_name}.models.")
        return model

    def pk_model(self, name: str) -> PkModel:
        """Return a PK model by name."""
        return self.model("pk_models", name)

    def effect_model(self, name: str) -> Any:
        """Return an effect model by name."""
        return self.model("effect", name)

    def baseline_model(self, name: str) -> Any:
        """Return a baseline model by name."""
        return self.model("baseline", name)

    def design_assumptions(self) -> list[DesignAssumptionEntry]:
        """Return every design assumption, so runs can report them as limitations."""
        return [node for node in self.all_nodes() if isinstance(node, DesignAssumptionEntry)]
