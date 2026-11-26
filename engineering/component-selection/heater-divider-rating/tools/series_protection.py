"""HD-007 steady-state protection study; never mutates the native design."""
from pathlib import Path
import itertools,json,hashlib
import pass_topology as p

M=p.M
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def build(c,base,vin,profile,cold,fault,sensitivity,preload,seed=True):
    cfg=json.loads(json.dumps(base));z=c['topology'];s=sensitivity
    cfg['topology'].update(gate_bias_each_ohm=z['gate_bias_total_each_ohm']/2,
        gate_upper_ohm=z['reference_upper_ohm'],gate_lower_ohm=z['reference_lower_ohm'],source_ohm=s['source_ohm'])
    text=p.deck(cfg,vin,profile,cold,vto=s['vto1'])
    for old,new in [('M1 D G S S QPASS','M1 D G MID MID QPASS\nM2 MID G2 S S QPASS2'),
                    ('RG GREF G 1000',f"RG GREF G {z['gate_resistor_each_ohm']}"),
                    ('CGS G S','CGS G MID'),('DB S D DBODY','DB MID D DBODY')]:
        assert text.count(old)==1,old
        text=text.replace(old,new)
    add=f'''.model QPASS2 NMOS LEVEL=1 VTO={s['vto2']} KP=.4898 LAMBDA=0 RD=.1 RS=.1
RB21 IN RB2MID {z['gate_bias_total_each_ohm']/2}
RB22 RB2MID GREF2 {z['gate_bias_total_each_ohm']/2}
RG2 GREF2 G2 {z['gate_resistor_each_ohm']}
RGH2 GREF2 REF2 {z['reference_upper_ohm']}
RGL2 REF2 OUT {z['reference_lower_ohm']}
XREF2 GREF2 REF2 OUT ATL_FLOAT
CGS2 G2 S 1000p
CGD2 G2 MID 17p
DB2 S MID DBODY
DZ1 Z1 G ZG
DZ2 Z1 MID ZG
DZ3 Z2 G2 ZG
DZ4 Z2 S ZG
.model ZG D BV=12 IBV=.02 RS=1 IS=1e-12
'''
    if preload:add+=f"RPRELOAD OUT 0 {z['preload_ohm']}\n"
    if fault=='q1_short':add+='RFAIL D MID .001\n'
    if fault=='q2_short':add+='RFAIL MID S .001\n'
    if fault=='regulator_short':add+='RFAIL REGIN OUT .001\n'
    if seed:
        q=base['profiles'][profile];v=q['vref']*(1+q['rlow']/q['rset'])+q['iadj']*q['rlow']
        guesses={'out':v,'adj':v-q['vref'],'gref':v+18,'gref2':v+18,'ref':v+2.5,'ref2':v+2.5,'g':v+18,'g2':v+18,'mid':v+21,'s':v+21,'regin':v+10}
        add+='.nodeset '+' '.join(f'v({k})={a}' for k,a in guesses.items())+'\n'
    return text.replace('\n.end\n','\n'+add+'.end\n')

NODES=['in','d','g','mid','g2','s','regin','out','adj','gref','gref2','ref','ref2']
def measure(n,c,base,profile,cold,s,preload):
    z=c['topology'];q=base['profiles'][profile]
    src=(n['s']-n['regin'])/s['source_ohm']
    bias=[(n['in']-n[x])/z['gate_bias_total_each_ohm'] for x in ['gref','gref2']]
    back=[(n[a]-n[b])/z['gate_resistor_each_ohm'] for a,b in [('g','gref'),('g2','gref2')]]
    load=n['out']/78000+n['adj']/q['rlow']+(0 if cold else n['out']/36200)+(n['out']/z['preload_ohm'] if preload else 0)
    refI=[bias[i]+back[i]-(n[a]-n[b])/z['reference_upper_ohm'] for i,(a,b) in enumerate([('gref','ref'),('gref2','ref2')])]
    return dict(output_KCL_A=src+sum(bias)+sum(back)-load,
        source_A=src,regulator_output_A=src-q['iadj'],regulator_delta_V=n['regin']-n['out'],
        gate_source_V=[n['g']-n['mid'],n['g2']-n['s']],reference_A=refI,
        reference_W=[refI[i]*(n[a]-n['out']) for i,a in enumerate(['gref','gref2'])],
        gate_resistor_W=[a*a*z['gate_resistor_each_ohm'] for a in back],
        preload_W=n['out']**2/z['preload_ohm'] if preload else 0)

