# Purpose: Verifies that landing form data is stored as a patient record plus a per-run patient document, and that the dashboard state is loaded from it.

from __future__ import annotations

import json
from uuid import UUID

from patients.models import PatientRecord
from runs.models import RunSnapshot


def _post_json(client, url: str, payload: dict):
    return client.post(url, data=json.dumps(payload), content_type="application/json")


def test_create_run_stores_patient_record_and_run_document(client, created_run) -> None:
    snapshot = RunSnapshot.objects.get(run_id=UUID(created_run["run_id"]))
    record = PatientRecord.objects.get()
    assert snapshot.patient_id == record.id
    assert record.gestational_age_days == 28 * 7 + 3
    assert record.birth_weight_grams == 980
    assert record.sex == "male"
    assert record.birth_time.isoformat() == "2026-01-15T08:30:00+00:00"

    document = snapshot.patient_document
    assert document["schema_version"] == 1
    assert document["patient_id"] == str(record.patient_id)
    assert document["covariates"]["gestational_age_days"] == 28 * 7 + 3
    assert [entry["support_mode"] for entry in document["context_log"]] == ["cpap"]
    assert [entry["fio2_fraction"] for entry in document["context_log"]] == [0.3]
    assert document["context_log"][0]["time_hours"] == 0.0


def test_dashboard_state_patient_comes_from_stored_patient(client, created_run) -> None:
    record = PatientRecord.objects.get()
    response = client.get(f"/api/v1/runs/{created_run['run_id']}/state")
    assert response.status_code == 200
    patient = response.json()["state"]["patient"]
    assert patient["patient_id"] == str(record.patient_id)
    assert patient["covariates"]["gestational_age_days"] == 28 * 7 + 3
    assert patient["covariates"]["birth_weight_g"] == 980
    assert patient["covariates"]["sex"] == "male"
    assert patient["covariates"]["birth_time"] == "2026-01-15T08:30:00+00:00"
    assert patient["current_weight_g"] == 980
    assert patient["flags"] == []


def test_dashboard_state_ages_follow_simulation_time(client, created_run) -> None:
    run_id = created_run["run_id"]
    _post_json(client, f"/api/v1/runs/{run_id}/advance", {"delta_sim_hours": 0.5, "state_version": created_run["state_version"]})
    patient = client.get(f"/api/v1/runs/{run_id}/state").json()["state"]["patient"]
    assert patient["postnatal_age_hours"] == 0.5
    assert patient["postmenstrual_age_days"] == 28 * 7 + 3 + 0.5 / 24


def test_birth_time_with_offset_is_stored_in_utc(client, create_run_payload) -> None:
    create_run_payload["patient"]["birth_time"] = "2026-01-15T10:30:00+02:00"
    response = _post_json(client, "/api/v1/runs", create_run_payload)
    assert response.status_code == 200
    assert PatientRecord.objects.get().birth_time.isoformat() == "2026-01-15T08:30:00+00:00"


def test_each_submission_creates_a_new_patient(client, create_run_payload) -> None:
    _post_json(client, "/api/v1/runs", create_run_payload)
    _post_json(client, "/api/v1/runs", create_run_payload)
    assert PatientRecord.objects.count() == 2
    assert RunSnapshot.objects.values("patient").distinct().count() == 2


def test_out_of_range_covariate_is_flagged_not_rejected(client, create_run_payload) -> None:
    create_run_payload["patient"]["birth_weight_g"] = 6000
    response = _post_json(client, "/api/v1/runs", create_run_payload)
    assert response.status_code == 200
    flags = client.get(f"/api/v1/runs/{response.json()['run_id']}/state").json()["state"]["patient"]["flags"]
    assert len(flags) == 1
    assert "weight" in flags[0]


def test_new_support_mode_values_are_accepted(client, create_run_payload) -> None:
    for support_mode in ["room_air", "low_flow", "hfnc", "cpap", "nippv", "invasive_ventilation"]:
        create_run_payload["initial_context"]["breathing_support"] = support_mode
        response = _post_json(client, "/api/v1/runs", create_run_payload)
        assert response.status_code == 200


def test_state_has_no_retention_field(client, created_run) -> None:
    assert "retention_delete_after" not in created_run["state"]["run"]
    assert not hasattr(RunSnapshot, "delete_after")
