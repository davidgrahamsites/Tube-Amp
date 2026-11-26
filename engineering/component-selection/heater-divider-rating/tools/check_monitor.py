"""Audit saved HD-011 evidence independently; failures remain engineering holds."""
from pathlib import Path
import csv,gzip,hashlib,io,json,math
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name,ok):
 checks.append(dict(name=name,passed=bool(ok)))
 if not ok:raise AssertionError(name)
c=json.loads((M/'monitor-contract.json').read_text())
for p,h in c['inputs'].items():check('input '+p,sha(M/p)==h)
for p,h in json.loads((M/'results/detector-screen.json').read_text())['native_sha256'].items():check('native '+p,sha(ROOT/p)==h)
packed=json.loads((M/'results/monitor-waveforms.json').read_text());data={};receipts={}
for p in packed:
 path=M/'results'/p['file'];check('compressed hash '+p['file'],sha(path)==p['compressed_sha256'])
 raw=gzip.decompress(path.read_bytes());check('raw hash '+p['file'],hashlib.sha256(raw).hexdigest()==p['raw_sha256'])
 name=p['file'].removeprefix('monitor-').removesuffix('.csv.gz');r=json.loads((M/'results'/('monitor-'+name+'.json')).read_text());receipts[name]=r
 check('deck '+name,sha(M/'results'/('monitor-'+name+'.cir'))==r['deck_sha256']);check('factory '+name,sha(M/'tools/monitor_hold.py')==r['factory_sha256'])
 a=[{k:float(v) for k,v in row.items()} for row in csv.DictReader(io.StringIO(raw.decode()))];data[name]=a
 check('finite '+name,all(math.isfinite(v) for row in a for v in row.values()));check('rows '+name,len(a)==r['rows']);check('time '+name,all(a[i]['time']>a[i-1]['time'] for i in range(1,len(a))))
 for k,limits in r['ranges'].items():check('extrema '+name+' '+k,abs(min(x[k] for x in a)-limits[0])<1e-10 and abs(max(x[k] for x in a)-limits[1])<1e-10)
 check('complete flag '+name,r['completed']==(abs(a[-1]['time']-(3 if 'resetprobe' in name else (1 if 'fixture' in name else .6)))<1e-9))
def sample(name,t):return min(data[name],key=lambda row:abs(row['time']-t))
normal=sample('fixture',.18);old=sample('fixture-rejected',.18)
check('normal LEDs off',abs(normal['i(vled)'])<1e-8);check('rejected divider loads LEDs',old['i(vled)']>50e-6)
check('fault hold below trip',sample('fixture',.4)['i(vled)']>.001)
check('low-output reset',abs(sample('fixture',.6)['i(vled)'])<1e-8)
check('default coupled branch fault held',sample('fault-550',.09)['i(vled)']>.001 and not receipts['fault-550']['trip'])
q=sample('resetprobe-550',1.4);check('normal state before fault',abs(q['v(out)']-267.11)<.02 and abs(q['i(vled)'])<1e-8)
# Steady normal-output KCL: source feed + two gate biases/backflows = all OUT loads.
kcl=(q['v(s)']-q['v(regin)'])/646+sum((q['v(in)']-q['v('+n+')'])/149700 for n in ['gref','gref2'])+sum((q['v('+a+')']-q['v('+b+')'])/100000 for a,b in [('g','gref'),('g2','gref2')])-q['v(out)']/78000-(q['v(out)']-1.25)/42200-q['v(out)']/100000-q['v(out)']/1186100
check('settled current balance',abs(kcl)<1e-7)
pk=receipts['resetprobe-550']['ranges']['v(out)'][1];fine=receipts['resetprobe-550-fine']['ranges']['v(out)'][1]
check('conditional peak below300',pk<300 and fine<300);check('refinement peak agreement',abs(pk-fine)<.001)
check('fault remains held',sample('resetprobe-550',2.99)['i(vled)']>.001)
check('startup failure preserved',not receipts['startup-550']['completed'] and receipts['startup-550']['ranges']['v(mon)'][0]<0)
failed=json.loads((M/'results/monitor-resetprobe-320.json').read_text());check('320V solver failure preserved',not failed['completed'] and failed['rows']==0)
b=json.loads((M/'results/monitor-budget.json').read_text());check('shunt reserve',b['shunt_reserve_min_A']>.000095);check('shunt current upper',b['feed_max_A']<.015)
check('trip normal margin',b['trip_min_V']-285.423863>2);check('trip ceiling margin',300-b['trip_max_V']>2)
check('reset below previous minimum forced clamp',b['reset_upper_allocation_V']<102.91447)
check('no adoption',c['adopted'] is False and b['qualified'] is False)
out=dict(passed=True,checks=checks,count=len(checks),normal_KCL_A=kcl,normal_LED_A=normal['i(vled)'],rejected_LED_A=old['i(vled)'],peak_refinement_delta_V=abs(pk-fine),engineering_qualified=False,holds=['Power-on startup invalid/aborted','320V coupled probe has no transient solution','Diagnostic reset source is not hardware','Typical/generic dynamic models and temperature allocations do not qualify protection'])
(M/'results/monitor-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='checks'},indent=2))
