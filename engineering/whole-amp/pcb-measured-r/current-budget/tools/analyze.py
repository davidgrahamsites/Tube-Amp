"""Passive output-load bounds; no semiconductor or IPC-2152 thermal model."""
from pathlib import Path
import hashlib
import json
import math
import re
import numpy as np

M = Path(__file__).resolve().parents[1]
ROOT = M.parents[3]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def measurement_sha(measured):
    """Bind the electrical measurement seam, not unrelated cabinet edits."""
    return hashlib.sha256(json.dumps(measured,sort_keys=True,separators=(',', ':')).encode()).hexdigest()

def scalar(value):
    n, suffix = re.fullmatch(r'([\d.]+)([Mkunp]?)', value).groups()
    return float(n) * {'': 1, 'M': 1e6, 'k': 1e3, 'u': 1e-6, 'n': 1e-9, 'p': 1e-12}[suffix]

def inputs():
    c = json.loads((M/'contract.json').read_text())
    path = ROOT/c['source']
    assert sha(path) == c['source_sha256'], 'Circuit revision changed'
    parts = {p['reference']: p for p in json.loads(path.read_text())['components']}
    for ref, expected in c['expected_parts'].items():
        assert {key: parts[ref][key] for key in expected} == expected, ref
    for ref in ['U10', 'U11', 'U12']:
        assert parts[ref]['value'] == 'OPA2134PA'
    for ref in ['R619', 'R620']:
        assert parts[ref]['value'] == '10k'
    assert parts['R619']['pins'] == {'1': '+15V', '2': 'GND'}
    assert parts['R620']['pins'] == {'1': 'GND', '2': '-15V'}
    fit = json.loads((ROOT/c['tank_source']).read_text())
    measured = fit['tank_received']['electrical_measurements']
    return c, {ref: scalar(p['value']) for ref,p in parts.items() if ref in c['expected_parts']}, measured

def wet_output(r, hz, out_v, fx_v):
    """Two unit-source columns; retain independent phases for current bound.
    The native R24 shunt is included. PI grid loading is omitted, and a separate
    1 Mohm resistive-load comparison is evaluated by the caller.
    """
    jw = 2j*math.pi*hz
    series = r['R616']+1/(jw*r['C607'])
    ya, ym, yl, yg = 1/series, 1/r['R618'], 1/r['R612'], 1/r['R617']
    matrix = np.array([[ya+ym+yg, -ym], [-ym, ym+yl+1/r['R24']]], complex)
    rhs = np.array([[ya, 0], [0, yl]], complex)
    v = np.linalg.solve(matrix, rhs)
    residual = float(np.max(abs(matrix @ v-rhs)))
    # Outgoing current at OUT_BUF for each independent voltage source.
    transfer = np.array([(1-v[0,0])/series, -v[0,1]/series])
    bound = abs(transfer[0])*out_v+abs(transfer[1])*fx_v
    wet_v = abs(v[0,0])*out_v+abs(v[0,1])*fx_v
    return float(bound), float(wet_v), residual

