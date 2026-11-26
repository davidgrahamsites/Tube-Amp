"""HD-008 forced-on actuator test. No automatic detector is represented."""
from pathlib import Path
import hashlib,itertools,json
import series_protection as s
M=s.M

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def deck(c,prior,base,case):
    text=s.build(prior,base,vin=case['vin'],profile=case['profile'],cold=case['cold'],fault='regulator_short',sensitivity=case['sensitivity'],preload=True,seed=True)
    a=c['actuator'];mode=case['mode']
    if mode=='reference_upper_shunt':
        extra=f"RCTRL1 GREF REF {a['upper_shunt_ohm']}\nRCTRL2 GREF2 REF2 {a['upper_shunt_ohm']}\n"
    else:
        nodes=['GREF','GREF2'] if mode=='direct_both' else ['GREF']
        extra=''.join(f"VSENSE{i} {node} CTRL{i} 0\nBCTRL{i} CTRL{i} OUT I=min({a['current_cap_A']},max(0,(V({node},OUT)-{a['offset_V']})*{a['conductance_S']}))\n" for i,node in enumerate(nodes,1))
    return text.replace('\n.end\n','\n'+extra+'.end\n')

def main():
    c=json.loads((M/'absolute-contract.json').read_text())
    for path,h in c['input_sha256'].items():assert sha(M/path)==h,path
    prior=json.loads((M/'series-contract.json').read_text());base=json.loads((M/'pass-contract.json').read_text())
    rows=[]
    for mode,vin,profile,cold,v1,v2,rs in itertools.product(c['modes'],c['input_V'],c['profiles'],c['cold'],c['vto_V'],c['vto_V'],c['source_ohm']):
        case=dict(mode=mode,vin=vin,profile=profile,cold=cold,sensitivity=dict(vto1=v1,vto2=v2,source_ohm=rs))
        text=deck(c,prior,base,case);n=s.p.op(text,s.NODES)
        # Save terminal currents separately from the DC nodal balance.
        currents=[] if mode=='reference_upper_shunt' else [float(s.p.sp.vector(f'i(vsense{i})')[-1]) for i in range(1,3 if mode=='direct_both' else 2)]
        rows.append(dict(case=case,nodes=n,actuator_A=currents,deck_sha256=hashlib.sha256(text.encode()).hexdigest()))
    summaries={}
    for mode in c['modes']:
        subset=[r for r in rows if r['case']['mode']==mode];worst=max(subset,key=lambda r:r['nodes']['out'])
        summaries[mode]=dict(cases=len(subset),maximum_output_V=worst['nodes']['out'],over_ceiling=sum(r['nodes']['out']>c['limits']['output_V'] for r in subset),maximum_actuator_A=max([v for r in subset for v in r['actuator_A']] or [0]),worst_case=worst['case'])
        (M/f'results/absolute-{mode}.cir').write_text(deck(c,prior,base,worst['case']))
    q=base['profiles']['high'];normal=q['vref']*(1+q['rlow']/q['rset'])+q['iadj']*q['rlow']
    # Necessary condition only, before dynamic margin, divider, Iref and cathode-voltage errors.
    reflo=(2.483-.034)/2.495;refhi=(2.507+.034)/2.495
    window=dict(normal_upper_V=normal,ceiling_V=300,nominal_trip_min_from_normal_V=normal/reflo,nominal_trip_max_from_ceiling_V=300/refhi,reference_ratio_low=reflo,reference_ratio_high=refhi,feasible=normal/reflo<300/refhi)
    result=dict(id=c['id'],contract_sha256=sha(M/'absolute-contract.json'),factory_sha256=sha(Path(__file__)),rows=rows,summary=summaries,detector_window=window,native_sha256=json.loads((M/'results/series-screen.json').read_text())['native_sha256'],automatic_protection=False,physical_qualification=False,adopted=False)
    (M/'results/absolute-screen.json').write_text(json.dumps(result,indent=2)+'\n')
    (M/'results/absolute-simulator.log').write_text('\n'.join(s.p.sp.logs)+'\n')
    print(json.dumps(dict(summary=summaries,detector_window=window),indent=2))
if __name__=='__main__':main()
