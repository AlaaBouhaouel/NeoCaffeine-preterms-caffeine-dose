# Purpose: Demo model for the live demo (proposal 06): caffeine concentration from the dose log, daily apnea counts, the daily estimator step, the dose suggestion, the confidence gate and the safety share.

from __future__ import annotations

import math
import random
from typing import Any

from backend.demo import thresholds as demo

PARAMETERS = (
    {"key": "log_CL", "label": "log CL", "unit": "L/h", "transform": "log"},
    {"key": "log_V", "label": "log V", "unit": "L", "transform": "log"},
    {"key": "logit_Emax", "label": "logit Emax", "unit": "fraction", "transform": "logit"},
    {"key": "log_EC50", "label": "log EC50", "unit": "mg/L", "transform": "log"},
    {"key": "log_beta_M", "label": "log beta_M", "unit": "per_week", "transform": "log"},
)
TRANSFORM_BY_KEY = {parameter["key"]: parameter["transform"] for parameter in PARAMETERS}
SEED_STRIDE = 7919


def to_transformed(transform: str, natural: float) -> float:
    """Return a natural-scale value on the estimation scale (log or logit)."""
    if transform == "logit":
        return math.log(natural / (1.0 - natural))
    return math.log(natural)


def to_natural(transform: str, transformed: float) -> float:
    """Return an estimation-scale value on the natural scale."""
    if transform == "logit":
        return 1.0 / (1.0 + math.exp(-transformed))
    return math.exp(transformed)


def true_values(weight_kg: float) -> dict[str, float]:
    """Return the demo true parameters of an infant, CL and V scaled to its weight."""
    return {
        "log_CL": demo.DEMO_TRUE_CL_L_PER_H_PER_KG * weight_kg,
        "log_V": demo.DEMO_TRUE_V_L_PER_KG * weight_kg,
        "logit_Emax": demo.DEMO_TRUE_EMAX,
        "log_EC50": demo.DEMO_TRUE_EC50_MG_PER_L,
        "log_beta_M": demo.DEMO_TRUE_BETA_M_PER_WEEK,
    }


def interval_90(transform: str, estimate: float, sd: float) -> dict[str, float]:
    """Return the 90% interval on the natural scale."""
    return {
        "lo": to_natural(transform, estimate - demo.Z_90 * sd),
        "hi": to_natural(transform, estimate + demo.Z_90 * sd),
    }


def initial_theta(weight_kg: float) -> list[dict[str, Any]]:
    """Return the estimator rows at the start: true values times the demo start factors, with the demo start SDs."""
    truth = true_values(weight_kg)
    rows = []
    for parameter in PARAMETERS:
        key, transform = parameter["key"], parameter["transform"]
        start_natural = truth[key] * demo.DEMO_START_FACTORS[key]
        estimate = to_transformed(transform, start_natural)
        sd = demo.DEMO_START_SD[key]
        rows.append({
            "key": key,
            "label": parameter["label"],
            "transformed_estimate": estimate,
            "transformed_sd": sd,
            "natural_estimate": start_natural,
            "natural_unit": parameter["unit"],
            "natural_interval_90": interval_90(transform, estimate, sd),
            "sparkline_transformed": [{"t_sim_hours": 0.0, "v": estimate}],
            "true_transformed": to_transformed(transform, truth[key]),
            "true_natural": truth[key],
        })
    return rows


def estimates(state: dict[str, Any]) -> dict[str, float]:
    """Return the current natural-scale estimates by parameter key."""
    return {row["key"]: row["natural_estimate"] for row in state["estimator_panel"]["theta"]}


def truths(state: dict[str, Any]) -> dict[str, float]:
    """Return the demo true natural-scale values by parameter key."""
    return {row["key"]: row["true_natural"] for row in state["estimator_panel"]["theta"]}


