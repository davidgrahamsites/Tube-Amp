"""Independent native delta and bounded two-pole button timing checks."""
import copy,hashlib,itertools,json,math,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2];D=M/'results/debounce-input'
sys.path.insert(0,str(M.parent/'tools'));import native_sexpr as v

def netlist(path):
 a=ET.parse(path).getroot()
 return {c.get('ref'):ET.tostring(c).decode() for c in a.findall('components/comp')}, {frozenset((x.get('ref'),x.get('pin')) for x in n.findall('node')) for n in a.findall('nets/net')}
def crossing(initial,final,threshold,r,c,rs,ci):
 # Exact two-capacitor passive ladder. Initial input and main capacitor are
 # both in equilibrium with the same constant input leakage before the step.
 # Slow pole computed without subtractive cancellation.
 b=(1/r+1/rs)/c+1/(rs*ci);det=1/(r*rs*c*ci)
 fast=(-b-math.sqrt(b*b-4*det))/2;slow=det/fast
 aa=-fast/(slow-fast);bb=slow/(slow-fast)
 def value(t):return final+(initial-final)*(aa*math.exp(slow*t)+bb*math.exp(fast*t))
 lo=0.;hi=1.
 for _ in range(70):
  t=(lo+hi)/2
  if (value(t)>threshold)==(initial>final):lo=t
  else:hi=t
 return (lo+hi)/2

