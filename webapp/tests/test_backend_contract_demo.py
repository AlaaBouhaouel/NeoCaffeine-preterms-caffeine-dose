# Purpose: Contract tests for SimulationBackend behavior executed on DemoSimulationBackend.

from __future__ import annotations

from backend.demo.demo_simulation_backend import DemoSimulationBackend


def test_contract_create_run_and_get_state() -> None:
    backend = DemoSimulationBackend()
    created = backend.create_run(
        patient={
            "gestational_age_weeks": 27,
            "gestational_age_days_extra": 4,
            "birth_weight_g": 1000,
            "sex": "female",
        },
        initial_context={
            "fiO2_fraction": 0.3,
            "breathing_support": "cpap",
            "monitoring_on": True,
        },
        random_seed=9,
    )
    assert created["ok"] is True
    run_id = created["run_id"]
    state = backend.get_state(run_id=run_id)
    assert state["ok"] is True
    assert state["state"]["meta"]["demo_data"] is True


def test_contract_advance_stops_at_hour_boundary() -> None:
    backend = DemoSimulationBackend()
    created = backend.create_run(
        patient={
            "gestational_age_weeks": 27,
            "gestational_age_days_extra": 4,
            "birth_weight_g": 1000,
            "sex": "female",
        },
        initial_context={
            "fiO2_fraction": 0.3,
            "breathing_support": "cpap",
            "monitoring_on": True,
        },
        random_seed=9,
    )
    advanced = backend.advance(run_id=created["run_id"], delta_sim_hours=2.75, state_version=created["state_version"])
    assert advanced["ok"] is True
    assert advanced["state"]["time"]["sim_time_hours"] == 1.0
    assert advanced["state"]["meta"]["phase"] == "awaiting_n"


def test_contract_submit_n_returns_to_playing_or_converged() -> None:
    backend = DemoSimulationBackend()
    created = backend.create_run(
        patient={
            "gestational_age_weeks": 27,
            "gestational_age_days_extra": 4,
            "birth_weight_g": 1000,
            "sex": "female",
        },
        initial_context={
            "fiO2_fraction": 0.3,
            "breathing_support": "cpap",
            "monitoring_on": True,
        },
        random_seed=9,
    )
    advanced = backend.advance(run_id=created["run_id"], delta_sim_hours=1.0, state_version=created["state_version"])
    submitted = backend.submit_observed_n(
        run_id=created["run_id"],
        hour_index=0,
        observed_n=2,
        state_version=advanced["state_version"],
    )
    assert submitted["ok"] is True
    assert submitted["state"]["meta"]["phase"] in {"playing", "converged"}


def test_contract_interventions_apply_at_current_server_time() -> None:
    backend = DemoSimulationBackend()
    created = backend.create_run(
        patient={
            "gestational_age_weeks": 27,
            "gestational_age_days_extra": 4,
            "birth_weight_g": 1000,
            "sex": "female",
        },
        initial_context={
            "fiO2_fraction": 0.3,
            "breathing_support": "cpap",
            "monitoring_on": True,
        },
        random_seed=9,
    )
    moved = backend.advance(run_id=created["run_id"], delta_sim_hours=0.4, state_version=created["state_version"])
    state_version = moved["state_version"]
    run_id = created["run_id"]
    dose = backend.give_dose(
        run_id=run_id,
        payload={
            "amount": 5.0,
            "amount_unit": "mg_per_kg",
            "route": "intravenous",
            "form": "citrate",
            "source": "manual",
        },
        state_version=state_version,
    )
    assert dose["ok"] is True
    marker = dose["state"]["pharmacology_panel"]["dose_markers"][-1]
    assert marker["t_sim_hours"] == dose["state"]["time"]["sim_time_hours"]
