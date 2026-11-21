"""Explicit broadband ideal transformer reference; excludes magnetics/stability qualification."""
from spice_runtime import *
import sys,os
step=sys.argv[1] if len(sys.argv)>1 else '1u';duration=sys.argv[2] if len(sys.argv)>2 else '80m';p=OUT/'ideal-transformer-candidate';p.mkdir(exist_ok=True);source=(OUT/'reverb-headroom/combined_80ms.cir').read_text();lines=[x for x in source.splitlines() if not x.startswith(('LPA ','LPB ','LS ','KOT '))];n=math.sqrt(7600/8)/2
ideal=f'''* Ideal centre-tapped ratio reference; no magnetizing/leakage/capacitance/saturation model.
EPA PA_W B_MAIN SPEAKER 0 {n}
EPB B_MAIN PB_W SPEAKER 0 {n}
FSA 0 SPEAKER EPA {n}
FSB 0 SPEAKER EPB {n}
'''
text='\n'.join(lines).replace('.end',ideal+'.end');name=step+'-'+duration;(p/(name+'.cir')).write_text(text)
try:
 load(text);cmd('tran '+step+' '+duration+' 0 '+step);t=vector('time');end=float(duration[:-1])/1000;result={'step':step,'duration':duration,'complete':t[-1]>=end*.99999,'end_s':t[-1],'points':len(t),'scope':'Ideal ratio/100ohm winding resistors, stiff400V/-40V, generic tubes; not real transformer or HF validation.'}
 for node in ['FX_RETURN','MIX_OUT','rv_dryin','rv_drybuf']:result[node+'_peak_V']=max(map(abs,vector('v('+node+')')))
 if result['complete']:
  ix=[i for i in range(1,len(t)) if t[i]>=end-.005];dt=sum(t[i]-t[i-1] for i in ix)
  def avg(y):return sum(.5*(y[i]+y[i-1])*(t[i]-t[i-1]) for i in ix)/dt
  b=vector('v(B_SCREEN)')
  for side in ['A','B']:
   s=vector('v(EL34_S'+side+')');k=vector('v(K_'+side+')');ig=[(v-w)/4700 for v,w in zip(b,s)];result['screen_'+side+'_W']=avg([(v-w)*i for v,w,i in zip(s,k,ig)]);result['resistor_'+side+'_W']=avg([i*i*4700 for i in ig])
   plate=vector('v(OT_P'+side+')');ip=[.00186*v for v in vector('v(xv'+('5' if side=='A' else '6')+'.cc)')];result['plate_'+side+'_W']=avg([(v-w)*i for v,w,i in zip(plate,k,ip)])
  v=vector('v(SPEAKER)');result['ideal_load_W']=avg([x*x/8 for x in v]);result['mean_Bplus_current_A']=-avg(vector('i(VSUP)'))
 os.chdir(p);cmd('write '+name+'.raw v(FX_RETURN) v(MIX_OUT) v(rv_dryin) v(rv_drybuf) v(SPEAKER)');(p/(name+'.json')).write_text(json.dumps(result,indent=2));print(result)
finally:(p/(name+'.log')).write_text('\n'.join(logs))
