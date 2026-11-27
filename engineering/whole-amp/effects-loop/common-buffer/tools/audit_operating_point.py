"""Independent CB-003 DC equations and stored complex-data audit."""
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
M=Path(__file__).resolve().parents[1];ROOT=M.parents[3];O=M/'results'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def audit_row(r):
 p=r['parameters'];v=r['voltages_V'];i=r['currents_A'];k=p['idss_A']/p['vto_V']**2
 # These valid points put both authored MOS devices in saturation.
 expected_gain=k*max(v['gate']-p['vto_V'],0)**2
 expected_follow=k*max(v['drive']-v['out']-p['vto_V'],0)**2
 errs=[abs((p['hv_V']-v['drive'])/p['drain_ohm']-i['mgain']),abs(i['mfollow']-p['sink_A']-(v['out']-v['fb'])/p['feedback_ohm']),abs((v['out']-v['fb'])/p['feedback_ohm']-v['fb']/p['ground_ohm'])]
 return (all(math.isfinite(x) for x in [*v.values(),*i.values()]) and 199<v['out']<201 and -p['rail_V']<v['err']<p['rail_V'] and abs(v['gate'])<20 and max(errs)<1e-7 and abs(i['mgain']-expected_gain)<1e-7 and abs(i['mfollow']-expected_follow)<1e-7),max(errs)
def main():
 s=json.loads((O/'op-summary.json').read_text());spec=json.loads((M/'operating-point.json').read_text());checks={};rows=s['cases'];checks['coverage']=len(rows)==20 and {(r['case'],r['method'],r['loop']) for r in rows}=={(c,m,l) for c in spec['cases'] for m in spec['methods'] for l in [False,True]};checks['completed']=all(r['status']=='completed' for r in rows)
 checks['input_hashes']=all(sha(ROOT/p)==h for p,h in s['input_hashes'].items());checks['native_hashes']=all(sha(ROOT/p)==h for p,h in s['native_hashes'].items());checks['seed_hash']=sha(O/'op-seed.json')==s['seed_sha256'];checks['no_release_claim']=not any(s[x] for x in ['startup_qualified','device_model_qualified','native_adopted','fabrication_ready']);residual=[]
 for r in rows:
  key=f"{r['case']}:{r['method']}:{r['loop']}";ok,err=audit_row(r);checks[key+':domain']=ok==r['op_valid'];checks[key+':artifacts']=all(sha(ROOT/p)==h for p,h in r['artifact_hashes'].items())
  if not ok:continue
  residual.append(err);csv=next(ROOT/p for p in r['artifact_hashes'] if p.endswith('.csv'));a=np.loadtxt(csv,delimiter=',',skiprows=1);f=a[:,0];z=a[:,1]+1j*a[:,2]
  if r['loop']:
   gain=20*np.log10(abs(z));ph=np.unwrap(np.angle(z))*180/np.pi;idx=np.where(np.diff(gain>0))[0];cross=[]
   for n in idx:
    frac=gain[n]/(gain[n]-gain[n+1]);cross.append((float(10**(np.log10(f[n])+frac*np.log10(f[n+1]/f[n]))),float(180+ph[n]+frac*(ph[n+1]-ph[n]))))
   checks[key+':phase']=len(cross)==len(r['crossings']) and all(abs(x[0]/y['frequency_Hz']-1)<1e-7 and abs(x[1]-y['phase_margin_deg'])<1e-6 for x,y in zip(cross,r['crossings']))
  else:
   val=20*math.log10(np.interp(math.log(20000),np.log(f),abs(z))/100);checks[key+':gain']=abs(val-r['gain_error_20k_dB'])<1e-7
 for c in spec['cases']:
  pair=[r for r in rows if r['case']==c and r['method']=='internal-nodeset'];checks[c+':recovered_pair']=all(r['op_valid'] for r in pair) and max(abs(pair[0]['voltages_V'][n]-pair[1]['voltages_V'][n]) for n in ['out','drive','gate','fb','err','inv'])<spec['paired_voltage_difference_limit_V']
 checks['original_failures_retained']=sum(not r['op_valid'] for r in rows if r['method']=='original')==3
 controls={};r=copy.deepcopy(next(x for x in rows if x['method']=='internal-nodeset'))
 bad=copy.deepcopy(r);bad['voltages_V']['err']=501;controls['outside_supply']=not audit_row(bad)[0]
 bad=copy.deepcopy(r);bad['currents_A']['mfollow']+=.001;controls['current_imbalance']=not audit_row(bad)[0]
 bad=copy.deepcopy(r);bad['parameters']['idss_A']*=2;controls['incorrect_device_current']=not audit_row(bad)[0]
 result={'id':'CB-003-audit','checks':checks,'negative_controls':controls,'passed':all(checks.values()) and all(controls.values()),'valid_point_max_KCL_residual_A':max(residual),'input_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [O/'op-summary.json',M/'operating-point.json',Path(__file__)]},'scope':'Stored DC equations and complex AC data, not physical startup, thermal, full-device or amplifier qualification.'};(O/'op-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'checks':len(checks),'controls':controls,'passed':result['passed'],'max_KCL_residual_A':max(residual),'failures':[k for k,v in checks.items() if not v]},indent=2));assert result['passed']
if __name__=='__main__':main()
