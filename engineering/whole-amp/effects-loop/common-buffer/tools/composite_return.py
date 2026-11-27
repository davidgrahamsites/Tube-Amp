"""CB-002: standalone composite-stage feasibility; no active circuit mutation."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
import numpy as np
M=Path(__file__).resolve().parents[1];ROOT=M.parents[3];O=M/'results';SPEC=M/'composite-return.json'
sys.path.insert(0,str(M.parent.parent/'tools'));import spice_runtime as sp

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def deck(c,loop=False):
 model=ROOT/c['opamp_model'];kp=2*c['idss_A']/c['vto_V']**2
 text=f'''CB-002 composite recovery feasibility; generic MOS and ideal sink
.include "{model}"
.options method=gear reltol=0.0001 abstol=1n
VHV hv 0 {c['hv_V']}
VP vp 0 {c['rail_V']}
VN vn 0 {-c['rail_V']}
VIN vin 0 DC {c['reference_V']} AC {0 if loop else 1} SIN({c['reference_V']} {c['input_peak_V']} {c['frequency_Hz']})
XERR {'pos' if loop else 'fb'} inv vp vn err OPAx134
RINV vin inv {c['input_ohm']}
RGATE err gate {c['gate_ohm']}
MGAIN drive gate 0 0 LNDgeneric
RDR hv drive {c['drain_ohm']}
MFOLLOW hv drive out out LNDgeneric
IBIAS out 0 {c['sink_A']}
RF out fb {c['feedback_ohm']}
RG fb 0 {c['ground_ohm']}
CF out fb {c['feedback_pF']}p
COUT out load {c['coupling_uF']}u
RLOAD load 0 {c['load_ohm']}
CLOAD load 0 {c['load_pF']}p
.model LNDgeneric NMOS (LEVEL=1 VTO={c['vto_V']} KP={kp} LAMBDA=0)
CGS1 gate 0 9p
CGD1 gate drive 1p
CDS1 drive 0 2.5p
CGS2 drive out 9p
CGD2 drive hv 1p
CDS2 hv out 2.5p
'''
 if c['sink_model']=='servo':
  text=text.replace(f"IBIAS out 0 {c['sink_A']}\n",f"VCSREF csref 0 {c['current_reference_V']}\nXCS csref sense vp vn csdrv OPAx134\nRCSG csdrv csgate 1000\nMSINK out csgate sense sense LNDgeneric\nRSENSE sense 0 {c['sense_ohm']}\nCGS3 csgate sense 9p\nCGD3 csgate out 1p\nCDS3 out sense 2.5p\n")
 if c['seed']:text+='.nodeset v(out)=200 v(drive)=200 v(gate)=0 v(err)=0 v(fb)=2 v(inv)=2\n'
 if c['compensation_pF']:text+=f"CCOMP err inv {c['compensation_pF']}p\n"
 if loop:text+='LBRIDGE fb pos 1e9\nCINJECT test pos 1e9\nVTEST test 0 DC 0 AC 1\n'
 return text+'.end\n'

def at(f,y,hz):return np.interp(np.log(hz),np.log(f),y)
def worker(case):
 spec=json.loads(SPEC.read_text());c={**spec['default'],**case,'opamp_model':spec['opamp_model']};name=case['id'];metrics={'case':case,'parameters':c};files=[]
 for loop in [False,True]:
  path=O/f'composite-{name}{"-loop" if loop else ""}.cir';text=deck(c,loop);path.write_text(text);files.append(path)
  sp.load(text);sp.cmd('op');op={n:float(sp.vector('v('+n+')')[-1]) for n in ['out','drive','gate','fb','err','inv']}
  sp.cmd('ac dec 100 1 100000000');freq=np.real(sp.vector('frequency'));out=np.array(sp.vector('v(load)'))
  if loop:
   transfer=-np.array(sp.vector('v(fb)'))/np.array(sp.vector('v(pos)'));mag=abs(transfer);phase=np.unwrap(np.angle(transfer))*180/np.pi;cross=[]
   for i in np.where(np.diff(mag>1))[0]:
    x=-np.log(mag[i])/(np.log(mag[i+1])-np.log(mag[i]));hz=np.exp(np.log(freq[i])+x*np.log(freq[i+1]/freq[i]));ph=phase[i]+x*(phase[i+1]-phase[i]);cross.append({'frequency_Hz':float(hz),'phase_deg':float(ph),'phase_margin_deg':float(180+ph),'direction':'falling' if mag[i]>mag[i+1] else 'rising'})
   metrics['loop']={'op':op,'crossings':cross,'low_frequency_return_ratio':float(mag[0])}
  else:
   closed_out=out.copy();metrics['op']=op;metrics['ac']={str(hz):{'gain':float(at(freq,abs(out),hz)),'gain_error_dB':float(20*np.log10(at(freq,abs(out),hz)/100)),'phase_deg':float(at(freq,np.unwrap(np.angle(out))*180/np.pi,hz))} for hz in [20,82.4,1000,5000,20000]}
  sp.cmd('destroy all')
 path=O/f'composite-{name}-ac.csv';np.savetxt(path,np.column_stack([freq,closed_out.real,closed_out.imag,transfer.real,transfer.imag]),delimiter=',',header='frequency_Hz,closed_real,closed_imag,return_real,return_imag',comments='',fmt='%.12g');files.append(path)
 metrics['operating_points_valid']=all(abs(q['out']-200)<1 and abs(q['err'])<c['rail_V'] and abs(q['gate'])<20 for q in [metrics['op'],metrics['loop']['op']])
 margins=[x['phase_margin_deg'] for x in metrics['loop']['crossings']];metrics['small_signal_screen_pass']=metrics['operating_points_valid'] and len(margins)==1 and margins[0]>=spec['acceptance_screen']['phase_margin_deg'] and all(abs(q['gain_error_dB'])<=.5 for q in metrics['ac'].values()) and abs(metrics['op']['out']-200)<=1
 if case['transient']:
  sp.load(deck(c));sp.cmd('op');nodes=['out','load','drive','gate','err']+(['sense','csgate'] if c['sink_model']=='servo' else []);sp.cmd('save '+' '.join('v('+n+')' for n in nodes)+' @mgain[id] @mfollow[id]'+(' @msink[id]' if c['sink_model']=='servo' else ''))
  end=c['end_s'];freq=c['frequency_Hz'];step=c['max_step_s'];start=max(0,end-20/freq);sp.cmd(f'tran {step} {end} {start} {step}');t=np.array(sp.vector('time'));assert t[-1]>=end*(1-1e-8)
  y={n:np.array(sp.vector('v('+n+')')) for n in nodes};curr={n:np.array(sp.vector('@'+n+'[id]')) for n in ['mgain','mfollow']+(['msink'] if c['sink_model']=='servo' else [])}
  sample=end-(10-np.arange(4096)/409.6)/freq;z={n:np.interp(sample,t,v) for n,v in y.items()};z.update({n:np.interp(sample,t,v) for n,v in curr.items()})
  signal=z['load'];fft=np.fft.rfft(signal)/len(signal);harm=2*abs(fft[np.arange(1,11)*10]);fit=np.column_stack([np.ones(len(sample)),np.sin(2*np.pi*freq*sample),np.cos(2*np.pi*freq*sample)]);coeff=np.linalg.lstsq(fit,signal,rcond=None)[0];fund=float(harm[0]);thd=float(100*np.linalg.norm(harm[1:])/fund)
  powers={'gain':z['drive']*z['mgain'],'follower':(c['hv_V']-z['out'])*z['mfollow'],'ideal_sink':z['out']*c['sink_A'],'drain_resistor':(c['hv_V']-z['drive'])**2/c['drain_ohm']}
  if c['sink_model']=='servo':powers['servo_sink']=(z['out']-z['sense'])*z['msink'];del powers['ideal_sink']
  metric={'end_s':float(t[-1]),'saved_points':len(t),'fundamental_Vpk':fund,'least_squares_fundamental_Vpk':float(np.hypot(coeff[1],coeff[2])),'THD_percent':thd,'output_min_V':float(signal.min()),'output_max_V':float(signal.max()),'gain_error_dB':float(20*np.log10(fund/(100*c['input_peak_V']))),'max_abs_Vgs_V':float(max(abs(z['gate']).max(),abs(z['drive']-z['out']).max())),'max_Vds_V':float(max(z['drive'].max(),(c['hv_V']-z['out']).max())),'power_W':{n:{'mean':float(a.mean()),'peak':float(a.max())} for n,a in powers.items()}}
  th=spec['thermal'];metric['junction_estimate_C']={n:th['ambient_C_assumed']+th['theta_JA_C_per_W_typical']*metric['power_W'][n]['mean'] for n in ['gain','follower',('servo_sink' if c['sink_model']=='servo' else 'ideal_sink')]}
  if c['sink_model']=='servo':metric['max_abs_Vgs_V']=max(metric['max_abs_Vgs_V'],float(abs(z['csgate']-z['sense']).max()));metric['sink_current_A']={'mean':float(z['msink'].mean()),'min':float(z['msink'].min()),'max':float(z['msink'].max())}
  metric['model_voltage_domain_valid']=metric['max_abs_Vgs_V']<20
  metric['screen_pass']=abs(metric['gain_error_dB'])<=.5 and thd<=1 and metric['max_abs_Vgs_V']<20
  metrics['transient']=metric
  path=O/f'composite-{name}.csv';np.savetxt(path,np.column_stack([sample,*z.values()]),delimiter=',',header='time_s,'+','.join(z),comments='',fmt='%.12g');files.append(path);sp.cmd('destroy all')
 metrics['artifact_hashes']={str(p.relative_to(ROOT)):sha(p) for p in files};(O/f'composite-{name}.json').write_text(json.dumps(metrics,indent=2)+'\n');print(name,metrics['small_signal_screen_pass'],metrics.get('transient',{}).get('screen_pass'),flush=True)

def main():
 sp.cmd('version');version=sp.logs[-8:];c=json.loads(SPEC.read_text());assert sha(ROOT/c['opamp_model'])==c['opamp_model_sha256'];native=list((M.parent.parent/'reverb-600/cad').glob('*.kicad_sch'))+list((M.parent.parent/'pcb-measured-r/boards').glob('*.kicad_pcb'));before={str(p.relative_to(ROOT)):sha(p) for p in native};rows=[]
 for case in c['cases']:
  name=case['id'];start=time.monotonic()
  for suffix in ['.json','.cir','-loop.cir','.csv','-ac.csv','.log']:(O/f'composite-{name}{suffix}').unlink(missing_ok=True)
  try:
   q=subprocess.run([sys.executable,__file__,'--worker',json.dumps(case)],capture_output=True,text=True,timeout=60);(O/f'composite-{name}.log').write_text(q.stdout+q.stderr)
   row=json.loads((O/f'composite-{name}.json').read_text()) if q.returncode==0 else {'case':case,'status':'failed','error':(q.stdout+q.stderr)[-1200:]}
   row.setdefault('status','completed')
  except subprocess.TimeoutExpired as e:
   (O/f'composite-{name}.log').write_bytes((e.stdout or b'')+(e.stderr or b''));row={'case':case,'status':'timeout','wall_limit_s':60}
  row['elapsed_s']=time.monotonic()-start;rows.append(row);print(name,row['status'],flush=True)
  (O/'composite-summary.json').write_text(json.dumps({'cases':rows,'partial':True},indent=2)+'\n')
 checks={'all_attempted':len(rows)==len(c['cases']),'all_completed':all(x['status']=='completed' for x in rows),'native_preserved':all(sha(ROOT/p)==h for p,h in before.items())}
 by={x['case']['id']:x for x in rows};checks['uncompensated_rejected']=not by['uncompensated'].get('small_signal_screen_pass',True)
 checks['nominal_AC_screen']=by['nominal'].get('small_signal_screen_pass',False);checks['nominal_transient_screen']=by['nominal'].get('transient',{}).get('screen_pass',False)
 if all('transient' in by[n] for n in ['nominal','nominal-fine']):
  a=by['nominal']['transient'];b=by['nominal-fine']['transient'];checks['half_step_gain_agreement']=abs(a['fundamental_Vpk']/b['fundamental_Vpk']-1)<.001;checks['half_step_THD_agreement']=abs(a['THD_percent']-b['THD_percent'])<.01
 inputs=[SPEC,Path(__file__),ROOT/c['opamp_model'],M.parent.parent/'tools/spice_runtime.py'];result={'id':'CB-002','date':c['date'],'simulator_version_log':version,'input_hashes':{str(p.relative_to(ROOT)):sha(p) for p in inputs},'native_hashes':before,'checks':checks,'evidence_checks_pass':all(checks.values()),'cases':rows,'partial':False,'device_model_qualified':False,'current_sink_implemented':True,'native_adopted':False,'fabrication_ready':False}
 (O/'composite-summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(checks,indent=2))
if __name__=='__main__':
 if '--worker' in sys.argv:
  try:worker(json.loads(sys.argv[-1]))
  finally:print('\n'.join(sp.logs[-15:]))
 else:main()
