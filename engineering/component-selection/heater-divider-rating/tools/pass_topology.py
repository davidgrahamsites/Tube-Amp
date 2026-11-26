"""HD-006: model translation fixtures and explicitly unqualified pass-stage screen."""
from pathlib import Path
import hashlib, itertools, json, sys
import numpy as np

M = Path(__file__).resolve().parents[1]
ROOT = M.parents[2]
sys.path.insert(0, str(ROOT / 'engineering/whole-amp/tools'))
import spice_runtime as sp

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def reference(stage='floating'):
    raw = (M / 'sources/ATL431A_TRANS.LIB').read_text()
    # Preserve the downloaded bytes; translate only the generated deck.
    raw = '\n'.join(line.rstrip() for line in raw.replace('TC=0,0', '').splitlines()) + '\n'
    funcs = '.func if(c,a,b) {c ? a : b}\n'
    if stage != 'syntax_only':
        raw = raw.replace('LIMIT(', 'LIMX(')
        funcs += '.func LIMX(x,a,b) {min(max(x,min(a,b)),max(a,b))}\n'
    wrapper = '''.subckt ATL_FLOAT K R A
E_K KC 0 K A 1
E_R RC 0 R A 1
X_CORE KC RC 0 ATL431A_TRANS
B_K K A I=-I(E_K)
B_R R A I=-I(E_R)
.ends ATL_FLOAT
'''
    return funcs + raw + '\n' + wrapper

def op(text, names):
    sp.cmd('destroy all')
    sp.load(text)
    sp.cmd('op')
    row = {n: float(sp.vector('v(' + n + ')')[-1]) for n in names}
    assert all(np.isfinite(v) for v in row.values()), row
    return row

def fixture(stage, offset, current):
    part = 'ATL_FLOAT' if stage == 'floating' else 'ATL431A_TRANS'
    deck = f'''HD006 floating-reference translation fixture
VA A 0 {offset}
IB A K {current}
RH K REF 700000
RL REF A 100000
XREF K REF A {part}
{reference(stage)}
.end
'''
    r = op(deck, ['a', 'k', 'ref'])
    r.update(stage=stage, offset_V=offset, injected_A=current,
             cathode_V=r['k']-r['a'], reference_V=r['ref']-r['a'])
    if stage == 'floating':
        r['core_K_A'] = -float(sp.vector('i(e.xref.e_k)')[-1])
        r['core_REF_A'] = -float(sp.vector('i(e.xref.e_r)')[-1])
    return r

def deck(c, vin, profile, cold, vto=-3.5, transient=False, fault=None):
    p = c['profiles'][profile]
    z = c['topology']
    source = f'PWL(0 0 .01 0 .02 {vin} 2 {vin})' if transient else str(vin)
    load = '' if cold else f"RLOAD OUT 0 {z['extra_warm_load_ohm']}"
    faultpart = {'output_short':'RFAULT OUT 0 1', 'pass_short':'RFAULT D S .001'}.get(fault, '')
    return f'''HD006 candidate; surrogate MOSFET and regulator; no circuit qualification
VIN IN 0 {source}
RF IN D {z['drain_feed_ohm']}
RB1 IN RBMID {z['gate_bias_each_ohm']}
RB2 RBMID GREF {z['gate_bias_each_ohm']}
RG GREF G 1000
RGH GREF REF {z['gate_upper_ohm']}
RGL REF OUT {z['gate_lower_ohm']}
XREF GREF REF OUT ATL_FLOAT
M1 D G S S QPASS
.model QPASS NMOS LEVEL=1 VTO={vto} KP=.4898 LAMBDA=0 RD=.1 RS=.1
CGS G S 1000p
CGD G D 17p
DB S D DBODY
.model DBODY D IS=1e-12 RS=.2
RS S REGIN {z['source_ohm']}
RCIN REGIN CIN {z['local_input_series_ohm']}
CIN CIN OUT {z['local_input_F']}
BREG REGIN OUT I=max(0,min(.2,min((V(REGIN,OUT)-3)/1,({p['vref']}-V(OUT,ADJ))*1000)))
BIPROG REGIN ADJ I={p['iadj']}*max(0,min(1,V(REGIN,OUT)/3))
RSET OUT ADJ {p['rset']}
RLOW ADJ 0 {p['rlow']}
COUT OUT 0 {z['output_F']}
RHEAT OUT 0 {z['heater_divider_ohm']}
{load}
{faultpart}
{reference()}
.end
'''