def mean_sd(state: dict[str, Any]) -> float:
    """Return the mean estimation-scale SD, the demo measure of remaining uncertainty."""
    rows = state["estimator_panel"]["theta"]
    return sum(row["transformed_sd"] for row in rows) / len(rows)


def dose_base_mg(dose: dict[str, Any], weight_kg: float) -> float:
    """Return the caffeine base amount in mg of one dose-log entry."""
    amount = float(dose["amount"])
    if dose.get("amount_unit", "mg_per_kg") == "mg_per_kg":
        amount *= weight_kg
    if dose.get("form", "citrate") == "citrate":
        amount *= demo.DEMO_CITRATE_TO_BASE
    return amount


def concentration(state: dict[str, Any], clearance: float, volume: float, t_hours: float) -> float:
    """Return C(t) in mg/L from every dose given at or before t (one compartment, IV bolus, closed form)."""
    weight_kg = state["demo_model"]["weight_kg"]
    elimination = clearance / volume
    amount = sum(
        dose_base_mg(dose, weight_kg) * math.exp(-elimination * (t_hours - float(dose["t_sim_hours"])))
        for dose in state["patient_file_panel"]["dose_log"]
        if float(dose["t_sim_hours"]) <= t_hours
    )
    return amount / volume


def apnea_rate_per_hour(c_mg_per_l: float, emax: float, ec50: float) -> float:
    """Return the demo apnea rate under caffeine: baseline x (1 - Emax x Hill(C))."""
    h = demo.DEMO_HILL_COEFFICIENT
    hill = c_mg_per_l ** h / (ec50 ** h + c_mg_per_l ** h) if c_mg_per_l > 0 else 0.0
    return demo.DEMO_BASELINE_APNEA_RATE_PER_HOUR * (1.0 - emax * hill)


def expected_daily_count(state: dict[str, Any], values: dict[str, float], day_index: int) -> float:
    """Return mu_d: the expected apneas over day d, summed hour by hour at mid-hour concentrations."""
    start = day_index * demo.HOURS_PER_DAY
    return sum(
        apnea_rate_per_hour(
            concentration(state, values["log_CL"], values["log_V"], start + hour + 0.5),
            values["logit_Emax"],
            values["log_EC50"],
        )
        for hour in range(demo.HOURS_PER_DAY)
    )


def poisson_draw(rng: random.Random, mean: float) -> int:
    """Return a Poisson draw (Knuth's method; fine for daily means of a few dozen)."""
    limit = math.exp(-mean)
    count, product = 0, rng.random()
    while product > limit:
        count += 1
        product *= rng.random()
    return count


def curve_point(state: dict[str, Any], t_hours: float) -> None:
    """Append the true and estimated concentration, and the estimate's band from the CL uncertainty, at time t."""
    current = estimates(state)
    truth = truths(state)
    cl_row = next(row for row in state["estimator_panel"]["theta"] if row["key"] == "log_CL")
    cl_low = math.exp(cl_row["transformed_estimate"] - demo.Z_90 * cl_row["transformed_sd"])
    cl_high = math.exp(cl_row["transformed_estimate"] + demo.Z_90 * cl_row["transformed_sd"])
    panel = state["pharmacology_panel"]
    panel["concentration_est_mg_per_l"].append({"t_sim_hours": t_hours, "v": concentration(state, current["log_CL"], current["log_V"], t_hours)})
    panel["true_concentration_mg_per_l"].append({"t_sim_hours": t_hours, "v": concentration(state, truth["log_CL"], truth["log_V"], t_hours)})
    panel["concentration_band_mg_per_l"].append({
        "t_sim_hours": t_hours,
        "lo": concentration(state, cl_high, current["log_V"], t_hours),
        "hi": concentration(state, cl_low, current["log_V"], t_hours),
    })


