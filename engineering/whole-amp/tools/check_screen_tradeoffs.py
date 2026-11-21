"""Diagnostic only: screen resistor sensitivity, both tubes, unchanged source architecture.
No production component or schematic substitution is made by this script.
"""
from simulate_amp import *
import sys,os
rs=float(sys.argv[1]); channel=sys.argv[2] if len(sys.argv)>2 else 'dirty'
amp=float(sys.argv[3]) if len(sys.argv)>3 else .2
text=circuit(channel,amp).replace('R41 B_SCREEN EL34_SA 1k',f'R41 B_SCREEN EL34_SA {rs}').replace('R42 B_SCREEN EL34_SB 1k',f'R42 B_SCREEN EL34_SB {rs}').replace('.end','.options itl1=500 itl4=500\n.end')
p=OUT/'screen-tradeoffs';p.mkdir(exist_ok=True);name=f'{channel}-{amp}-{rs:g}'
(p/(name+'.cir')).write_text(text)
try:
 load(text);cmd('tran 1u 80m 0 1u');t=vector('time');os.chdir(p);cmd('write '+name+'.raw v(SPEAKER) v(EL34_SA) v(EL34_SB) v(B_SCREEN) v(K_A) v(K_B) v(OT_PA) v(OT_PB) v(xv5.cc) v(xv6.cc)')
 result={'screen_resistance_ohm':rs,'channel':channel,'input_peak_V':amp,'end_s':t[-1],'complete':t[-1]>=.079999,'points':len(t)}
 if result['complete']:
  for start in [.06,.07]:
   ix=[i for i in range(1,len(t)) if t[i]>=start];duration=sum(t[i]-t[i-1] for i in ix)
   def avg(y):return sum(.5*(y[i]+y[i-1])*(t[i]-t[i-1]) for i in ix)/duration
   row={};b=vector('v(B_SCREEN)');out=vector('v(SPEAKER)')
   row['output_W']=avg([v*v/8 for v in out])
   for side in ['A','B']:
    s=vector(f'v(EL34_S{side})');k=vector(f'v(K_{side})');a=vector(f'v(OT_P{side})')
    ig=[(bb-ss)/rs for bb,ss in zip(b,s)]
    row['screen_'+side+'_W']=avg([(ss-kk)*ii for ss,kk,ii in zip(s,k,ig)])
    row['resistor_'+side+'_W']=avg([ii*ii*rs for ii in ig])
    # 1-ohm cathode sense includes plate, screen, grid and capacitive current.
    # Use the unchanged model equation Ba=1.86e-3*V(cc), excluding capacitive current.
    ip=[.00186*v for v in vector(f'v(xv{5 if side=="A" else 6}.cc)')]
    row['plate_'+side+'_W']=avg([(aa-kk)*ii for aa,kk,ii in zip(a,k,ip)])
    row['screen_'+side+'_peak_mA']=max(ig[i] for i in ix)*1000
   for n in ['FX_RETURN','MIX_OUT','rv_drybuf','rv_suminv','B_SCREEN']:
    v=vector('v('+n+')');row[n+'_peak_V']=max(abs(v[i]) for i in ix)
   result[f'last_{round((.08-start)*1000)}ms']=row
 (p/(name+'.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
finally:(p/(name+'.log')).write_text('\n'.join(logs))
