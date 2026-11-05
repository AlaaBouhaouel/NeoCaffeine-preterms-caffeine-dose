# Conversion of raw registry YAML maps into typed entries, rejecting unknown keys and wrong types.

from collections.abc import Mapping
from typing import Any

from neocaffeine.registry.entry import (
    EVIDENCE_TIERS,
    NOT_REPORTED,
    ChoiceEntry,
    Citation,
    DesignAssumptionEntry,
    EntryGroup,
    EventDefinition,
    ExclusionEntry,
    FallbackEntry,
    FormulaEntry,
    PopulationLimit,
    PopulationOfValidity,
    RangeEntry,
    ScalarEntry,
    Source,
    StructuralEntry,
    Symbol,
)
from neocaffeine.registry.pk_model import PkModel
from neocaffeine.registry.registry_errors import RegistrySchemaError
from neocaffeine.registry.units import require_valid_unit

CHOICE_OPTIONS = {
    "dosing.dosing_weight_rule": ("birth_weight", "latest_weight_on_or_before_dose"),
    "events.event_overlap_rule": ("separate", "merge_within_window"),
}
CHOICE_SETTINGS = {
    "events.event_overlap_rule": ("merge_window", "merge_window_unit"),
}

SOURCE_KEYS = ("meaning", "evidence_tier", "population", "citations", "conflicts_with", "conflict_note")
CITATION_KEYS = (
    "authors", "year", "title", "journal_or_source", "location",
    "doi", "pmid", "url", "volume", "issue", "pages", "notes",
)
POPULATION_DIMENSIONS = ("gestational_age", "postnatal_age", "weight")
POPULATION_LIMIT_KEYS = ("min", "max", "unit")
SYMBOL_KEYS = ("symbol", "meaning", "unit")
SCALAR_KEYS = ("value", "unit", "not_reported_note", *SOURCE_KEYS)
RANGE_KEYS = ("minimum", "maximum", "unit", "not_reported_note", *SOURCE_KEYS)
CHOICE_KEYS = ("value", "unit", *SOURCE_KEYS)
FORMULA_KEYS = ("equation", "symbols", "coefficients", *SOURCE_KEYS)
DESIGN_ASSUMPTION_KEYS = ("entry_type", "equation", "symbols", "meaning", "rationale", "citations")
STRUCTURAL_KEYS = ("entry_type", "meaning")
EVENT_KEYS = (
    "signal", "threshold", "threshold_unit", "min_duration", "max_duration", "duration_unit", "counts_toward_N",
    *SOURCE_KEYS,
)
FALLBACK_KEYS = ("rate", "rate_unit", "reported_maturity", "reported_maturity_unit", "not_reported_note", *SOURCE_KEYS)
EXCLUSION_KEYS = ("enabled", "value", "unit", "not_reported_note", *SOURCE_KEYS)
PK_MODEL_KEYS = (
    "structure", "clearance_equation", "volume_equation", "coefficients", "residual_error", *SOURCE_KEYS,
)
ENTRY_TYPES = ("structural", "design_assumption")


def require_map(path: str, raw: object) -> Mapping[str, Any]:
    """Return raw if it is a map, or raise RegistrySchemaError."""
    if not isinstance(raw, Mapping):
        raise RegistrySchemaError(f"{path}: expected a map, got {raw!r}.")
    return raw


def require_list(path: str, raw: object) -> list[Any]:
    """Return raw if it is a list, or raise RegistrySchemaError."""
    if not isinstance(raw, list):
        raise RegistrySchemaError(f"{path}: expected a list, got {raw!r}.")
    return raw


def reject_unknown_keys(path: str, raw: Mapping[str, Any], allowed_keys: tuple[str, ...]) -> None:
    """Raise RegistrySchemaError if raw holds any key outside allowed_keys."""
    unknown_keys = sorted(set(raw) - set(allowed_keys))
    if unknown_keys:
        raise RegistrySchemaError(f"{path}: unknown keys {unknown_keys}.")


def is_number(raw: object) -> bool:
    """Return True for int or float values, excluding booleans."""
    return isinstance(raw, (int, float)) and not isinstance(raw, bool)


def text_field(path: str, raw: Mapping[str, Any], key: str) -> str | None:
    """Return a text field, or None if empty."""
    value = raw.get(key)
    if value is not None and not isinstance(value, str):
        raise RegistrySchemaError(f"{path}.{key}: expected text, got {value!r}.")
    return None if value is None else str(value)


def identifier_field(path: str, raw: Mapping[str, Any], key: str) -> str | None:
    """Return an identifier or citation detail written as text or a number, as text."""
    value = raw.get(key)
    if value is None:
        return None
    if isinstance(value, str) or is_number(value):
        return str(value)
    raise RegistrySchemaError(f"{path}.{key}: expected text or a number, got {value!r}.")


