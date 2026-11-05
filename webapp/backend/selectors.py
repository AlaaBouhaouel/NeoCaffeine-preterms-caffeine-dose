# Purpose: Single active-backend selector controlled by environment setting.

from __future__ import annotations

import os

from backend.demo.demo_simulation_backend import DemoSimulationBackend
from backend.interfaces.simulation_backend import SimulationBackend
from backend.runtime import BackendRuntime


def get_active_simulation_backend() -> SimulationBackend:
    selected_backend = os.environ.get("ACTIVE_SIMULATION_BACKEND", "demo").strip().lower()
    if selected_backend == "demo":
        return DemoSimulationBackend()
    raise ValueError("ACTIVE_SIMULATION_BACKEND must be 'demo' in current scope")


def get_backend_runtime() -> BackendRuntime:
    return BackendRuntime(get_active_simulation_backend())
