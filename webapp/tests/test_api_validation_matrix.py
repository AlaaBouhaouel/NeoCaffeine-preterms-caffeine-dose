# Purpose: Validates API error-code to HTTP-status mapping and rejected request scenarios.

from __future__ import annotations

import json

from simulator.views.api_utils import ERROR_HTTP_STATUS


def _post_json(client, url: str, payload: dict):
    return client.post(url, data=json.dumps(payload), content_type="application/json")


def test_error_http_status_mapping_rows_present() -> None:
    assert ERROR_HTTP_STATUS["invalid_json"] == 400
    assert ERROR_HTTP_STATUS["missing_field"] == 400
    assert ERROR_HTTP_STATUS["invalid_type"] == 400
    assert ERROR_HTTP_STATUS["invalid_enum"] == 400
    assert ERROR_HTTP_STATUS["out_of_definition"] == 400
    assert ERROR_HTTP_STATUS["invalid_blood_level_shape"] == 400
    assert ERROR_HTTP_STATUS["run_not_found"] == 404
    assert ERROR_HTTP_STATUS["stale_state_version"] == 409
    assert ERROR_HTTP_STATUS["phase_awaiting_n_requires_submission"] == 409
    assert ERROR_HTTP_STATUS["phase_not_awaiting_n"] == 409
    assert ERROR_HTTP_STATUS["hour_index_mismatch"] == 409
    assert ERROR_HTTP_STATUS["phase_awaiting_n_locked"] == 409
    assert ERROR_HTTP_STATUS["run_converged_locked"] == 423
    assert ERROR_HTTP_STATUS["method_not_allowed"] == 405


def test_invalid_json_returns_400(client) -> None:
    response = client.post("/api/v1/runs", data="{", content_type="application/json")
    body = response.json()
    assert response.status_code == 400
    assert body["error"]["code"] == "invalid_json"


def test_missing_field_returns_400(client, create_run_payload) -> None:
    payload = dict(create_run_payload)
    payload.pop("patient")
    response = _post_json(client, "/api/v1/runs", payload)
    body = response.json()
    assert response.status_code == 400
    assert body["error"]["code"] == "missing_field"


def test_invalid_type_rejects_bool_as_integer(client, create_run_payload) -> None:
    payload = dict(create_run_payload)
    payload["patient"] = dict(payload["patient"])
    payload["patient"]["birth_weight_g"] = True
    response = _post_json(client, "/api/v1/runs", payload)
    body = response.json()
    assert response.status_code == 400
    assert body["error"]["code"] == "invalid_type"


def test_invalid_enum_returns_400(client, create_run_payload) -> None:
    payload = dict(create_run_payload)
    payload["patient"] = dict(payload["patient"])
    payload["patient"]["sex"] = "invalid"
    response = _post_json(client, "/api/v1/runs", payload)
    body = response.json()
    assert response.status_code == 400
    assert body["error"]["code"] == "invalid_enum"


def test_out_of_definition_on_create_fields(client, create_run_payload) -> None:
    payload = dict(create_run_payload)
    payload["patient"] = dict(payload["patient"])
    payload["patient"]["gestational_age_days_extra"] = 7
    response = _post_json(client, "/api/v1/runs", payload)
    body = response.json()
    assert response.status_code == 400
    assert body["error"]["code"] == "out_of_definition"


def test_run_not_found_returns_404(client) -> None:
    response = client.get("/api/v1/runs/11111111-1111-1111-1111-111111111111/state")
    body = response.json()
    assert response.status_code == 404
    assert body["error"]["code"] == "run_not_found"


def test_stale_state_version_returns_409(client, created_run) -> None:
    run_id = created_run["run_id"]
    response = _post_json(client, f"/api/v1/runs/{run_id}/advance", {"delta_sim_hours": 0.25, "state_version": 0})
    body = response.json()
    assert response.status_code == 409
    assert body["error"]["code"] == "stale_state_version"


def test_phase_awaiting_n_requires_submission_returns_409(client, created_run) -> None:
    run_id = created_run["run_id"]
    first = _post_json(client, f"/api/v1/runs/{run_id}/advance", {"delta_sim_hours": 2.0, "state_version": created_run["state_version"]})
    assert first.status_code == 200
    body_first = first.json()
    second = _post_json(client, f"/api/v1/runs/{run_id}/advance", {"delta_sim_hours": 0.1, "state_version": body_first["state_version"]})
    body_second = second.json()
    assert second.status_code == 409
    assert body_second["error"]["code"] == "phase_awaiting_n_requires_submission"


