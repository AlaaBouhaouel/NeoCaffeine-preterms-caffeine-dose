# Purpose: Action handlers with contract validation for advance, N submission, and interventions.

from __future__ import annotations

from uuid import UUID

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from backend.selectors import get_backend_runtime
from simulator.views.api_utils import (
    error_response,
    has_field,
    is_bool,
    is_int_not_bool,
    is_number_not_bool,
    is_string,
    parse_json_body,
)


DOSE_UNITS = {"mg_per_kg", "mg"}
DOSE_ROUTES = {"intravenous", "oral"}
DOSE_FORMS = {"citrate", "base"}
DOSE_SOURCES = {"manual", "suggested"}
BREATHING_SUPPORT_VALUES = {
    "room_air",
    "low_flow_cannula",
    "high_flow_cannula",
    "cpap",
    "nippv",
    "invasive_ventilation",
}


def _backend_error(result: dict) -> JsonResponse:
    err = result.get("error", {})
    return error_response(err.get("code", "invalid_json"), err.get("message", "Request failed."), err.get("details", {}), result.get("run_id"))


def _validate_state_version(payload: dict) -> JsonResponse | None:
    if not has_field(payload, "state_version"):
        return error_response("missing_field", "Missing required field: state_version.")
    if not is_int_not_bool(payload["state_version"]):
        return error_response("invalid_type", "Field state_version must be an integer.")
    return None


@csrf_exempt
@require_POST
def advance_run(request: HttpRequest, run_id: UUID) -> JsonResponse:
    payload, error = parse_json_body(request)
    if error is not None:
        return error
    if payload is None:
        return error_response("invalid_json", "Request body must be valid JSON.")
    version_error = _validate_state_version(payload)
    if version_error is not None:
        return version_error
    if not has_field(payload, "delta_sim_hours"):
        return error_response("missing_field", "Missing required field: delta_sim_hours.")
    if not is_number_not_bool(payload["delta_sim_hours"]):
        return error_response("invalid_type", "Field delta_sim_hours must be a number.")
    if float(payload["delta_sim_hours"]) <= 0:
        return error_response("out_of_definition", "Field delta_sim_hours must be greater than 0.")

    runtime = get_backend_runtime()
    result = runtime.advance(run_id=run_id, delta_sim_hours=float(payload["delta_sim_hours"]), state_version=payload["state_version"])
    if not result.get("ok"):
        return _backend_error(result)
    return JsonResponse(result)


@csrf_exempt
@require_POST
def submit_hour_n(request: HttpRequest, run_id: UUID, hour_index: int) -> JsonResponse:
    payload, error = parse_json_body(request)
    if error is not None:
        return error
    if payload is None:
        return error_response("invalid_json", "Request body must be valid JSON.")
    version_error = _validate_state_version(payload)
    if version_error is not None:
        return version_error
    if not has_field(payload, "observed_n"):
        return error_response("missing_field", "Missing required field: observed_n.")
    if not is_int_not_bool(payload["observed_n"]):
        return error_response("invalid_type", "Field observed_n must be an integer.")
    if payload["observed_n"] < 0:
        return error_response("out_of_definition", "Field observed_n must be greater than or equal to 0.")

    runtime = get_backend_runtime()
    result = runtime.submit_observed_n(
        run_id=run_id,
        hour_index=hour_index,
        observed_n=payload["observed_n"],
        state_version=payload["state_version"],
    )
    if not result.get("ok"):
        return _backend_error(result)
    return JsonResponse(result)


@csrf_exempt
@require_POST
def give_dose(request: HttpRequest, run_id: UUID) -> JsonResponse:
    payload, error = parse_json_body(request)
    if error is not None:
        return error
    if payload is None:
        return error_response("invalid_json", "Request body must be valid JSON.")
    version_error = _validate_state_version(payload)
    if version_error is not None:
        return version_error

    required = ["amount", "amount_unit", "route", "form", "source"]
    for field_name in required:
        if not has_field(payload, field_name):
            return error_response("missing_field", f"Missing required field: {field_name}.")

    if not is_number_not_bool(payload["amount"]):
        return error_response("invalid_type", "Field amount must be a number.")
    if float(payload["amount"]) <= 0:
        return error_response("out_of_definition", "Field amount must be greater than 0.")
    if not is_string(payload["amount_unit"]):
        return error_response("invalid_type", "Field amount_unit must be a string.")
    if payload["amount_unit"] not in DOSE_UNITS:
        return error_response("invalid_enum", "Field amount_unit has an invalid value.")
    if not is_string(payload["route"]):
        return error_response("invalid_type", "Field route must be a string.")
    if payload["route"] not in DOSE_ROUTES:
        return error_response("invalid_enum", "Field route has an invalid value.")
    if not is_string(payload["form"]):
        return error_response("invalid_type", "Field form must be a string.")
    if payload["form"] not in DOSE_FORMS:
        return error_response("invalid_enum", "Field form has an invalid value.")
    if not is_string(payload["source"]):
        return error_response("invalid_type", "Field source must be a string.")
    if payload["source"] not in DOSE_SOURCES:
        return error_response("invalid_enum", "Field source has an invalid value.")

    runtime = get_backend_runtime()
    result = runtime.give_dose(run_id=run_id, payload=payload, state_version=payload["state_version"])
    if not result.get("ok"):
        return _backend_error(result)
    return JsonResponse(result)


