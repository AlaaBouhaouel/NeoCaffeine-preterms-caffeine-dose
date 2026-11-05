# Dataclass for one published population pharmacokinetic model.

from dataclasses import dataclass
from typing import Any

from neocaffeine.registry.entry import EntryGroup, FormulaEntry, ScalarEntry, Source


@dataclass(frozen=True)
class PkModel:
    """A population PK model: structure, documented equations, coefficients and residual error."""

    name: str
    structure: str | None
    clearance_equation: FormulaEntry
    volume_equation: FormulaEntry
    coefficients: EntryGroup
    residual_error: ScalarEntry
    source: Source

    def children(self) -> dict[str, Any]:
        """Return the nested entries of the model by short name."""
        return {
            "clearance_equation": self.clearance_equation,
            "volume_equation": self.volume_equation,
            "coefficients": self.coefficients,
            "residual_error": self.residual_error,
        }
