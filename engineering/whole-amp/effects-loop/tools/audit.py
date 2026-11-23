"""Check evidence consistency and numerical sensitivity, not hardware acceptance."""
import hashlib
import json
import math
from pathlib import Path
from fixture import ROOT, WHOLE, deck

out=ROOT/'results'
base=json.loads((out/'summary.json').read_text())
send=json.loads((out/'send-isolation-summary.json').read_text())
checks={}
checks['74_reference_AC_cases']=len(base['ac_cases'])==74
checks['108_send_branch_cases']=len(send['cases'])==108
checks['six_bounded_transients_completed']=all(r['status']=='completed' for r in base['transient_cases']+base['refinements'])
refinement=[]
for fine in base['refinements']:
    coarse=next(r for r in base['transient_cases'] if r['config']==fine['config'])
    for node in ['FX_SEND','PI_G1','SPEAKER']:
        a=coarse['signals'][node];b=fine['signals'][node]
        refinement.append(dict(channel=fine['config']['channel'],node=node,
            amplitude_change_percent=100*abs(b['fundamental_Vpk']/a['fundamental_Vpk']-1),
            THD_change_percentage_points=abs(b['THD_2_to_10_percent']-a['THD_2_to_10_percent'])))
checks['refined_amplitudes_within_0_1_percent']=max(r['amplitude_change_percent'] for r in refinement)<.1
checks['refined_THD_within_0_02_percentage_points']=max(r['THD_change_percentage_points'] for r in refinement)<.02
checks['retained_window_settled_0_1_percent']=all(
    r['settling_relative_fundamental'][n]<.001
    for r in base['transient_cases']+base['refinements'] for n in ['FX_SEND','PI_G1','SPEAKER'])
checks['send_branch_within_0_5dB']=send['screen_pass']
polarity=json.loads((out/'polarity-check.json').read_text())
checks['negative_feedback_reduces_gain']=polarity[1]['points']['1000']['magnitude']['SPEAKER']<polarity[0]['points']['1000']['magnitude']['SPEAKER']
wet=[]
for ch in ['clean','dirty']:
    rows=[r for r in base['ac_cases'] if r['config'].get('channel')==ch and r['config'].get('volume')==.25 and r['config'].get('tone')==.5 and r['config'].get('stimulus')=='wet']
    a=next(r for r in rows if r['config']['mode']=='native')['points']['1000']['magnitude']['PI_G1']
    b=next(r for r in rows if r['config']['mode']=='buffer')['points']['1000']['magnitude']['PI_G1']
    wet.append(dict(channel=ch,change_dB=20*math.log10(b/a)))
failure=json.loads((out/'overdrive-coverage.json').read_text())
checks['historical_unguarded_failure_retained']=failure['status'] in ['failed','timeout']
solver=json.loads((out/'solver-review.json').read_text())
diagnostic={r['variant']:r for r in solver['diagnostics']}
checks['legacy_failure_and_guard_success_reproduced']=diagnostic['baseline']['status']=='failed' and diagnostic['guarded-power']['status']=='completed'
checks['nominal_model_guard_agrees_within_0_0001_percent']=solver['max_nominal_relative_fundamental_change']<1e-6
fine=json.loads((out/'guard-heavy-refined-384.json').read_text())
coarse=solver['cases']['guard-heavy-refined']
checks['overdrive_refinement_completed']=fine['status']==coarse['status']=='completed'
overdrive_refinement=[]
for node in ['FX_SEND','PI_G1','SPEAKER']:
    a=coarse['signals'][node];b=fine['signals'][node]
    overdrive_refinement.append(dict(node=node,amplitude_change_percent=100*abs(b['fundamental_Vpk']/a['fundamental_Vpk']-1),
        THD_change_percentage_points=abs(b['THD_2_to_10_percent']-a['THD_2_to_10_percent'])))
checks['overdrive_refined_amplitude_within_0_1_percent']=max(r['amplitude_change_percent'] for r in overdrive_refinement)<.1
checks['overdrive_refined_THD_within_0_02_percentage_points']=max(r['THD_change_percentage_points'] for r in overdrive_refinement)<.02
checks['overdrive_coverage_states_explicit']=all(r['status'] in ['completed','failed','timeout'] for r in solver['cases'].values())
heavy = {k:r for k,r in solver['cases'].items() if k.startswith('guard-heavy-') and 'refined' not in k}
checks['twelve_heavy_cases_complete_full_window'] = len(heavy)==12 and all(r['status']=='completed' and r['end_s']>=.5*(1-1e-8) for r in heavy.values())
equivalence=json.loads((out/'save-vector-equivalence-check.json').read_text())
checks['save_list_equivalence'] = equivalence['passes'] and equivalence['max_relative_fundamental_change'] < 1e-9
return_result=json.loads((out/'return-real-summary.json').read_text())
checks['return_cases_have_explicit_status'] = return_result['all_requested_cases_attempted'] and len(return_result['cases']) == return_result['expected_cases'] and all(r['status'] in ['completed','failed','timeout'] for r in return_result['cases'])
checks['no_premature_return_release'] = return_result['headroom_qualified'] is False and return_result['fabrication_release'] is False

real_send=json.loads((out/'send-real-summary.json').read_text())
checks['six_real_send_AC_cases']=len(real_send['ac'])==6
checks['four_real_send_transients_complete']=len(real_send['transient'])==4 and all(r['status']=='completed' for r in real_send['transient'])
checks['real_send_AC_flatness_within_0_1dB']=all(abs(r['gain_20k_relative_1k_dB'])<.1 for r in real_send['ac'])
files=list((ROOT/'tools').glob('*.py'))+[WHOLE/'tools/spice_runtime.py',out/'source-components.json']
manifest={str(p.relative_to(WHOLE.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
result=dict(checks=checks,refinement=refinement,overdrive_refinement=overdrive_refinement,nominal_wet_buffer_changes=wet,
    guarded_case_statuses={name:row['status'] for name,row in solver['cases'].items()},
    factory_and_input_hashes=manifest,source_contract_hashes=base['source_hashes'],
    fabrication_release=False,large_signal_qualified=False)
(out/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
assert all(checks.values()),checks
