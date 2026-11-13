# Purpose: Verifies main successful API flows for run lifecycle and interventions.

from __future__ import annotations

import json


def _post_json(client, url: str, payload: dict):
    return client.post(url, data=json.dumps(payload), content_type="application/json")


def test_create_and_get_state_success(client, create_run_payload) -> None:
    created = _post_json(client, "/api/v1/runs", create_run_payload)
    assert created.status_code == 200
    body = created.json()
    run_id = body["run_id"]

    state = client.get(f"/api/v1/runs/{run_id}/state")
    assert state.status_code == 200
    state_body = state.json()
    assert state_body["state"]["meta"]["phase"] == "playing"


def test_advance_stops_at_day_boundary_success(client, created_run) -> None:
    run_id = created_run["run_id"]
    response = _post_json(client, f"/api/v1/runs/{run_id}/advance", {"delta_sim_hours": 30.0, "state_version": created_run["state_version"]})
    assert response.status_code == 200
    body = response.json()
    assert body["state"]["meta"]["phase"] == "awaiting_n"
    assert body["state"]["time"]["sim_time_hours"] == 24.0
    assert body["state"]["time"]["last_advanced_hours"] == 24.0
    assert body["state"]["n_gate"]["awaiting_n_for_day_index"] == 0


def test_submit_n_and_resume_playing_success(client, created_run) -> None:
    run_id = created_run["run_id"]
    advanced = _post_json(client, f"/api/v1/runs/{run_id}/advance", {"delta_sim_hours": 24.0, "state_version": created_run["state_version"]})
    advanced_body = advanced.json()

    submitted = _post_json(
        client,
        f"/api/v1/runs/{run_id}/days/0/n",
        {"observed_n": 2, "state_version": advanced_body["state_version"]},
    )
    assert submitted.status_code == 200
    submitted_body = submitted.json()
    assert submitted_body["state"]["meta"]["phase"] == "playing"
    assert submitted_body["state"]["estimator_panel"]["last_day"]["observed_n"] == 2
    assert submitted_body["state"]["estimator_panel"]["last_day"]["day_index"] == 0


def test_intervention_success_paths(client, created_run) -> None:
    run_id = created_run["run_id"]
    version = created_run["state_version"]

    dose = _post_json(
        client,
        f"/api/v1/runs/{run_id}/interventions/dose",
        {
            "state_version": version,
            "amount": 5.0,
            "amount_unit": "mg_per_kg",
            "route": "iv",
            "form": "citrate",
            "source": "manual",
        },
    )
    assert dose.status_code == 200
    version = dose.json()["state_version"]

    context = _post_json(
        client,
        f"/api/v1/runs/{run_id}/interventions/context",
        {"state_version": version, "fiO2_fraction": 0.35, "breathing_support": "nippv"},
    )
    assert context.status_code == 200
    version = context.json()["state_version"]

    monitoring = _post_json(
        client,
        f"/api/v1/runs/{run_id}/interventions/monitoring",
        {"state_version": version, "monitoring_on": False},
    )
    assert monitoring.status_code == 200
    version = monitoring.json()["state_version"]

    blood = _post_json(
        client,
        f"/api/v1/runs/{run_id}/interventions/blood-level",
        {
            "state_version": version,
            "below_detection_limit": False,
            "detection_limit_mg_per_l": 1.0,
            "concentration_mg_per_l": 9.5,
        },
    )
    assert blood.status_code == 200
    body = blood.json()
    assert len(body["state"]["patient_file_panel"]["context_log"]) >= 3
    assert len(body["state"]["patient_file_panel"]["dose_log"]) == 1
    assert len(body["state"]["patient_file_panel"]["blood_levels"]) == 1


def test_summary_success(client, created_run) -> None:
    run_id = created_run["run_id"]
    response = client.get(f"/api/v1/runs/{run_id}/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["summary"]["rule_name"] == "DEMO"
