#!/usr/bin/env python3
"""Offline design arithmetic. No hardware access or authorization to energize.

Run from any directory: python3 /absolute/path/to/calculations.py
Default writes calculation-report.json beside this file. All tube examples
are synthetic; the script is not a health screening or instrument driver.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def positive(value):
    if not math.isfinite(value) or value <= 0:
        raise ValueError("Matching requires finite, positive, uncensored values")
    return value


def mismatch_pct(x, y):
    positive(x)
    positive(y)
    return 200 * abs(x - y) / (x + y)


def uncertainty_mismatch_pct(x, y, ux, uy):
    """Maximum endpoint mismatch for positive measurements +/- absolute bounds."""
    if not all(math.isfinite(v) and v >= 0 for v in (ux, uy)):
        raise ValueError("Uncertainty bounds must be finite and nonnegative")
    xs, ys = (x - ux, x + ux), (y - uy, y + uy)
    for value in xs + ys:
        positive(value)
    return max(mismatch_pct(a, b) for a in xs for b in ys)


def metric_gate(x, y, relative_u_pct, limit_pct):
    if relative_u_pct < 0 or not math.isfinite(relative_u_pct):
        raise ValueError("Relative uncertainty must be finite and nonnegative")
    if limit_pct <= 0 or not math.isfinite(limit_pct):
        raise ValueError("Acceptance limit must be finite and positive")
    central = mismatch_pct(x, y)
    bounded = uncertainty_mismatch_pct(
        x, y, x * relative_u_pct / 100, y * relative_u_pct / 100
    )
    result = "accept-metric" if bounded <= limit_pct else (
        "uncertain-retest" if central <= limit_pct else "outside-limit"
    )
    return {"central_mismatch_pct": central, "worst_case_mismatch_pct": bounded,
            "uncertainty_each_pct": relative_u_pct, "limit_pct": limit_pct,
            "metric_result": result}


def gm_ma_per_v(ip_minus_ma, ip_plus_ma, vg_minus_v, vg_plus_v):
    vals = (ip_minus_ma, ip_plus_ma, vg_minus_v, vg_plus_v)
    if not all(math.isfinite(v) for v in vals) or vg_plus_v <= vg_minus_v:
        raise ValueError("Invalid transconductance interval")
    slope = (ip_plus_ma - ip_minus_ma) / (vg_plus_v - vg_minus_v)
    return positive(slope)


def rp_kohm(vp_low_v, vp_high_v, ip_low_ma, ip_high_ma):
    if not all(math.isfinite(v) for v in (vp_low_v, vp_high_v, ip_low_ma, ip_high_ma)):
        raise ValueError("Nonfinite plate resistance input")
    if vp_high_v <= vp_low_v or ip_high_ma <= ip_low_ma:
        raise ValueError("Invalid plate resistance interval")
    return (vp_high_v - vp_low_v) / (ip_high_ma - ip_low_ma)


def bin_interval(value, width):
    positive(value)
    positive(width)
    # Tiny rounding allowance solely for exact decimal boundaries in floats.
    index = math.floor(value / width + 1e-10)
    return {"lower_inclusive": index * width, "upper_exclusive": (index + 1) * width}


def discharge_example(cap_uf, resistance_ohm, start_v, finish_v):
    for value in (cap_uf, resistance_ohm, start_v, finish_v):
        positive(value)
    if finish_v >= start_v:
        raise ValueError("Discharge end voltage must be below start voltage")
    cap_f = cap_uf * 1e-6
    return {"capacitance_uf": cap_uf, "resistance_ohm": resistance_ohm,
            "start_v": start_v, "finish_v": finish_v,
            "stored_energy_j": 0.5 * cap_f * start_v ** 2,
            "initial_resistor_power_w": start_v ** 2 / resistance_ohm,
            "ideal_time_s": cap_f * resistance_ohm * math.log(start_v / finish_v),
            "scope": "one rail, ideal RC; not a guard-release criterion"}


def profile_checks(data):
    t = data["instrument_targets"]
    checks = []
    if data["energization_authorized"] or data["hardware_validated"]:
        raise ValueError("This artifact must remain an unvalidated, unreleased design")
    for p in data["profiles"]:
        if p["heater_nominal_a"] > t["heater_capacity_a"]:
            raise ValueError("Heater capacity insufficient")
        if not t["bias_min_v"] <= p["hold_bias_v"] <= t["bias_max_v"]:
            raise ValueError("Hold bias outside range")
        a, limits = p["anchor"], p["proposed_stop_limits"]
        if a["vpk_v"] > t["plate_max_v"] or limits["ip_ma"] > t["plate_capacity_ma"]:
            raise ValueError("Plate demand outside instrument range")
        if "vg2k_v" in a:
            if a["vg2k_v"] > t["screen_max_v"] or limits["is_ma"] > t["screen_capacity_ma"]:
                raise ValueError("Screen demand outside instrument range")
            expected_screen_w = a["vg2k_v"] * limits["is_ma"] / 1000
            if not math.isclose(expected_screen_w, limits["screen_w"]):
                raise ValueError("Screen reference envelope arithmetic mismatch")
        expected_plate_w = a["vpk_v"] * limits["ip_ma"] / 1000
        if not math.isclose(expected_plate_w, limits["plate_w"]):
            raise ValueError("Plate reference envelope arithmetic mismatch")
        if not t["bias_min_v"] <= a["vgk_v"] - p["gm_grid_delta_v"] < a["vgk_v"] + p["gm_grid_delta_v"] <= 0:
            raise ValueError("gm excursion outside bias range")
        checks.append({"profile": p["id"], "result": "range-and-anchor-arithmetic-consistent",
                       "limitation": "does not predict actual tube current or validate protection"})
    return checks


def numerical_checks():
    checks = []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)
    check("mismatch identity", mismatch_pct(1, 1) == 0)
    check("mismatch symmetry", mismatch_pct(40, 41.2) == mismatch_pct(41.2, 40))
    check("gm analytic example", math.isclose(gm_ma_per_v(1.04, 1.36, -2.1, -1.9), 1.6))
    check("rp analytic example", math.isclose(rp_kohm(240, 250, 1.04, 1.20), 62.5))
    check("bin boundary is half-open", math.isclose(bin_interval(1.2, 0.1)["lower_inclusive"], 1.2))
    check("uncertainty can prevent acceptance", metric_gate(1.6, 1.62, 2, 5)["metric_result"] == "uncertain-retest")
    for value in (0, -1, float("nan"), float("inf")):
        try:
            mismatch_pct(value, 1)
        except ValueError:
            checks.append("invalid matching value rejected: " + str(value))
        else:
            raise AssertionError("Invalid input accepted")
    try:
        uncertainty_mismatch_pct(1, 1, 1, 0)
    except ValueError:
        checks.append("uncertainty interval reaching zero rejected")
    else:
        raise AssertionError("Zero-crossing interval accepted")
    check("same coarse bin can fail pair gate", mismatch_pct(38.001, 39.999) > 5)
    check("adjacent coarse bins can match", mismatch_pct(39.99, 40.01) < 0.1)
    return checks


def main():
    data = json.loads((ROOT / "profiles.json").read_text())
    t = data["instrument_targets"]
    output_w = t["plate_max_v"] * t["plate_capacity_ma"] / 1000 + (
        t["screen_max_v"] * t["screen_capacity_ma"] / 1000
    ) + t["heater_v"] * t["heater_capacity_a"]
    input_w = output_w / t["conversion_efficiency_assumption"] + (
        t["pi_display_allowance_w"] + t["measurement_fan_allowance_w"]
    )
    curve_a, curve_b = [20, 40, 52], [20.9, 41.2, 53.9]
    curve_worst = [uncertainty_mismatch_pct(a, b, a * .01, b * .01)
                   for a, b in zip(curve_a, curve_b)]
    report = {
        "revision": data["revision"], "status": "offline-arithmetic-only",
        "all_tube_values_synthetic": True, "hardware_tests_run": False,
        "profile_checks": profile_checks(data), "numerical_checks": numerical_checks(),
        "power_budget": {"regulated_output_capacity_w": output_w,
                         "estimated_input_with_allowances_w": input_w,
                         "adapter_capacity_w": t["adapter_v"] * t["adapter_a"],
                         "remaining_allowance_w": t["adapter_v"] * t["adapter_a"] - input_w,
                         "efficiency_assumed_not_measured": True},
        "passive_discharge": discharge_example(t["rail_capacitance_example_uf"], t["passive_bleeder_example_ohm"], 300, 10),
        "active_discharge": discharge_example(t["rail_capacitance_example_uf"], t["active_discharge_example_ohm"], 300, 10),
        "acquisition_examples": {"triode_shunt_v_at_1p2ma": .0012 * 100,
                                 "triode_shunt_v_at_3ma": .003 * 100,
                                 "el34_shunt_v_at_60ma": .060 * 1,
                                 "screen_shunt_v_at_10ma": .010 * 10,
                                 "ideal_bias_dac_step_mv": 60 / 65536 * 1000,
                                 "current_change_ua_at_gm11": 60 / 65536 * 11 * 1000},
        "synthetic_el34_metric_examples": {
            "anchor_current": metric_gate(40, 41.2, 1, 5),
            "gm": metric_gate(10.5, 10.8, 1, 10),
            "curve_worst_case_rms_pct": math.sqrt(sum(x*x for x in curve_worst) / len(curve_worst)),
            "complete_pair_accepted": False,
            "reason": "illustrates numeric gates only; no real health, drift, calibration or curve measurements"},
        "synthetic_12ax7_metric_examples": {
            "current": metric_gate(1.20, 1.22, 1, 5),
            "gm_at_1pct_uncertainty": metric_gate(1.60, 1.62, 1, 5),
            "gm_at_2pct_uncertainty": metric_gate(1.60, 1.62, 2, 5),
            "rp_kohm": rp_kohm(240, 250, 1.04, 1.20),
            "mu_estimate": gm_ma_per_v(1.04, 1.36, -2.1, -1.9) * rp_kohm(240, 250, 1.04, 1.20),
            "complete_bottle_accepted": False,
            "reason": "synthetic local slopes only; no real health, secondary-point or calibration checks"}
    }
    (ROOT / "calculation-report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print("Offline profile arithmetic and", len(report["numerical_checks"]), "numerical checks passed.")
    print("Budget:", round(input_w, 2), "W assumed input against", t["adapter_v"] * t["adapter_a"], "W adapter target.")
    print("Synthetic values only. No tube, circuit, hardware safety or metrology validation.")
    print("Wrote", ROOT / "calculation-report.json")


if __name__ == "__main__":
    main()
