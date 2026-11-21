"""Isolated output-stage diagnostic. Ideal supply/OT and generic EL34 remain unqualified."""
from simulate_amp import *
import sys
rs=float(sys.argv[1]);drive=float(sys.argv[2]) if len(sys.argv)>2 else 40
text=circuit('dirty',.2)
# Keep source output stage only and substitute explicit, complementary grid drive.
keep=['.include','.options','VSUP','R41 ','R42 ','XV5 ','XV6 ','R110 ','R111 ','RPA ','RPB ','LPA ','LPB ','LS ','KOT ','RLOAD ']
lines=[text.splitlines()[0]]+[l for l in text.splitlines() if any(l.startswith(x) for x in keep)]
lines += ['VSCREEN B_SCREEN 0 400',f'VGA EL34_GA 0 SIN(-40 {drive} 1000)',f'VGB EL34_GB 0 SIN(-40 {-drive} 1000)','.options itl1=500 itl4=500','.end']
text='\n'.join(lines).replace('R41 B_SCREEN EL34_SA 1k',f'R41 B_SCREEN EL34_SA {rs}').replace('R42 B_SCREEN EL34_SB 1k',f'R42 B_SCREEN EL34_SB {rs}')
p=OUT/'output-stage';p.mkdir(exist_ok=True);name=f'{rs:g}-{drive:g}';(p/(name+'.cir')).write_text(text)
try:
 load(text);cmd('tran 1u 40m 0 1u');t=vector('time');assert t[-1]>=.039999
 ix=[i for i in range(1,len(t)) if t[i]>=.03];dt=sum(t[i]-t[i-1] for i in ix)
 def avg(y):return sum(.5*(y[i]+y[i-1])*(t[i]-t[i-1]) for i in ix)/dt
 row={'screen_resistance_ohm':rs,'drive_peak_V':drive,'end_s':t[-1],'points':len(t),'output_W':avg([v*v/8 for v in vector('v(SPEAKER)')])}
 for side,num in [('A',5),('B',6)]:
  s=vector(f'v(EL34_S{side})');k=vector(f'v(K_{side})');a=vector(f'v(OT_P{side})');ip=[.00186*v for v in vector(f'v(xv{num}.cc)')];ig=[(400-v)/rs for v in s]
  row['screen_'+side+'_W']=avg([(ss-kk)*ii for ss,kk,ii in zip(s,k,ig)])
  row['resistor_'+side+'_W']=avg([ii*ii*rs for ii in ig])
  row['plate_'+side+'_W']=avg([(aa-kk)*ii for aa,kk,ii in zip(a,k,ip)])
 (p/(name+'.json')).write_text(json.dumps(row,indent=2));print(json.dumps(row))
finally:(p/(name+'.log')).write_text('\n'.join(logs))