def test_phase_not_awaiting_n_returns_409(client, created_run) -> None:
    run_id = created_run["run_id"]
    response = _post_json(
        client,
        f"/api/v1/runs/{run_id}/hours/0/n",
        {"observed_n": 1, "state_version": created_run["state_version"]},
    )
    body = response.json()
    assert response.status_code == 409
    assert body["error"]["code"] == "phase_not_awaiting_n"


def test_hour_index_mismatch_returns_409(client, created_run) -> None:
    run_id = created_run["run_id"]
    advanced = _post_json(client, f"/api/v1/runs/{run_id}/advance", {"delta_sim_hours": 1.5, "state_version": created_run["state_version"]})
    body_advanced = advanced.json()
    response = _post_json(
        client,
        f"/api/v1/runs/{run_id}/hours/3/n",
        {"observed_n": 1, "state_version": body_advanced["state_version"]},
    )
    body = response.json()
    assert response.status_code == 409
    assert body["error"]["code"] == "hour_index_mismatch"


def test_phase_awaiting_n_locked_returns_409(client, created_run) -> None:
    run_id = created_run["run_id"]
    advanced = _post_json(client, f"/api/v1/runs/{run_id}/advance", {"delta_sim_hours": 1.0, "state_version": created_run["state_version"]})
    body_advanced = advanced.json()
    response = _post_json(
        client,
        f"/api/v1/runs/{run_id}/interventions/context",
        {
            "state_version": body_advanced["state_version"],
            "fiO2_fraction": 0.4,
            "breathing_support": "cpap",
        },
    )
    body = response.json()
    assert response.status_code == 409
    assert body["error"]["code"] == "phase_awaiting_n_locked"


def test_run_converged_locked_returns_423(client, created_run) -> None:
    run_id = created_run["run_id"]
    state_version = created_run["state_version"]
    for _ in range(24):
        advanced = _post_json(client, f"/api/v1/runs/{run_id}/advance", {"delta_sim_hours": 1.0, "state_version": state_version})
        assert advanced.status_code == 200
        state_version = advanced.json()["state_version"]
        submitted = _post_json(client, f"/api/v1/runs/{run_id}/hours/{_}/n", {"observed_n": 0, "state_version": state_version})
        assert submitted.status_code == 200
        state_version = submitted.json()["state_version"]

    response = _post_json(
        client,
        f"/api/v1/runs/{run_id}/interventions/monitoring",
        {"state_version": state_version, "monitoring_on": False},
    )
    body = response.json()
    assert response.status_code == 423
    assert body["error"]["code"] == "run_converged_locked"


def test_invalid_blood_level_shape_returns_400(client, created_run) -> None:
    run_id = created_run["run_id"]
    response = _post_json(
        client,
        f"/api/v1/runs/{run_id}/interventions/blood-level",
        {
            "state_version": created_run["state_version"],
            "below_detection_limit": True,
            "detection_limit_mg_per_l": 2.0,
            "concentration_mg_per_l": 1.0,
        },
    )
    body = response.json()
    assert response.status_code == 400
    assert body["error"]["code"] == "invalid_blood_level_shape"


def test_out_of_definition_for_dose_and_blood_fields(client, created_run) -> None:
    run_id = created_run["run_id"]
    dose_response = _post_json(
        client,
        f"/api/v1/runs/{run_id}/interventions/dose",
        {
            "state_version": created_run["state_version"],
            "amount": 0,
            "amount_unit": "mg",
            "route": "oral",
            "form": "base",
            "source": "manual",
        },
    )
    assert dose_response.status_code == 400
    assert dose_response.json()["error"]["code"] == "out_of_definition"

    blood_response = _post_json(
        client,
        f"/api/v1/runs/{run_id}/interventions/blood-level",
        {
            "state_version": created_run["state_version"],
            "below_detection_limit": False,
            "detection_limit_mg_per_l": -1.0,
            "concentration_mg_per_l": 0.0,
        },
    )
    assert blood_response.status_code == 400
    assert blood_response.json()["error"]["code"] == "out_of_definition"
