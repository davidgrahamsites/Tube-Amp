"""Reproducible nominal/hypothetical arithmetic; no design qualification."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
raw = (ROOT / "inputs.json").read_bytes()
inputs = json.loads(raw)
n, h = inputs["nominal"], inputs["hypothetical"]
pre = n["preamp_count"] * n["preamp_heater_A"]
power = n["output_count"] * n["output_heater_A"]
mid = n["heater_V"] / n["midpoint_resistors_series_ohm"]
total = pre + power + mid + n["pilot_allowance_A"]
loop = h["full_heater_loop_ohm"]
cap = n["reservoir_each_uF"] * 1e-6
voltage = h["illustrative_cap_voltage_V"]
rows = []


def add(name, formula, substitution, value, unit, scope):
    rows.append(dict(name=name, formula=formula, substitution=substitution,
                     result=value, unit=unit, scope=scope))


add("nominal_preamp_heaters", "N * I_each", f"{n['preamp_count']} * {n['preamp_heater_A']}", pre, "A", "nominal")
add("nominal_output_heaters", "N * I_each", f"{n['output_count']} * {n['output_heater_A']}", power, "A", "nominal")
add("midpoint_current", "V / R_series", f"{n['heater_V']} / {n['midpoint_resistors_series_ohm']}", mid, "A", "existing nominal topology")
add("heater_inventory", "I_pre + I_output + I_midpoint + I_pilot", f"{pre} + {power} + {mid} + {n['pilot_allowance_A']}", total, "A", "nominal plus pilot allowance; not maximum")
for name, current in [("existing_inventory", total), ("preamp_only", pre), ("output_only", power)]:
    add(name + "_drop", "I * R_loop", f"{current} * {loop}", current * loop, "V", "hypothetical loop; isolated groups not adopted")
    add(name + "_heat", "I^2 * R_loop", f"{current}^2 * {loop}", current**2 * loop, "W", "hypothetical loop")
for budget in h["drop_budget_examples_V"]:
    add(f"loop_R_for_{budget}V", "V_budget / I", f"{budget} / {total}", budget / total, "ohm", "illustrative budget, not an allowed design drop")
add("series_reservoir", "C_equal / 2", f"{cap} / 2", cap / 2, "F", "two equal nominal capacitors")
add("isolated_bleeder_tau", "R_each * C_each", f"{n['reservoir_each_bleeder_ohm']} * {cap}", n["reservoir_each_bleeder_ohm"] * cap, "s", "isolated nominal RC, not safe service delay")
for name, capacitance in [("one_film", h["film_cap_uF"] * 1e-6), ("raw_series_pair", cap / 2)]:
    add(name + "_energy", "0.5 * C * V^2", f"0.5 * {capacitance} * {voltage}^2", 0.5 * capacitance * voltage**2, "J", "illustrative voltage; no actual rail claim")
receipt = dict(input_sha256=hashlib.sha256(raw).hexdigest(),
               factory_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               sources=inputs["sources"], calculations=rows,
               limits=inputs["limits"], design_qualified=False)
(ROOT / "results/arithmetic.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(f"Saved {len(rows)} nominal/hypothetical calculations; design not qualified.")
