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
checks['large_signal_gap_explicit']=failure['status'] in ['failed','timeout']
files=list((ROOT/'tools').glob('*.py'))+[WHOLE/'tools/spice_runtime.py',out/'source-components.json']
manifest={str(p.relative_to(WHOLE.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
result=dict(checks=checks,refinement=refinement,nominal_wet_buffer_changes=wet,
    factory_and_input_hashes=manifest,source_contract_hashes=base['source_hashes'],
    fabrication_release=False,large_signal_qualified=False)
(out/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
assert all(checks.values()),checks
