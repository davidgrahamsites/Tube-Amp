"""Datasheet-limit arithmetic, separated from nominal SPICE models."""
import copy, hashlib, itertools, json, math
from pathlib import Path
M=Path(__file__).resolve().parents[1]

def reset_bounds(c,life=False):
 r=c['reset_candidate'];dt=max(abs(t-25) for t in c['logic_temperature_C'])
 tol=r['divider_tolerance']+dt*r['divider_tcr_per_C']+(r['divider_life_allowance'] if life else 0)
 absolute=r['divider_life_absolute_ohm'] if life else 0
 endpoints=lambda x:[x*(1-tol)-absolute,x*(1+tol)+absolute]
 values=[]
 for top,bot,acc,leak in itertools.product(endpoints(r['divider_top_ohm']),endpoints(r['divider_bottom_ohm']),[1-r['threshold_tolerance'],1+r['threshold_tolerance']],[-r['sense_leakage_abs_A'],r['sense_leakage_abs_A']]):
  values.append([(r[k]*acc)*(1+top/bot)+leak*top for k in ['fall_threshold_V','rise_threshold_V']])
 lo=min(v[0] for v in values);hi=max(v[1] for v in values)
 return dict(falling_min_V=lo,rising_max_V=hi,falling_margin_above_4p5V=lo-4.5,rising_margin_below_supply_min_V=c['logic_supply_V'][0]-hi,dc_window_pass=lo>4.5 and hi<c['logic_supply_V'][0],corners=len(values))

def main():
 c=json.loads((M/'contract.json').read_text());r=c['reset_candidate'];d=c['driver_candidate'];coil=c['coil']
 fresh=reset_bounds(c);life=reset_bounds(c,True)
 rg=d['gate_series_ohm']*(1+d['resistor_tolerance']);rp=d['gate_pulldown_ohm']*(1-d['resistor_tolerance'])
 gate=(d['hc74_voh_min_at_4p5V_V']-d['gate_leakage_abs_A']*rg)*rp/(rg+rp)
 resistance=coil['resistance_23C_ohm']*(1-coil['resistance_tolerance'])*(1+coil['copper_tcr_screen_per_C']*(min(c['relay_temperature_C'])-23))
 imax=max(coil['parallel_counts'])*max(coil['voltage_V'])/resistance
 cmin=r['timing_cap_F']*(1-r['timing_initial_tolerance']);cmax=r['timing_cap_F']*(1+r['timing_initial_tolerance'])
 times=dict(nominal_equation_s=r['timing_cap_F']*1e6*1.07+25e-6,initial_fast_s=cmin*min(r['ct_threshold_V'])/max(r['ct_current_A']),initial_slow_s=cmax*max(r['ct_threshold_V'])/min(r['ct_current_A']),slow_with_provisional_leakage_s=cmax*max(r['ct_threshold_V'])/(min(r['ct_current_A'])-max(r['ct_leakage_screen_A'])))
 # A conservative 10-90% total rise-time comparison; no invented inter-voltage timing interpolation.
 edges=[dict(capacitance_F=x,rise_10_90_s=math.log(9)*r['reset_pullup_ohm']*x,under_500ns=math.log(9)*r['reset_pullup_ohm']*x<=500e-9) for x in r['reset_capacitance_screen_F']]
 bad=copy.deepcopy(c);bad['reset_candidate']['divider_top_ohm']=32000
 assert not reset_bounds(bad)['dc_window_pass'],'Oversized-divider negative control escaped'
 assert fresh['dc_window_pass'] and life['dc_window_pass']
 assert gate>2.5
 assert gate<4.5,'Original 2N7000 negative control unexpectedly qualified'
 result=dict(contract_sha256=hashlib.sha256((M/'contract.json').read_bytes()).hexdigest(),fresh_thresholds=fresh,endurance_sensitivity=life,timing=times,reset_edge_screen=edges,reset_edge_qualification_complete=False,driver=dict(gate_min_V=gate,gate_margin_over_2p5V_V=gate-2.5,cold_coil_resistance_ohm=resistance,two_coil_max_current_A=imax,hot_surrogate_power_W=imax**2*d['rds_max_25C_at_2p5V_ohm']*d['rds_hot_multiplier_screen']),negative_controls_rejected=['32k_top_resistor_exceeds_release_window','original_2N7000_not_guaranteed_at_available_gate_voltage'],fabrication_ready=False)
 (M/'results/bounds.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
