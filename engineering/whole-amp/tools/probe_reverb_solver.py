import sys, json, os
from pathlib import Path
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'engineering/whole-amp/tools'))
from spice_runtime import *
mode=sys.argv[1]
p=OUT/'reverb-headroom';text=(p/'dirty-trap.cir').read_text().replace('method=trap','method=gear')
if mode=='cshunt':text=text.replace('cshunt=1e-14','cshunt=1e-12')
if mode=='inputcap':text=text.replace('.end','CFILTER rv_dryin 0 22p\n.end')
if mode=='no_clamp':text='\n'.join(x for x in text.splitlines() if not x.startswith(('DREV_601','DREV_602')))
if mode in ['fine_step','no_shunt','fine_5ms','fine_20ms','combined_80ms']:text=text.replace('cshunt=1e-14','cshunt=0')
if mode=='combined_80ms':text=text.replace('R41 B_SCREEN EL34_SA 1k','R41 B_SCREEN EL34_SA 4700').replace('R42 B_SCREEN EL34_SB 1k','R42 B_SCREEN EL34_SB 4700')
if mode=='isolated':
 pos=text.index('CREV_601');text='Reverb isolated headroom\n'+ '\n'.join(x for x in text.splitlines() if x.startswith(('.include','.options','VPLUS','VMINUS'))) +'\nVTEST FX_RETURN 0 SIN(0 50 1000)\n'+text[pos:]
 text=text.replace('RDRY FX_RETURN MIX_OUT 100k','RDRY FX_RETURN MIX_OUT 100k\nRPI MIX_OUT 0 1meg')
(p/(mode+'.cir')).write_text(text)
f=(p/(mode+'.log')).open('w')
@CHAR
def live(t,i,u):f.write(t.decode(errors='replace')+'\n');f.flush();return 0
lib.ngSpice_Init(live,None,ex,None,None,None,None)
for cm in Path('/Applications/KiCad/KiCad.app/Contents/PlugIns/sim/ngspice').glob('*.cm'):cmd('codemodel '+str(cm))
load(text);cmd('tran 100n 80m 0 100n' if mode=='combined_80ms' else 'tran 100n 1m 0 100n' if mode=='fine_step' else ('tran 100n 20m 0 100n' if mode=='fine_20ms' else ('tran 100n 5m 0 100n' if mode=='fine_5ms' else 'tran 1u 5m 0 1u')));t=vector('time')
r={'mode':mode,'complete':t[-1]>=(.079999 if mode=='combined_80ms' else .019999 if mode=='fine_20ms' else (.0009999 if mode=='fine_step' else .004999)),'end_s':t[-1],'points':len(t)}
for n in ['FX_RETURN','MIX_OUT','rv_dryin','rv_drybuf','rv_driver']:r[n+'_peak_V']=max(map(abs,vector('v('+n+')')))

if mode=='combined_80ms' and r['complete']:
 ix=[i for i in range(1,len(t)) if t[i]>=.07];dt=sum(t[i]-t[i-1] for i in ix)
 def avg(y):return sum(.5*(y[i]+y[i-1])*(t[i]-t[i-1]) for i in ix)/dt
 b=vector('v(B_SCREEN)')
 for side in ['A','B']:
  sc=vector('v(EL34_S'+side+')');k=vector('v(K_'+side+')');ig=[(v-w)/4700 for v,w in zip(b,sc)]
  r['screen_'+side+'_W']=avg([(v-w)*i for v,w,i in zip(sc,k,ig)]);r['resistor_'+side+'_W']=avg([i*i*4700 for i in ig])
 v=vector('v(SPEAKER)');r['ideal_load_W']=avg([x*x/8 for x in v])
 os.chdir(p);cmd('write '+mode+'.raw v(FX_RETURN) v(MIX_OUT) v(rv_dryin) v(rv_drybuf) v(SPEAKER)')
(p/(mode+'.json')).write_text(json.dumps(r,indent=2));print(r)