def update_monitor_rate(state: dict[str, Any]) -> None:
    """Set the apnea rate the browser uses to place apnea episodes, from the true model at the current time."""
    truth = truths(state)
    t_hours = float(state["time"]["sim_time_hours"])
    c_true = concentration(state, truth["log_CL"], truth["log_V"], t_hours)
    state["monitor_panel"]["demo_apnea_rate_per_hour"] = apnea_rate_per_hour(c_true, truth["logit_Emax"], truth["log_EC50"])
    state["monitor_panel"]["demo_true_concentration_mg_per_l"] = c_true


def update_decision(state: dict[str, Any]) -> None:
    """Recompute the confidence gate, the suggested maintenance dose and its safety share."""
    weight_kg = state["demo_model"]["weight_kg"]
    current = estimates(state)
    uncertainty = mean_sd(state)
    gate_open = uncertainty < demo.DEMO_GATE_THRESHOLD
    decision = state["decision_panel"]
    target = decision["target_concentration_mg_per_l"]
    if gate_open:
        base_mg_per_day = target * current["log_CL"] * demo.DOSING_INTERVAL_HOURS
        citrate_mg_per_kg = base_mg_per_day / demo.DEMO_CITRATE_TO_BASE / weight_kg
        step = demo.DEMO_DOSE_ROUNDING_MG_PER_KG
        amount = max(step, round(citrate_mg_per_kg / step) * step)
        reason = f"Uncertainty {uncertainty:.3f} below {demo.DEMO_GATE_THRESHOLD}: individualized dose."
    else:
        amount = demo.DEMO_STANDARD_REGIMEN_MG_PER_KG_CITRATE
        reason = f"Uncertainty {uncertainty:.3f} above {demo.DEMO_GATE_THRESHOLD}: standard regimen."
    decision["suggested_dose"] = {"amount": amount, "amount_unit": "mg_per_kg", "route": "iv", "form": "citrate"}
    decision["confidence_gate"] = {"open": gate_open, "reason": reason}
    decision["safety_share_vs_limit"] = safety_share(state, amount)


def safety_share(state: dict[str, Any], amount_mg_per_kg_citrate: float) -> float:
    """Return the share of parameter samples whose steady-state peak concentration exceeds the demo C_max."""
    weight_kg = state["demo_model"]["weight_kg"]
    rows = {row["key"]: row for row in state["estimator_panel"]["theta"]}
    rng = random.Random(int(state["run"]["random_seed"]) + len(state["estimator_panel"]["uncertainty_chart"]) * SEED_STRIDE)
    dose_base = amount_mg_per_kg_citrate * weight_kg * demo.DEMO_CITRATE_TO_BASE
    above = 0
    for _ in range(demo.DEMO_SAFETY_SAMPLES):
        clearance = math.exp(rng.gauss(rows["log_CL"]["transformed_estimate"], rows["log_CL"]["transformed_sd"]))
        volume = math.exp(rng.gauss(rows["log_V"]["transformed_estimate"], rows["log_V"]["transformed_sd"]))
        accumulation = 1.0 - math.exp(-(clearance / volume) * demo.DOSING_INTERVAL_HOURS)
        if (dose_base / volume) / accumulation > demo.DEMO_C_MAX_MG_PER_L:
            above += 1
    return above / demo.DEMO_SAFETY_SAMPLES


def trajectory_point(state: dict[str, Any], step: int) -> dict[str, Any]:
    """Return one point of the 3D convergence path: the natural estimates after `step` daily updates."""
    return {"step": step, "natural": estimates(state)}


