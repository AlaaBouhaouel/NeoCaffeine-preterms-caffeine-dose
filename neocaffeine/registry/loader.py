# Loading of every registry file into a Registry; works on incomplete registries for editing.

from pathlib import Path

from neocaffeine.registry.entry_parser import parse_category, reject_unknown_keys
from neocaffeine.registry.registry import Registry
from neocaffeine.registry.registry_errors import RegistrySchemaError
from neocaffeine.registry.yaml_reader import read_yaml_file

DEFAULT_DATA_DIRECTORY = Path(__file__).parent / "data"
META_FILE_NAME = "registry_meta.yaml"
META_KEYS = ("version", "date")
CATEGORY_NAMES = (
    "pk_models",
    "dosing",
    "effect",
    "maturity",
    "baseline",
    "priors",
    "bounds",
    "events",
    "observation",
    "validation_ranges",
    "decision",
)


def require_conflict_references_exist(registry: Registry) -> None:
    """Raise RegistrySchemaError if any conflicts_with names an entry that does not exist."""
    for node in registry.all_nodes():
        source = getattr(node, "source", None)
        for conflicting_name in () if source is None else source.conflicts_with:
            if registry.find(conflicting_name) is None:
                raise RegistrySchemaError(f"{node.name}.conflicts_with: no entry named {conflicting_name!r}.")


def load_registry(data_directory: Path) -> Registry:
    """Load the registry meta file and every category file from data_directory."""
    meta = read_yaml_file(data_directory / META_FILE_NAME)
    reject_unknown_keys("registry_meta", meta, META_KEYS)
    categories = {
        name: parse_category(name, read_yaml_file(data_directory / f"{name}.yaml"))
        for name in CATEGORY_NAMES
    }
    registry = Registry(version=meta.get("version"), date=meta.get("date"), categories=categories)
    require_conflict_references_exist(registry)
    return registry