NODES = ['in', 'd', 'g', 's', 'regin', 'out', 'adj', 'gref', 'ref']

def metrics(r, c):
    z = c['topology']
    ids = (r['in']-r['d'])/z['drain_feed_ohm']
    isource = (r['s']-r['regin'])/z['source_ohm']
    ibias = (r['in']-r['gref'])/(2*z['gate_bias_each_ohm'])
    return dict(source_A=isource, drain_A=ids, gate_bias_A=ibias,
                regulator_delta_V=r['regin']-r['out'], gate_source_V=r['g']-r['s'],
                pass_W=ids*(r['d']-r['s']), source_W=isource**2*z['source_ohm'],
                bias_each_W=ibias**2*z['gate_bias_each_ohm'])

def main():
    c = json.loads((M/'pass-contract.json').read_text())
    assert sha(M/c['model']) == c['model_sha256']
    fixtures = [fixture(stage, offset, current) for stage, offset, current in
                itertools.product(['syntax_only', 'clamp_fixed', 'floating'], [0,273], [80e-6,.001,.005])]
    rows = []
    for vin, profile, cold, vto in itertools.product(c['input_V'], c['profiles'], [False,True], c['vto_sensitivity_V']):
        text = deck(c, vin, profile, cold, vto)
        r = op(text, NODES)
        rows.append(dict(input_V=vin, profile=profile, cold=cold, vto_V=vto,
                         nodes=r, metrics=metrics(r,c), deck_sha256=hashlib.sha256(text.encode()).hexdigest()))
    faults = []
    for fault in ['output_short','pass_short']:
        text = deck(c,550,'nominal',False,fault=fault)
        r = op(text,NODES)
        faults.append(dict(fault=fault,nodes=r,metrics=metrics(r,c)))
        (M/f'results/pass-{fault}.cir').write_text(text)
    transient = []
    for vin, step in [(320,1e-4),(380,1e-4),(550,1e-4),(320,5e-5)]:
        text=deck(c,vin,'nominal',False,transient=True)
        name=f'pass-start-{vin}-{step:g}'
        sp.cmd('destroy all');sp.load(text)
        sp.cmd('save '+ ' '.join('v('+n+')' for n in NODES))
        sp.cmd(f'tran {step} 2 0 {step}')
        t=np.array(sp.vector('time'))
        data={n:np.array(sp.vector('v('+n+')')) for n in NODES}
        complete=bool(t[-1]>=2-1e-9 and all(np.all(np.isfinite(a)) for a in data.values()))
        path=M/f'results/{name}.npz'
        np.savez_compressed(path,time=t,**data)
        (M/f'results/{name}.cir').write_text(text)
        derived=metrics(data,c)
        transient.append(dict(id=name,complete=complete,end_s=float(t[-1]),
            deck_sha256=sha(M/f'results/{name}.cir'),waveform_sha256=sha(path),
            output_last_V=float(data['out'][-1]),output_max_V=float(data['out'].max()),
            extrema={k:dict(min=float(v.min()),max=float(v.max())) for k,v in derived.items()}))
    prior=json.loads((M/'ceiling-contract.json').read_text())['supply_contract']
    result=dict(id=c['id'],contract_sha256=sha(M/'pass-contract.json'),factory_sha256=sha(Path(__file__)),
        runtime_sha256=sha(ROOT/'engineering/whole-amp/tools/spice_runtime.py'),model_sha256=sha(M/c['model']),
        fixtures=fixtures,dc=rows,faults=faults,transients=transient,
        native_sha256=prior['native_sha256'],limitations=c['limitations'],
        adopted=False,hardware_qualified=False,stability_qualified=False,protection_qualified=False)
    (M/'results/pass-screen.json').write_text(json.dumps(result,indent=2)+'\n')
    (M/'results/pass-simulator.log').write_text('\n'.join(sp.logs)+'\n')
    print(json.dumps(dict(fixtures=len(fixtures),dc=len(rows),faults=faults,transients=transient),indent=2))

if __name__ == '__main__':
    main()
