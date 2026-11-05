# Purpose: Dashboard page handler keyed by run ID.

from uuid import UUID

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def dashboard_view(request: HttpRequest, run_id: UUID) -> HttpResponse:
    return render(request, "dashboard.html", {"run_id": str(run_id)})
