from spice_runtime import *
import os,json,sys
name=sys.argv[1] if len(sys.argv)>1 else 'tube-only'
p=OUT/'candidate-hf';source=(OUT/'reverb-headroom/combined_80ms.cir').read_text().split('CREV_601')[0]
source+='''* Diagnostic: passive reverb input load retained, active reverb excluded.
Csend FX_RETURN rv_acin 100n
Rsend rv_acin rv_dryin 1meg
RSENDLOAD rv_dryin 0 100k
RDRY FX_RETURN MIX_OUT 100k
RWET MIX_OUT 0 1meg
.options method=gear itl1=500 itl4=500
.end
'''
if name=='coupling995':source=source.replace('KOT LPA LPB LS .999','KOT LPA LPB LS .995')
if name=='coupling9995':source=source.replace('KOT LPA LPB LS .999','KOT LPA LPB LS .9995')
(p/(name+'.cir')).write_text(source)
try:
 load(source);cmd('tran 50n 5m 0 50n');t=vector('time');r={'complete':t[-1]>=.004999,'end_s':t[-1],'points':len(t),'scope':'No active reverb or clamps; preserves passive send and approximate HF wet loading. Diagnostic only.'}
 for n in ['MIX_OUT','FX_RETURN','rv_dryin']:r[n+'_peak_V']=max(map(abs,vector('v('+n+')')))
 os.chdir(p);cmd('write '+name+'.raw v(MIX_OUT) v(FX_RETURN) v(rv_dryin)');(p/(name+'.json')).write_text(json.dumps(r,indent=2));print(r)
finally:(p/(name+'.log')).write_text('\n'.join(logs))
