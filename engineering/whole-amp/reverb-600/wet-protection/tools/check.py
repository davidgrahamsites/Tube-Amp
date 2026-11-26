"""Evidence and engineering acceptance are distinct; neither qualifies hardware."""
from pathlib import Path
import copy
import json
import math
from analyze import M, ROOT, sha, inputs


def validate(c,a,s):
    assert a['source_sha256']==s['source_sha256']==c['source_sha256']
    assert a['contract_sha256']==s['contract_sha256']==sha(M/'contract.json')
    assert a['factory_sha256']==sha(M/'tools/analyze.py')
    for name,h in s['factory_sha256'].items():assert sha(M/'tools'/name)==h,name
    for group in ['deck_sha256','waveform_sha256']:
        for name,h in s[group].items():assert sha(M/'results'/name)==h,name
    assert len(a['dc'])==1024 and len(a['ac'])==96
    assert len(s['dc'])==24 and len(s['ac'])==48 and len(s['closing'])==13
    assert not a['native_integrated'] and not s['native_integrated']
    assert not a['hardware_qualified'] and not s['hardware_qualified']
    assert s['DC_independent_max_error_V']<1e-5
    assert s['AC_independent_max_error_V']<1e-7


def main():
    c,r=inputs();a=json.loads((M/'results/analytic.json').read_text());s=json.loads((M/'results/screen.json').read_text())
    validate(c,a,s);negative=[]
    for what in ['missing run','false native adoption','changed source']:
        bad=copy.deepcopy(s)
        if what=='missing run':bad['closing'].pop()
        elif what=='false native adoption':bad['native_integrated']=True
        else:bad['source_sha256']='0'*64
        try:validate(c,a,bad)
        except AssertionError:negative.append(what)
        else:raise AssertionError(what)
    base=next(x for x in s['closing'] if x['supply_V']==400 and x['threshold_V']==40 and x['wet_source_V']==0 and x['maxstep_s']==.5e-6)
    fine=s['closing'][-1]
    assert fine['maxstep_s']==base['maxstep_s']/2
    refinement={key:abs(fine[key]-base[key])/max(abs(fine[key]),1e-15) for key in ['contact_peak_A','R616_energy_J','R616_peak_W']}
    assert max(refinement.values())<.001,refinement
    for x in s['closing']:
        assert x['end_s']>=.03 and x['contact_peak_A']<a['contact']['current_A']
        # Independent RC energy: C607 changes its voltage by the initial wet voltage.
        # Sustained dry-feed current adds a small amount; 1% comparison includes it.
        predicted=.5*r['C607']*1.1*x['initial_wet_V']**2
        assert abs(x['R616_energy_J']-predicted)/predicted<.01
    acceptance={
        'ideal_clamp_voltage_below_relay_limit':a['contact']['voltage_V']<c['contact']['max_voltage_V'],
        'C607_branch_current_below_relay_limit':a['contact']['current_A']<c['contact']['max_current_A'],
        'resistive_load_product_screen':a['contact']['load_product_W']<c['contact']['max_resistive_switch_W'],
        'normal_peak_below_leakage_test_voltage':a['maximum_normal_wet_V']<20,
        'normal_peak_below_low_clamp_screen':a['maximum_normal_wet_V']<min(c['candidate']['clamp_threshold_screen_V']),
        'capacitance_audio_sensitivity':a['max_audio_change_dB']<c['ac']['gain_change_limit_dB'],
        'pair_thermal_screen':a['thermal']['pair_max_W']<a['thermal']['single_device_allowed_W_at_85C_lead'],
        'existing_R618_250V_sufficient':a['max_R618_voltage_V']<250,
        'proposed_R618_350V_sufficient_in_screen':a['max_R618_voltage_V']<350,
    }
    assert not acceptance['existing_R618_250V_sufficient']
    assert all(v for k,v in acceptance.items() if k!='existing_R618_250V_sufficient')
    receipt=json.loads((M/'sources/retrieval.json').read_text());assert sha(M/'sources'/receipt['file'])==receipt['sha256']
    pulse=json.loads((M/'results/pulse-budget.json').read_text())
    assert pulse['source_sha256']==c['source_sha256'] and pulse['passed']
    for name,h in pulse['inputs_sha256'].items():assert sha(M/name)==h,name
    assert pulse['peak_W']<pulse['rectangular_screen']['peak_W']<pulse['manufacturer_curve']['conservative_power_W']
    assert pulse['C607_branch_peak_A']<c['contact']['max_current_A']
    assert pulse['C607_branch_peak_A']*a['contact']['voltage_V']<c['contact']['max_resistive_switch_W']
    result=dict(evidence_passed=True,negative_controls=negative,engineering_screens=acceptance,
                timestep_refinement_relative=refinement,
                required_native_delta={'D603/D604':'Proposed opposing-series Vishay BZX55C27-TAP pair; reference availability checked',
                    'R618':'Keep1M resistance; adopt already-investigated MF0207FTE52-1M350V/0.6W package with exact pin/courtyard review',
                    'R616':'PR01000101000JA500100ohm5% candidate passes isolated-event pulse screen; integration pending'},
                unresolved=['Exact current Chinese stock/MOQ and Shanghai address route',
                    'Actual hot/cold leakage and capacitance; no manufacturer nonlinear/SPICE model',
                    'R616 repeated-pulse/application qualification; capacitive contact life/bounce/arcing',
                    'Direct diode/PCB-capacitance contact pulse, not included in0.405A bound',
                    'Native readable schematic, PCB integration and fresh voltage/routing checks',
                    'Integrated loop/power/protection, harness and populated three-board fit'],
                native_integrated=False,all_six_complete=False,
                input_sha256={str(p.relative_to(M)):sha(p) for p in [M/'contract.json',M/'results/analytic.json',M/'results/screen.json',M/'results/pulse-budget.json',M/'tools/check.py',M/'sources/retrieval.json']})
    (M/'results/checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
