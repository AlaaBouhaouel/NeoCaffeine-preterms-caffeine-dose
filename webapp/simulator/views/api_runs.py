# Purpose: Run-creation API handler with strict request validation per approved contract.

from __future__ import annotations

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from backend.contracts.schemas import BREATHING_SUPPORT_VALUES, SEX_VALUES
from backend.patient_bridge import birth_time_from_text
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


@csrf_exempt
@require_POST
def create_run(request: HttpRequest) -> JsonResponse:
    payload, error = parse_json_body(request)
    if error is not None:
        return error
    if payload is None:
        return error_response("invalid_json", "Request body must be valid JSON.")

    if not has_field(payload, "patient"):
        return error_response("missing_field", "Missing required field: patient.")
    if not isinstance(payload["patient"], dict):
        return error_response("invalid_type", "Field patient must be an object.")
    patient = payload["patient"]

    if not has_field(payload, "initial_context"):
        return error_response("missing_field", "Missing required field: initial_context.")
    if not isinstance(payload["initial_context"], dict):
        return error_response("invalid_type", "Field initial_context must be an object.")
    initial_context = payload["initial_context"]

    required_patient = ["gestational_age_weeks", "gestational_age_days_extra", "birth_weight_g", "sex", "birth_time"]
    for field_name in required_patient:
        if not has_field(patient, field_name):
            return error_response("missing_field", f"Missing required field: patient.{field_name}.")

    if not is_int_not_bool(patient["gestational_age_weeks"]):
        return error_response("invalid_type", "Field patient.gestational_age_weeks must be an integer.")
    if not is_int_not_bool(patient["gestational_age_days_extra"]):
        return error_response("invalid_type", "Field patient.gestational_age_days_extra must be an integer.")
    if not (0 <= patient["gestational_age_days_extra"] <= 6):
        return error_response("out_of_definition", "Field patient.gestational_age_days_extra must be between 0 and 6.")
    if not is_int_not_bool(patient["birth_weight_g"]):
        return error_response("invalid_type", "Field patient.birth_weight_g must be an integer.")
    if not is_string(patient["sex"]):
        return error_response("invalid_type", "Field patient.sex must be a string.")
    if patient["sex"] not in SEX_VALUES:
        return error_response("invalid_enum", "Field patient.sex has an invalid value.")
    if not is_string(patient["birth_time"]):
        return error_response("invalid_type", "Field patient.birth_time must be a string.")
    if birth_time_from_text(patient["birth_time"]) is None:
        return error_response("invalid_type", "Field patient.birth_time must be an ISO 8601 timestamp with a time zone.")

    required_context = ["fiO2_fraction", "breathing_support", "monitoring_on"]
    for field_name in required_context:
        if not has_field(initial_context, field_name):
            return error_response("missing_field", f"Missing required field: initial_context.{field_name}.")

    if not is_number_not_bool(initial_context["fiO2_fraction"]):
        return error_response("invalid_type", "Field initial_context.fiO2_fraction must be a number.")
    if not (0.21 <= float(initial_context["fiO2_fraction"]) <= 1.0):
        return error_response("out_of_definition", "Field initial_context.fiO2_fraction must be between 0.21 and 1.0.")
    if not is_string(initial_context["breathing_support"]):
        return error_response("invalid_type", "Field initial_context.breathing_support must be a string.")
    if initial_context["breathing_support"] not in BREATHING_SUPPORT_VALUES:
        return error_response("invalid_enum", "Field initial_context.breathing_support has an invalid value.")
    if not is_bool(initial_context["monitoring_on"]):
        return error_response("invalid_type", "Field initial_context.monitoring_on must be a boolean.")

    random_seed = payload.get("random_seed")
    if random_seed is not None and not is_int_not_bool(random_seed):
        return error_response("invalid_type", "Field random_seed must be an integer or null.")

    runtime = get_backend_runtime()
    result = runtime.create_run(patient=patient, initial_context=initial_context, random_seed=random_seed)
    if not result.get("ok"):
        err = result.get("error", {})
        return error_response(err.get("code", "invalid_json"), err.get("message", "Request failed."), err.get("details", {}), result.get("run_id"))
    return JsonResponse(result)
