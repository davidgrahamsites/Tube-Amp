"""HD-005 independent KVL, loading, waveform and preservation checks."""
from pathlib import Path
import hashlib,json,math
import numpy as np
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((M/'ceiling-contract.json').read_text());s=json.loads((M/'results/ceiling-screen.json').read_text());checks=[]
def ck(n,b):checks.append(dict(name=n,passed=bool(b)))
ck('contract receipt',sha(M/'ceiling-contract.json')==s['contract_sha256'])
ck('factory receipt',sha(M/'tools/ceiling.py')==s['factory_sha256'])
ck('adapter receipt',sha(M/'tools/supply.py')==s['adapter_sha256'])
ck('prior result unchanged',sha(M/'results/supply-screen.json')==c['prior_result_sha256'])
for group in ['inputs','native_sha256']:
 for path,h in s[group].items():ck('preserved '+path,sha(ROOT/path)==h)
ck('36 DC cases',len(s['dc'])==36)
# Reconstruct the declared resistance bounds without calling the factory.
r=c['feed_resistor']; temperature=r['temperature_coefficient_ppm_per_K']*1e-6*abs(r['allocated_film_temperature_max_C']-r['reference_temperature_C'])
lo=r['nominal_ohm']*(1-r['initial_tolerance'])*(1-temperature)
hi=r['nominal_ohm']*(1+r['initial_tolerance'])*(1+temperature)
for shift in r['qualification_shifts']:
 lo=lo*(1-shift['fraction'])-shift['offset_ohm'];hi=hi*(1+shift['fraction'])+shift['offset_ohm']
ck('declared feed range encloses allocation',c['feed_range_ohm'][0]<=lo and c['feed_range_ohm'][1]>=hi)
expected={(p,v,f,cold) for p in ['low','nominal','high'] for v in [320,380,550] for f in c['feed_range_ohm'] for cold in [False,True]}
actual={(r['profile'],r['case']['input_V'],r['feed_ohm'],r['case']['cold']) for r in s['dc']}
ck('all declared DC corners exactly covered',actual==expected and len(s['dc'])==len(expected))
ck('current-limit feed fault power',abs(s['short_with_current_limit']['feed_W']-.03**2*c['feed_range_ohm'][1])<1e-12)
ck('unlimited fault energy balance',abs(s['pass_short_unlimited']['current_A']*550-s['pass_short_unlimited']['feed_W'])<1e-10)

ck('shunt lower-bound heat',abs(s['shunt_min_feed_W']-(550-300)*((550-300)/10500))<1e-12)
ck('existing5W inadequate at550',s['shunt_min_feed_W']>5)
for r in s['dc']:
 case=r['case'];name=case['id'];vin=case['input_V'];i=r['input_A'];rf=r['feed_ohm'];v=r['pre_V'];head=vin-i*rf-v
 ck(name+' deck receipt',sha(M/f'results/supply-{name}.cir')==r['deck_sha256'])
 ck(name+' output screens unchanged','VSCREEN B_SCREEN 0 380' in (M/f'results/supply-{name}.cir').read_text())
 target={'low':1.2*(1+42984/201),'nominal':1.25*(1+43200/200)+.00005*43200,'high':1.313*(1+43416/199)+.000101*43416}[r['profile']]
 ck(name+' independent voltage target',abs(target-r['target_V'])<1e-8)
 ck(name+' regulation within10mV',abs(v-target)<.01)
 ck(name+' declared ceiling',v<300)
 ck(name+' adequate behavioral headroom',head>=10+100*i-1e-5)
 ck(name+' heat KVL',abs(r['pass_W']-head*i)<1e-5 and abs(r['feed_W']-i*i*rf)<1e-10)
 ck(name+' bounded current',0<i<.03)
 if case['cold']:
  if r['profile']=='low':rt,rb,ia=201,42984,0
  elif r['profile']=='high':rt,rb,ia=199,43416,.000101
  else:rt,rb,ia=200,43200,.00005
  ck(name+' cold load nodal balance',abs(i-v/78000-(v+ia*rt)/(rt+rb))<1e-8)
rows={r['case']['id']:r for r in s['audio']};ck('four audio cases complete',len(rows)==4 and all(r['status']=='completed' for r in rows.values()))
for name,r in rows.items():
 if r['status']!='completed':continue
 d=np.genfromtxt(M/f'results/supply-{name}.csv',delimiter=',',names=True);a=np.fft.rfft(d['SPEAKER']-np.mean(d['SPEAKER']));vp=2*abs(a[10])/len(d);thd=100*math.sqrt(sum(abs(a[k*10])**2 for k in range(2,11)))/abs(a[10])
 ck(name+' deck receipt',sha(M/f'results/supply-{name}.cir')==r['deck_sha256'])
 ck(name+' waveform power',abs(vp*vp/16-r['fundamental_W'])<1e-6)
 ck(name+' waveform distortion',abs(thd-r['signals']['SPEAKER']['THD_2_to_10_percent'])<1e-6)
 ck(name+' settled',r['settled_relative']<.001)
 ck(name+' source ceiling',max(d['B_PRE'])<300)
a=rows['ceiling-audio-high'];b=rows['ceiling-audio-high-fine']
ck('fine power agreement0.1percent',abs(a['fundamental_W']/b['fundamental_W']-1)<.001)
ck('fine THD agreement0.02point',abs(a['signals']['SPEAKER']['THD_2_to_10_percent']-b['signals']['SPEAKER']['THD_2_to_10_percent'])<.02)
ck('fault heat cannot be rated as normal heat',s['short_with_current_limit']['pass_W']>max(r['pass_W'] for r in s['dc']))
ck('no physical or native adoption',s['adopted'] is False and s['hardware_qualified'] is False)
out=dict(passed=all(x['passed'] for x in checks),checks=checks,result_sha256=sha(M/'results/ceiling-screen.json'),scope='Conditional feed-budget and evidence checks, not real semiconductor/fault/thermal acceptance.')
(M/'results/ceiling-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=out['passed'],count=len(checks),failures=[x for x in checks if not x['passed']]),indent=2));assert out['passed']