def number_field(path: str, raw: Mapping[str, Any], key: str) -> int | float | None:
    """Return a numeric field, or None if empty."""
    value = raw.get(key)
    if value is not None and not is_number(value):
        raise RegistrySchemaError(f"{path}.{key}: expected a number, got {value!r}.")
    return value


def integer_field(path: str, raw: Mapping[str, Any], key: str) -> int | None:
    """Return an integer field, or None if empty."""
    value = raw.get(key)
    if value is not None and (not isinstance(value, int) or isinstance(value, bool)):
        raise RegistrySchemaError(f"{path}.{key}: expected a whole number, got {value!r}.")
    return value


def boolean_field(path: str, raw: Mapping[str, Any], key: str) -> bool | None:
    """Return a true/false field, or None if empty."""
    value = raw.get(key)
    if value is not None and not isinstance(value, bool):
        raise RegistrySchemaError(f"{path}.{key}: expected true or false, got {value!r}.")
    return value


def value_field(path: str, raw: Mapping[str, Any], key: str) -> int | float | str | None:
    """Return a sourced value: a number, the not_reported marker, or None if empty."""
    value = raw.get(key)
    if value is None or is_number(value) or value == NOT_REPORTED:
        return value
    raise RegistrySchemaError(f"{path}.{key}: expected a number or {NOT_REPORTED!r}, got {value!r}.")


def unit_field(path: str, raw: Mapping[str, Any], key: str) -> str | None:
    """Return a unit string checked by pint, or None if empty."""
    return require_valid_unit(raw.get(key), f"{path}.{key}")


def require_note_for_not_reported(path: str, raw: Mapping[str, Any], value_keys: tuple[str, ...]) -> str | None:
    """Return the not_reported note; raise if any value is not_reported without a note."""
    note = text_field(path, raw, "not_reported_note")
    if note is None and any(raw.get(key) == NOT_REPORTED for key in value_keys):
        raise RegistrySchemaError(f"{path}: a value marked {NOT_REPORTED!r} needs a not_reported_note.")
    return note


def parse_citation(path: str, raw: object) -> Citation:
    """Parse one citation record."""
    citation = require_map(path, raw)
    reject_unknown_keys(path, citation, CITATION_KEYS)
    return Citation(
        authors=text_field(path, citation, "authors"),
        year=integer_field(path, citation, "year"),
        title=text_field(path, citation, "title"),
        journal_or_source=text_field(path, citation, "journal_or_source"),
        location=text_field(path, citation, "location"),
        doi=identifier_field(path, citation, "doi"),
        pmid=identifier_field(path, citation, "pmid"),
        url=text_field(path, citation, "url"),
        volume=identifier_field(path, citation, "volume"),
        issue=identifier_field(path, citation, "issue"),
        pages=identifier_field(path, citation, "pages"),
        notes=text_field(path, citation, "notes"),
    )


def parse_citations(path: str, raw: object) -> tuple[Citation, ...]:
    """Parse the list of citations of an entry; an empty field is an empty list."""
    if raw is None:
        return ()
    return tuple(parse_citation(f"{path}[{index}]", item) for index, item in enumerate(require_list(path, raw)))


def parse_population_limit(path: str, raw: object) -> PopulationLimit:
    """Parse the minimum, maximum and unit of one population dimension."""
    limit = require_map(path, {} if raw is None else raw)
    reject_unknown_keys(path, limit, POPULATION_LIMIT_KEYS)
    return PopulationLimit(
        minimum=number_field(path, limit, "min"),
        maximum=number_field(path, limit, "max"),
        unit=unit_field(path, limit, "unit"),
    )


def parse_population(path: str, raw: object) -> PopulationOfValidity:
    """Parse the population of validity of an entry."""
    population = require_map(path, {} if raw is None else raw)
    reject_unknown_keys(path, population, POPULATION_DIMENSIONS)
    return PopulationOfValidity(
        gestational_age=parse_population_limit(f"{path}.gestational_age", population.get("gestational_age")),
        postnatal_age=parse_population_limit(f"{path}.postnatal_age", population.get("postnatal_age")),
        weight=parse_population_limit(f"{path}.weight", population.get("weight")),
    )


def parse_conflicts(path: str, raw: object) -> tuple[str, ...]:
    """Parse the list of full entry names this entry conflicts with."""
    if raw is None:
        return ()
    names = require_list(path, raw)
    for name in names:
        if not isinstance(name, str):
            raise RegistrySchemaError(f"{path}: expected full entry names as text, got {name!r}.")
    return tuple(names)


