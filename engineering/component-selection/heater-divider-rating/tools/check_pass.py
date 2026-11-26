"""Independent HD-006 arithmetic, adapter KCL, evidence and applicability audit."""
from pathlib import Path
import hashlib, itertools, json
import numpy as np

M=Path(__file__).resolve().parents[1]; ROOT=M.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((M/'pass-contract.json').read_text())
r=json.loads((M/'results/pass-screen.json').read_text())
checks=[]
def ck(name,passed): checks.append(dict(name=name,passed=bool(passed)))
ck('contract receipt',sha(M/'pass-contract.json')==r['contract_sha256'])
ck('factory receipt',sha(M/'tools/pass_topology.py')==r['factory_sha256'])
ck('prior contract',sha(M/c['prior_contract'])==c['prior_contract_sha256'])
ck('manufacturer model preserved',sha(M/c['model'])==c['model_sha256']==r['model_sha256'])
ck('runtime receipt',sha(ROOT/'engineering/whole-amp/tools/spice_runtime.py')==r['runtime_sha256'])
for p,h in r['native_sha256'].items(): ck('native preserved '+p,sha(ROOT/p)==h)
f={(a['stage'],a['offset_V'],a['injected_A']):a for a in r['fixtures']}
ck('18 fixtures',len(f)==len(r['fixtures'])==18)
for current in [80e-6,.001,.005]:
    a=f['floating',0,current];b=f['floating',273,current]
    ck(f'{current} voltage translation',abs(a['cathode_V']-b['cathode_V'])<1e-9)
    for row in [a,b]:
        ck(f'{current}/{row["offset_V"]} grounded expected reference',2.49<row['reference_V']<2.51 and 19.9<row['cathode_V']<20.2)
        upper=(row['k']-row['ref'])/700000
        lower=(row['ref']-row['a'])/100000
        ck(f'{current}/{row["offset_V"]} cathode KCL',abs(current-upper-row['core_K_A'])<1e-10)
        ck(f'{current}/{row["offset_V"]} reference KCL',abs(upper-lower-row['core_REF_A'])<1e-10)
    ck(f'{current} current translation',abs(a['core_K_A']-b['core_K_A'])<1e-12 and abs(a['core_REF_A']-b['core_REF_A'])<1e-12)
    ck(f'{current} reject syntax-only grounded result',abs(f['syntax_only',0,current]['cathode_V']-20)>10)
    ck(f'{current} reject unwrapped floating result',abs(f['clamp_fixed',273,current]['cathode_V']-20)>10)
expected=set(itertools.product(c['input_V'],c['profiles'],[False,True],c['vto_sensitivity_V']))
actual={(a['input_V'],a['profile'],a['cold'],a['vto_V']) for a in r['dc']}
ck('all54 declared DC cases',expected==actual and len(r['dc'])==54)
for i,row in enumerate(r['dc']):
    n=row['nodes'];p=c['profiles'][row['profile']];m=row['metrics']
    source=(n['s']-n['regin'])/680
    bias=(n['in']-n['gref'])/99800
    target=p['vref']*(1+p['rlow']/p['rset'])+p['iadj']*p['rlow']
    ck(f'{i} voltage target within10mV',abs(n['out']-target)<.01)
    load=n['out']/78000+(0 if row['cold'] else n['out']/36200)+n['adj']/p['rlow']
    ck(f'{i} total output KCL',abs(source+bias-load)<1e-8)
    ck(f'{i} reported source current',abs(source-m['source_A'])<1e-12)
    ck(f'{i} normal differential',3<n['regin']-n['out']<40)
    ck(f'{i} normal gate voltage',abs(n['g']-n['s'])<20)
    ck(f'{i} rail ceiling',n['out']<300)
fault={a['fault']:a for a in r['faults']}
ck('pass-short detected beyond regulator applicability',fault['pass_short']['metrics']['regulator_delta_V']>40)
ck('pass-short detected beyond gate applicability',abs(fault['pass_short']['metrics']['gate_source_V'])>20)
ck('output-short thermal demand retained',fault['output_short']['metrics']['pass_W']>15)
ck('four diagnostic startups',len(r['transients'])==4)
for a in r['transients']:
    name=a['id'];d=np.load(M/f'results/{name}.npz');time=d['time']
    ck(name+' waveform receipt',sha(M/f'results/{name}.npz')==a['waveform_sha256'])
    ck(name+' deck receipt',sha(M/f'results/{name}.cir')==a['deck_sha256'])
    ck(name+' full finite run',a['complete'] and time[-1]>=2 and np.all(np.diff(time)>0) and all(np.all(np.isfinite(d[k])) for k in d.files))
    ck(name+' saved final output',abs(d['out'][-1]-a['output_last_V'])<1e-10)
    ck(name+' saved source peak',abs(max((d['s']-d['regin'])/680)-a['extrema']['source_A']['max'])<1e-10)
    ck(name+' saved pass peak',abs(max((d['in']-d['d'])/100*(d['d']-d['s']))-a['extrema']['pass_W']['max'])<1e-10)
    ck(name+' saved differential peak',abs(max(d['regin']-d['out'])-a['extrema']['regulator_delta_V']['max'])<1e-10)
base=r['transients'][0];fine=r['transients'][3]
peak_delta=abs(base['extrema']['regulator_delta_V']['max']/fine['extrema']['regulator_delta_V']['max']-1)
ck('final output timestep agreement',abs(base['output_last_V']-fine['output_last_V'])<1e-6)
ck('transient peak sensitivity not hidden',peak_delta>.01)
for key in ['adopted','hardware_qualified','stability_qualified','protection_qualified']:
    ck(key+' remains false',r[key] is False)
out=dict(passed=all(a['passed'] for a in checks),checks=checks,
         transient_peak_relative_change=peak_delta,engineering_qualified=False,
         result_sha256=sha(M/'results/pass-screen.json'),
         scope='Evidence and model-applicability checks only; fault protection and physical operation fail acceptance.')
(M/'results/pass-checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(passed=out['passed'],count=len(checks),failures=[a for a in checks if not a['passed']]),indent=2))
assert out['passed']
