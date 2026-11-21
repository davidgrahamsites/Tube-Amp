from spice_runtime import *
import sys,os
p=OUT/'candidate-hf';source=(OUT/'reverb-headroom/combined_80ms.cir').read_text();variant=sys.argv[1];step='50n' if variant=='half-step' else '100n'
if variant=='feedback-zero':source=source.replace('ENFB OT_4 0 SPEAKER 0 -.7071067812','ENFB OT_4 0 SPEAKER 0 0')
(p/(variant+'.cir')).write_text(source)
try:
 load(source);cmd('tran '+step+' 5m 0 '+step);t=vector('time');r={'variant':variant,'max_step':step,'complete':t[-1]>=.004999,'end_s':t[-1],'points':len(t)}
 for n in ['MIX_OUT','FX_RETURN','rv_dryin']:r[n+'_peak_V']=max(map(abs,vector('v('+n+')')))
 os.chdir(p);cmd('write '+variant+'.raw v(MIX_OUT) v(FX_RETURN) v(rv_dryin)')
 (p/(variant+'.json')).write_text(json.dumps(r,indent=2));print(r)
finally:(p/(variant+'.log')).write_text('\n'.join(logs))
