# Dataclasses for registry entries: sources, populations, citations and every entry kind.

from dataclasses import dataclass
from typing import Any

NOT_REPORTED = "not_reported"
EVIDENCE_TIERS = frozenset({"A", "B", "C"})
DESIGN_ASSUMPTION_TIER = "C"

type RegistryValue = int | float | str | None


@dataclass(frozen=True)
class Citation:
    """One cited source, including the exact table, equation or page used."""

    authors: str | None
    year: int | None
    title: str | None
    journal_or_source: str | None
    location: str | None
    doi: str | None
    pmid: str | None
    url: str | None
    volume: str | None
    issue: str | None
    pages: str | None
    notes: str | None


@dataclass(frozen=True)
class PopulationLimit:
    """Minimum and maximum of one population dimension, with their unit."""

    minimum: int | float | None
    maximum: int | float | None
    unit: str | None


@dataclass(frozen=True)
class PopulationOfValidity:
    """The population a value was established in."""

    gestational_age: PopulationLimit
    postnatal_age: PopulationLimit
    weight: PopulationLimit


@dataclass(frozen=True)
class Symbol:
    """One symbol of a documented equation."""

    symbol: str | None
    meaning: str | None
    unit: str | None


@dataclass(frozen=True)
class Source:
    """Meaning, evidence tier, population, citations and conflicts shared by sourced entries."""

    meaning: str | None
    evidence_tier: str | None
    population: PopulationOfValidity
    citations: tuple[Citation, ...]
    conflicts_with: tuple[str, ...]
    conflict_note: str | None


@dataclass(frozen=True)
class ScalarEntry:
    """A single sourced value: a constant, threshold, prior or variability."""

    name: str
    value: RegistryValue
    unit: str | None
    source: Source
    not_reported_note: str | None


@dataclass(frozen=True)
class RangeEntry:
    """A sourced minimum and maximum: a bound or a validation range."""

    name: str
    minimum: RegistryValue
    maximum: RegistryValue
    unit: str | None
    source: Source
    not_reported_note: str | None


@dataclass(frozen=True)
class ChoiceEntry:
    """A sourced rule whose value is one of a fixed list of options."""

    name: str
    value: str | None
    options: tuple[str, ...]
    unit: str | None
    settings: dict[str, Any]
    source: Source


@dataclass(frozen=True)
class EntryGroup:
    """A named map of entries, such as models or per-model variabilities."""

    name: str
    entries: dict[str, Any]

    def children(self) -> dict[str, Any]:
        """Return the entries of the group by short name."""
        return dict(self.entries)


@dataclass(frozen=True)
class FormulaEntry:
    """A documented equation; the code implements it, the registry holds its coefficients."""

    name: str
    equation: str | None
    symbols: tuple[Symbol, ...]
    source: Source
    coefficients: EntryGroup | None

    def children(self) -> dict[str, Any]:
        """Return the coefficient group, if this formula has one."""
        return {} if self.coefficients is None else {"coefficients": self.coefficients}


@dataclass(frozen=True)
class DesignAssumptionEntry:
    """A modelling choice of NeoCaffeine, not a published value; tier fixed at C."""

    name: str
    equation: str | None
    symbols: tuple[Symbol, ...]
    meaning: str | None
    rationale: str | None
    citations: tuple[Citation, ...]

    @property
    def evidence_tier(self) -> str:
        """Return the fixed evidence tier of every design assumption."""
        return DESIGN_ASSUMPTION_TIER


@dataclass(frozen=True)
class StructuralEntry:
    """A structural rule of the system; needs a meaning only."""

    name: str
    meaning: str | None


@dataclass(frozen=True)
class EventDefinition:
    """The criteria of one event type, sourced as a whole."""

    name: str
    signal: str | None
    threshold: int | float | None
    threshold_unit: str | None
    min_duration: int | float | None
    max_duration: int | float | None
    duration_unit: str | None
    counts_toward_n: bool | None
    source: Source


@dataclass(frozen=True)
class FallbackEntry:
    """A population baseline rate and the maturity it was reported at, from one source."""

    name: str
    rate: RegistryValue
    rate_unit: str | None
    reported_maturity: RegistryValue
    reported_maturity_unit: str | None
    source: Source
    not_reported_note: str | None


@dataclass(frozen=True)
class ExclusionEntry:
    """A valid-time exclusion criterion that can be switched on or off."""

    name: str
    enabled: bool | None
    value: RegistryValue
    unit: str | None
    source: Source
    not_reported_note: str | None


def child_nodes(node: Any) -> dict[str, Any]:
    """Return the nested entries of a composite entry by short name, or an empty map."""
    children = getattr(node, "children", None)
    return children() if callable(children) else {}
