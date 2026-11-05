# Completeness check: lists every empty item of the entries a run requires, and refuses incomplete registries.

from typing import Any

from neocaffeine.registry.entry import (
    NOT_REPORTED,
    ChoiceEntry,
    Citation,
    DesignAssumptionEntry,
    EntryGroup,
    EventDefinition,
    ExclusionEntry,
    FallbackEntry,
    FormulaEntry,
    PopulationOfValidity,
    RangeEntry,
    ScalarEntry,
    Source,
    StructuralEntry,
    Symbol,
    child_nodes,
)
from neocaffeine.registry.pk_model import PkModel
from neocaffeine.registry.registry import ModelSelection, Registry
from neocaffeine.registry.registry_errors import IncompleteRegistryError, NotReportedValueError

MODELS_GROUP_NAME = "models"
SELECTED_MODEL_ATTRIBUTE = {
    "pk_models": "pk_model",
    "effect": "effect_model",
    "baseline": "baseline_model",
}
PER_PK_MODEL_GROUPS = (
    ("priors", "clearance_variability"),
    ("priors", "volume_variability"),
)
CONDITIONAL_SETTINGS = {
    "events.event_overlap_rule": {"merge_within_window": ("merge_window", "merge_window_unit")},
}
REQUIRED_CITATION_FIELDS = ("authors", "year", "title", "journal_or_source", "location")
CITATION_IDENTIFIERS = ("doi", "pmid", "url")


def empty_fields(path: str, record: Any, field_names: tuple[str, ...]) -> list[str]:
    """Return one missing item per empty field of a record."""
    return [f"{path}.{name}: empty" for name in field_names if getattr(record, name) is None]


def missing_citation_items(path: str, citation: Citation) -> list[str]:
    """Return the missing required fields of one citation, including its identifier."""
    missing = empty_fields(path, citation, REQUIRED_CITATION_FIELDS)
    if all(getattr(citation, name) is None for name in CITATION_IDENTIFIERS):
        missing.append(f"{path}.doi|pmid|url: empty, at least one is required")
    return missing


def missing_citations_items(path: str, citations: tuple[Citation, ...]) -> list[str]:
    """Return the missing items of a citation list; at least one citation is required."""
    if not citations:
        return [f"{path}.citations: empty"]
    return [
        item
        for index, citation in enumerate(citations)
        for item in missing_citation_items(f"{path}.citations[{index}]", citation)
    ]


def missing_population_items(path: str, population: PopulationOfValidity) -> list[str]:
    """Return the empty limits and units of a population of validity."""
    return [
        f"{path}.population.{dimension}.{yaml_key}: empty"
        for dimension in ("gestational_age", "postnatal_age", "weight")
        for attribute, yaml_key in (("minimum", "min"), ("maximum", "max"), ("unit", "unit"))
        if getattr(getattr(population, dimension), attribute) is None
    ]


def missing_source_items(path: str, source: Source) -> list[str]:
    """Return the missing meaning, tier, population, citations and conflict note of a sourced entry."""
    missing = empty_fields(path, source, ("meaning", "evidence_tier"))
    missing += missing_population_items(path, source.population)
    missing += missing_citations_items(path, source.citations)
    if source.conflicts_with and source.conflict_note is None:
        missing.append(f"{path}.conflict_note: empty, required when conflicts_with is filled")
    return missing


def missing_symbols_items(path: str, symbols: tuple[Symbol, ...]) -> list[str]:
    """Return the missing items of an equation's symbol definitions."""
    if not symbols:
        return [f"{path}.symbols: empty"]
    return [
        item
        for index, symbol in enumerate(symbols)
        for item in empty_fields(f"{path}.symbols[{index}]", symbol, ("symbol", "meaning", "unit"))
    ]


def missing_choice_settings(entry: ChoiceEntry) -> list[str]:
    """Return the empty settings that the chosen option of a choice entry requires."""
    required_settings = CONDITIONAL_SETTINGS.get(entry.name, {}).get(entry.value, ())
    return [f"{entry.name}.{key}: empty, required by {entry.value!r}" for key in required_settings if entry.settings.get(key) is None]