def initialize(state: dict[str, Any], weight_kg: float) -> None:
    """Set up the demo model, estimator, concentration curves and decision of a new run (caffeine-naive at t = 0)."""
    state["demo_model"] = {"weight_kg": weight_kg, "last_curve_hour": 0}
    state["estimator_panel"]["theta"] = initial_theta(weight_kg)
    state["estimator_panel"]["uncertainty_chart"] = [{"day_index": 0, "value": mean_sd(state)}]
    state["estimator_panel"]["trajectory"] = [trajectory_point(state, 0)]
    state["pharmacology_panel"]["concentration_est_mg_per_l"] = []
    state["pharmacology_panel"]["true_concentration_mg_per_l"] = []
    state["pharmacology_panel"]["concentration_band_mg_per_l"] = []
    state["pharmacology_panel"]["concentration_bounds_mg_per_l"] = dict(demo.DEMO_CONCENTRATION_BOUNDS_MG_PER_L)
    state["decision_panel"]["target_concentration_mg_per_l"] = demo.DEMO_TARGET_CONCENTRATION_MG_PER_L
    curve_point(state, float(state["time"]["sim_time_hours"]))
    update_monitor_rate(state)
    update_decision(state)


def ensure_initialized(state: dict[str, Any]) -> None:
    """Give a run created before the live demo its demo model, keeping its time and logs."""
    if "demo_model" in state:
        return
    weight_kg = float(state["patient"]["covariates"]["birth_weight_g"]) / 1000.0
    initialize(state, weight_kg)
    state["demo_model"]["last_curve_hour"] = int(math.floor(float(state["time"]["sim_time_hours"])))


def on_advance(state: dict[str, Any]) -> None:
    """After time moved forward: append one curve point per whole simulated hour crossed and refresh the apnea rate."""
    model = state["demo_model"]
    current_hour = int(math.floor(float(state["time"]["sim_time_hours"])))
    for hour in range(model["last_curve_hour"] + 1, current_hour + 1):
        curve_point(state, float(hour))
    model["last_curve_hour"] = max(model["last_curve_hour"], current_hour)
    update_monitor_rate(state)


def on_dose(state: dict[str, Any]) -> None:
    """After a dose was logged: show the jump in concentration at the current time."""
    curve_point(state, float(state["time"]["sim_time_hours"]))
    update_monitor_rate(state)


def daily_count_prefill(state: dict[str, Any], day_index: int) -> int:
    """Return the demo 'observed' N for day d: a seeded Poisson draw from the true expected count."""
    rng = random.Random(int(state["run"]["random_seed"]) + day_index * SEED_STRIDE)
    return poisson_draw(rng, expected_daily_count(state, truths(state), day_index))


def on_daily_n(state: dict[str, Any], day_index: int, observed_n: int) -> None:
    """The daily estimator step: score the prediction, move each estimate toward its true value, narrow its SD, refresh the decision."""
    predicted = expected_daily_count(state, estimates(state), day_index)
    loss = predicted - observed_n * math.log(max(predicted, 1e-9)) + math.lgamma(observed_n + 1)
    t_hours = float(state["time"]["sim_time_hours"])
    for row in state["estimator_panel"]["theta"]:
        transform = TRANSFORM_BY_KEY[row["key"]]
        gap = row["true_transformed"] - row["transformed_estimate"]
        row["transformed_estimate"] += demo.DEMO_DAILY_GAP_FRACTION * gap
        row["transformed_sd"] *= demo.DEMO_DAILY_SD_FACTOR
        row["natural_estimate"] = to_natural(transform, row["transformed_estimate"])
        row["natural_interval_90"] = interval_90(transform, row["transformed_estimate"], row["transformed_sd"])
        row["sparkline_transformed"].append({"t_sim_hours": t_hours, "v": row["transformed_estimate"]})

    panel = state["estimator_panel"]
    panel["last_day"] = {"day_index": day_index, "predicted_n": predicted, "observed_n": observed_n}
    panel["diagnostics"]["loss_negative_log_likelihood"].append({"day_index": day_index, "value": loss})
    panel["diagnostics"]["newton_iterations_last_update"] = demo.DEMO_NEWTON_ITERATIONS
    panel["diagnostics"]["gradient_norm_last_update"] = abs(1.0 - observed_n / max(predicted, 1e-9))
    panel["uncertainty_chart"].append({"day_index": day_index + 1, "value": mean_sd(state)})
    panel["trajectory"].append(trajectory_point(state, day_index + 1))
    update_decision(state)
