"""CB-006 thermal and protection bounds; record the assumptions for the layout gate."""
import json
import math
from pathlib import Path

results = Path(__file__).resolve().parents[1]/'results'
normal = json.loads((results/'apex-return.json').read_text())['guard-hot']
fault = json.loads((results/'apex-protection.json').read_text())['runs'][-1]
# Add the full maximum quiescent allowance to modeled total loss as a deliberately
# conservative reserve. This is not a statistical or guaranteed silicon corner.
budget = {}
for name,loss in [('hot_full_sine',normal['power_stage_W']),('hot_port_short',fault['chip_W'])]:
    reserve = loss + 320*.0025
    budget[name] = dict(modeled_W=loss,trial_budget_W=reserve,
                        max_case_to_air_K_W=(85-70)/reserve, junction_at_85C=85+8.9*reserve)
# Prescribed fast output midpoint step. Contact disconnected during precharge.
step, cout, iso, precharge = 160, 1.1e-6, 3300, 10000
tau=(iso+precharge)*cout
budget['precharge'] = dict(step_V=step, charge_uC=step*cout*1e6,energy_mJ=.5*cout*step**2*1000,
    peak_mA=1000*step/(iso+precharge),tau_ms=tau*1e3,
    resistor_node_below_1V_ms=1000*tau*math.log(step*precharge/(iso+precharge)))
budget['faults'] = dict(raw_short_overvoltage_V=440-350,
    stuck_320V_to_ground_current_mA=1000*320/3300,stuck_320V_resistor_W=320**2/3300,
    step_input_from_intact_divider_mA=1000*160/(235000+48000),
    step_input_from_shorted_to_rail_mA=1000*320/48000,
    min_slew_V_us=2*math.pi*20000*135/1e6)
(results/'apex-fault-budget.json').write_text(json.dumps(budget,indent=2)+'\n')
