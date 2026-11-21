"""TI OPAx134 manufacturer model; electrical tank surrogate only.
No model of acoustic decay, vibration, cabinet hum, original tube amp or safety.
"""
from pathlib import Path
import ctypes as ct,json,math,hashlib,csv
R=Path(__file__).resolve().parents[1];OUT=R/'simulation'
CHAR=ct.CFUNCTYPE(ct.c_int,ct.c_char_p,ct.c_int,ct.c_void_p)
EXIT=ct.CFUNCTYPE(ct.c_int,ct.c_int,ct.c_bool,ct.c_bool,ct.c_int,ct.c_void_p)
class Complex(ct.Structure):_fields_=[('real',ct.c_double),('imag',ct.c_double)]
class Vector(ct.Structure):_fields_=[('name',ct.c_char_p),('type',ct.c_int),('flags',ct.c_short),('real',ct.POINTER(ct.c_double)),('complex',ct.POINTER(Complex)),('length',ct.c_int)]
logs=[]
@CHAR
def cb(t,i,u):logs.append(t.decode(errors='replace'));return 0
@EXIT
def ex(s,im,q,i,u):logs.append('EXIT '+str(s));return 0
lib=ct.CDLL('/Applications/KiCad/KiCad.app/Contents/Frameworks/libngspice.0.dylib');lib.ngSpice_Init.argtypes=[ct.c_void_p]*7;lib.ngSpice_Init(cb,None,ex,None,None,None,None)
lib.ngSpice_Circ.argtypes=[ct.POINTER(ct.c_char_p)];lib.ngSpice_Command.argtypes=[ct.c_char_p];lib.ngGet_Vec_Info.argtypes=[ct.c_char_p];lib.ngGet_Vec_Info.restype=ct.POINTER(Vector)
for cm in Path('/Applications/KiCad/KiCad.app/Contents/PlugIns/sim/ngspice').glob('*.cm'):
 lib.ngSpice_Command(('codemodel '+str(cm)).encode())
lib.ngSpice_Command(b'set ngbehavior=ps')
def cmd(s):
 v=lib.ngSpice_Command(s.encode());assert v==0,(s,v,logs[-10:])
def vector(n):
 p=lib.ngGet_Vec_Info(n.encode());assert p,(n,logs[-30:]);v=p.contents
 if bool(v.real):return [v.real[i] for i in range(v.length)]
 return [complex(v.complex[i].real,v.complex[i].imag) for i in range(v.length)]
base='''Reverb 0.4 TI OPAx134 electrical analysis
.include "{model}"
VP vp 0 15
VN vn 0 -15
VIN input 0 DC 0 AC {dry} SIN(0 {amp} 1000)
RSOURCE input fx 100k
C601 fx acin 100n
R601 acin dryin 100k
R602 dryin 0 10meg
D601 dryin vp DC
D602 vn dryin DC
.model DC D(Is=2.52n Rs=.568 N=1.906 Cjo=4p)
X10a dryin drybuf vp vn drybuf OPAx134
C602 drybuf sendtop 22n
RPT sendtop sendw {trimtop}
RPB sendw 0 {trimbot}
X10b sendw drvfb vp vn driver OPAx134
R603 drvfb 0 10k
R604 driver drvfb 10k
R605 driver drivecap 220
C603 drivecap tankin 2.2u
RTANK tankin ti 58
LTANK ti 0 127m
* Independent tank-output electrical injection: NOT an acoustic transfer model.
VTANK tanksrc 0 DC 0 AC {wet}
ROUTT tanksrc to 200
LOUTT to tankout 409m
C604 tankout recin 100n
R606 recin 0 220k
X11a recin recfb vp vn recout OPAx134
R607 recfb 0 1k
R608 recout recfb 100k
C605 recout recfb 330p
C606 recout wettop 1u
RWT wettop wetw {wettop}
RWB wetw 0 {wetbot}
R609 wetw 0 1meg
X11b wetw wetbuf vp vn wetbuf OPAx134
R610 wetbuf wetmute 10k
RMUTE wetmute 0 {mute}
R611 wetmute sum 100k
R612 drybuf sum 100k
X12a 0 sum vp vn suminv OPAx134
R613 suminv sum 100k
R614 suminv outfb 100k
X12b 0 outfb vp vn outbuf OPAx134
R615 outbuf outfb 100k
R616 outbuf outac 100
C607 outac mix 1u
R617 mix 0 1meg
R24 mix 0 10meg
* Representative original PI input load, excludes nonlinear grid-current/clipping.
C19 mix pi 22n
RPI pi 0 1meg
.end
'''
results=[]
try:
 for mode in ['dry','wet']:
  for w in [0,.5,1]:
   for mute in ([False,True] if mode=='dry' else [False]):
    text=base.format(model=str(OUT/'models/OPAx134.LIB'),dry=1 if mode=='dry' else 0,wet=0 if mode=='dry' else .001,amp=1,trimtop=90000,trimbot=10000,wettop=max(1,100000*(1-w)),wetbot=max(1,100000*w),mute=1 if mute else 1e12)
    name=f'{mode}-wet{w}-mute{mute}';(OUT/(name+'.cir')).write_text(text)
    lines=[s.encode() for s in text.splitlines()]+[None];rc=lib.ngSpice_Circ((ct.c_char_p*len(lines))(*lines));assert rc==0,(rc,logs[-30:])
    cmd('ac dec 30 10 100000');freq=vector('frequency');out=vector('v(mix)');drive=vector('v(tankin)')
    rows=[(float(f.real),abs(v),math.degrees(math.atan2(v.imag,v.real)),abs(d)) for f,v,d in zip(freq,out,drive)]
    with (OUT/(name+'.csv')).open('w') as fi:
     wr=csv.writer(fi);wr.writerow(['Hz','mix_magnitude_V','mix_phase_deg','tank_voltage_V']);wr.writerows(rows)
    def near(hz):return min(rows,key=lambda r:abs(r[0]-hz))
    results.append({'mode':mode,'wet_fraction':w,'muted':mute,'at_82Hz':near(82.4),'at_1kHz':near(1000),'at_5kHz':near(5000)})
    cmd('destroy all')
 report={'model':'TI OPAx134 final1.4 2022-07-01 SBOM042F, unmodified','model_sha256':hashlib.sha256((OUT/'models/OPAx134.LIB').read_bytes()).hexdigest(),'pin_order':['IN+','IN-','VCC','VEE','OUT'],'solver':'KiCad bundled ngspice; PSpice compatibility','source_impedance_ohm':100000,'results':results,'limitations':['Tank coil R/L are nominal electrical surrogates, not qualified physical tank models','Wet test injects 1mV independently; no modeled acoustic transfer or decay','Ideal +/-15V rails; no regulator startup/load/thermal validation','No nonlinear tube amplifier/integrated simulation; required before build release']}
 dry=[r['at_1kHz'][1] for r in results if r['mode']=='dry'];report['dry_gain_spread']=max(dry)-min(dry);report['dry_control_independence_pass']=report['dry_gain_spread']<.001
 (OUT/'results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
finally:(OUT/'ngspice.log').write_text('\n'.join(logs))
