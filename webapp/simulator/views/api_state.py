# Purpose: State and summary retrieval handlers for persisted simulator runs.

from __future__ import annotations

from uuid import UUID

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET

from backend.selectors import get_active_simulation_backend
from simulator.views.api_utils import error_response


@require_GET
def get_run_state(_request: HttpRequest, run_id: UUID) -> JsonResponse:
    backend = get_active_simulation_backend()
    result = backend.get_state(run_id)
    if not result.get("ok"):
        err = result.get("error", {})
        return error_response(err.get("code", "run_not_found"), err.get("message", "Request failed."), err.get("details", {}), result.get("run_id"))
    return JsonResponse(result)


@require_GET
def get_run_summary(_request: HttpRequest, run_id: UUID) -> JsonResponse:
    backend = get_active_simulation_backend()
    result = backend.get_summary(run_id)
    if not result.get("ok"):
        err = result.get("error", {})
        return error_response(err.get("code", "run_not_found"), err.get("message", "Request failed."), err.get("details", {}), result.get("run_id"))
    return JsonResponse(result)
