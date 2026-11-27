"""Independent saved-data and necessary-current audit for CB-002."""
from pathlib import Path
import hashlib,json,math
import numpy as np
M=Path(__file__).resolve().parents[1];ROOT=M.parents[3];O=M/'results'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def audit(data):
 checks={};by={r['case']['id']:r for r in data['cases']}
 for kind in ['input_hashes','native_hashes']:
  checks[kind]=all(sha(ROOT/p)==h for p,h in data[kind].items())
 checks['complete_set']=not data['partial'] and len(by)==18 and all(r['status']=='completed' for r in by.values())
 for name,r in by.items():
  checks[name+'_artifacts']=all(sha(ROOT/p)==h for p,h in r['artifact_hashes'].items())
  a=np.genfromtxt(O/f'composite-{name}-ac.csv',delimiter=',',names=True);h=a['closed_real']+1j*a['closed_imag'];t=a['return_real']+1j*a['return_imag'];f=a['frequency_Hz'];phase=np.unwrap(np.angle(t))*180/np.pi
  ix=np.flatnonzero((abs(t[:-1])-1)*(abs(t[1:])-1)<0);cross=[]
  for i in ix:
   k=(0-math.log(abs(t[i])))/(math.log(abs(t[i+1]))-math.log(abs(t[i])));cross.append(180+phase[i]+k*(phase[i+1]-phase[i]))
  checks[name+'_loop_crossings']=len(cross)==len(r['loop']['crossings']) and all(abs(v-q['phase_margin_deg'])<1e-6 for v,q in zip(cross,r['loop']['crossings']))
  opvalid=all(abs(q['out']-200)<1 and abs(q['err'])<r['parameters']['rail_V'] and abs(q['gate'])<20 for q in [r['op'],r['loop']['op']])
  checks[name+'_invalid_OP_rejected']=r['operating_points_valid']==opvalid and (opvalid or not r['small_signal_screen_pass'])
  if 'transient' not in r:continue
  z=np.genfromtxt(O/f'composite-{name}.csv',delimiter=',',names=True);freq=r['parameters']['frequency_Hz'];cols=[np.ones(len(z))]
  for k in range(1,11):cols.extend([np.sin(2*np.pi*k*freq*z['time_s']),np.cos(2*np.pi*k*freq*z['time_s'])])
  coeff=np.linalg.lstsq(np.column_stack(cols),z['load'],rcond=None)[0];amps=np.hypot(coeff[1::2],coeff[2::2]);thd=100*np.linalg.norm(amps[1:])/amps[0];m=r['transient']
  checks[name+'_independent_harmonics']=abs(amps[0]-m['fundamental_Vpk'])<1e-6 and abs(thd-m['THD_percent'])<1e-5
  checks[name+'_invalid_voltage_rejected']=m['model_voltage_domain_valid']==(m['max_abs_Vgs_V']<20) and (m['model_voltage_domain_valid'] or not m['screen_pass'])
 checks['uncompensated_negative_margin']=by['uncompensated']['loop']['crossings'][0]['phase_margin_deg']<0 and not by['uncompensated']['small_signal_screen_pass']
 checks['servo_not_ideal']=all('MSINK out csgate sense sense LNDgeneric' in (O/f'composite-{n}.cir').read_text() and 'IBIAS out 0' not in (O/f'composite-{n}.cir').read_text() for n in ['servo-sink-1k','servo-sink-20k'])
 checks['20k_distortion_hold']=by['servo-sink-20k']['transient']['THD_percent']>1 and not by['servo-sink-20k']['transient']['screen_pass']
 return checks

def main():
 path=O/'composite-summary.json';d=json.loads(path.read_text());checks=audit(d);controls={}
 for name,change in [('accept_invalid_OP',lambda x:next(r for r in x['cases'] if r['case']['id']=='low-threshold').update(small_signal_screen_pass=True)),('erase_failed_20k',lambda x:next(r for r in x['cases'] if r['case']['id']=='servo-sink-20k')['transient'].update(screen_pass=True)),('claim_500p_model_valid',lambda x:next(r for r in x['cases'] if r['case']['id']=='20k-cap500')['transient'].update(model_voltage_domain_valid=True))]:
  trial=json.loads(json.dumps(d));change(trial);controls[name]=not all(audit(trial).values())
 A=135;R=340000;f=20000;Iq=.002;current={str(c):A*math.hypot(1/R,2*math.pi*f*c*1e-12) for c in [100,500]};cmax=math.sqrt((Iq/A)**2-(1/R)**2)/(2*math.pi*f)
 phase=np.linspace(0,2*np.pi,200001);sample=A/R*np.sin(phase)+A*2*np.pi*f*100e-12*np.cos(phase);checks['independent_current_peak']=abs(max(sample)-current['100'])<1e-11
 result={'id':'CB-002-audit','date':'2026-11-26','input_hashes':{str(path.relative_to(ROOT)):sha(path),str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))},'checks':{k:bool(v) for k,v in checks.items()},'controls':controls,'evidence_checks_pass':all(checks.values()) and all(controls.values()),'necessary_sink_bound':{'peak_V':A,'load_ohm':R,'frequency_Hz':f,'bias_A':Iq,'required_peak_current_A_by_pF':current,'max_total_capacitance_pF':cmax*1e12,'limits':'Sinusoidal necessary no-cutoff condition for ideal constant-current sink; excludes internal displacement currents, tolerance, stability, distortion and thermal margin.'},'engineering_qualified':False,'native_adopted':False}
 (O/'composite-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'checks':len(checks),'controls':controls,'passed':result['evidence_checks_pass'],'failed':[k for k,v in checks.items() if not v]},indent=2));assert result['evidence_checks_pass']
if __name__=='__main__':main()