def calculate(c, nominal, measured):
    r = dict(nominal)
    for ref in r:
        if ref.startswith('R'):
            r[ref] *= 1-c['resistor_low_fraction']
    r['R616'] = c['R616_low_ohm']
    rdc = measured['input_DC_resistance_ohm']*(1-c['driver_Rdc_low_fraction_screen'])
    rows = []
    max_residual = 0
    for z in c['tank_impedance_at_assumed_1kHz_ohm']:
        inductance = math.sqrt(z*z-measured['input_DC_resistance_ohm']**2)/(2*math.pi*1000)
        for capscale in c['C603_scales']:
            cap = r['C603']*capscale
            resonance = 1/(2*math.pi*math.sqrt(inductance*cap))
            frequencies = sorted(set(np.geomspace(c['frequency_min_Hz'],c['frequency_max_Hz'],c['frequency_points']).tolist()+[resonance]))
            for peak in c['opamp_output_peak_V']:
                maxima = {key: {'peak_A':0} for key in c['source_outputs']}
                max_tank = {'rms_A':0}
                max_wet = 0
                for hz in frequencies:
                    jw=2j*math.pi*hz
                    tank_z=r['R605']+rdc+jw*inductance+1/(jw*cap)
                    tank_peak=peak/abs(tank_z)
                    loads={
                        'SEND_BUF': peak/abs(c['pot_total_low_ohm']+1/(jw*r['C602'])),
                        'DRIVER': tank_peak+peak/(r['R603']+r['R604']),
                        'REC_OUT': peak/abs(r['R607']+1/(1/r['R608']+jw*r['C605']))+peak/c['pot_total_low_ohm']+peak/r['R609'],
                        # Grounding WET_MUTE gives the largest ordinary load.
                        'WET_BUF':peak/r['R610'],
                        'SUM_INV':peak/r['R613']+peak/r['R614']}
                    currents=[]
                    for pi_load in [False,True]:
                        rr=dict(r)
                        if pi_load: rr['R24']=1/(1/r['R24']+1/1e6)
                        value, wet_v, residual=wet_output(rr,hz,peak,c['tube_interface_peak_V'])
                        currents.append(value);max_residual=max(max_residual,residual);max_wet=max(max_wet,wet_v)
                    loads['OUT_BUF']=max(currents)+peak/r['R615']
                    for net,value in loads.items():
                        if value>maxima[net]['peak_A']:
                            maxima[net]={'peak_A':float(value),'at_Hz':float(hz)}
                    if tank_peak/math.sqrt(2)>max_tank['rms_A']:
                        max_tank={'rms_A':float(tank_peak/math.sqrt(2)),'at_Hz':float(hz)}
                q=6*c['quiescent_A_per_channel_25C']
                outsum=sum(item['peak_A'] for item in maxima.values())
                # Sum of absolute output-current peaks is deliberately used as
                # a bound on each supply's signal contribution; no half-wave
                # average/RMS discount, no assumed phase cancellation.
                supply=q+outsum+c['rail_load_maximum_A']
                rows.append({'output_peak_V':peak,'Z1k_surrogate_ohm':z,'input_Rdc_screen_ohm':rdc,'L_H':inductance,'C603_scale':capscale,'resonance_Hz':resonance,'outputs':maxima,'tank':max_tank,'output_current_peak_sum_A':outsum,'each_rail_conditional_A':supply,'max_wet_node_peak_bound_V':max_wet,'driver_resonance_closed_form_peak_A':peak/(r['R605']+rdc),'R605_normal_sine_W':max_tank['rms_A']**2*r['R605']})
    g=c['geometry_scenarios'];rho=g['copper_resistivity_20C_ohm_m']*(1+g['temperature_coefficient_per_C']*(g['copper_temperature_C']-20))
    geometric=[]
    for width in [0.3,0.4,0.6,1.0]:
        resistance=rho*0.1/(width*1e-3*(1-g['width_negative_fraction'])*g['copper_thickness_um']*1e-6)
        geometric.append({'drawn_width_mm':width,'resistance_ohm_per_100mm':resistance,'drop_V_at_100mA':resistance*.1,'loss_W_at_100mA':resistance*.1**2})
    return {'cases':rows,'case_count':len(rows),'maximum_KCL_residual_A_per_V':max_residual,'width_resistance_scenarios':geometric,'native_values_used':nominal,'driver_resonance_screen_not_safe_tank_current':True,'supply_basis':'25C quiescent limit plus independent output-load peak sums; ideal sinusoidal output sources, passive loads and stated tolerances. Not a hot/startup/fault bound.','muted_output':'U12 steady output ideally vanishes when K3 grounds WET_MUTE; WET_AC grounding makes R616/C607 a substantial transient load. Existing VAL-067 pulse screen remains separate.','thermal_current_capacity_qualified':False,'all_board_current_budget_complete':False,'fabrication_ready':False}

def main():
    c,r,measured=inputs();result=calculate(c,r,measured)
    result['input_sha256']={p:sha(ROOT/p) for p in [c['source'],'engineering/whole-amp/pcb-measured-r/current-budget/contract.json']}
    result['tank_measurement_evidence']={'path':c['tank_source'],'field':'tank_received.electrical_measurements','sha256':measurement_sha(measured)}
    result['factory_sha256']=sha(Path(__file__))
    (M/'results/budget.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'cases':result['case_count'],'KCL_residual':result['maximum_KCL_residual_A_per_V'],'each_rail_max_A_by_output':{str(v):max(x['each_rail_conditional_A'] for x in result['cases'] if x['output_peak_V']==v) for v in c['opamp_output_peak_V']},'tank_max_mArms':1000*max(x['tank']['rms_A'] for x in result['cases'])},indent=2))

if __name__=='__main__':main()
