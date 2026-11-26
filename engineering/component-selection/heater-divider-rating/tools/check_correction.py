"""Independent HD-003 arithmetic, artifact and preservation audit."""
from pathlib import Path
import hashlib
import itertools
import json
import math

M=Path(__file__).resolve().parents[1]
ROOT=M.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((M/'correction-contract.json').read_text())
s=json.loads((M/'results/correction-screen.json').read_text())
checks=[]
def check(name,passed):
    checks.append(dict(name=name,passed=bool(passed)))
p=c['candidate'];vmax=p['preamp_ceiling_V']
check('contract receipt',sha(M/'correction-contract.json')==s['contract_sha256'])
check('factory receipt',sha(M/'tools/correction.py')==s['factory_sha256'])
for path,h in {**c['source_sha256'],**c['native_sha256']}.items():check('preserved '+path,sha(ROOT/path)==h)
check('16 reference corners',len(s['analytic']['corners'])==len(s['reference_transients'])==16)
for i,r in enumerate(s['analytic']['corners']):
    # Enumerate state extrema without using the closed-form bound under test.
    extremes=[]
    for u,z in itertools.product([0,vmax],repeat=2):
        ref=r['ai']*u+(r['a0']-r['ai'])*z
        for cathode in [0,u]:
            for polarity in [-1,1]:
                heater=ref+polarity*(s['analytic']['heater_endpoint_peak_V']+p['total_leakage_budget_A']*(r['rth_ohm']+p['midpoint_R_ohm']*(1+p['midpoint_total_tolerance'])))
                extremes.append(abs(heater-cathode))
    check(f'corner {i} independent state bound',abs(max(extremes)-r['worst_hk_V'])<1e-9)
    check(f'corner {i} normal voltage allocation',r['worst_hk_V']<p['preamp_hk_limit_V'])
    t=s['reference_transients'][i]
    check(f'corner {i} transfer vs ngspice',t['max_error_V']<.001)
    check(f'corner {i} simulated no-leak bound',t['worst_hk_without_leak_V']<=r['worst_hk_V']+.001)
    check(f'corner {i} deck receipt',sha(M/f'results/correction-ref-{i:02}.cir')==t['deck_sha256'])
source=json.loads((ROOT/'engineering/whole-amp/reverb-600/circuit.json').read_text())
resistors={x['reference']:x for x in source['components'] if x['reference'].startswith('R')}
for r in s['analytic']['cathode_return_paths']:
    check(r['node']+' full DC path',r['total_reference_max_ohm']<r['limit_ohm'])
    check(r['node']+' source-open DC path',r['source_open_reference_max_ohm']<r['limit_ohm'])
    previous=r['node']
    for ref,expected in c['cathode_return_paths'][r['node']]:
        component=resistors[ref];value=component['value'];actual=float(value[:-1])*1000 if value.endswith('k') else float(value)
        pins=set(component['pins'].values())
        check(ref+' value and path',actual==expected and previous in pins)
        previous=next(iter(pins-{previous}))
    check(r['node']+' ends at GND',previous=='GND')
check('355 V negative control rejected',.55*355+s['analytic']['heater_endpoint_peak_V']>p['preamp_hk_limit_V'])
check('eight single-fault envelopes remain rejected',len(s['analytic']['faults'])==8 and all(not f['passes'] for f in s['analytic']['faults']))
check('five audio comparisons complete',len(s['audio'])==5 and all(r['status']=='completed' for r in s['audio']))
comparisons=[]
for ch in ['clean','dirty']:
    rows=[r for r in s['audio'] if r['case']['channel']==ch and not r['case'].get('refine')]
    if len(rows)!=2 or any(r['status']!='completed' for r in rows):continue
    a,b=rows
    def normalized(r):
        text=(M/f'results/correction-{r["case"]["id"]}.cir').read_text()
        return text.replace(f'VPRE B_PRE 0 {r["case"]["pre_V"]}','VPRE B_PRE 0 COMPARE')
    check(ch+' paired decks differ only at preamp rail',normalized(a)==normalized(b))
    comparisons.append(dict(channel=ch,gain_delta_dB={f:20*math.log10(b['ac'][f]['gain']/a['ac'][f]['gain']) for f in a['ac']},
                            fundamental_change_percent=100*(b['fundamental_W']/a['fundamental_W']-1)))
for r in s['audio']:
    if r['status']!='completed':continue
    check(r['case']['id']+' deck receipt',sha(M/f'results/correction-{r["case"]["id"]}.cir')==r['deck_sha256'])
    check(r['case']['id']+' settled speaker fundamental',r['settling_relative']['SPEAKER']<.001)
normal=[r for r in s['audio'] if r['case']['id']=='clean-300'][0]
fine=[r for r in s['audio'] if r['case']['id']=='clean-300-fine'][0]
if normal['status']==fine['status']=='completed':
    check('refined power within 0.1 percent',abs(fine['fundamental_W']/normal['fundamental_W']-1)<.001)
    check('refined THD within 0.02 percentage point',abs(fine['signals']['SPEAKER']['THD_2_to_10_percent']-normal['signals']['SPEAKER']['THD_2_to_10_percent'])<.02)
check('not promoted to native or hardware acceptance',s['adopted'] is False and s['hardware_qualified'] is False)
out=dict(checks=checks,comparisons=comparisons,passed=all(x['passed'] for x in checks),
         scope='Evidence arithmetic and preservation only; supply implementation, fault protection and hardware qualification remain open.',
         result_sha256=sha(M/'results/correction-screen.json'))
(M/'results/correction-checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(passed=out['passed'],checks=len(checks),failures=[x for x in checks if not x['passed']],comparisons=comparisons),indent=2))
assert out['passed']
