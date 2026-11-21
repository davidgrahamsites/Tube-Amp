"""Explore rated-voltage leakage bound at low cathode bias; not a low-voltage guarantee."""
from pathlib import Path
import sys,itertools,json
p=Path(__file__).resolve().parent;sys.path.insert(0,str(p.parent/'whole-amp/tools'))
from simulate_amp import *
rows=[];out=p/'cathode-cap-screen';out.mkdir(exist_ok=True)
for ch in ['clean','dirty']:
 for l1,l5 in itertools.product([0,215e-6],repeat=2):
  text=circuit(ch);lines={x.split()[0]:x.split() for x in text.splitlines() if x.startswith('C')};extra=[]
  for ref,leak in [('C1',l1),('C5',l5)]:
   _,a,b,_=lines[ref];extra.append(f'BL{ref} {a} {b} I={leak}*tanh(v({a},{b})/.05)')
  text=text.replace('.end','\n'.join(extra)+'\n.end');name=f'{ch}-{l1}-{l5}';(out/(name+'.cir')).write_text(text);load(text);cmd('op');r={'channel':ch,'C1_leak_A':l1,'C5_leak_A':l5}
  for n in ['CL_K1','DR_K1','CL_P1','DR_P1']:r[n]=vector('v('+n+')')[-1]
  cmd('ac lin 1 1000 1000');r['gain_at1kHz']=abs(vector('v(SPEAKER)')[0]);rows.append(r);cmd('destroy all')
(out/'results.json').write_text(json.dumps({'assumption':'Use215uA rated400V/20C/2min maximum as a hypothetical low-bias bound; real low-voltage/hot leakage not specified. Nominal caps and fixed resistors; generic tubes.','cases':rows},indent=2)+'\n');(out/'ngspice.log').write_text('\n'.join(logs))
for ch in ['clean','dirty']:
 a=[r for r in rows if r['channel']==ch];print(ch,'gain spread%',100*(max(r['gain_at1kHz'] for r in a)/min(r['gain_at1kHz'] for r in a)-1))
