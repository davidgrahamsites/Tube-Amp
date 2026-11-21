"""Reproduce original16 bias resistor screens and extended high-source corners.
No canonical design or old evidence outputs are modified.
"""
from pathlib import Path
import sys, json, hashlib, itertools, math, re
ROOT=Path(__file__).resolve().parents[4]
MODULE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'whole-amp/tools'))
from spice_runtime import load,cmd,vector,logs
OUT=MODULE/'runs'; OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mean(t,y,start):
 j=next(i for i,x in enumerate(t) if x>=start)
 return sum(.5*(y[i]+y[i-1])*(t[i]-t[i-1]) for i in range(j+1,len(t)))/(t[-1]-t[j])
def assess(deck,case,res39=4700,res40=1000):
 load(deck);cmd('tran 50u 2 0 50u uic');t=vector('time')
 assert t[-1]>=1.999
 a,d,r,b=[vector('v('+n+')') for n in ['ac','diode_ac','raw','filt']]
 results={}
 for name,x,y,res in [('R40',a,d,res40),('R39',r,b,res39)]:
  volts=[v-w for v,w in zip(x,y)];p=[v*v/res for v in volts]
  results[name]={'steady_mean_W':mean(t,p,1.9),'peak_W':max(p),'peak_differential_V':max(map(abs,volts)), 'first_100ms_J':sum(.5*(p[i]+p[i-1])*(t[i]-t[i-1]) for i in range(1,len(t)) if t[i]<=.1)}
 cmd('destroy all');return dict(case=case,deck=deck,deck_sha256=hashlib.sha256(deck.encode()).hexdigest(),results=results)
def main():
 cmd('version'); rows=[]; sources={}
 for f in sorted((ROOT/'component-selection/bias-cap-screen').glob('*.cir')):
  sources[str(f.relative_to(ROOT))]=sha(f)
  # Original comparison must use the same non-UIC command as prose screen.
  deck=f.read_text();load(deck);cmd('tran 50u 2 0 50u');t=vector('time')
  assert t[-1]>=1.999
  results={}
  for name,n1,n2,res in [('R40','ac','diode_ac',1000),('R39','raw','filt',4700)]:
   v=[a-b for a,b in zip(vector('v('+n1+')'),vector('v('+n2+')'))];p=[x*x/res for x in v]
   results[name]={'steady_mean_W':mean(t,p,1.9),'peak_W':max(p),'peak_differential_V':max(map(abs,v)),'first_100ms_J':sum(.5*(p[i]+p[i-1])*(t[i]-t[i-1]) for i in range(1,len(t)) if t[i]<=.1)}
  cmd('destroy all');rows.append(dict(case={'suite':'original16','source':f.name,'uic':False},deck=deck,deck_sha256=sha(f),results=results))
 template=(ROOT/'component-selection/bias-cap-screen/235.4-1.12-1-6.5e-05.cir').read_text()
 for r39,r40,c28,c27,phase,pot in itertools.product([4465,4935],[950,1050],[8,12],[8,12],[0,90,180,270],[1,55000]):
  deck=template.replace('SIN(0 84.73967665739588 50)',f'SIN(0 84.73967665739588 50 0 0 {phase})').replace('R40 ac diode_ac 1k',f'R40 ac diode_ac {r40}').replace('R39 raw filt 4.7k',f'R39 raw filt {r39}').replace('C28 0 raw 8u',f'C28 0 raw {c28}u IC=0').replace('C27 0 filt 8u',f'C27 0 filt {c27}u IC=0').replace('R38 filt bias 22k','R38 filt bias 20900').replace('R503 stop 0 33k','R503 stop 0 31350').replace('RPOT bias stop 1',f'RPOT bias stop {pot}')
  case=dict(suite='high_source_corners',uic=True,R39_ohm=r39,R40_ohm=r40,C28_uF=c28,C27_uF=c27,phase_deg=phase,pot_ohm=pot,R38_ohm=20900,R503_ohm=31350,each_leakage_A=65e-6)
  rows.append(assess(deck,case,r39,r40))
 metadata={'factory_sha256':sha(Path(__file__)),'runtime_sha256':sha(ROOT/'whole-amp/tools/spice_runtime.py'),'source_hashes':sources,'command_original':'tran 50u 2 0 50u','command_corners':'tran 50u 2 0 50u uic','source_peak_V':84.73967665739588,'case_count':len(rows),'meaning':'scoped ideal-source simulations, not hardware qualification'}
 (OUT/'results.json').write_text(json.dumps(dict(metadata=metadata,cases=rows),indent=2)+'\n')
 (OUT/'ngspice.log').write_text('\n'.join(logs)+'\n')
 for suite in ['original16','high_source_corners']:
  subset=[r for r in rows if r['case']['suite']==suite]
  for ref in ['R39','R40']:
   print(suite,ref,{k:max(r['results'][ref][k] for r in subset) for k in subset[0]['results'][ref]})
 print('cases',len(rows))
if __name__=='__main__':main()
