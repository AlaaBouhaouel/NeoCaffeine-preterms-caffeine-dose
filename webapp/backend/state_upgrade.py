# Purpose: Upgrades run states stored before daily N (hour_gate, last_hour, hourly diagnostics) to the daily-N shape, so older runs still load.

from __future__ import annotations

import math
from typing import Any

HOURS_PER_DAY = 24


def _day_from_hour(hour: Any) -> int | None:
    """Return the observation day containing an hour index, or None if there is none."""
    if hour is None:
        return None
    return int(hour) // HOURS_PER_DAY


def upgrade_state(state: dict[str, Any]) -> dict[str, Any]:
    """Convert an hourly-N run state to the daily-N shape in place and return it; a daily-N state is returned unchanged."""
    if "hour_gate" not in state:
        return state
    state.pop("hour_gate")
    state["n_gate"] = {
        "editable_day_index_for_n": None,
        "n_prefill_value": None,
        "n_input_locked": True,
        "awaiting_n_for_day_index": None,
    }
    if state["meta"]["phase"] == "awaiting_n":
        state["meta"]["phase"] = "playing"
        state["meta"]["status_text"] = "Playing"

    sim_time_hours = float(state["time"]["sim_time_hours"])
    state["time"]["sim_day_index"] = int(math.floor(sim_time_hours / HOURS_PER_DAY))
    state["time"]["day_progress_01"] = (sim_time_hours % HOURS_PER_DAY) / HOURS_PER_DAY

    estimator = state["estimator_panel"]
    last_hour = estimator.pop("last_hour", {})
    estimator["last_day"] = {
        "day_index": _day_from_hour(last_hour.get("hour_index")),
        "predicted_n": last_hour.get("predicted_n", 0.0),
        "observed_n": last_hour.get("observed_n"),
    }
    for row in estimator["diagnostics"]["loss_negative_log_likelihood"] + estimator["uncertainty_chart"]:
        if "hour_index" in row:
            row["day_index"] = _day_from_hour(row.pop("hour_index"))
    return state
