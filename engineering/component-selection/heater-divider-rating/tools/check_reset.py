"""HD012 independent endpoint, waveform and preservation checks."""
from pathlib import Path
import csv,gzip,hashlib,io,json,math
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(n,ok):
 checks.append(dict(name=n,passed=bool(ok)))
 if not ok:raise AssertionError(n)
c=json.loads((M/'reset-contract.json').read_text());b=json.loads((M/'results/reset-bounds.json').read_text())
for p,h in c['inputs'].items():check('source '+p,sha(M/p)==h)
for p,h in json.loads((M/'results/detector-screen.json').read_text())['native_sha256'].items():check('native '+p,sha(ROOT/p)==h)
for name in ['old','candidate']:
 rows=b[name]['corners'];check(name+' corners',len(rows)==512 and len({tuple(x['signs']) for x in rows})==512)
 for num,row in enumerate(rows):
  a,d,e,f,g,h,i,j,k=row['signs'];ref=2.5*(1+a*c['reference_fraction']);ri=10000*(1+d*.004);rr=b[name]['reset_resistor_ohm']*(1+e*.004);lo=0 if f<0 else .55;top=1176000*(1+i*.004);bot=10100*(1+j*.004);sense=row['reset_V']*bot/(top+bot)-k*162.5e-9*top*bot/(top+bot)
  check(name+' threshold '+str(num),abs(sense-row['positive_V']-h*.004)<1e-12)
  if rr:check(name+' positive-node balance '+str(num),abs((ref-row['positive_V'])/ri+(lo-row['positive_V'])/rr-g*162.5e-9)<1e-15)
check('old reset lacks positive guarantee',b['old']['minimum_V']<0)
check('candidate reset window',b['candidate']['minimum_V']>20 and b['candidate']['maximum_V']<90)
check('reset below forced clamp',b['candidate']['maximum_V']<c['prior_minimum_forced_clamp_V'])
runs={};waves={}
for name in ['release','release-fine','trip','monitor-startup','coupled-320','coupled-550']:
 stem='reset-'+name;r=json.loads((M/'results'/f'{stem}.json').read_text());runs[name]=r
 check('factory '+name,r['factory_sha256']==sha(M/'tools/reset_recovery.py'));check('deck '+name,r['deck_sha256']==sha(M/'results'/f'{stem}.cir'))
 p=M/'results'/f'{stem}.csv.gz';check('compressed '+name,r['compressed_sha256']==sha(p));raw=gzip.decompress(p.read_bytes());check('raw '+name,hashlib.sha256(raw).hexdigest()==r['raw_sha256']);a=[{k:float(v) for k,v in row.items()} for row in csv.DictReader(io.StringIO(raw.decode()))];waves[name]=a
 check('rows '+name,len(a)==r['rows']);check('finite '+name,all(math.isfinite(v) for row in a for v in row.values()));check('completed '+name,r['completed']==(name in ['release','release-fine','trip']))
 for key,lohi in r['ranges'].items():check('extrema '+name+' '+key,abs(min(x[key] for x in a)-lohi[0])<1e-10 and abs(max(x[key] for x in a)-lohi[1])<1e-10)
 check('reset events '+name,len(r['reset'])==sum(a[i-1]['i(vled)']>=.0005>a[i]['i(vled)'] for i in range(1,len(a))))
for name in ['release','release-fine','trip']:
 check(name+' reset nominal',len(runs[name]['reset'])==1 and 27<runs[name]['reset'][0]['output_V']<30)
 check(name+' valid rail',runs[name]['ranges']['v(mon)'][0]>8)
 check(name+' final off',abs(runs[name]['final']['i(vled)'])<1e-8)
check('trip retained',len(runs['trip']['trip'])==1 and 293<runs['trip']['trip'][0]['output_V']<295)
check('refinement',abs(runs['release']['reset'][0]['output_V']-runs['release-fine']['reset'][0]['output_V'])<.01)
check('startup invalid-range boundary',runs['monitor-startup']['final']['v(mon)']<4.5)
check('not adopted',c['adopted'] is False)
out=dict(passed=True,count=len(checks),checks=checks,reset_range_V=[b['candidate']['minimum_V'],b['candidate']['maximum_V']],nominal_reset_V=runs['release']['reset'][0]['output_V'],fine_reset_V=runs['release-fine']['reset'][0]['output_V'],full_startup_qualified=False,hardware_verified=False)
(M/'results/reset-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='checks'},indent=2))
