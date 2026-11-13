# Purpose: Verifies the live demo model (proposal 06): concentration from doses, daily convergence over 7 days, confidence gate and dose suggestion, and bounded state size.

from __future__ import annotations

import json
import math

import pytest

from backend.demo import thresholds as demo
from backend.demo import updater


def _post_json(client, url: str, payload: dict):
    return client.post(url, data=json.dumps(payload), content_type="application/json")


def _dose(client, run_id: str, state_version: int, amount: float) -> dict:
    response = _post_json(client, f"/api/v1/runs/{run_id}/interventions/dose", {
        "state_version": state_version, "amount": amount, "amount_unit": "mg_per_kg",
        "route": "iv", "form": "citrate", "source": "manual",
    })
    assert response.status_code == 200
    return response.json()


def _advance(client, run_id: str, state_version: int, hours: float) -> dict:
    response = _post_json(client, f"/api/v1/runs/{run_id}/advance", {"delta_sim_hours": hours, "state_version": state_version})
    assert response.status_code == 200
    return response.json()


def _submit_prefill(client, run_id: str, body: dict) -> dict:
    day = body["state"]["n_gate"]["awaiting_n_for_day_index"]
    observed = body["state"]["n_gate"]["n_prefill_value"]
    response = _post_json(client, f"/api/v1/runs/{run_id}/days/{day}/n", {"observed_n": observed, "state_version": body["state_version"]})
    assert response.status_code == 200
    return response.json()


def _run_days(client, created_run: dict, days: int) -> dict:
    run_id, body = created_run["run_id"], created_run
    body = _dose(client, run_id, body["state_version"], 20.0)
    for _ in range(days):
        body = _advance(client, run_id, body["state_version"], 24.0)
        body = _submit_prefill(client, run_id, body)
        if body["state"]["meta"]["phase"] == "playing":
            body = _dose(client, run_id, body["state_version"], 5.0)
    return body


def test_new_run_is_caffeine_naive_with_offset_estimates_and_closed_gate(created_run) -> None:
    state = created_run["state"]
    assert state["pharmacology_panel"]["concentration_est_mg_per_l"][-1]["v"] == 0.0
    assert state["pharmacology_panel"]["true_concentration_mg_per_l"][-1]["v"] == 0.0
    cl = next(row for row in state["estimator_panel"]["theta"] if row["key"] == "log_CL")
    assert cl["natural_estimate"] == pytest.approx(cl["true_natural"] * demo.DEMO_START_FACTORS["log_CL"])
    assert cl["true_natural"] == pytest.approx(demo.DEMO_TRUE_CL_L_PER_H_PER_KG * 0.98)
    assert state["decision_panel"]["confidence_gate"]["open"] is False
    assert state["decision_panel"]["suggested_dose"]["amount"] == demo.DEMO_STANDARD_REGIMEN_MG_PER_KG_CITRATE
    assert state["monitor_panel"]["demo_apnea_rate_per_hour"] == pytest.approx(demo.DEMO_BASELINE_APNEA_RATE_PER_HOUR)


def test_dose_raises_concentration_which_then_decays(client, created_run) -> None:
    run_id = created_run["run_id"]
    body = _dose(client, run_id, created_run["state_version"], 20.0)
    expected_peak = 20.0 * 0.98 * demo.DEMO_CITRATE_TO_BASE / (demo.DEMO_TRUE_V_L_PER_KG * 0.98)
    assert body["state"]["pharmacology_panel"]["true_concentration_mg_per_l"][-1]["v"] == pytest.approx(expected_peak)
    body = _advance(client, run_id, body["state_version"], 10.0)
    true_curve = body["state"]["pharmacology_panel"]["true_concentration_mg_per_l"]
    elimination = demo.DEMO_TRUE_CL_L_PER_H_PER_KG / demo.DEMO_TRUE_V_L_PER_KG
    assert true_curve[-1]["t_sim_hours"] == 10.0
    assert true_curve[-1]["v"] == pytest.approx(expected_peak * math.exp(-elimination * 10.0))
    assert body["state"]["monitor_panel"]["demo_apnea_rate_per_hour"] < demo.DEMO_BASELINE_APNEA_RATE_PER_HOUR


def test_one_curve_point_per_simulated_hour(client, created_run) -> None:
    body = _advance(client, created_run["run_id"], created_run["state_version"], 5.5)
    hours = [point["t_sim_hours"] for point in body["state"]["pharmacology_panel"]["true_concentration_mg_per_l"]]
    assert hours == [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]


def test_estimates_converge_and_gate_opens_after_seven_days(client, created_run) -> None:
    body = _run_days(client, created_run, 7)
    state = body["state"]
    assert state["meta"]["phase"] == "converged"
    for row in state["estimator_panel"]["theta"]:
        assert abs(row["natural_estimate"] - row["true_natural"]) / row["true_natural"] < 0.01
    assert len(state["estimator_panel"]["trajectory"]) == 8
    decision = state["decision_panel"]
    assert decision["confidence_gate"]["open"] is True
    expected = demo.DEMO_TARGET_CONCENTRATION_MG_PER_L * demo.DEMO_TRUE_CL_L_PER_H_PER_KG * 24 / demo.DEMO_CITRATE_TO_BASE
    assert abs(decision["suggested_dose"]["amount"] - expected) <= demo.DEMO_DOSE_ROUNDING_MG_PER_KG
    assert 0.0 <= decision["safety_share_vs_limit"] <= 1.0


def test_predicted_and_observed_daily_counts_are_recorded(client, created_run) -> None:
    body = _run_days(client, created_run, 1)
    last_day = body["state"]["estimator_panel"]["last_day"]
    assert last_day["day_index"] == 0
    assert last_day["predicted_n"] > 0
    assert last_day["observed_n"] is not None
    assert len(body["state"]["estimator_panel"]["diagnostics"]["loss_negative_log_likelihood"]) == 1


def test_prefill_is_reproducible_for_the_same_seed(client, create_run_payload) -> None:
    prefills = []
    for _ in range(2):
        created = _post_json(client, "/api/v1/runs", create_run_payload).json()
        advanced = _advance(client, created["run_id"], created["state_version"], 24.0)
        prefills.append(advanced["state"]["n_gate"]["n_prefill_value"])
    assert prefills[0] == prefills[1]


def test_state_stays_small_after_seven_days(client, created_run) -> None:
    body = _run_days(client, created_run, 7)
    assert len(json.dumps(body["state"])) < 200_000


def test_run_created_before_the_live_demo_gets_a_demo_model(created_run) -> None:
    state = json.loads(json.dumps(created_run["state"]))
    state.pop("demo_model")
    updater.ensure_initialized(state)
    assert state["demo_model"]["weight_kg"] == pytest.approx(0.98)
    assert len(state["estimator_panel"]["trajectory"]) == 1