@csrf_exempt
@require_POST
def accept_suggested_dose(request: HttpRequest, run_id: UUID) -> JsonResponse:
    payload, error = parse_json_body(request)
    if error is not None:
        return error
    if payload is None:
        return error_response("invalid_json", "Request body must be valid JSON.")
    version_error = _validate_state_version(payload)
    if version_error is not None:
        return version_error

    runtime = get_backend_runtime()
    result = runtime.accept_suggested_dose(run_id=run_id, state_version=payload["state_version"])
    if not result.get("ok"):
        return _backend_error(result)
    return JsonResponse(result)


@csrf_exempt
@require_POST
def change_context(request: HttpRequest, run_id: UUID) -> JsonResponse:
    payload, error = parse_json_body(request)
    if error is not None:
        return error
    if payload is None:
        return error_response("invalid_json", "Request body must be valid JSON.")
    version_error = _validate_state_version(payload)
    if version_error is not None:
        return version_error

    required = ["fiO2_fraction", "breathing_support"]
    for field_name in required:
        if not has_field(payload, field_name):
            return error_response("missing_field", f"Missing required field: {field_name}.")

    if not is_number_not_bool(payload["fiO2_fraction"]):
        return error_response("invalid_type", "Field fiO2_fraction must be a number.")
    if not (0.21 <= float(payload["fiO2_fraction"]) <= 1.0):
        return error_response("out_of_definition", "Field fiO2_fraction must be between 0.21 and 1.0.")
    if not is_string(payload["breathing_support"]):
        return error_response("invalid_type", "Field breathing_support must be a string.")
    if payload["breathing_support"] not in BREATHING_SUPPORT_VALUES:
        return error_response("invalid_enum", "Field breathing_support has an invalid value.")

    runtime = get_backend_runtime()
    result = runtime.change_context(run_id=run_id, payload=payload, state_version=payload["state_version"])
    if not result.get("ok"):
        return _backend_error(result)
    return JsonResponse(result)


@csrf_exempt
@require_POST
def set_monitoring(request: HttpRequest, run_id: UUID) -> JsonResponse:
    payload, error = parse_json_body(request)
    if error is not None:
        return error
    if payload is None:
        return error_response("invalid_json", "Request body must be valid JSON.")
    version_error = _validate_state_version(payload)
    if version_error is not None:
        return version_error
    if not has_field(payload, "monitoring_on"):
        return error_response("missing_field", "Missing required field: monitoring_on.")
    if not is_bool(payload["monitoring_on"]):
        return error_response("invalid_type", "Field monitoring_on must be a boolean.")

    runtime = get_backend_runtime()
    result = runtime.set_monitoring(run_id=run_id, payload=payload, state_version=payload["state_version"])
    if not result.get("ok"):
        return _backend_error(result)
    return JsonResponse(result)


@csrf_exempt
@require_POST
def add_blood_level(request: HttpRequest, run_id: UUID) -> JsonResponse:
    payload, error = parse_json_body(request)
    if error is not None:
        return error
    if payload is None:
        return error_response("invalid_json", "Request body must be valid JSON.")
    version_error = _validate_state_version(payload)
    if version_error is not None:
        return version_error
    if not has_field(payload, "concentration_mg_per_l"):
        return error_response("missing_field", "Missing required field: concentration_mg_per_l.")

    below_detection_limit = payload.get("below_detection_limit", False)
    if not is_bool(below_detection_limit):
        return error_response("invalid_type", "Field below_detection_limit must be a boolean.")

    detection_limit = payload.get("detection_limit_mg_per_l")
    if detection_limit is not None and not is_number_not_bool(detection_limit):
        return error_response("invalid_type", "Field detection_limit_mg_per_l must be a number or null.")
    if detection_limit is not None and float(detection_limit) < 0:
        return error_response("out_of_definition", "Field detection_limit_mg_per_l must be greater than or equal to 0.")

    concentration = payload["concentration_mg_per_l"]
    if below_detection_limit:
        if concentration is not None:
            return error_response("invalid_blood_level_shape", "concentration_mg_per_l must be null when below_detection_limit is true.")
    else:
        if not is_number_not_bool(concentration):
            return error_response("invalid_type", "Field concentration_mg_per_l must be a number when below_detection_limit is false.")
        if float(concentration) < 0:
            return error_response("out_of_definition", "Field concentration_mg_per_l must be greater than or equal to 0.")

    payload["below_detection_limit"] = below_detection_limit
    payload["detection_limit_mg_per_l"] = detection_limit

    runtime = get_backend_runtime()
    result = runtime.add_blood_level(run_id=run_id, payload=payload, state_version=payload["state_version"])
    if not result.get("ok"):
        return _backend_error(result)
    return JsonResponse(result)
