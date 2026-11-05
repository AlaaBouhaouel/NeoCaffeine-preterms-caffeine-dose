# Purpose: URL routing for landing, dashboard, and API placeholders.

from django.urls import path

from simulator.views.api_actions import (
    accept_suggested_dose,
    add_blood_level,
    advance_run,
    change_context,
    give_dose,
    set_monitoring,
    submit_hour_n,
)
from simulator.views.api_runs import create_run
from simulator.views.api_state import get_run_state, get_run_summary
from simulator.views.dashboard import dashboard_view
from simulator.views.landing import landing_view


urlpatterns = [
    path("", landing_view),
    path("runs/<uuid:run_id>/", dashboard_view),
    path("api/v1/runs", create_run),
    path("api/v1/runs/<uuid:run_id>/state", get_run_state),
    path("api/v1/runs/<uuid:run_id>/advance", advance_run),
    path("api/v1/runs/<uuid:run_id>/hours/<int:hour_index>/n", submit_hour_n),
    path("api/v1/runs/<uuid:run_id>/interventions/dose", give_dose),
    path("api/v1/runs/<uuid:run_id>/interventions/dose/accept", accept_suggested_dose),
    path("api/v1/runs/<uuid:run_id>/interventions/context", change_context),
    path("api/v1/runs/<uuid:run_id>/interventions/monitoring", set_monitoring),
    path("api/v1/runs/<uuid:run_id>/interventions/blood-level", add_blood_level),
    path("api/v1/runs/<uuid:run_id>/summary", get_run_summary),
]
