# Purpose: Abstract simulation backend contract consumed by web views and clients.

from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID


StateEnvelope = dict[str, Any]
SummaryEnvelope = dict[str, Any]
CreatePatientPayload = dict[str, Any]
InitialContextPayload = dict[str, Any]
DosePayload = dict[str, Any]
ContextPayload = dict[str, Any]
MonitoringPayload = dict[str, Any]
BloodLevelPayload = dict[str, Any]


class SimulationBackend(Protocol):
    def create_run(
        self,
        patient: CreatePatientPayload,
        initial_context: InitialContextPayload,
        random_seed: int | None = None,
    ) -> StateEnvelope: ...

    def get_state(self, run_id: UUID) -> StateEnvelope: ...

    def advance(self, run_id: UUID, delta_sim_hours: float, state_version: int) -> StateEnvelope: ...

    def submit_observed_n(
        self,
        run_id: UUID,
        hour_index: int,
        observed_n: int,
        state_version: int,
    ) -> StateEnvelope: ...

    def give_dose(self, run_id: UUID, payload: DosePayload, state_version: int) -> StateEnvelope: ...

    def accept_suggested_dose(self, run_id: UUID, state_version: int) -> StateEnvelope: ...

    def change_context(self, run_id: UUID, payload: ContextPayload, state_version: int) -> StateEnvelope: ...

    def set_monitoring(self, run_id: UUID, payload: MonitoringPayload, state_version: int) -> StateEnvelope: ...

    def add_blood_level(self, run_id: UUID, payload: BloodLevelPayload, state_version: int) -> StateEnvelope: ...

    def get_summary(self, run_id: UUID) -> SummaryEnvelope: ...
