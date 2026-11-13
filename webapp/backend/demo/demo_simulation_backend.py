# Purpose: Demo backend implementing stateful simulation behavior; the patient comes from neocaffeine.patient and is persisted per run.

from __future__ import annotations

import math
import random
from typing import Any
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone

from backend.demo import updater
from backend.demo.thresholds import DEMO_CONVERGENCE_DAY_INDEX, HOURS_PER_DAY
from backend.patient_bridge import build_patient, patient_document, patient_from_document, patient_state
from backend.state_upgrade import upgrade_state
from neocaffeine.clock.clock_errors import ClockError
from neocaffeine.patient.patient_errors import PatientError
from patients.repositories import create_patient_record
from runs.repositories import create_run_snapshot, get_run_snapshot, save_run_state


class DemoSimulationBackend:
    def _error(self, code: str, message: str, details: dict[str, Any] | None = None, run_id: UUID | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "ok": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            },
        }
        if run_id is not None:
            payload["run_id"] = str(run_id)
        return payload

    def _envelope(self, run_id: UUID, state_version: int, state: dict[str, Any]) -> dict[str, Any]:
        state["versioning"]["state_version"] = state_version
        state["versioning"]["server_time"] = timezone.now().isoformat()
        state["run"]["last_updated_at"] = timezone.now().isoformat()
        return {
            "ok": True,
            "run_id": str(run_id),
            "server_time": state["versioning"]["server_time"],
            "state_version": state_version,
            "state": state,
            "warnings": [],
        }

    def _get_snapshot(self, run_id: UUID):
        try:
            snapshot = get_run_snapshot(run_id)
        except ObjectDoesNotExist:
            return None
        upgrade_state(snapshot.state_json)
        updater.ensure_initialized(snapshot.state_json)
        return snapshot

    def _update_derived_times(self, state: dict[str, Any]) -> None:
        sim_time_hours = float(state["time"]["sim_time_hours"])
        ga_days = int(state["patient"]["covariates"]["gestational_age_days"])
        state["patient"]["postnatal_age_hours"] = sim_time_hours
        state["patient"]["postmenstrual_age_days"] = ga_days + (sim_time_hours / 24.0)
        state["time"]["sim_hour_index"] = int(math.floor(sim_time_hours))
        state["time"]["hour_progress_01"] = sim_time_hours - math.floor(sim_time_hours)
        state["time"]["sim_day_index"] = int(math.floor(sim_time_hours / HOURS_PER_DAY))
        state["time"]["day_progress_01"] = (sim_time_hours % HOURS_PER_DAY) / HOURS_PER_DAY

    def _current_context_row(self, state: dict[str, Any]) -> dict[str, Any]:
        return {
            "t_sim_hours": float(state["time"]["sim_time_hours"]),
            "fiO2_fraction": float(state["context"]["fiO2_fraction"]),
            "breathing_support": str(state["context"]["breathing_support"]),
            "monitoring_on": bool(state["context"]["monitoring_on"]),
        }

    def _persist_and_wrap(self, snapshot, state: dict[str, Any]) -> dict[str, Any]:
        next_version = snapshot.state_version + 1
        saved = save_run_state(snapshot.run_id, next_version, state)
        return self._envelope(saved.run_id, saved.state_version, saved.state_json)

    def create_run(self, patient: dict[str, Any], initial_context: dict[str, Any], random_seed: int | None = None) -> dict[str, Any]:
        try:
            new_patient = build_patient(patient, initial_context)
        except (PatientError, ClockError) as error:
            return self._error("out_of_definition", str(error))
        created_at = timezone.now()
        chosen_seed = random_seed if random_seed is not None else random.randint(1, 10_000_000)
        state = {
            "meta": {
                "demo_data": True,
                "phase": "playing",
                "status_text": "Playing",
            },
            "versioning": {
                "state_version": 1,
                "server_time": created_at.isoformat(),
            },
            "run": {
                "run_id": "",
                "created_at": created_at.isoformat(),
                "last_updated_at": created_at.isoformat(),
                "random_seed": chosen_seed,
            },
            "time": {
                "sim_time_hours": 0.0,
                "sim_hour_index": 0,
                "hour_progress_01": 0.0,
                "sim_day_index": 0,
                "day_progress_01": 0.0,
                "last_advanced_hours": 0.0,
            },
            "patient": patient_state(new_patient, 0.0),
            "context": {
                "fiO2_fraction": float(initial_context["fiO2_fraction"]),
                "breathing_support": initial_context["breathing_support"],
                "monitoring_on": bool(initial_context["monitoring_on"]),
            },
            "n_gate": {
                "editable_day_index_for_n": None,
                "n_prefill_value": None,
                "n_input_locked": True,
                "awaiting_n_for_day_index": None,
            },
            "monitor_panel": {
                "demo_badge": True,
                "sampling_hz_equivalent": 1,
                "traces": {
                    "heart_rate": [{"t_sim_hours": 0.0, "v": 145.0}],
                    "spo2": [{"t_sim_hours": 0.0, "v": 96.0}],
                    "respiration": [{"t_sim_hours": 0.0, "v": 36.0}],
                },
                "tiles": {
                    "heart_rate_bpm": 145.0,
                    "spo2_pct": 96.0,
                    "resp_rate_bpm": 36.0,
                },
                "events": [],
                "demo_apnea_rate_per_hour": 0.0,
                "demo_true_concentration_mg_per_l": 0.0,
            },
            "pharmacology_panel": {
                "demo_badge": True,
                "concentration_est_mg_per_l": [{"t_sim_hours": 0.0, "v": 7.0}],
                "concentration_band_mg_per_l": [{"t_sim_hours": 0.0, "lo": 6.5, "hi": 7.5}],
                "concentration_bounds_mg_per_l": {"min": 5.0, "max": 20.0},
                "dose_markers": [],
                "true_concentration_mg_per_l": [{"t_sim_hours": 0.0, "v": 7.2}],
            },
            "estimator_panel": {
                "demo_badge": True,
                "theta": [
                    {
                        "key": "log_CL",
                        "label": "log CL",
                        "transformed_estimate": -2.3,
                        "transformed_sd": 0.4,
                        "natural_estimate": 0.10,
                        "natural_unit": "L/h",
                        "natural_interval_90": {"lo": 0.07, "hi": 0.14},
                        "sparkline_transformed": [{"t_sim_hours": 0.0, "v": -2.3}],
                        "true_transformed": -2.25,
                        "true_natural": 0.11,
                    },
                    {
                        "key": "log_V",
                        "label": "log V",
                        "transformed_estimate": 0.75,
                        "transformed_sd": 0.3,
                        "natural_estimate": 2.12,
                        "natural_unit": "L",
                        "natural_interval_90": {"lo": 1.60, "hi": 2.80},
                        "sparkline_transformed": [{"t_sim_hours": 0.0, "v": 0.75}],
                        "true_transformed": 0.80,
                        "true_natural": 2.23,
                    },
                    {
                        "key": "logit_Emax",
                        "label": "logit Emax",
                        "transformed_estimate": 0.6,
                        "transformed_sd": 0.5,
                        "natural_estimate": 0.65,
                        "natural_unit": "fraction",
                        "natural_interval_90": {"lo": 0.45, "hi": 0.82},
                        "sparkline_transformed": [{"t_sim_hours": 0.0, "v": 0.6}],
                        "true_transformed": 0.55,
                        "true_natural": 0.63,
                    },
                    {
                        "key": "log_EC50",
                        "label": "log EC50",
                        "transformed_estimate": 2.2,
                        "transformed_sd": 0.45,
                        "natural_estimate": 9.03,
                        "natural_unit": "mg/L",
                        "natural_interval_90": {"lo": 5.8, "hi": 13.4},
                        "sparkline_transformed": [{"t_sim_hours": 0.0, "v": 2.2}],
                        "true_transformed": 2.1,
                        "true_natural": 8.17,
                    },
                    {
                        "key": "log_beta_M",
                        "label": "log beta_M",
                        "transformed_estimate": -1.4,
                        "transformed_sd": 0.25,
                        "natural_estimate": 0.246,
                        "natural_unit": "per_week",
                        "natural_interval_90": {"lo": 0.16, "hi": 0.36},
                        "sparkline_transformed": [{"t_sim_hours": 0.0, "v": -1.4}],
                        "true_transformed": -1.35,
                        "true_natural": 0.26,
                    },
                ],
                "last_day": {
                    "day_index": 0,
                    "predicted_n": 0.0,
                    "observed_n": None,
                },
                "diagnostics": {
                    "loss_negative_log_likelihood": [],
                    "newton_iterations_last_update": 0,
                    "gradient_norm_last_update": 0.0,
                },
                "uncertainty_chart": [{"day_index": 0, "value": 1.0}],
            },
            "patient_file_panel": {
                "demo_badge": True,
                "dose_log": [],
                "event_log": [],
                "blood_levels": [],
                "context_log": [],
            },
            "decision_panel": {
                "demo_badge": True,
                "target_concentration_mg_per_l": 10.0,
                "suggested_dose": {
                    "amount": 5.0,
                    "amount_unit": "mg_per_kg",
                    "route": "iv",
                    "form": "citrate",
                },
                "safety_share_vs_limit": 0.15,
                "confidence_gate": {
                    "open": True,
                    "reason": "Demo confidence gate open.",
                },
            },
            "convergence": {
                "is_converged": False,
                "rule_name": "DEMO",
                "summary": None,
            },
            "ui_contract": {
                "true_values_always_in_payload": True,
                "show_true_values_toggle_is_client_side_only": True,
            },
        }
        state["patient_file_panel"]["context_log"].append(self._current_context_row(state))
        updater.initialize(state, float(new_patient.covariates.birth_weight_grams) / 1000.0)
        with transaction.atomic():
            patient_record = create_patient_record(new_patient.covariates)
            snapshot = create_run_snapshot(
                state_json=state,
                patient=patient_record,
                patient_document=patient_document(new_patient),
            )
            state["run"]["run_id"] = str(snapshot.run_id)
            snapshot = save_run_state(snapshot.run_id, snapshot.state_version, state)
        return self._envelope(snapshot.run_id, snapshot.state_version, snapshot.state_json)

    def get_state(self, run_id: UUID) -> dict[str, Any]:
        snapshot = self._get_snapshot(run_id)
        if snapshot is None:
            return self._error("run_not_found", "Run was not found.", run_id=run_id)
        state = snapshot.state_json
        if snapshot.patient_document is not None:
            stored_patient = patient_from_document(snapshot.patient_document)
            state["patient"] = patient_state(stored_patient, float(state["time"]["sim_time_hours"]))
        return self._envelope(snapshot.run_id, snapshot.state_version, state)

    def advance(self, run_id: UUID, delta_sim_hours: float, state_version: int) -> dict[str, Any]:
        snapshot = self._get_snapshot(run_id)
        if snapshot is None:
            return self._error("run_not_found", "Run was not found.", run_id=run_id)
        state = snapshot.state_json
        current_time = float(state["time"]["sim_time_hours"])
        current_day = int(math.floor(current_time / HOURS_PER_DAY))
        boundary = float((current_day + 1) * HOURS_PER_DAY)
        requested_target = current_time + delta_sim_hours
        if requested_target >= boundary:
            new_time = boundary
            state["meta"]["phase"] = "awaiting_n"
            state["meta"]["status_text"] = "Awaiting N"
            awaiting_day = current_day
            state["n_gate"]["awaiting_n_for_day_index"] = awaiting_day
            state["n_gate"]["editable_day_index_for_n"] = awaiting_day
            state["n_gate"]["n_prefill_value"] = updater.daily_count_prefill(state, awaiting_day)
            state["n_gate"]["n_input_locked"] = False
        else:
            new_time = requested_target
            state["meta"]["phase"] = "playing"
            state["meta"]["status_text"] = "Playing"
        advanced_hours = new_time - current_time
        state["time"]["sim_time_hours"] = new_time
        state["time"]["last_advanced_hours"] = advanced_hours
        self._update_derived_times(state)
        updater.on_advance(state)
        return self._persist_and_wrap(snapshot, state)

    def submit_observed_n(self, run_id: UUID, day_index: int, observed_n: int, state_version: int) -> dict[str, Any]:
        snapshot = self._get_snapshot(run_id)
        if snapshot is None:
            return self._error("run_not_found", "Run was not found.", run_id=run_id)
        state = snapshot.state_json

        updater.on_daily_n(state, day_index, observed_n)

        state["n_gate"]["awaiting_n_for_day_index"] = None
        state["n_gate"]["editable_day_index_for_n"] = None
        state["n_gate"]["n_prefill_value"] = None
        state["n_gate"]["n_input_locked"] = True

        if day_index >= DEMO_CONVERGENCE_DAY_INDEX:
            state["meta"]["phase"] = "converged"
            state["meta"]["status_text"] = "Converged"
            state["convergence"]["is_converged"] = True
            state["convergence"]["rule_name"] = "DEMO"
            state["convergence"]["summary"] = self._build_summary(state)
        else:
            state["meta"]["phase"] = "playing"
            state["meta"]["status_text"] = "Playing"
        return self._persist_and_wrap(snapshot, state)

    def give_dose(self, run_id: UUID, payload: dict[str, Any], state_version: int) -> dict[str, Any]:
        snapshot = self._get_snapshot(run_id)
        if snapshot is None:
            return self._error("run_not_found", "Run was not found.", run_id=run_id)
        state = snapshot.state_json
        now_t = float(state["time"]["sim_time_hours"])
        marker = {
            "id": f"dose_{len(state['patient_file_panel']['dose_log']) + 1}",
            "t_sim_hours": now_t,
            "amount": payload["amount"],
            "amount_unit": payload["amount_unit"],
            "route": payload["route"],
            "form": payload["form"],
            "source": payload["source"],
        }
        state["patient_file_panel"]["dose_log"].append(marker)
        state["pharmacology_panel"]["dose_markers"].append(marker)
        updater.on_dose(state)
        return self._persist_and_wrap(snapshot, state)

    def accept_suggested_dose(self, run_id: UUID, state_version: int) -> dict[str, Any]:
        snapshot = self._get_snapshot(run_id)
        if snapshot is None:
            return self._error("run_not_found", "Run was not found.", run_id=run_id)
        state = snapshot.state_json
        suggested = state["decision_panel"]["suggested_dose"].copy()
        return self.give_dose(
            run_id,
            {
                "amount": suggested["amount"],
                "amount_unit": suggested["amount_unit"],
                "route": suggested["route"],
                "form": suggested["form"],
                "source": "suggested",
            },
            state_version,
        )

    def change_context(self, run_id: UUID, payload: dict[str, Any], state_version: int) -> dict[str, Any]:
        snapshot = self._get_snapshot(run_id)
        if snapshot is None:
            return self._error("run_not_found", "Run was not found.", run_id=run_id)
        state = snapshot.state_json
        state["context"]["fiO2_fraction"] = payload["fiO2_fraction"]
        state["context"]["breathing_support"] = payload["breathing_support"]
        state["patient_file_panel"]["context_log"].append(self._current_context_row(state))
        return self._persist_and_wrap(snapshot, state)

    def set_monitoring(self, run_id: UUID, payload: dict[str, Any], state_version: int) -> dict[str, Any]:
        snapshot = self._get_snapshot(run_id)
        if snapshot is None:
            return self._error("run_not_found", "Run was not found.", run_id=run_id)
        state = snapshot.state_json
        state["context"]["monitoring_on"] = payload["monitoring_on"]
        state["patient_file_panel"]["context_log"].append(self._current_context_row(state))
        return self._persist_and_wrap(snapshot, state)

    def add_blood_level(self, run_id: UUID, payload: dict[str, Any], state_version: int) -> dict[str, Any]:
        snapshot = self._get_snapshot(run_id)
        if snapshot is None:
            return self._error("run_not_found", "Run was not found.", run_id=run_id)
        state = snapshot.state_json
        state["patient_file_panel"]["blood_levels"].append(
            {
                "id": f"bl_{len(state['patient_file_panel']['blood_levels']) + 1}",
                "t_sim_hours": float(state["time"]["sim_time_hours"]),
                "concentration_mg_per_l": payload["concentration_mg_per_l"],
                "below_detection_limit": payload["below_detection_limit"],
                "detection_limit_mg_per_l": payload["detection_limit_mg_per_l"],
            }
        )
        return self._persist_and_wrap(snapshot, state)

    def _build_summary(self, state: dict[str, Any]) -> dict[str, Any]:
        theta_rows = []
        true_rows = []
        error_rows = []
        for row in state["estimator_panel"]["theta"]:
            theta_rows.append(
                {
                    "param": row["key"],
                    "estimate": row["natural_estimate"],
                    "unit": row["natural_unit"],
                    "interval_90": row["natural_interval_90"],
                }
            )
            true_rows.append(
                {
                    "param": row["key"],
                    "value": row["true_natural"],
                    "unit": row["natural_unit"],
                }
            )
            error_rows.append(
                {
                    "param": row["key"],
                    "error": row["natural_estimate"] - row["true_natural"],
                    "unit": row["natural_unit"],
                }
            )
        return {
            "hours_to_convergence": float(state["time"]["sim_time_hours"]),
            "final_natural_estimates": theta_rows,
            "true_values": true_rows,
            "errors": error_rows,
            "doses_given_count": len(state["patient_file_panel"]["dose_log"]),
            "blood_levels_used_count": len(state["patient_file_panel"]["blood_levels"]),
        }

    def get_summary(self, run_id: UUID) -> dict[str, Any]:
        snapshot = self._get_snapshot(run_id)
        if snapshot is None:
            return self._error("run_not_found", "Run was not found.", run_id=run_id)
        state = snapshot.state_json
        summary = state["convergence"]["summary"]
        if summary is None:
            summary = self._build_summary(state)
        return {
            "ok": True,
            "run_id": str(run_id),
            "summary": {
                "is_converged": state["convergence"]["is_converged"],
                "rule_name": state["convergence"]["rule_name"],
                **summary,
            },
        }
