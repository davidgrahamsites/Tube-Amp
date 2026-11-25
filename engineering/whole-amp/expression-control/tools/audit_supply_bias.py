"""Evidence integrity and numerical checks; circuit release remains a separate gate."""
from pathlib import Path
import hashlib,json,math
import ota_screen as ota
checks=[]
def check(name,value):
    checks.append(dict(name=name,passed=bool(value)))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def finite_tree(x):
    if isinstance(x,float):return math.isfinite(x)
    if isinstance(x,dict):return all(finite_tree(v) for v in x.values())
    if isinstance(x,list):return all(finite_tree(v) for v in x)
    return True

def read_report(filename):
    d=json.loads((ota.OUT/filename).read_text())
    for p,h in d['provenance'].items():check(filename+' source '+p,sha(ota.ROOT/p)==h)
    for c in d['cases']:
        check(filename+' deck '+c['name'],sha(ota.OUT/c['deck'])==c['deck_sha256'])
        check(filename+' finite '+c['name'],finite_tree(c))
        if c['status']=='complete' and 'end_s' in c:
            check(filename+' duration '+c['name'],abs(c['end_s']-16/c['case'].get('hz',1000))<1e-8)
    return d,{c['name']:c for c in d['cases']}

def main():
    supply,s=read_report('supply-probes.json');bias,b=read_report('bias-screen.json')
    check('supply nine causal cases',len(s)==9)
    check('original timeout retained',s['baseline12']['status']=='timeout')
    for n in ['dc12','shunt12']:
        check(n+' invalid DC not accepted',s[n]['status']=='complete' and not s[n]['op_within_supply'] and abs(s[n]['op']['out'])>400)
    good=['nodeset12','seed-minus','seed-plus','refined12','nodeset15','weak-shunt12']
    for n in good:check(n+' physical and finished',s[n]['status']=='complete' and s[n]['op_within_supply'])
    base=s['nodeset12']
    seed_delta=max(abs(s[n]['gain']/base['gain']-1) for n in ['seed-minus','seed-plus'])
    refine_delta=abs(s['refined12']['gain']/base['gain']-1)
    check('seed-independent gain 1 ppm',seed_delta<1e-6)
    check('supply half-step gain 0.01 percent',refine_delta<.0001)
    check('supply weak-shunt gain 1 ppm',abs(s['weak-shunt12']['gain']/base['gain']-1)<1e-6)
    check('bias calibration inside travel',0<bias['trim_fraction']<1)
    check('bias calibration residual <1 mV',b['calibrated']['status']=='complete' and abs(b['calibrated']['op']['out'])<.001)
    for rail in [12,15,16.5]:
        for target in [0,2.5]:
            c=b[f'dc-{rail}-{target}'];check(c['name']+' physical OP',c['status']=='complete' and c['op_within_supply'])
        c=b[f'dc-{rail}-0']
        check(c['name']+' nominal DC <1 mV',abs(c['op']['out'])<.001)
        check(c['name']+' nominal bias 475-525uA',.000475<-c['collector_currents_A']['qbi']<.000525)
        check(c['name']+' diode bias 0.95-1.05mA',.00095<-c['collector_currents_A']['qdm']<.00105)
    for n in ['audio-12','audio-15','audio-refined']:
        c=b[n];check(n+' completed and physical',c['status']=='complete' and c['op_within_supply'])
        if c['status']=='complete':
            check(n+' nominal 1k THD <0.1 percent',c['thd_percent']<.1)
            check(n+' amplitude gain 0.9-1.1',.9<c['gain']<1.1)
    if b['audio-refined']['status']==b['audio-15']['status']=='complete':
        check('bias half-step gain 0.1 percent',abs(b['audio-refined']['gain']/b['audio-15']['gain']-1)<.001)
    failures=[dict(name=c['name'],status=c['status']) for c in bias['cases'] if c['status']!='complete']
    # Integrity check explicitly carries engineering failures forward; it does not excuse them.
    check('unresolved heel endpoint exposed',all(b[f'dc-{v}-5']['status']!='complete' for v in [12,15,16.5]))
    # Recorded baseline is also checked against Git's current committed native files.
    import subprocess
    for name in ["Main","Power","Control","Reverb"]:
        p=Path('engineering/whole-amp/pcb-measured-r/boards')/f'Renegade_{name}.kicad_pcb'
        committed=subprocess.check_output(['git','show','HEAD:'+str(p)],cwd=ota.ROOT)
        check('native '+name+' unchanged',sha(ota.ROOT/p)==hashlib.sha256(committed).hexdigest())
    result=dict(evidence_checks_passed=all(c['passed'] for c in checks),check_count=len(checks),checks=checks,
                circuit_qualified=False,unresolved_simulations=failures,git_baseline=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ota.ROOT,text=True).strip(),
                limitations=['No protected pedal or selector integration','Heel operating point and candidate trim margin require repair','No startup/ESD/tolerance/noise/stability or actual reference qualification','No socket/PCB/chassis adoption','Shanghai checkout and marketplace seller verification not complete'],
                seed_relative_gain_delta=seed_delta,supply_refinement_relative_gain_delta=refine_delta,
                provenance={str(Path(__file__).relative_to(ota.ROOT)):sha(Path(__file__)),
                    'supply-probes.json':sha(ota.OUT/'supply-probes.json'),'bias-screen.json':sha(ota.OUT/'bias-screen.json')})
    (ota.OUT/'supply-bias-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['checks','provenance']},indent=2))
    for c in checks:
        if not c['passed']:print('FAIL',c['name'])
    assert result['evidence_checks_passed']
if __name__=='__main__':main()
