"""DC resistor stress screening of existing generic full-amp fixture, not release."""
from pathlib import Path
import sys,json,re,hashlib
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'whole-amp/tools'))
from simulate_amp import circuit,load,cmd,vector,logs

def resistance(s):
 m=re.fullmatch(r'([0-9.]+)(meg|k|m)?',s,re.I)
 return float(m[1])*{'':1,'meg':1e6,'k':1e3,'m':1e-3}[ (m[2] or '').lower()]
results=[]
try:
 for channel in ['clean','dirty']:
  deck=circuit(channel)
  (HERE/f'{channel}-resistor-op.cir').write_text(deck)
  load(deck);cmd('op');rows=[]
  for line in deck.splitlines():
   w=line.split()
   if len(w)!=4 or not re.fullmatch(r'R\d+',w[0]):continue
   r=resistance(w[3]);v=[0 if n=='0' else vector('v('+n+')')[-1] for n in w[1:3]]
   dv=abs(v[0]-v[1]);rows.append({'reference':w[0],'ohms':r,'voltage_V':dv,'power_W':dv*dv/r})
  results.append({'channel':channel,'deck_sha256':hashlib.sha256(deck.encode()).hexdigest(),'resistors':sorted(rows,key=lambda x:-x['power_W'])});cmd('destroy all')
 (HERE/'resistor-op-results.json').write_text(json.dumps({'scope':'400 V stiff supply, -40 V bias, generic tubes, nominal passives. DC only; no overload, hot ambient, tolerance or transient qualification.','cases':results},indent=2)+'\n')
 for case in results:print(case['channel'],json.dumps(case['resistors'][:12],indent=2))
finally:(HERE/'resistor-op-ngspice.log').write_text('\n'.join(logs)+'\n')