def parse_source(path: str, raw: Mapping[str, Any]) -> Source:
    """Parse the meaning, tier, population, citations and conflicts of a sourced entry."""
    evidence_tier = text_field(path, raw, "evidence_tier")
    if evidence_tier is not None and evidence_tier not in EVIDENCE_TIERS:
        raise RegistrySchemaError(f"{path}.evidence_tier: expected one of A, B, C, got {evidence_tier!r}.")
    return Source(
        meaning=text_field(path, raw, "meaning"),
        evidence_tier=evidence_tier,
        population=parse_population(f"{path}.population", raw.get("population")),
        citations=parse_citations(f"{path}.citations", raw.get("citations")),
        conflicts_with=parse_conflicts(f"{path}.conflicts_with", raw.get("conflicts_with")),
        conflict_note=text_field(path, raw, "conflict_note"),
    )


def parse_symbols(path: str, raw: object) -> tuple[Symbol, ...]:
    """Parse the symbol definitions of a documented equation."""
    if raw is None:
        return ()
    symbols = []
    for index, item in enumerate(require_list(path, raw)):
        item_path = f"{path}[{index}]"
        symbol = require_map(item_path, item)
        reject_unknown_keys(item_path, symbol, SYMBOL_KEYS)
        symbols.append(Symbol(
            symbol=text_field(item_path, symbol, "symbol"),
            meaning=text_field(item_path, symbol, "meaning"),
            unit=unit_field(item_path, symbol, "unit"),
        ))
    return tuple(symbols)


def parse_scalar(path: str, raw: Mapping[str, Any]) -> ScalarEntry:
    """Parse a scalar entry."""
    reject_unknown_keys(path, raw, SCALAR_KEYS)
    return ScalarEntry(
        name=path,
        value=value_field(path, raw, "value"),
        unit=unit_field(path, raw, "unit"),
        source=parse_source(path, raw),
        not_reported_note=require_note_for_not_reported(path, raw, ("value",)),
    )


def parse_range(path: str, raw: Mapping[str, Any]) -> RangeEntry:
    """Parse a range entry."""
    reject_unknown_keys(path, raw, RANGE_KEYS)
    return RangeEntry(
        name=path,
        minimum=value_field(path, raw, "minimum"),
        maximum=value_field(path, raw, "maximum"),
        unit=unit_field(path, raw, "unit"),
        source=parse_source(path, raw),
        not_reported_note=require_note_for_not_reported(path, raw, ("minimum", "maximum")),
    )


def parse_choice(path: str, raw: Mapping[str, Any]) -> ChoiceEntry:
    """Parse a choice entry whose value must be one of the options the code accepts."""
    setting_keys = CHOICE_SETTINGS.get(path, ())
    reject_unknown_keys(path, raw, (*CHOICE_KEYS, *setting_keys))
    options = CHOICE_OPTIONS[path]
    value = text_field(path, raw, "value")
    if value is not None and value not in options:
        raise RegistrySchemaError(f"{path}.value: expected one of {list(options)}, got {value!r}.")
    settings = {
        key: unit_field(path, raw, key) if key.endswith("_unit") else number_field(path, raw, key)
        for key in setting_keys
    }
    return ChoiceEntry(
        name=path,
        value=value,
        options=options,
        unit=unit_field(path, raw, "unit"),
        settings=settings,
        source=parse_source(path, raw),
    )


def parse_coefficients(path: str, raw: object) -> EntryGroup:
    """Parse a map of coefficient names to scalar entries."""
    coefficients = require_map(path, {} if raw is None else raw)
    return EntryGroup(
        name=path,
        entries={
            name: parse_scalar(f"{path}.{name}", require_map(f"{path}.{name}", value))
            for name, value in coefficients.items()
        },
    )


def parse_formula(path: str, raw: Mapping[str, Any]) -> FormulaEntry:
    """Parse a documented equation, with its coefficients when it has them."""
    reject_unknown_keys(path, raw, FORMULA_KEYS)
    has_coefficients = "coefficients" in raw
    return FormulaEntry(
        name=path,
        equation=text_field(path, raw, "equation"),
        symbols=parse_symbols(f"{path}.symbols", raw.get("symbols")),
        source=parse_source(path, raw),
        coefficients=parse_coefficients(f"{path}.coefficients", raw.get("coefficients")) if has_coefficients else None,
    )


def parse_design_assumption(path: str, raw: Mapping[str, Any]) -> DesignAssumptionEntry:
    """Parse a design assumption: equation, meaning, rationale and supporting citations."""
    reject_unknown_keys(path, raw, DESIGN_ASSUMPTION_KEYS)
    return DesignAssumptionEntry(
        name=path,
        equation=text_field(path, raw, "equation"),
        symbols=parse_symbols(f"{path}.symbols", raw.get("symbols")),
        meaning=text_field(path, raw, "meaning"),
        rationale=text_field(path, raw, "rationale"),
        citations=parse_citations(f"{path}.citations", raw.get("citations")),
    )


