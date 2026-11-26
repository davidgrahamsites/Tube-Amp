"""Independent terminal-current and fault-applicability audit for HD-007."""
from pathlib import Path
import itertools,json,hashlib,math
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((M/'series-contract.json').read_text());b=json.loads((M/'pass-contract.json').read_text());r=json.loads((M/'results/series-screen.json').read_text());checks=[]
def ck(name,passed):checks.append(dict(name=name,passed=bool(passed)))
ck('contract receipt',sha(M/'series-contract.json')==r['contract_sha256'])
ck('factory receipt',sha(M/'tools/series_protection.py')==r['factory_sha256'])
ck('adapter frozen',sha(M/c['adapter'])==c['adapter_sha256']==r['adapter_sha256'])
ck('prior contract frozen',sha(M/c['prior_contract'])==c['prior_contract_sha256'])
ck('original model frozen',sha(M/b['model'])==b['model_sha256'])
for p,h in r['native_sha256'].items():ck('native preserved '+p,sha(ROOT/p)==h)
def key(a):
    s=a['sensitivity'];return(a['vin'],a['profile'],a['cold'],a['fault'],s['vto1'],s['vto2'],s['source_ohm'])
expect={(v,p,cold,f,s['vto1'],s['vto2'],s['source_ohm']) for v,p,cold,f,s in itertools.product(c['input_V'],c['profiles'],c['cold'],c['faults'],c['sensitivity'])}
ck('270 declared corners covered',len(r['dc'])==270 and {key(a['case']) for a in r['dc']}==expect)
def kcl(row):
    n=row['nodes'];case=row['case'];q=b['profiles'][case['profile']]
    supply=(n['s']-n['regin'])/case['sensitivity']['source_ohm']
    supply+=(2*n['in']-n['gref']-n['gref2'])/149700
    supply+=(n['g']-n['gref']+n['g2']-n['gref2'])/100000
    load=n['out']*(1/78000+(0 if case['cold'] else 1/36200)+(1/100000 if case['preload'] else 0))+n['adj']/q['rlow']
    return supply-load
for i,a in enumerate(r['dc']):
    n=a['nodes'];m=a['metrics'];case=a['case'];q=b['profiles'][case['profile']]
    target=q['vref']*(1+q['rlow']/q['rset'])+q['iadj']*q['rlow']
    current=(n['s']-n['regin'])/case['sensitivity']['source_ohm']-q['iadj']
    ck(f'{i} finite nodes',all(math.isfinite(v) for v in n.values()))
    ck(f'{i} independently balanced output',abs(kcl(a))<1e-7)
    ck(f'{i} reported residual',abs(kcl(a)-m['output_KCL_A'])<1e-12)
    ck(f'{i} requested setting',abs(n['out']-target)<.01)
    ck(f'{i} sampled output ceiling',n['out']<300)
    ck(f'{i} sampled regulator differential',3<n['regin']-n['out']<40)
    ck(f'{i} sampled both gate voltages',abs(n['g']-n['mid'])<20 and abs(n['g2']-n['s'])<20)
    ck(f'{i} regulator minimum load',current>=.005 and abs(current-m['regulator_output_A'])<1e-12)
    ck(f'{i} preload heat',abs(n['out']*n['out']/100000-m['preload_W'])<1e-12)
for i,a in enumerate(r['comparisons']):
    ck(f'comparison{i} independent residual',abs(kcl(a)-a['metrics']['output_KCL_A'])<1e-12)
    if not a['case']['seed']:
        ck(f'comparison{i} reject invalid OP despite returned vectors',abs(kcl(a))>.001)
    elif a['case']['fault']=='q1_short':
        ck('no-preload minimum load defect retained',abs(kcl(a))<1e-7 and a['metrics']['regulator_output_A']<.005)
    else:
        ck('seeded control is balanced',abs(kcl(a))<1e-7)
a=r['regulator_fault']
ck('regulator-short result is balanced',abs(kcl(a))<1e-7)
ck('independent output-protection gap retained',a['nodes']['out']>300)
for flag in ['model_qualification','adopted','full_fault_qualification']:ck(flag+' remains false',r[flag] is False)
out=dict(passed=all(x['passed'] for x in checks),checks=checks,result_sha256=sha(M/'results/series-screen.json'),
    scope='Current balance and bounded DC comparison only; no dynamic, complete protection, parts or physical qualification.')
(M/'results/series-checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(passed=out['passed'],count=len(checks),failures=[x for x in checks if not x['passed']]),indent=2));assert out['passed']
