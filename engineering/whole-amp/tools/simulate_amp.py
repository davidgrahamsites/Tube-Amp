"""Full signal path from explicit v0.4 pin register; source models retained unmodified.
Educational prototype exploration, not validation of a selected production tube.
"""
from spice_runtime import *
import re,csv
ROOT=R;OLD=R.parent/'solid-state-reverb'
cs=json.loads((OLD/'design-connectivity.json').read_text())['components']
def node(n):return '0' if n=='GND' else n

def circuit(channel='clean',amp=.001,bplus=400,bias=-40):
 lines=['Renegade full signal path v0.4 baseline', '.include "'+str(OUT/'models/dm12ax7s.inc')+'"','.include "'+str(OUT/'models/6ca7s.inc')+'"', '.include "'+str(OLD/'simulation/models/OPAx134.LIB')+'"', '.options method=gear maxord=2 reltol=0.003 abstol=1n vntol=10u gmin=1e-10 rshunt=1e12 cshunt=1e-14',f'VSUP B_MAIN 0 {bplus}',f'VBIAS BIAS_OUT 0 {bias}',f'VIN INPUT 0 DC 0 AC 1 SIN(0 {amp} 1000)', 'VPLUS vp 0 15','VMINUS vn 0 -15']
 for c in cs:
  r=c['reference'];sh=c['sheet'];p=c['pins'];v=c['value'].split()[0]
  if not sh.startswith(('01','02','03','04','05_')):continue
  if r in ['R100','F1','F2','S1','S2','T1','C29','C30','D3','D4','D5','D6','R501','R502']:continue
  if r.startswith('RV'):
   value=re.sub('M$', 'meg',v);total=float(re.match(r'[\d.]+',value)[0])*({'k':1e3,'meg':1e6}.get(re.sub(r'[\d.]','',value),1))
   # Linear electrical fractions; audio-pot rotational law not assumed.
   f=.5
   if r in ['RV3','RV8']:f=.25
   if r=='RV4':f=.5
   lines += [f'{r}A {node(p["1"])} {node(p["2"])} {max(1,total*(1-f))}',f'{r}B {node(p["2"])} {node(p["3"])} {max(1,total*f)}']
  elif r.startswith(('R','C')):
   value=re.sub('M$', 'meg',v)
   lines.append(f'{r} {node(p["1"])} {node(p["2"])} {value}')
  elif r.startswith('V'):
   if sh=='04_output' and r in ['V5','V6']:
    lines.append(f'X{r} {p["3"]} {p["4"]} {p["5"]} {p["8"]} 6CA7')
   else:
    pins=['1','2','3'] if '1' in p else ['6','7','8']
    lines.append(f'X{r}_{pins[0]} '+' '.join(p[x] for x in pins)+' 12AX7A')
  elif r=='L1':lines += ['RL1 B_MAIN CHOKE 75','L1 CHOKE B_SCREEN 8']
 # Ideal contact resistances only, with explicit channel grounding per source.
 for a,b in ([('INPUT_STOP','CL_IN'),('0','DR_G2'),('FX_SEND','CLEAN_OUT')] if channel=='clean' else [('INPUT_STOP','DR_IN'),('0','CL_G2'),('FX_SEND','DIRTY_OUT')]):lines.append(f'RK{len(lines)} {a} {b} .05')
 lines+=['RNORMAL FX_SEND FX_RETURN .05', 'RPA OT_PA PA_W 100','RPB OT_PB PB_W 100','LPA B_MAIN PA_W 10','LPB PB_W B_MAIN 10','LS SPEAKER 0 0.04210526316','KOT LPA LPB LS .999','RLOAD SPEAKER 0 8','ENFB OT_4 0 SPEAKER 0 -.7071067812']
 # Full six-section TI model, existing reverb topology, wet zero.
 src=(OLD/'tools/simulate_reverb.py').read_text().split("base='''")[1].split("'''",1)[0]
 src=src.format(model='',dry=0,wet=0,amp=amp,trimtop=90000,trimbot=10000,wettop=100000,wetbot=1,mute=1)
 raw=src.splitlines();start=next(i for i,x in enumerate(raw) if x.startswith('C601 '));end=next(i for i,x in enumerate(raw) if x.startswith('R24 '))
 for ln in raw[start:end]:
  if ln.startswith('*') or ln.startswith('.'):lines.append(ln.replace('Cjo=4p)', 'Cjo=4p Tt=4n)'));continue
  words=ln.split();typ=words[0][0].upper();words[0]=typ+'REV_'+words[0][1:];n=5 if typ=='X' else 2
  for i in range(1,n+1):
   words[i]={'fx':'FX_RETURN','mix':'MIX_OUT','0':'0','vp':'vp','vn':'vn'}.get(words[i],'rv_'+words[i])
  lines.append(' '.join(words))
 lines+=['.end'];return '\n'.join(lines)+'\n'
if __name__ == "__main__":
 results=[]
 try:
  for channel in ['clean','dirty']:
   text=circuit(channel);(OUT/(channel+'-full.cir')).write_text(text);load(text);cmd('op')
   nodes=['B_MAIN','B_SCREEN','B_PRE','B_EARLY','CL_P1','CL_K1','CL_P2','DR_P1','DR_P2','DR_P3','DR_CF','PI_P1','PI_P2','PI_K','OT_PA','OT_PB','EL34_SA','EL34_SB','K_A','K_B','MIX_OUT']
   op={n:vector('v('+n+')')[-1] for n in nodes};op['plate_dissipation_A_W']=(op['OT_PA']-op['K_A'])*(op['K_A']-(op['B_SCREEN']-op['EL34_SA'])/1000)
   cmd('ac dec 25 10 100000');freq=vector('frequency');vo=vector('v(SPEAKER)');fx=vector('v(FX_RETURN)');mix=vector('v(MIX_OUT)')
   with (OUT/(channel+'-ac.csv')).open('w') as fi:
    wr=csv.writer(fi);wr.writerow(['Hz','speaker_V_per_V','fx_V_per_V','mix_V_per_V']);wr.writerows((f.real,abs(a),abs(b),abs(c)) for f,a,b,c in zip(freq,vo,fx,mix))
   ix=min(range(len(freq)),key=lambda i:abs(freq[i].real-1000))
   results.append({'channel':channel,'op':op,'gain_1kHz':abs(vo[ix]),'fx_gain_1kHz':abs(fx[ix]),'mix_gain_1kHz':abs(mix[ix])});cmd('destroy all')
  (OUT/'full-amp-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
 finally:(OUT/'full-amp-ngspice.log').write_text('\n'.join(logs))
