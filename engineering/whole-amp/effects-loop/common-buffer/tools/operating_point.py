"""CB-003: reproduce invalid OPs and test released initial guesses; no CAD writes."""
from pathlib import Path
import json,re,subprocess,sys,time
import numpy as np
import composite_return as base
M=base.M;ROOT=base.ROOT;O=base.O;sp=base.sp;SPEC=M/'operating-point.json'
def emit(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def voltage(n):return float(sp.vector('v('+n+')')[-1])
def residuals(c,v,i):
 return {'drive':(c['hv_V']-v['drive'])/c['drain_ohm']-i['mgain'],
         'out':i['mfollow']-c['sink_A']-(v['out']-v['fb'])/c['feedback_ohm'],
         'fb':(v['out']-v['fb'])/c['feedback_ohm']-v['fb']/c['ground_ohm']}
def acceptable(c,v,res,limit):
 return all(np.isfinite(x) for x in [*v.values(),*res.values()]) and abs(v['out']-200)<1 and abs(v['err'])<c['rail_V'] and abs(v['gate'])<20 and max(abs(x) for x in res.values())<limit

def worker(case_id,method,loop):
 spec=json.loads(SPEC.read_text());s=json.loads((M/spec['baseline']).read_text());case=next(x for x in s['cases'] if x['id']==case_id);c={**s['default'],**case,'opamp_model':s['opamp_model']};assert c['sink_model']=='ideal'
 name=f'op-{case_id}-{method}-'+('loop' if loop else 'closed');text=base.deck(c,loop)
 if method=='internal-nodeset':
  seed=json.loads((O/'op-seed.json').read_text())['voltages'];text=text.replace('.end','\n'.join(f'.nodeset v({n})={v:.15g}' for n,v in seed.items())+'\n.end')
 deck=O/(name+'.cir');deck.write_text(text);sp.load(text);sp.cmd('save all @mgain[id] @mfollow[id]');sp.cmd('op')
 v={n:voltage(n) for n in ['out','drive','gate','fb','err','inv','vin','hv','vp','vn']};i={n:float(sp.vector('@'+n+'[id]')[-1]) for n in ['mgain','mfollow']};res=residuals(c,v,i);valid=acceptable(c,v,res,spec['dc_current_residual_limit_A']);row={'case':case_id,'method':method,'loop':loop,'parameters':c,'voltages_V':v,'currents_A':i,'residuals_A':res,'op_valid':valid,'artifact_hashes':{str(deck.relative_to(ROOT)):base.sha(deck)}}
 if valid:
  sp.cmd('ac dec 100 1 100000000');f=np.real(sp.vector('frequency'));z=-np.array(sp.vector('v(fb)'))/np.array(sp.vector('v(pos)')) if loop else np.array(sp.vector('v(load)'));path=O/(name+'.csv');np.savetxt(path,np.column_stack([f,z.real,z.imag]),delimiter=',',header='frequency_Hz,real,imag',comments='',fmt='%.12g');row['artifact_hashes'][str(path.relative_to(ROOT))]=base.sha(path)
  if loop:
   mag=abs(z);phase=np.unwrap(np.angle(z))*180/np.pi;cross=[]
   for k in np.where(np.diff(mag>1))[0]:
    x=-np.log(mag[k])/np.log(mag[k+1]/mag[k]);cross.append({'frequency_Hz':float(np.exp(np.log(f[k])+x*np.log(f[k+1]/f[k]))),'phase_margin_deg':float(180+phase[k]+x*(phase[k+1]-phase[k]))})
   row['crossings']=cross
  else:row['gain_error_20k_dB']=float(20*np.log10(base.at(f,abs(z),20000)/100))
 emit(O/(name+'.json'),row);print(case_id,method,loop,valid,flush=True)

def main():
 spec=json.loads(SPEC.read_text());s=json.loads((M/spec['baseline']).read_text());assert base.sha(ROOT/s['opamp_model'])==s['opamp_model_sha256'];native=list((M.parent.parent/'reverb-600/cad').glob('*.kicad_sch'))+list((M.parent.parent/'pcb-measured-r/boards').glob('*.kicad_pcb'));before={str(p.relative_to(ROOT)):base.sha(p) for p in native}
 c={**s['default'],'opamp_model':s['opamp_model']};sp.load(base.deck(c));sp.cmd('op');assert abs(voltage('out')-200)<1 and abs(voltage('err'))<15;sp.logs.clear();sp.cmd('display');names=[re.match(r'stdout (\S+)\s*: voltage',x).group(1) for x in sp.logs if re.match(r'stdout (\S+)\s*: voltage',x)];seed={n:float(sp.vector(n)[-1]) for n in names if n.startswith('xerr.')};assert len(seed)>50;emit(O/'op-seed.json',{'origin':'nominal CB-002 closed operating point','voltages':seed});sp.cmd('destroy all');rows=[]
 for case in spec['cases']:
  for method in spec['methods']:
   for loop in [False,True]:
    name=f'op-{case}-{method}-'+('loop' if loop else 'closed')
    for suffix in ['.json','.csv','.cir','.log']:(O/(name+suffix)).unlink(missing_ok=True)
    start=time.monotonic()
    try:
     p=subprocess.run([sys.executable,__file__,'--worker',case,method,str(int(loop))],capture_output=True,text=True,timeout=spec['worker_limit_s']);(O/(name+'.log')).write_text(p.stdout+p.stderr);row=json.loads((O/(name+'.json')).read_text()) if p.returncode==0 else {'case':case,'method':method,'loop':loop,'status':'failed','error':(p.stdout+p.stderr)[-1000:]};row.setdefault('status','completed')
    except subprocess.TimeoutExpired as e:
     (O/(name+'.log')).write_bytes((e.stdout or b'')+(e.stderr or b''));row={'case':case,'method':method,'loop':loop,'status':'timeout'}
    row['elapsed_s']=time.monotonic()-start;rows.append(row);print(name,row['status'],row.get('op_valid'),flush=True)
 inputs=[SPEC,M/spec['baseline'],Path(__file__),M/'tools/composite_return.py',ROOT/s['opamp_model'],M.parent.parent/'tools/spice_runtime.py'];emit(O/'op-summary.json',{'id':spec['id'],'date':spec['date'],'input_hashes':{str(p.relative_to(ROOT)):base.sha(p) for p in inputs},'seed_sha256':base.sha(O/'op-seed.json'),'native_hashes':before,'native_preserved':all(base.sha(ROOT/p)==h for p,h in before.items()),'cases':rows,'startup_qualified':False,'device_model_qualified':False,'native_adopted':False,'fabrication_ready':False})
if __name__=='__main__':
 if '--worker' in sys.argv:
  try:worker(sys.argv[2],sys.argv[3],bool(int(sys.argv[4])))
  finally:print('\n'.join(sp.logs[-10:]))
 else:main()