def main():
 base=json.loads((D/'baseline.json').read_text());integration=json.loads((D/'integration.json').read_text())
 protected={p:h for p,h in base['sha256'].items() if p not in integration['changed_paths']}
 for p,h in protected.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 for p,h in integration['after_sha256'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 cb,nb=netlist(D/'before.xml');ca,na=netlist(D/'after.xml')
 assert set(ca)-set(cb)=={'R304','R314'} and not set(cb)-set(ca)
 for r in cb:assert cb[r]==ca[r],r
 expected=copy.deepcopy(nb)
 for cap,oldr,newr,pin,net in [('C301','R303','R304','1','DB_CH'),('C311','R313','R314','3','DB_REV')]:
  group=frozenset([(cap,'1'),(oldr,'2'),('U1',pin)]);assert group in expected;expected.remove(group)
  expected.add(frozenset([(cap,'1'),(oldr,'2'),(newr,'1')]))
  expected.add(frozenset([(newr,'2'),('U1',pin)]))
 assert expected==na,'unexpected net partition delta'
 def issues(path,key):
  j=json.loads(path.read_text())
  rows=j.get(key,[])
  if key=='erc':rows=[x for s in j['sheets'] for x in s['violations']]
  return {(x['type'],x['description'],tuple(sorted(i['uuid'] for i in x.get('items',[])))) for x in rows}
 assert issues(D/'before-erc.json','erc')==issues(D/'after-erc.json','erc')
 assert issues(D/'before-drc.json','violations')==issues(D/'after-drc.json','violations')
 b=v.parse((ROOT/'engineering/whole-amp/pcb-measured-r/boards/Renegade_Control.kicad_pcb').read_text());fps=v.fps(b)
 # All prior PCB objects, copper, mounting geometry and holes are retained;
 # only the two declared U1 pad nets differ.
 oldb=v.parse(subprocess.check_output(['git','show',base['commit']+':engineering/whole-amp/pcb-measured-r/boards/Renegade_Control.kicad_pcb'],cwd=ROOT,text=True))
 oldfps=v.fps(oldb)
 expected_u1=copy.deepcopy(oldfps['U1'])
 for pin,net in [('1','DB_CH_INPUT'),('3','DB_REV_INPUT')]:
  pad=next(p for p in v.children(expected_u1,'pad') if p[1]==json.dumps(pin));v.field(pad,'net')[1]=json.dumps(net)
 assert fps['U1']==expected_u1
 for ref,f in oldfps.items():
  if ref!='U1':assert fps[ref]==f,ref
 assert set(fps)-set(oldfps)=={'R304','R314'}
 for kind in ['segment','via','zone','gr_line','gr_arc','gr_rect','gr_circle']:
  assert all(x in v.children(b,kind) for x in v.children(oldb,kind)),kind
 c=json.loads((ROOT/'engineering/whole-amp/reverb-600/circuit.json').read_text())
 for ref,oldnet,newnet,pin in [('R304','DB_CH','DB_CH_INPUT','1'),('R314','DB_REV','DB_REV_INPUT','3')]:
  x=next(x for x in c['components'] if x['reference']==ref);assert x['pins']=={'1':oldnet,'2':newnet} and x['selected_mpn']=='RT0603BRD0710KL'
  u=next(x for x in c['components'] if x['reference']=='U1' and pin in x['pins']);assert u['pins'][pin]==newnet
 routes=[s for s in v.children(b,'segment') if v.field(s,'net')[1] in ['"DB_CH_INPUT"','"DB_REV_INPUT"']]
 assert len(routes)==6
 for s in routes:
  p=list(map(float,v.field(s,'start')[1:]));q=list(map(float,v.field(s,'end')[1:]));dx=abs(p[0]-q[0]);dy=abs(p[1]-q[1]);assert min(dx,dy)<1e-7 or abs(dx-dy)<1e-7
  assert float(v.field(s,'width')[1])>=.3
 for ref,pin,net in [('R304','1','DB_CH'),('R314','3','DB_REV')]:
  f=fps[ref];pads=v.children(f,'pad');assert len(pads)==2 and all(p[2]=='smd' and not v.children(p,'drill') for p in pads)
  assert [v.field(p,'net')[1] for p in pads]==[json.dumps(net),json.dumps(net+'_INPUT')]
  p=next(p for p in v.children(fps['U1'],'pad') if p[1]==json.dumps(pin));assert v.field(p,'net')[1]==json.dumps(net+'_INPUT')
 cases=[]
 # Existing capacitor procurement/native parity is unresolved. ±20% is an
 # engineering screen, not a new guarantee for a selected part.
 for vv,rp,r15,r1,c,rs,ci,leak in itertools.product([4.75,5.25],[9900,10100],[14850,15150],[0,990,1010],[.8e-6,1.2e-6],[9800,10200],[10e-12,50e-12],[-1e-6,1e-6]):
  rh=rp+r15;rl=r15+(rp*r1/(rp+r1));vl=vv*r1/(rp+r1)
  high=vv-leak*(rh+rs);low=vl-leak*(rl+rs)
  assert high>4.2 and low<.9
  for action,th in [('press',.9),('press',2.6),('release',2.),('release',4.2)]:
   falling=action=='press';r=rl if falling else rh
   initial,final=(high,low) if falling else (low,high)
   # With same leakage, remove only the added series resistance for baseline.
   initial0=initial+leak*rs;final0=final+leak*rs
   before=-r*(c+ci)*math.log((th-final0)/(initial0-final0))
   after=crossing(initial,final,th,r,c,rs,ci)
   cases.append(dict(action=action,threshold_V=th,supply_V=vv,rpull_ohm=rp,rdebounce_ohm=r15,rbutton_ohm=r1,C_F=c,Rseries_ohm=rs,Cinput_F=ci,leak_A=leak,initial_V=initial,final_V=final,thevenin_ohm=r,before_s=before,after_s=after,delta_s=after-before))
 max_delta=max(abs(x['delta_s']) for x in cases);assert max_delta<.001
 per=5.25/9800;pair=2*per;power=5.25**2/9800
 # Previously accepted bound covers only the candidate reference/timer paths.
 result={'native_delta_pass':True,'protected_native_files':len(protected),'existing_ERC_violations':1,'existing_DRC_violations':13,'remaining_Control_opens':len(json.loads((D/'after-drc.json').read_text())['unconnected_items']),'timing_cases':len(cases),'maximum_added_timing_change_s':max_delta,'per_input_injection_upper_A':per,'two_input_injection_upper_A':pair,'resistor_power_upper_W':power,'input_DC_shift_upper_V':1e-6*10200,'new_paths_only_phantom_5V_bound_V':.578558,'combined_loose_phantom_5V_bound_V':.578558+pair*930.8,'whole_logic_power_sequence_qualified':False,'all_routing_complete':False,'fabrication_ready':False,'timing_cases_data':cases,'worst_added_timing_case':max(cases,key=lambda x:abs(x['delta_s'])),'assumptions':['5V rail initially <=5.25V; zero internal clamp drop gives upper current','Series resistors ±2% engineering allocation, not lifetime guarantee','Input capacitance 10..50pF incl socket/trace; target must be measured','HC14 leakage ±1uA; threshold envelope 0.9..2.6 fall,2..4.2 rise is a conservative screen of datasheet4.5/6V rows, intermediate supply not guaranteed','Existing 1uF capacitors ±20% engineering screen; selected part/source/schematic parity unresolved','No model of contact bounce, ESD, cable injection, below2V logic or complete rail sequence'],'input_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),D/'before.xml',D/'after.xml',D/'after-erc.json',D/'after-drc.json',D/'integration.json']}}
 assert per<.020 and pair<.050 and power<.01
 (D/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:x for k,x in result.items() if k not in ['timing_cases_data','input_hashes','assumptions','worst_added_timing_case']},indent=2))
if __name__=='__main__':main()
