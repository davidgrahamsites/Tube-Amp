"""Verify provenance, DC KCL, refinement and the declared rail-load decision."""
from pathlib import Path
import hashlib
import json
from analyze import source

M=Path(__file__).resolve().parents[1];D=M/'results'

def main():
    c,_=source();s=json.loads((D/'screen.json').read_text());a=json.loads((D/'analytic.json').read_text())
    assert s['source_sha256']==a['source_sha256']==c['circuit_sha256']
    for name,h in s['factory_sha256'].items():
        p=M/name if name=='contract.json' else M/'tools'/name
        assert hashlib.sha256(p.read_bytes()).hexdigest()==h,name
    assert len(s['dc'])==36 and len(s['transients'])==14 and len(s['deck_sha256'])==50
    for name,h in s['deck_sha256'].items():assert hashlib.sha256((D/name).read_bytes()).hexdigest()==h,name
    residuals=[]
    for row in s['dc']:
        v=row['nodes_V'];vp=v['VP'];vn=v['VN'];vi=v['SEND_IN'];drop=row['drop_V']
        ip=max(0,vi-vp-drop);inn=max(0,vn-vi-drop);g=1/(row['load_ohm']*1.02) if row['load_ohm'] else 0
        rp=max(0,15-vp) if row['powered_source_only'] else 0
        rn=max(0,vn+15) if row['powered_source_only'] else 0
        residuals += [(vi-v['IN_AC'])/980000+vi/102000+ip-inn,ip+rp-vp*(g+1e-12),inn+rn+vn*(g+1e-12)]
    assert max(map(abs,residuals))<1e-8
    chosen=[x for x in s['transients'] if x['load_ohm']==10000]
    assert all(x['end_s']==12 and x['maximum_rail_span_V']<30.001 for x in chosen)
    assert max(x['maximum_output_clamp_A'] for x in s['transients'])<c['terminal_envelope']['output_clamp_injection_allocation_A']
    errors=[]
    for load in [None,10000]:
        pair=[x for x in s['transients'] if x['load_ohm']==load and x['fault']=='C6_short' and x['powered_source_only']]
        assert len(pair)==2 and {x['maxstep_s'] for x in pair}=={.001,.0005}
        errors.append(abs(pair[0]['maximum_rail_span_V']-pair[1]['maximum_rail_span_V']))
    assert max(errors)<.001
    byload={x['nominal_rail_load_ohm']:x for x in a['comparison']}
    assert not byload[47000]['holds_15V_without_regulator_sink'] and byload[10000]['holds_15V_without_regulator_sink']
    assert a['selected_10k_max_power_at_18V_W']<a['selected_MF0207_power_allowance_at_100C_W']
    assert not s['native_integrated'] and not s['hardware_qualified']
    out={'evidence_checks_passed':True,'DC_cases':36,'transient_cases_including_refinements':14,'maximum_DC_KCL_residual_A':max(map(abs,residuals)),
         'maximum_refinement_difference_V':max(errors),'maximum_output_clamp_screen_A':max(x['maximum_output_clamp_A'] for x in s['transients']),
         'maximum_selected_transient_span_V':max(x['maximum_rail_span_V'] for x in chosen),'native_source_unchanged':True,
         'rail_load_native_integrated':False,'whole_amp_qualified':False,'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [D/'analytic.json',D/'screen.json']}}
    (D/'checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':main()
