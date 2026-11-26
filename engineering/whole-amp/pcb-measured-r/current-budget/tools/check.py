"""Independent arithmetic/freshness checks for the declared passive-load screen."""
import copy
import json
import math
from analyze import M, ROOT, inputs, sha, measurement_sha

def validate(data):
    c, r, measured = inputs()
    required = {c['source'], str((M/'contract.json').relative_to(ROOT))}
    assert set(data['input_sha256']) == required
    for p,h in data['input_sha256'].items():
        assert sha(ROOT/p)==h, p
    assert data['tank_measurement_evidence']=={'path':c['tank_source'],'field':'tank_received.electrical_measurements','sha256':measurement_sha(measured)}
    assert data['factory_sha256']==sha(M/'tools/analyze.py')
    assert len(data['cases'])==data['case_count']==12
    expected={(v,z,k) for v in c['opamp_output_peak_V'] for z in c['tank_impedance_at_assumed_1kHz_ohm'] for k in c['C603_scales']}
    assert {(x['output_peak_V'],x['Z1k_surrogate_ohm'],x['C603_scale']) for x in data['cases']}==expected
    for x in data['cases']:
        peak=x['output_peak_V']
        # At series resonance, capacitor and inductive reactances cancel.
        # This independent maximum must match the sampled calculation exactly.
        resistance=r['R605']*(1-c['resistor_low_fraction'])+measured['input_DC_resistance_ohm']*(1-c['driver_Rdc_low_fraction_screen'])
        expected_rms=peak/(resistance*math.sqrt(2))
        assert math.isclose(x['tank']['rms_A'],expected_rms,rel_tol=1e-10)
        assert math.isclose(x['outputs']['DRIVER']['peak_A'],peak/resistance+peak/((r['R603']+r['R604'])*(1-c['resistor_low_fraction'])),rel_tol=1e-10)
        assert math.isclose(x['resonance_Hz'],1/(2*math.pi*math.sqrt(x['L_H']*r['C603']*x['C603_scale'])),rel_tol=1e-10)
        assert math.isclose(x['each_rail_conditional_A'],.030+c['rail_load_maximum_A']+sum(y['peak_A'] for y in x['outputs'].values()),rel_tol=1e-10)
        assert x['max_wet_node_peak_bound_V']<20, 'Linear clamp-off allocation exceeded'
    assert data['maximum_KCL_residual_A_per_V']<1e-12
    g=data['width_resistance_scenarios']
    assert math.isclose(g[0]['resistance_ohm_per_100mm']/g[2]['resistance_ohm_per_100mm'],2,rel_tol=1e-12)
    assert math.isclose(g[3]['drop_V_at_100mA'],.008594858333333334,rel_tol=1e-12)
    assert not data['thermal_current_capacity_qualified'] and not data['all_board_current_budget_complete'] and not data['fabrication_ready']

if __name__=='__main__':
    data=json.loads((M/'results/budget.json').read_text());validate(data)
    controls=[]
    for name,mutate in [
        ('halved_driver_current',lambda d:d['cases'][0]['tank'].update(rms_A=d['cases'][0]['tank']['rms_A']/2)),
        ('missing_case',lambda d:d['cases'].pop()),
        ('invented_thermal_approval',lambda d:d.update(thermal_current_capacity_qualified=True)),
        ('missing_source_hash',lambda d:d['input_sha256'].pop(next(iter(d['input_sha256']))))]:
        bad=copy.deepcopy(data);mutate(bad)
        try: validate(bad)
        except AssertionError:controls.append(name)
        else:raise AssertionError('Corruption not detected: '+name)
    out={'passed':True,'cases':12,'negative_controls_rejected':controls,'budget_sha256':sha(M/'results/budget.json'),'checks':'source/contract freshness, full case matrix, independent resonant driver maximum, current summation, wet clamp-off envelope, nodal residual and resistance scaling','scope':'Conditional passive model only; hot/startup/fault and physical tank limits remain open'}
    (M/'results/checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
