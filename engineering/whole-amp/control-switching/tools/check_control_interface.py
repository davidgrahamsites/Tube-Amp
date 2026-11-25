"""Independent current-integration and source/native provenance acceptance."""
import copy,json,hashlib
from pathlib import Path
from rail_delay_budget import integrate_crossing
BASE=Path(__file__).resolve().parents[1];DEST=BASE/'results/control-interface'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(r):
    assert r['qualified'] is False and r['native_adopted'] is False and r['whole_logic_power_sequence_qualified'] is False
    assert len(r['passive_off_cases'])==4 and len(r['timer_cases'])==192
    assert all(r['checks'].values())
    for p,h in r['inputs'].items():assert sha(BASE.parent/p)==h,p
    for p,h in r['native_sha256'].items():assert sha(BASE.parent/p)==h,p
    assert {x['capacitor'] for x in r['native_direct_capacitor_inputs']}=={'C301','C311'}
    assert r['summary']['rejected_10k_timer_phantom_5V_upper_V']>.65
    assert r['prior_brownout_margin_after_added_input_allocation_s']>0

def main():
    r=json.loads((DEST/'screen.json').read_text());validate(r)
    cases=r['timer_cases'];witnesses=[min(cases,key=lambda x:x['release_s']),max(cases,key=lambda x:x['release_s']),max(cases,key=lambda x:x['discharge_s'])];numeric=[]
    for row in witnesses:
        for fault,key in [(False,'release_s'),(True,'discharge_s')]:
            expected=row[key]-(r['summary']['input_settling_allocation_s'] if fault else 0)
            found=integrate_crossing(row,fault,expected*1.25,8192);assert found is not None
            error=abs(found-expected);assert error<1e-7
            numeric.append({'phase':key,'expected_s':expected,'numerical_s':found,'error_s':error})
    rejected=[]
    for label,change in [('false whole-sequence qualification',lambda x:x.update(whole_logic_power_sequence_qualified=True)),('removed native capacitor finding',lambda x:x['native_direct_capacitor_inputs'].pop()),('altered input hash',lambda x:x['inputs'].__setitem__(next(iter(x['inputs'])),'0'*64))]:
        test=copy.deepcopy(r);change(test)
        try:validate(test)
        except AssertionError:rejected.append(label)
        else:raise AssertionError(label)
    source=json.loads((DEST/'source-observations.json').read_text());assert sha(DEST/source['primary']['retained_Yageo'])==source['primary']['Yageo_sha256']
    selected=['RT0603BRD0710KL','RT0603BRD0749K9L','RT0603BRD07100KL']
    assert all(next(p for p in source['parts'] if p['mpn']==mpn)['stockNumber']>0 for mpn in selected)
    output={'evidence_checks_passed':True,'qualified':False,'native_adopted':False,'whole_logic_power_sequence_qualified':False,'independent_RC_integrations':numeric,'negative_controls_rejected':rejected,'selected_candidate_MPNs':selected,'native_preserved_count':len(r['native_sha256']),'inputs':{str(p.relative_to(BASE)):sha(p) for p in [Path(__file__),DEST/'screen.json',DEST/'source-observations.json',BASE/'tools/rail_delay_budget.py']}}
    (DEST/'checks.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2))
if __name__=='__main__':main()
