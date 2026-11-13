# Purpose: Shared API parsing, validation, and error-response helpers for simulator endpoints.

from __future__ import annotations

import json
from typing import Any

from django.http import HttpRequest, JsonResponse


ERROR_HTTP_STATUS = {
    "invalid_json": 400,
    "missing_field": 400,
    "invalid_type": 400,
    "invalid_enum": 400,
    "out_of_definition": 400,
    "invalid_blood_level_shape": 400,
    "run_not_found": 404,
    "stale_state_version": 409,
    "phase_awaiting_n_requires_submission": 409,
    "phase_not_awaiting_n": 409,
    "day_index_mismatch": 409,
    "phase_awaiting_n_locked": 409,
    "run_converged_locked": 423,
    "method_not_allowed": 405,
}


def error_response(code: str, message: str, details: dict[str, Any] | None = None, run_id: str | None = None) -> JsonResponse:
    payload: dict[str, Any] = {
        "ok": False,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
    }
    if run_id is not None:
        payload["run_id"] = run_id
    return JsonResponse(payload, status=ERROR_HTTP_STATUS.get(code, 500))


def parse_json_body(request: HttpRequest) -> tuple[dict[str, Any] | None, JsonResponse | None]:
    try:
        if not request.body:
            return {}, None
        parsed = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, error_response("invalid_json", "Request body must be valid JSON.")
    if not isinstance(parsed, dict):
        return None, error_response("invalid_type", "Request body must be a JSON object.")
    return parsed, None


def has_field(data: dict[str, Any], field_name: str) -> bool:
    return field_name in data


def is_bool(value: Any) -> bool:
    return isinstance(value, bool)


def is_int_not_bool(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def is_number_not_bool(value: Any) -> bool:
    return (isinstance(value, int) or isinstance(value, float)) and not isinstance(value, bool)


def is_string(value: Any) -> bool:
    return isinstance(value, str)
