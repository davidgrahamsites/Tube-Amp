"""Preliminary calculations/RC simulation; never a selected-component amp pass."""
import ctypes as ct,json,math,hashlib,sys,csv
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'simulation'
CHAR=ct.CFUNCTYPE(ct.c_int,ct.c_char_p,ct.c_int,ct.c_void_p)
EXIT=ct.CFUNCTYPE(ct.c_int,ct.c_int,ct.c_bool,ct.c_bool,ct.c_int,ct.c_void_p)
class Vector(ct.Structure):
 _fields_=[('name',ct.c_char_p),('type',ct.c_int),('flags',ct.c_short),('real',ct.POINTER(ct.c_double)),('complex',ct.c_void_p),('length',ct.c_int)]
logs=[]
@CHAR
def cb(t,i,u):logs.append(t.decode(errors='replace'));return 0
@EXIT
def ex(s,im,q,i,u):logs.append('EXIT '+str(s));return 0
lib=ct.CDLL('/Applications/KiCad/KiCad.app/Contents/Frameworks/libngspice.0.dylib');lib.ngSpice_Init.argtypes=[ct.c_void_p]*7;lib.ngSpice_Init(cb,None,ex,None,None,None,None)
lib.ngSpice_Circ.argtypes=[ct.POINTER(ct.c_char_p)];lib.ngSpice_Command.argtypes=[ct.c_char_p];lib.ngGet_Vec_Info.argtypes=[ct.c_char_p];lib.ngGet_Vec_Info.restype=ct.POINTER(Vector)
def vector(n):
 p=lib.ngGet_Vec_Info(n.encode());assert p and p.contents.real
 return [p.contents.real[i] for i in range(p.contents.length)]
def run(name,netlist,command,vectors):
 (OUT/name).write_text(netlist);lines=[s.encode() for s in netlist.splitlines()]+[None];assert lib.ngSpice_Circ((ct.c_char_p*len(lines))(*lines))==0
 assert lib.ngSpice_Command(command.encode())==0
 data={n:vector(n) for n in vectors}
 with (OUT/(name+'.csv')).open('w') as file:
  w=csv.writer(file);w.writerow(vectors);w.writerows(zip(*(data[n] for n in vectors)))
 lib.ngSpice_Command(b'destroy all');return data
# Bounce: three brief contacts on press, sustained closure; brief release bounce.
events=[(0,0),(.5,0),(.50001,5),(.501,5),(.50101,0),(.502,0),(.50201,5),(.503,5),(.50301,0),(.504,0),(.50401,5),(.57,5),(.57001,0),(.571,0),(.57101,5),(.572,5),(.57201,0),(1,0),(1.00001,5),(1.08,5),(1.08001,0),(1.3,0)]
pwl=' '.join('%g %g'%e for e in events)
netlist='''Debounce v0.2 - RC circuit with bounded ideal Schmitt surrogate
VDD vdd 0 5
VE evt 0 PWL(%s)
RPULL vdd btn 10k
RCABLE btn pedal 1k
SFOOT pedal 0 evt 0 FOOT
.model FOOT SW(Ron=0.1 Roff=1e12 Vt=2.5 Vh=0.1)
RDB btn db 15k
CDB db 0 1u IC=5
RLOGIC vdd clk 1k
SINV clk 0 db 0 HYST
.model HYST SW(Ron=1 Roff=1e12 Vt=2.25 Vh=0.75)
.end
'''%pwl
wave=run('debounce-reference.cir',netlist,'tran 0.1m 1.3 uic',['time','v(db)','v(clk)'])
edges=[]
for i in range(1,len(wave['time'])):
 if wave['time'][i]>.4 and wave['v(clk)'][i-1]<2.5<=wave['v(clk)'][i]:edges.append(wave['time'][i])
assert len(edges)==2,edges
# Negative bias network, exact draft resistances/capacitances; ideal AC and reference diode.
bias=[]
for mains in [198,220,235.4,242]:
 for pot in [1,25000,50000]:
  peak=50*mains/220*math.sqrt(2)
  nl='''Bias v0.2 - ideal transformer tap / reference diode, no winding regulation
VAC ac 0 SIN(0 %g 50)
R40 ac diode_ac 1k
D7 raw diode_ac DREF
.model DREF D(Is=5n Rs=0.05 N=1.8 Bv=1000 Ibv=5u)
C28 0 raw 10u
R39 raw filt 4.7k
C27 0 filt 10u
R38 filt bias 22k
RPOT bias stop %g
R503 stop 0 33k
R33 ga bias 100k
R34 gb bias 100k
RTESTA ga 0 1e12
RTESTB gb 0 1e12
.end
'''%(peak,pot)
  name='bias-%gV-%gohm.cir'%(mains,pot);w=run(name,nl,'tran 0.5m 8',['time','v(bias)','v(filt)']);last=[v for t,v in zip(w['time'],w['v(bias)']) if t>7.8]
  bias.append({'mains_v':mains,'pot_ohm':pot,'bias_mean_v':sum(last)/len(last),'bias_ripple_vpp':max(last)-min(last)})
# Worst-case simple budgets; bounded conditions are assumptions, not measurements.
calculations={'heater_a':6*.3+2*1.5,'pilot_allowance_a':.15,'heater_total_allowance_a':4.95,'reference_heater_capacity_a':6,'reference_hv_ac_capacity_a':.230,'coil_h1_all_on_a':3*.0125,'nominal_control_budget_a':.10,'reverb_transformer_turns_ratio':math.sqrt(22800/8),'reservoir_effective_u':220/2,'reservoir_series_rating_v':350*2,'nominal_unloaded_rectified_v':300*math.sqrt(2),'high_stress_unloaded_v_assuming_12pct_regulation':300*(242/220)*1.12*math.sqrt(2),'h_ref_at_screen_400v':400*39/(220+39),'max_r504_w_at_screen_530v_clamp_240v':(530-240)**2/15000}
report={'revision':'0.2-DRAFT','purpose':'Preliminary bias/RC exploration and arithmetic only; not full amplifier or selected-component validation','python':sys.executable,'engine':[s for s in logs if 'ngspice-' in s],'debounce':{'rising_edges_after_400ms_reset':edges,'expected_edges':2,'final_toggle_state':0,'schmitt_thresholds_v':[1.5,3.0],'limitations':'Ideal hysteretic switch, not TI macromodel; thresholds/tolerances/ESD/held switches/brownouts/jack insertion/relay/audio transients not qualified'},'bias':bias,'calculations':calculations,'limitations':['Ideal transformer secondary; actual regulation/DCR/core and actual 1N4007 model not qualified','Bias extrema must match the eventual tube operating point; no hardware acceptance inferred','No nonlinear tube, output transformer, spring tank acoustic, integrated load or startup/shutdown validation','Complete baseline and selected-component S01-S06 analyses still pending'],'input_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.cir')}}
lib.ngSpice_Command(b'version');report['engine']=[s for s in logs if 'ngspice-' in s]
(OUT/'explorations.json').write_text(json.dumps(report,indent=2)+'\n');(OUT/'ngspice.log').write_text('\n'.join(logs)+'\n')
print(json.dumps(report,indent=2))