def missing_items(entry: Any) -> list[str]:
    """Return every empty required item of an entry or group, nested entries included."""
    if isinstance(entry, EntryGroup):
        if not entry.entries:
            return [f"{entry.name}: empty"]
        return [item for child in entry.entries.values() for item in missing_items(child)]
    if isinstance(entry, ScalarEntry):
        return empty_fields(entry.name, entry, ("value", "unit")) + missing_source_items(entry.name, entry.source)
    if isinstance(entry, RangeEntry):
        return empty_fields(entry.name, entry, ("minimum", "maximum", "unit")) + missing_source_items(entry.name, entry.source)
    if isinstance(entry, ChoiceEntry):
        return (
            empty_fields(entry.name, entry, ("value", "unit"))
            + missing_choice_settings(entry)
            + missing_source_items(entry.name, entry.source)
        )
    if isinstance(entry, FormulaEntry):
        missing = empty_fields(entry.name, entry, ("equation",)) + missing_symbols_items(entry.name, entry.symbols)
        missing += missing_source_items(entry.name, entry.source)
        if entry.coefficients is not None:
            missing += missing_items(entry.coefficients)
        return missing
    if isinstance(entry, DesignAssumptionEntry):
        return (
            empty_fields(entry.name, entry, ("equation", "meaning", "rationale"))
            + missing_symbols_items(entry.name, entry.symbols)
            + missing_citations_items(entry.name, entry.citations)
        )
    if isinstance(entry, StructuralEntry):
        return empty_fields(entry.name, entry, ("meaning",))
    if isinstance(entry, EventDefinition):
        fields = ("signal", "threshold", "threshold_unit", "min_duration", "max_duration", "duration_unit")
        missing = empty_fields(entry.name, entry, fields)
        if entry.counts_toward_n is None:
            missing.append(f"{entry.name}.counts_toward_N: empty")
        return missing + missing_source_items(entry.name, entry.source)
    if isinstance(entry, FallbackEntry):
        fields = ("rate", "rate_unit", "reported_maturity", "reported_maturity_unit")
        return empty_fields(entry.name, entry, fields) + missing_source_items(entry.name, entry.source)
    if isinstance(entry, ExclusionEntry):
        return empty_fields(entry.name, entry, ("enabled", "value", "unit")) + missing_source_items(entry.name, entry.source)
    if isinstance(entry, PkModel):
        missing = empty_fields(entry.name, entry, ("structure",)) + missing_source_items(entry.name, entry.source)
        return missing + [item for child in entry.children().values() for item in missing_items(child)]
    raise TypeError(f"Unknown registry entry kind: {type(entry).__name__}")


def not_reported_items(entry: Any) -> list[str]:
    """Return the full names of every value marked not_reported in an entry, nested entries included."""
    value_fields = {
        ScalarEntry: ("value",),
        RangeEntry: ("minimum", "maximum"),
        FallbackEntry: ("rate", "reported_maturity"),
        ExclusionEntry: ("value",),
    }.get(type(entry), ())
    marked = [f"{entry.name}.{name}" for name in value_fields if getattr(entry, name) == NOT_REPORTED]
    return marked + [item for child in child_nodes(entry).values() for item in not_reported_items(child)]


def required_entry_names(registry: Registry, selection: ModelSelection) -> list[str]:
    """Return the full names of the entries and groups a run with this model selection requires."""
    selected_pk_model = selection.pk_model
    names = []
    for category_name in registry.category_names():
        for entry_name in registry.category(category_name):
            if entry_name == MODELS_GROUP_NAME and category_name in SELECTED_MODEL_ATTRIBUTE:
                model_name = getattr(selection, SELECTED_MODEL_ATTRIBUTE[category_name])
                registry.model(category_name, model_name)
                names.append(f"{category_name}.{MODELS_GROUP_NAME}.{model_name}")
            elif (category_name, entry_name) in PER_PK_MODEL_GROUPS:
                names.append(f"{category_name}.{entry_name}.{selected_pk_model}")
            else:
                names.append(f"{category_name}.{entry_name}")
    return names


def missing_meta_items(registry: Registry) -> list[str]:
    """Return the empty fields of the registry version file."""
    return [f"registry_meta.{name}: empty" for name in ("version", "date") if getattr(registry, name) is None]


def require_complete(registry: Registry, selection: ModelSelection) -> None:
    """Raise if any entry this run requires is empty or not_reported, listing every one at once."""
    required_names = required_entry_names(registry, selection)
    missing = missing_meta_items(registry)
    required_nodes = []
    for name in required_names:
        node = registry.find(name)
        if node is None:
            missing.append(f"{name}: entry missing")
        else:
            required_nodes.append(node)
            missing += missing_items(node)
    if missing:
        raise IncompleteRegistryError(missing)
    not_reported = [item for node in required_nodes for item in not_reported_items(node)]
    if not_reported:
        raise NotReportedValueError(not_reported)
