"""Validate retained diagnostic evidence without treating unresolved circuits as passed."""
import hashlib,json,math
from pathlib import Path
import ota_screen as ota
checks=[]
def check(n,v):checks.append(dict(name=n,passed=bool(v)))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    reports={}
    for filename in ['trim-screen.json','bias-isolation.json','continuation.json']:
        d=json.loads((ota.OUT/filename).read_text());reports[filename]=d
        for p,h in d['provenance'].items():check(filename+' provenance '+p,sha(ota.ROOT/p)==h)
        for r in d.get('cases',[]):
            n=r.get('name',r.get('mode'))
            for k in ['deck','log']:check(filename+' '+n+' '+k,sha(ota.OUT/r[k])==r[k+'_sha256'])
            if 'op' in r:check(n+' finite OP',all(math.isfinite(x) for x in r['op'].values()))
            if 'end_s' in r:check(n+' final time',abs(r['end_s']-(.001 if 'mode' in r else 16/r['case'].get('hz',1000)))<1e-9)
    d=reports['trim-screen.json'];cases={r['name']:r for r in d['cases']}
    check('trim nominal center margin',.4<d['calibrated_fractions']['150000']<.7)
    check('220k nominal margin',.6<d['calibrated_fractions']['220000']<.85)
    for n in ['150000-cal-3','220000-cal-3']:check(n+' residual under 1uV',abs(cases[n]['op']['out'])<1e-6)
    for n in ['audio-100','audio-1000','audio-10000','audio-12','audio-refined']:
        r=cases[n];check(n+' valid transient',r['status']=='complete' and r['op_within_supply'])
        check(n+' nominal THD under 0.1 percent',r['thd_percent']<.1)
    check('half-step gain agreement 0.01 percent',abs(cases['audio-refined']['gain']/cases['audio-1000']['gain']-1)<.0001)
    # New failure is carried forward, not hidden by the successful trim adjustment.
    check('12V midpoint regression retained',cases['dc-12-2.5']['status']=='failed-op')
    check('heel failures retained',all(cases[f'dc-{v}-5']['status']=='failed-op' for v in [12,15,16.5]))
    iso={r['mode']:r for r in reports['bias-isolation.json']['cases']}
    check('full circuit failure retained',iso['complete-circuit']['status']=='failed-op')
    for n in ['fixed-base','ideal-servo']:check(n+' isolated diagnostic only',iso[n]['status']=='diagnostic-complete' and abs(iso[n]['op']['out'])<.001)
    servo=iso['servo-alone'];check('pseudo transient OP not mistaken for settled state',servo['op_used_transient_fallback'] and servo['op_to_final_max_delta_V']>2)
    check('servo final agrees with previous ramp at 1mV',abs(servo['final']['bo']-5.006036)<.001)
    check('all-node continuation remains failed',reports['continuation.json']['status']=='failed' and reports['continuation.json']['seeds']==267)
    result=dict(evidence_checks_passed=all(x['passed'] for x in checks),checks=checks,circuit_qualified=False,
        unresolved=[r['name'] for r in d['cases'] if r['status']!='complete'],
        provenance={str(Path(__file__).relative_to(ota.ROOT)):sha(Path(__file__))})
    (ota.OUT/'trim-isolation-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=result['evidence_checks_passed'],checks=len(checks),circuit_qualified=False,unresolved=result['unresolved'])))
    assert result['evidence_checks_passed'],[r for r in checks if not r['passed']]
if __name__=='__main__':main()
