"""Transient witnesses for the passive timing model; no simulated HC14 qualification."""
import json,sys,hashlib
from pathlib import Path
M=Path(__file__).resolve().parents[1];D=M/'results/debounce-input';sys.path.insert(0,str(M.parent/'tools'));import spice_runtime as sp
r=json.loads((D/'checks.json').read_text());cases=r['timing_cases_data'];witness=[]
for action in ['press','release']:
 subset=[x for x in cases if x['action']==action]
 witness.extend([max(subset,key=lambda x:abs(x['delta_s'])),min(subset,key=lambda x:x['after_s'])])
outputs=[]
for index,x in enumerate(witness):
 for step in [2e-6,1e-6]:
  end=max(.01,x['after_s']*1.2);vth=x['final_V']+x['leak_A']*(x['thevenin_ohm']+x['Rseries_ohm'])
  deck=f'''Debounce native series resistor witness {index}
Vsrc source 0 {vth}
Rdeb source cap {x['thevenin_ohm']}
Cdeb cap 0 {x['C_F']} ic={x['initial_V']+x['leak_A']*x['Rseries_ohm']}
Rlim cap input {x['Rseries_ohm']}
Cin input 0 {x['Cinput_F']} ic={x['initial_V']}
Ileak input 0 {x['leak_A']}
.options reltol=1e-7 abstol=1e-12 vntol=1e-9
.tran {step} {end} 0 {step} uic
.end'''
  sp.cmd('destroy all');sp.load(deck);sp.cmd('run');ts=sp.vector('time');vs=sp.vector('v(input)');th=x['threshold_V'];found=None
  for k in range(1,len(ts)):
   if (vs[k-1]-th)*(vs[k]-th)<=0:
    found=ts[k-1]+(ts[k]-ts[k-1])*(th-vs[k-1])/(vs[k]-vs[k-1]);break
  assert found is not None
  err=abs(found-x['after_s']);assert err<2e-7,err
  outputs.append({'witness':index,'action':x['action'],'step_s':step,'analytic_crossing_s':x['after_s'],'spice_crossing_s':found,'error_s':err,'deck_sha256':hashlib.sha256(deck.encode()).hexdigest()})
(D/'spice-witnesses.json').write_text(json.dumps({'passed':True,'whole_logic_power_sequence_qualified':False,'checks_sha256':hashlib.sha256((D/'checks.json').read_bytes()).hexdigest(),'witnesses':outputs,'model':'linear passive ladder plus bounded leakage, no semiconductor power-down behavior'},indent=2)+'\n')
print('Eight ngspice passive witnesses passed; max error',max(x['error_s'] for x in outputs))
