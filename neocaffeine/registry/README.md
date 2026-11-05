# registry

## Purpose
The parameter registry: every physiological value, formula, prior, variability, bound and threshold, with its unit, plain-language meaning, evidence tier, population of validity and citations. Values are never written in code. The data files (YAML) are kept separate from the loader and validator (Python). A run refuses to start if any entry it requires is empty, and lists all missing entries at once.

The code is read-only: it never writes to the registry. Loading always works, even when entries are empty, so the files can be edited step by step. Completeness is checked only when a run starts.

## Contents
- `data/`: the YAML registry files, the version file and the changelog (see `data/README.md` for the schema).
- `registry_errors.py`: `RegistryError` and its subclasses `RegistrySchemaError`, `UnitError`, `UnknownModelError`, `IncompleteRegistryError` (lists every missing item), `NotReportedValueError` (lists every required `not_reported` value).
- `entry.py`: dataclasses for citations, populations, symbols, sources and every entry kind; `child_nodes` for nested entries.
- `pk_model.py`: the `PkModel` dataclass.
- `yaml_reader.py`: `read_yaml_file` with ruamel.yaml.
- `entry_parser.py`: `parse_category` and `parse_node`; recognises each entry kind, rejects unknown keys, wrong types, invalid tiers, choice values outside their options, and `not_reported` without a note.
- `units.py`: the shared pint `unit_registry` and `require_valid_unit`.
- `registry.py`: `ModelSelection` (PK, effect and baseline model names) and `Registry` (lookup by full name, models by name, version, `design_assumptions()` for reporting limitations).
- `loader.py`: `load_registry(data_directory)` and `DEFAULT_DATA_DIRECTORY`; checks that every `conflicts_with` name exists.
- `completeness.py`: `missing_items`, `not_reported_items`, `required_entry_names`, and `require_complete`, which the runner calls before a simulation or estimation run.

## Inputs/Outputs
- Inputs: the files in `data/`; a `ModelSelection` built from the run configuration.
- Outputs: a read-only `Registry`; at run start, either nothing (complete) or one error listing every missing or `not_reported` item; the registry version recorded by each run.

## Depends on
- ruamel.yaml, pint.
- `config/` (selection of the models in use).

## Used by
- `neocaffeine/patient/` (validation ranges)
- `neocaffeine/features/`, `neocaffeine/maturity/`, `neocaffeine/models/`, `neocaffeine/estimator/`, `neocaffeine/decision/`, `neocaffeine/simulator/`
