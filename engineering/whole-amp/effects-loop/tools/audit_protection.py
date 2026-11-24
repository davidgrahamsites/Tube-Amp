"""Audit the fixed protection matrix; passing is numerical evidence, not release."""
import hashlib
import json
import math
from pathlib import Path
from protection_model import screen_resistances
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]

def main():
    report=json.loads((ROOT/'results/protection-acceptance-summary.json').read_text())
    expected={'target','target-refined','clean-overload','dirty-1k','dirty-5k','peaking-20k','bass-overload','high-clean','high-dirty','high-bass'}
    cases={r['name'].removeprefix('protection-acceptance-'):r for r in report['cases']}
    checks={'exact_case_inventory':set(cases)==expected}
    for name,r in cases.items():
        checks[name+':completed']=r['status']=='completed'
        if r['status']!='completed':continue
        p=ROOT/'results'/('protection-acceptance-'+name+'.cir')
        text=p.read_text();rs=screen_resistances(text)
        checks[name+':deck_hash']=hashlib.sha256(p.read_bytes()).hexdigest()==r['deck_sha256']
        checks[name+':factory_hashes']=all(hashlib.sha256((REPO/p).read_bytes()).hexdigest()==h for p,h in r['factory_hashes'].items())
        checks[name+':resistance_measurement']=all(rs[s]==r['stress'][s]['screen_resistor_ohm'] for s in ['A','B'])
        checks[name+':full_window']=r['end_s']>=.5-1e-8
        checks[name+':settling']=max(r['settling_relative_fundamental'].values())<.01
        checks[name+':secondary_DC']=abs(r['op_speaker_DC_V'])<1e-6
        checks[name+':screen_reference_limit']=all(0<=v['screen_W']<8 for v in r['stress'].values())
        checks[name+':plate_reference_limit']=all(0<=v['plate_W']<25 for v in r['stress'].values())
        # RESI 10W candidate: conditional 125C allowance interpolated from its
        # manufacturer curve, NOT the actual cabinet ambient or a part release.
        checks[name+':conditional_resistor_allowance']=all(0<=v['screen_resistor_W']<7.315 for v in r['stress'].values())
    if all(cases.get(n,{}).get('status')=='completed' for n in ['target','target-refined']):
        a,b=cases['target'],cases['target-refined']
        checks['approximately_25W_at_5percent']=23.75<=b['fundamental_load_W']<=26.25 and b['signals']['SPEAKER']['THD_2_to_10_percent']<=5.1
        checks['target_timestep_power']=abs(a['fundamental_load_W']-b['fundamental_load_W'])/b['fundamental_load_W']<.005
        checks['target_timestep_THD']=abs(a['signals']['SPEAKER']['THD_2_to_10_percent']-b['signals']['SPEAKER']['THD_2_to_10_percent'])<.1
    else:checks['target_refinement_available']=False
    result=dict(scope='Finite matrix and reference-rating screen; no fault, thermal or stability certification',
                checks=checks,passed=all(checks.values()),physical_qualified=False,fabrication_ready=False)
    (ROOT/'results/protection-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=result['passed'],checks=len(checks),failures=[k for k,v in checks.items() if not v]),indent=2))
    assert result['passed']

if __name__=='__main__':main()
