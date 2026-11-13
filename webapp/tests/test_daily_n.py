# Purpose: Verifies the daily N gate (one N per 24 h day), the 7-day demo convergence, and the upgrade of run states stored with hourly N.

from __future__ import annotations

import json
from uuid import UUID

from backend.state_upgrade import upgrade_state
from runs.models import RunSnapshot


def _post_json(client, url: str, payload: dict):
    return client.post(url, data=json.dumps(payload), content_type="application/json")


def _advance_and_submit_day(client, run_id: str, day: int, state_version: int) -> dict:
    advanced = _post_json(client, f"/api/v1/runs/{run_id}/advance", {"delta_sim_hours": 24.0, "state_version": state_version})
    assert advanced.status_code == 200
    assert advanced.json()["state"]["n_gate"]["awaiting_n_for_day_index"] == day
    submitted = _post_json(client, f"/api/v1/runs/{run_id}/days/{day}/n", {"observed_n": 1, "state_version": advanced.json()["state_version"]})
    assert submitted.status_code == 200
    return submitted.json()


def test_no_n_gate_inside_a_day(client, created_run) -> None:
    response = _post_json(client, f"/api/v1/runs/{created_run['run_id']}/advance", {"delta_sim_hours": 23.5, "state_version": created_run["state_version"]})
    state = response.json()["state"]
    assert state["meta"]["phase"] == "playing"
    assert state["time"]["sim_time_hours"] == 23.5
    assert state["time"]["sim_day_index"] == 0


def test_demo_still_playing_after_six_days_and_converged_after_seven(client, created_run) -> None:
    run_id = created_run["run_id"]
    state_version = created_run["state_version"]
    for day in range(6):
        body = _advance_and_submit_day(client, run_id, day, state_version)
        state_version = body["state_version"]
    assert body["state"]["meta"]["phase"] == "playing"
    body = _advance_and_submit_day(client, run_id, 6, state_version)
    assert body["state"]["meta"]["phase"] == "converged"
    assert body["state"]["time"]["sim_time_hours"] == 7 * 24.0


def test_old_hourly_state_is_upgraded(client, created_run) -> None:
    snapshot = RunSnapshot.objects.get(run_id=UUID(created_run["run_id"]))
    state = snapshot.state_json
    state.pop("n_gate")
    state["hour_gate"] = {"editable_hour_index_for_n": 30, "n_prefill_value": 2, "n_input_locked": False, "awaiting_n_for_hour_index": 30}
    state["meta"]["phase"] = "awaiting_n"
    state["time"]["sim_time_hours"] = 31.0
    estimator = state["estimator_panel"]
    estimator.pop("last_day")
    estimator["last_hour"] = {"hour_index": 29, "predicted_n": 1.0, "observed_n": 3}
    estimator["uncertainty_chart"] = [{"hour_index": 30, "value": 0.5}]
    snapshot.state_json = state
    snapshot.save()

    response = client.get(f"/api/v1/runs/{created_run['run_id']}/state")
    assert response.status_code == 200
    upgraded = response.json()["state"]
    assert "hour_gate" not in upgraded
    assert upgraded["n_gate"]["awaiting_n_for_day_index"] is None
    assert upgraded["meta"]["phase"] == "playing"
    assert upgraded["time"]["sim_day_index"] == 1
    assert upgraded["estimator_panel"]["last_day"] == {"day_index": 1, "predicted_n": 1.0, "observed_n": 3}
    assert upgraded["estimator_panel"]["uncertainty_chart"] == [{"day_index": 1, "value": 0.5}]

    advanced = _post_json(client, f"/api/v1/runs/{created_run['run_id']}/advance", {"delta_sim_hours": 1.0, "state_version": response.json()["state_version"]})
    assert advanced.status_code == 200


def test_daily_state_is_left_unchanged(created_run) -> None:
    state = json.loads(json.dumps(created_run["state"]))
    assert upgrade_state(state) == created_run["state"]
