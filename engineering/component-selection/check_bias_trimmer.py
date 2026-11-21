"""Bias supply endpoint screen with NFA capacitors and Bourns3296W50k tolerance.
Ideal 50VAC tap scaled with mains and assumed 12% regulation; no tube warmup.
"""
from pathlib import Path
import sys,json,math
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'whole-amp/tools'))
from spice_runtime import load,cmd,vector,logs
rows=[];out=HERE/'bias-trimmer-screen';out.mkdir(exist_ok=True)
try:
 for line in [198,235.4]:
  for reg in [1,1.12]:
   for pot in [550,45000,55000]:
    for leakage in [0,65e-6]:
     name=f'{line}-{reg}-{pot}-{leakage}'
     deck=f'''Bias cap 20C five-minute leakage bounding screen
.options method=gear reltol=.001
VAC ac 0 SIN(0 {50*line/220*reg*math.sqrt(2)} 50)
R40 ac diode_ac 1k
D7 raw diode_ac DREF
.model DREF D(Is=5n Rs=.05 N=1.8 Bv=1000 Ibv=5u)
C28 0 raw 8u
R39 raw filt 4.7k
C27 0 filt 8u
* Smooth direction-correct leakage saturates at specification; avoids unphysical startup current source.
BLC28 0 raw I={leakage}*tanh(-v(raw))
BLC27 0 filt I={leakage}*tanh(-v(filt))
R38 filt bias 22k
RPOT bias stop {pot}
R503 stop 0 33k
R33 ga bias 220k
R34 gb bias 220k
RTESTA ga 0 1e12
RTESTB gb 0 1e12
.save all @c28[i] @c27[i]
.end
'''
     (out/(name+'.cir')).write_text(deck);load(deck);cmd('tran 100u 2.0 1.9 100u');t=vector('time');assert t[-1]>=1.999
     b=vector('v(bias)');raw=vector('v(raw)');f=vector('v(filt)');dt=t[-1]-t[0]
     def rms(y): return math.sqrt(sum(.5*(y[i]**2+y[i-1]**2)*(t[i]-t[i-1]) for i in range(1,len(t)))/dt)
     i28=rms(vector('@c28[i]'));i27=rms(vector('@c27[i]'));rows.append({'line_V':line,'secondary_multiplier':reg,'pot_ohms':pot,'each_cap_leakage_A':leakage,'capacitance_each_uF':8,'cap28_ripple_Arms':i28,'cap27_ripple_Arms':i27,'bias_min_V':min(b),'bias_max_V':max(b),'cap28_peak_V':max(abs(x) for x in raw),'cap27_peak_V':max(abs(x) for x in f)});cmd('destroy all')
 (out/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print('cases',len(rows),'cap peak',max(x['cap28_peak_V'] for x in rows),'bias range',min(x['bias_min_V'] for x in rows),max(x['bias_max_V'] for x in rows))
finally:(out/'ngspice.log').write_text('\n'.join(logs))