def parse_structural(path: str, raw: Mapping[str, Any]) -> StructuralEntry:
    """Parse a structural rule."""
    reject_unknown_keys(path, raw, STRUCTURAL_KEYS)
    return StructuralEntry(name=path, meaning=text_field(path, raw, "meaning"))


def parse_event_definition(path: str, raw: Mapping[str, Any]) -> EventDefinition:
    """Parse the criteria of one event type."""
    reject_unknown_keys(path, raw, EVENT_KEYS)
    return EventDefinition(
        name=path,
        signal=text_field(path, raw, "signal"),
        threshold=number_field(path, raw, "threshold"),
        threshold_unit=unit_field(path, raw, "threshold_unit"),
        min_duration=number_field(path, raw, "min_duration"),
        max_duration=number_field(path, raw, "max_duration"),
        duration_unit=unit_field(path, raw, "duration_unit"),
        counts_toward_n=boolean_field(path, raw, "counts_toward_N"),
        source=parse_source(path, raw),
    )


def parse_fallback(path: str, raw: Mapping[str, Any]) -> FallbackEntry:
    """Parse a population fallback: a rate and the maturity it was reported at."""
    reject_unknown_keys(path, raw, FALLBACK_KEYS)
    return FallbackEntry(
        name=path,
        rate=value_field(path, raw, "rate"),
        rate_unit=unit_field(path, raw, "rate_unit"),
        reported_maturity=value_field(path, raw, "reported_maturity"),
        reported_maturity_unit=unit_field(path, raw, "reported_maturity_unit"),
        source=parse_source(path, raw),
        not_reported_note=require_note_for_not_reported(path, raw, ("rate", "reported_maturity")),
    )


def parse_exclusion(path: str, raw: Mapping[str, Any]) -> ExclusionEntry:
    """Parse a valid-time exclusion criterion with its enabled switch."""
    reject_unknown_keys(path, raw, EXCLUSION_KEYS)
    return ExclusionEntry(
        name=path,
        enabled=boolean_field(path, raw, "enabled"),
        value=value_field(path, raw, "value"),
        unit=unit_field(path, raw, "unit"),
        source=parse_source(path, raw),
        not_reported_note=require_note_for_not_reported(path, raw, ("value",)),
    )


def parse_pk_model(path: str, raw: Mapping[str, Any]) -> PkModel:
    """Parse one population PK model."""
    reject_unknown_keys(path, raw, PK_MODEL_KEYS)
    return PkModel(
        name=path,
        structure=text_field(path, raw, "structure"),
        clearance_equation=parse_formula(
            f"{path}.clearance_equation", require_map(f"{path}.clearance_equation", raw.get("clearance_equation", {}))
        ),
        volume_equation=parse_formula(
            f"{path}.volume_equation", require_map(f"{path}.volume_equation", raw.get("volume_equation", {}))
        ),
        coefficients=parse_coefficients(f"{path}.coefficients", raw.get("coefficients")),
        residual_error=parse_scalar(
            f"{path}.residual_error", require_map(f"{path}.residual_error", raw.get("residual_error", {}))
        ),
        source=parse_source(path, raw),
    )


def parse_group(path: str, raw: Mapping[str, Any]) -> EntryGroup:
    """Parse a named map of entries."""
    return EntryGroup(name=path, entries={name: parse_node(f"{path}.{name}", value) for name, value in raw.items()})


def parse_node(path: str, raw: object) -> Any:
    """Parse an entry or a group of entries, recognising its kind from its keys."""
    node = require_map(path, raw)
    entry_type = node.get("entry_type")
    if entry_type is not None:
        if entry_type == "structural":
            return parse_structural(path, node)
        if entry_type == "design_assumption":
            return parse_design_assumption(path, node)
        raise RegistrySchemaError(f"{path}.entry_type: expected one of {list(ENTRY_TYPES)}, got {entry_type!r}.")
    if path in CHOICE_OPTIONS:
        return parse_choice(path, node)
    if "structure" in node:
        return parse_pk_model(path, node)
    if "signal" in node:
        return parse_event_definition(path, node)
    if "rate" in node:
        return parse_fallback(path, node)
    if "equation" in node:
        return parse_formula(path, node)
    if "minimum" in node:
        return parse_range(path, node)
    if "enabled" in node:
        return parse_exclusion(path, node)
    if "value" in node:
        return parse_scalar(path, node)
    return parse_group(path, node)


def parse_category(category_name: str, raw: Mapping[str, Any]) -> dict[str, Any]:
    """Parse every top-level entry or group of one category file."""
    return {name: parse_node(f"{category_name}.{name}", value) for name, value in raw.items()}
