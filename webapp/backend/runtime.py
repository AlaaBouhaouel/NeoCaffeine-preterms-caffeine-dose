# Purpose: Backend-agnostic rule enforcement layer between API handlers and backend implementations.

from __future__ import annotations

from typing import Any
from uuid import UUID

from backend.interfaces.simulation_backend import SimulationBackend
from backend.state_upgrade import upgrade_state
from runs.repositories import get_run_snapshot


class BackendRuntime:
    def __init__(self, backend: SimulationBackend) -> None:
        self._backend = backend

    def _error(self, code: str, message: str, details: dict[str, Any] | None = None, run_id: UUID | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "ok": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            },
        }
        if run_id is not None:
            payload["run_id"] = str(run_id)
        return payload

    def _run_not_found(self, run_id: UUID) -> dict[str, Any]:
        return self._error("run_not_found", "Run was not found.", run_id=run_id)

    def _load_state(self, run_id: UUID):
        try:
            snapshot = get_run_snapshot(run_id)
        except Exception:
            return None, self._run_not_found(run_id)
        return snapshot, upgrade_state(snapshot.state_json)

    def _check_state_version(self, snapshot, state_version: int, run_id: UUID):
        if snapshot.state_version != state_version:
            return self._error("stale_state_version", "state_version is stale.", run_id=run_id)
        return None

    def _check_converged_lock(self, state: dict[str, Any], run_id: UUID):
        if bool(state["convergence"]["is_converged"]):
            return self._error("run_converged_locked", "Run is converged and controls are locked.", run_id=run_id)
        return None

    def create_run(self, patient: dict[str, Any], initial_context: dict[str, Any], random_seed: int | None = None) -> dict[str, Any]:
        return self._backend.create_run(patient=patient, initial_context=initial_context, random_seed=random_seed)

    def get_state(self, run_id: UUID) -> dict[str, Any]:
        return self._backend.get_state(run_id)

    def get_summary(self, run_id: UUID) -> dict[str, Any]:
        return self._backend.get_summary(run_id)

    def advance(self, run_id: UUID, delta_sim_hours: float, state_version: int) -> dict[str, Any]:
        snapshot, loaded = self._load_state(run_id)
        if snapshot is None:
            return loaded
        state = loaded
        stale = self._check_state_version(snapshot, state_version, run_id)
        if stale is not None:
            return stale
        converged = self._check_converged_lock(state, run_id)
        if converged is not None:
            return converged
        if str(state["meta"]["phase"]) == "awaiting_n":
            return self._error("phase_awaiting_n_requires_submission", "Cannot advance while awaiting N submission.", run_id=run_id)
        return self._backend.advance(run_id=run_id, delta_sim_hours=delta_sim_hours, state_version=state_version)

    def submit_observed_n(self, run_id: UUID, day_index: int, observed_n: int, state_version: int) -> dict[str, Any]:
        snapshot, loaded = self._load_state(run_id)
        if snapshot is None:
            return loaded
        state = loaded
        stale = self._check_state_version(snapshot, state_version, run_id)
        if stale is not None:
            return stale
        converged = self._check_converged_lock(state, run_id)
        if converged is not None:
            return converged
        if str(state["meta"]["phase"]) != "awaiting_n":
            return self._error("phase_not_awaiting_n", "N submission is only allowed while awaiting N.", run_id=run_id)
        expected_day = state["n_gate"]["awaiting_n_for_day_index"]
        if expected_day != day_index:
            return self._error("day_index_mismatch", "day_index does not match the awaiting day.", {"expected": expected_day}, run_id=run_id)
        return self._backend.submit_observed_n(
            run_id=run_id,
            day_index=day_index,
            observed_n=observed_n,
            state_version=state_version,
        )

    def give_dose(self, run_id: UUID, payload: dict[str, Any], state_version: int) -> dict[str, Any]:
        snapshot, loaded = self._load_state(run_id)
        if snapshot is None:
            return loaded
        state = loaded
        stale = self._check_state_version(snapshot, state_version, run_id)
        if stale is not None:
            return stale
        converged = self._check_converged_lock(state, run_id)
        if converged is not None:
            return converged
        if str(state["meta"]["phase"]) == "awaiting_n":
            return self._error("phase_awaiting_n_locked", "Interventions are locked while waiting for N submission.", run_id=run_id)
        return self._backend.give_dose(run_id=run_id, payload=payload, state_version=state_version)

    def accept_suggested_dose(self, run_id: UUID, state_version: int) -> dict[str, Any]:
        snapshot, loaded = self._load_state(run_id)
        if snapshot is None:
            return loaded
        state = loaded
        stale = self._check_state_version(snapshot, state_version, run_id)
        if stale is not None:
            return stale
        converged = self._check_converged_lock(state, run_id)
        if converged is not None:
            return converged
        if str(state["meta"]["phase"]) == "awaiting_n":
            return self._error("phase_awaiting_n_locked", "Interventions are locked while waiting for N submission.", run_id=run_id)
        return self._backend.accept_suggested_dose(run_id=run_id, state_version=state_version)

    def change_context(self, run_id: UUID, payload: dict[str, Any], state_version: int) -> dict[str, Any]:
        snapshot, loaded = self._load_state(run_id)
        if snapshot is None:
            return loaded
        state = loaded
        stale = self._check_state_version(snapshot, state_version, run_id)
        if stale is not None:
            return stale
        converged = self._check_converged_lock(state, run_id)
        if converged is not None:
            return converged
        if str(state["meta"]["phase"]) == "awaiting_n":
            return self._error("phase_awaiting_n_locked", "Interventions are locked while waiting for N submission.", run_id=run_id)
        return self._backend.change_context(run_id=run_id, payload=payload, state_version=state_version)

    def set_monitoring(self, run_id: UUID, payload: dict[str, Any], state_version: int) -> dict[str, Any]:
        snapshot, loaded = self._load_state(run_id)
        if snapshot is None:
            return loaded
        state = loaded
        stale = self._check_state_version(snapshot, state_version, run_id)
        if stale is not None:
            return stale
        converged = self._check_converged_lock(state, run_id)
        if converged is not None:
            return converged
        if str(state["meta"]["phase"]) == "awaiting_n":
            return self._error("phase_awaiting_n_locked", "Interventions are locked while waiting for N submission.", run_id=run_id)
        return self._backend.set_monitoring(run_id=run_id, payload=payload, state_version=state_version)

    def add_blood_level(self, run_id: UUID, payload: dict[str, Any], state_version: int) -> dict[str, Any]:
        snapshot, loaded = self._load_state(run_id)
        if snapshot is None:
            return loaded
        state = loaded
        stale = self._check_state_version(snapshot, state_version, run_id)
        if stale is not None:
            return stale
        converged = self._check_converged_lock(state, run_id)
        if converged is not None:
            return converged
        if str(state["meta"]["phase"]) == "awaiting_n":
            return self._error("phase_awaiting_n_locked", "Interventions are locked while waiting for N submission.", run_id=run_id)
        return self._backend.add_blood_level(run_id=run_id, payload=payload, state_version=state_version)
