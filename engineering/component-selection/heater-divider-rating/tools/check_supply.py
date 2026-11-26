"""HD-004 independent KCL, voltage-divider, FFT and preservation checks."""
from pathlib import Path
import hashlib,itertools,json,math
import numpy as np
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def audit(c,s):
 checks=[]
 def ck(n,b):checks.append(dict(name=n,passed=bool(b)))
 ck('contract receipt',sha(M/'supply-contract.json')==s['contract_sha256'])
 ck('factory receipt',sha(M/'tools/supply.py')==s['factory_sha256'])
 for path,h in {**c['inputs'],**c['native_sha256']}.items():ck('preserved '+path,sha(ROOT/path)==h)
 source={x['reference']:x for x in json.loads((ROOT/'engineering/whole-amp/reverb-600/circuit.json').read_text())['components']}
 for ref,v in c['source_values'].items():
  actual=source[ref]['value'];scale=1000 if actual.endswith('k') else 1e-6 if actual.endswith('u') else 1
  ck(ref+' source value',math.isclose(float(actual[:-1] if scale!=1 else actual)*scale,v))
 ck('coupled early rail path',source['R17']['pins']=={'1':'B_PRE','2':'B_EARLY'})
 ck('16 DC cases',len(s['dc'])==16)
 p=c['regulator'];rn=2*c['proposed_reference_R_each_ohm']
 for r in s['dc']:
  case=r['case'];name=case['id'];deck=(M/f'results/supply-{name}.cir').read_text()
  ck(name+' deck receipt',sha(M/f'results/supply-{name}.cir')==r['deck_sha256'])
  ck(name+' fixed output screen',deck.count('VSCREEN B_SCREEN 0 380')==1)
  ck(name+' early resistor current',abs(r['early_A']-(r['pre_V']-r['early_V'])/c['source_values']['R17'])<1e-12)
  if case.get('cold'):ck(name+' cold tubes removed','\nXV' not in deck)
  if case['mode']=='passive':
   ck(name+' feed KCL',abs(r['input_A']-(case['input_V']-r['pre_V'])/c['source_values']['R35'])<1e-8)
   if case.get('cold'):ck(name+' cold divider analytical',abs(r['pre_V']-case['input_V']*rn/(rn+c['source_values']['R35']))<.001)
  if case['mode']=='limited':
   ck(name+' headroom KVL',abs(r['pass_V']-(case['input_V']-r['input_A']*p['series_feed_candidate_ohm']-r['pre_V']))<1e-5)
   ck(name+' current limit',0<r['input_A']<p['provisional_current_limit_A'])
   if case.get('cold'):
    # KCL at ADJ: total program input = (Vout + Iadj*Rset)/(Rset+Rlower).
    ip=(r['pre_V']+p['adjust_A'][1]*p['Rset_ohm'])/(p['Rset_ohm']+p['Rlower_ohm'])
    ck(name+' independent cold load KCL',abs(r['input_A']-r['pre_V']/rn-ip)<1e-8)
 for i,r in enumerate(s['budget']['corners']):
  # Solve the ADJ node current balance rather than repeat output equation.
  adj=r['output_V']-r['vref_V'];residual=adj/r['rb_ohm']-r['vref_V']/r['rt_ohm']-r['iadj_A']
  ck(f'program corner {i} nodal balance',abs(residual)<1e-12)
  ck(f'program corner {i} minimum load',r['program_A']>=p['minimum_load_A'])
 ck('16 programming corners',len(s['budget']['corners'])==16)
 ck('allocated DC ceiling only',s['budget']['max_with_allocated_drift_V']<300)
 audio={r['case']['id']:r for r in s['audio']};ck('six completed audio cases',len(audio)==6 and all(r['status']=='completed' for r in audio.values()))
 for name,r in audio.items():
  if r['status']!='completed':continue
  path=M/f'results/supply-{name}.cir';ck(name+' deck receipt',sha(path)==r['deck_sha256'])
  ck(name+' fixed output screens','VSCREEN B_SCREEN 0 380' in path.read_text())
  data=np.genfromtxt(M/f'results/supply-{name}.csv',delimiter=',',names=True)
  y=data['SPEAKER'];spec=np.fft.rfft(y-y.mean());fund=2*abs(spec[10])/len(y);thd=100*np.sqrt(sum(abs(spec[k*10])**2 for k in range(2,11)))/abs(spec[10])
  ck(name+' saved waveform power',abs(fund**2/16-r['fundamental_W'])<1e-6)
  ck(name+' saved waveform THD',abs(thd-r['signals']['SPEAKER']['THD_2_to_10_percent'])<1e-6)
  ck(name+' settled',r['settled_relative']<.001)
  ck(name+' end reached',r['end_s']>=1)
 a=audio['audio-limited-380'];b=audio['audio-limited-380-fine']
 ck('refinement power 0.1 percent',abs(a['fundamental_W']/b['fundamental_W']-1)<.001)
 ck('refinement THD 0.02 point',abs(a['signals']['SPEAKER']['THD_2_to_10_percent']-b['signals']['SPEAKER']['THD_2_to_10_percent'])<.02)
 a=audio['audio-limited-380'];b=audio['audio-limited-550']
 ck('regulated input change power agreement 0.01 percent',abs(a['fundamental_W']/b['fundamental_W']-1)<.0001)
 ta=(M/'results/supply-audio-limited-380.cir').read_text().replace('VSUPPLY SUPPLY_IN 0 380','VSUPPLY SUPPLY_IN 0 INPUT')
 tb=(M/'results/supply-audio-limited-550.cir').read_text().replace('VSUPPLY SUPPLY_IN 0 550','VSUPPLY SUPPLY_IN 0 INPUT')
 ck('paired supplies only input differs',ta==tb)
 dc={r['case']['id']:r for r in s['dc']}
 ck('passive cold 380 ceiling failure retained',dc['passive-380-cold']['pre_V']>300)
 ck('low-input dropout retained',dc['limited-320-warm']['pre_V']<s['budget']['nominal_V']-1)
 ck('no adoption or hardware claim',s['adopted'] is False and s['hardware_qualified'] is False)
 return checks
if __name__=='__main__':
 c=json.loads((M/'supply-contract.json').read_text());s=json.loads((M/'results/supply-screen.json').read_text());checks=audit(c,s)
 result=dict(passed=all(x['passed'] for x in checks),checks=checks,result_sha256=sha(M/'results/supply-screen.json'),scope='Evidence checks only; real limiter, startup/fault response and assembled fit are unqualified.')
 (M/'results/supply-checks.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(dict(passed=result['passed'],count=len(checks),failures=[x for x in checks if not x['passed']]),indent=2));assert result['passed']
