"""Numerical sensitivity runs; no component or physical circuit changes."""
from simulate_amp import *
import sys
variant=sys.argv[1] if len(sys.argv)>1 else 'iterations'
a=float(sys.argv[2]) if len(sys.argv)>2 else .02
base=circuit('dirty',a)
options={'iterations':'.options itl1=500 itl4=500','trap':'.options method=trap itl1=500 itl4=500','tight':'.options reltol=0.0003 abstol=100p vntol=1u itl1=500 itl4=500'}
text=base.replace('.end',options[variant]+'\n.end')
p=OUT/'convergence';p.mkdir(exist_ok=True);name=f'{variant}-{a}';(p/(name+'.cir')).write_text(text)
try:
 load(text);cmd('tran 1u 40m 0 1u');t=vector('time')
 complete=len(t)>100 and t[-1]>=.039999
 row={'variant':variant,'amplitude_V':a,'complete':complete,'end_s':t[-1] if t else None,'points':len(t)}
 if complete:
  ix=[i for i,x in enumerate(t) if x>=.03 and i];dt=sum(t[i]-t[i-1] for i in ix)
  def avg(y):return sum(.5*(y[i]+y[i-1])*(t[i]-t[i-1]) for i in ix)/dt
  out=vector('v(SPEAKER)');fx=vector('v(FX_RETURN)');mix=vector('v(MIX_OUT)');s=vector('v(EL34_SA)');k=vector('v(K_A)');b=vector('v(B_SCREEN)')
  row.update(output_W=avg([v*v/8 for v in out]),screen_A_W=avg([(v-c)*(bb-v)/1000 for v,c,bb in zip(s,k,b)]),fx_peak_V=max(abs(fx[i]) for i in ix),mix_peak_V=max(abs(mix[i]) for i in ix))
 (p/(name+'.json')).write_text(json.dumps(row,indent=2));print(json.dumps(row))
finally:(p/(name+'.log')).write_text('\n'.join(logs))