def run(c,base,case):
    text=build(c,base,**case);nodes=p.op(text,NODES)
    metrics=measure(nodes,c,base,case['profile'],case['cold'],case['sensitivity'],case['preload'])
    return dict(case=case,nodes=nodes,metrics=metrics,deck_sha256=hashlib.sha256(text.encode()).hexdigest())

def main():
    c=json.loads((M/'series-contract.json').read_text());base=json.loads((M/c['prior_contract']).read_text())
    assert sha(M/c['adapter'])==c['adapter_sha256']
    assert sha(M/c['prior_contract'])==c['prior_contract_sha256']
    rows=[];rejected=[]
    for vin,profile,cold,fault,s in itertools.product(c['input_V'],c['profiles'],c['cold'],c['faults'],c['sensitivity']):
        case=dict(vin=vin,profile=profile,cold=cold,fault=fault,sensitivity=s,preload=True,seed=True)
        row=run(c,base,case);assert abs(row['metrics']['output_KCL_A'])<c['output_KCL_tolerance_A'],row
        rows.append(row)
    for preload,seed in [(False,False),(False,True),(True,False)]:
        case=dict(vin=550,profile='nominal',cold=True,fault='q2_short',sensitivity=c['sensitivity'][0],preload=preload,seed=seed)
        rejected.append(run(c,base,case))
    case=dict(vin=550,profile='nominal',cold=True,fault='q1_short',sensitivity=c['sensitivity'][0],preload=False,seed=True)
    rejected.append(run(c,base,case))
    case=dict(vin=550,profile='nominal',cold=False,fault='regulator_short',sensitivity=c['sensitivity'][0],preload=True,seed=True)
    regulator_fault=run(c,base,case)
    assert abs(regulator_fault['metrics']['output_KCL_A'])<c['output_KCL_tolerance_A']
    (M/'results/series-regulator_short.cir').write_text(build(c,base,**case))
    names=['none','q1_short','q2_short']
    for fault in names:
        case=dict(vin=550,profile='nominal',cold=True,fault=fault,sensitivity=c['sensitivity'][0],preload=True,seed=True)
        (M/f'results/series-{fault}.cir').write_text(build(c,base,**case))
    result=dict(id=c['id'],contract_sha256=sha(M/'series-contract.json'),factory_sha256=sha(Path(__file__)),
        adapter_sha256=sha(M/c['adapter']),dc=rows,comparisons=rejected,regulator_fault=regulator_fault,
        native_sha256=json.loads((M/'results/pass-screen.json').read_text())['native_sha256'],
        model_qualification=False,adopted=False,full_fault_qualification=False,
        scope='Steady-state sensitivity only. Node guesses aid solving; KCL is independently required. No dynamic or physical protection claim.')
    (M/'results/series-screen.json').write_text(json.dumps(result,indent=2)+'\n')
    (M/'results/series-simulator.log').write_text('\n'.join(p.sp.logs)+'\n')
    print(json.dumps(dict(cases=len(rows),comparisons=rejected,
        minimum_regulator_output_A=min(a['metrics']['regulator_output_A'] for a in rows),
        maximum_regulator_differential_V=max(a['metrics']['regulator_delta_V'] for a in rows),
        maximum_abs_gate_source_V=max(max(abs(v) for v in a['metrics']['gate_source_V']) for a in rows)),indent=2))

if __name__=='__main__':main()
