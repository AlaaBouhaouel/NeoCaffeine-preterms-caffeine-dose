# Reading of one registry YAML file with ruamel.yaml.

from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from neocaffeine.registry.registry_errors import RegistrySchemaError


def read_yaml_file(path: Path) -> dict[str, Any]:
    """Return the top-level map of a YAML file; an empty file reads as an empty map."""
    yaml = YAML(typ="rt")
    try:
        with path.open(encoding="utf-8") as stream:
            content = yaml.load(stream)
    except FileNotFoundError as error:
        raise RegistrySchemaError(f"Registry file not found: {path}") from error
    except YAMLError as error:
        raise RegistrySchemaError(f"Registry file {path} is not valid YAML: {error}") from error
    if content is None:
        return {}
    if not isinstance(content, dict):
        raise RegistrySchemaError(f"Registry file {path} must contain a map at the top level.")
    return content
