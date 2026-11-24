"""Independent pin, geometry, preservation and native-report checks for this change."""
import copy,hashlib,json,math,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2];OUT=M/'results'
sys.path.insert(0,str(M.parent/'tools'));import native_sexpr as v
BASE=json.loads((M/'contract.json').read_text())['baseline_commit']
CIR='engineering/whole-amp/reverb-600/circuit.json';SCH='engineering/whole-amp/reverb-600/cad/09b_latches_drivers.kicad_sch';PCB='engineering/whole-amp/pcb-measured-r/boards/Renegade_Control.kicad_pcb'
def old(p):return subprocess.check_output(['/usr/bin/git','show',BASE+':'+p],cwd=ROOT).decode()
def ref(x):return next(p[2].strip('"') for p in v.children(x,'property') if p[1]=='"Reference"')
def check_pads(fps):
 for q,gate,net in [('Q1','CH_GATE','COIL_CH'),('Q2','REV_GATE','COIL_REV')]:
  pads={p[1].strip('"'):p for p in v.children(fps[q],'pad')}
  assert set(pads)=={'1','2','3'}
  for n,name,pos in [('1',gate,(-.95,1.2)),('2','GND',(.95,1.2)),('3',net,(0,-1.2))]:
   p=pads[n];assert v.field(p,'net')[1]=='"'+name+'"',(q,n)
   assert p[2:4]==['smd','rect'] and not v.children(p,'drill')
   assert tuple(map(float,v.field(p,'at')[1:3]))==pos
   assert list(map(float,v.field(p,'size')[1:]))==[.8,.8]
 for d,net in [('D333','COIL_CH'),('D342','COIL_REV')]:
  pads={p[1].strip('"'):p for p in v.children(fps[d],'pad')}
  for n,name in [('1','+12V'),('2',net)]:
   p=pads[n];assert v.field(p,'net')[1]=='"'+name+'"'
   assert p[2]=='thru_hole' and v.field(p,'drill')[1:] == ['1.2']

def main():
 checks={};prior=json.loads(old(CIR));now=json.loads((ROOT/CIR).read_text())
 a={ (x['reference'],x['unit']):x for x in prior['components']};b={(x['reference'],x['unit']):x for x in now['components']}
 assert set(b)-set(a)=={('D333',1),('D342',1)}
 assert all(a[k]==b[k] for k in a if k[0] not in ['Q1','Q2']);checks['unrelated_source_components_unchanged']=True
 expected={'Q1':{'1':'CH_GATE','2':'GND','3':'COIL_CH'},'Q2':{'1':'REV_GATE','2':'GND','3':'COIL_REV'}}
 for q in expected:assert b[(q,1)]['pins']==expected[q] and b[(q,1)]['selected_mpn']=='AO3400A'
 for d,net in [('D333','COIL_CH'),('D342','COIL_REV')]:assert b[(d,1)]['pins']=={'1':'+12V','2':net}
 # Compare exported graph after translating only the intentional G/S numbering swap.
 before=ET.parse(OUT/'before.xml').getroot();after=ET.parse(OUT/'after.xml').getroot()
 def graph(tree,changed=False):
  out={}
  for net in tree.findall('./nets/net'):
   nodes=[]
   for n in net.findall('node'):
    if changed and n.get('ref') in ['D333','D342']:continue
    d=dict(n.attrib)
    if changed and d['ref'] in ['Q1','Q2']:
     d['pin']={'1':'2','2':'1','3':'3'}[d['pin']]
     d['pinfunction']=d['pinfunction'].split('_')[0]+'_'+d['pin']
    nodes.append(tuple(sorted(d.items())))
   out[net.get('name')]=sorted(nodes)
  return out
 assert graph(before)==graph(after,True);checks['native_netlist_only_intended_changes']=True
 ac={x.get('ref'):ET.tostring(x) for x in before.findall('./components/comp')};bc={x.get('ref'):ET.tostring(x) for x in after.findall('./components/comp')}
 assert all(ac[k]==bc[k] for k in ac if k not in ['Q1','Q2']);checks['unrelated_exported_components_unchanged']=True
 aa=v.parse(old(PCB));bb=v.parse((ROOT/PCB).read_text());fa=v.fps(aa);fb=v.fps(bb)
 assert set(fb)-set(fa)=={'D333','D342'};check_pads(fb)
 assert all(fa[k]==fb[k] for k in fa if k not in ['Q1','Q2']);checks['unrelated_native_footprints_unchanged']=True
 original=[x for x in aa[1:] if not isinstance(x,list) or x[0]!='footprint'];current=[x for x in bb[1:] if not isinstance(x,list) or x[0]!='footprint']
 assert current[:len(original)]==original;checks['all_existing_tracks_vias_and_board_settings_unchanged']=True
 new=current[len(original):];assert all(x[0] in ['segment','via'] for x in new)
 for track in [x for x in new if x[0]=='segment']:
  dx,dy=[abs(a-b) for a,b in zip(map(float,v.field(track,'start')[1:]),map(float,v.field(track,'end')[1:]))]
  assert min(dx,dy)<1e-7 or abs(dx-dy)<1e-7
  assert float(v.field(track,'width')[1])>=.3
 # New graph: local drain to clamp anode, gate to series/pulldown, source to pulldown ground.
 for gate,coil,dx in [('CH_GATE','COIL_CH',0),('REV_GATE','COIL_REV',60.68)]:
  tests=[(gate,(113.545+dx,46.305),(89.535+dx,43.875)),('GND',(115.445+dx,46.305),(105.845+dx,43.875)),(coil,(114.495+dx,43.905),(117.035+dx,45.105)),(coil,(114.495+dx,43.905),(117.84,38) if dx==0 else (175.52,40))]
  for net,start,end in tests:
   point=lambda p:tuple(round(a,5) for a in p)
   seen={point(start)};edges=[(point(map(float,v.field(x,'start')[1:])),point(map(float,v.field(x,'end')[1:]))) for x in new if x[0]=='segment' and v.field(x,'net')[1]=='"'+net+'"']
   for _ in edges:
    for a,b in edges:
     if a in seen:seen.add(b)
     if b in seen:seen.add(a)
   assert point(end) in seen,(net,start,end)
 checks['new_pad_routes_and_HV45_min_width_checked']=True
 sa=v.parse(old(SCH));sb=v.parse((ROOT/SCH).read_text())
 for kind in ['wire','junction','global_label','no_connect']:
  assert all(x in v.children(sb,kind) for x in v.children(sa,kind))
 checks['existing_schematic_wires_junctions_labels_preserved']=True
 for kind in ['erc','drc']:
  a=json.loads((OUT/f'before-{kind}.json').read_text());b=json.loads((OUT/f'after-{kind}.json').read_text())
  a.pop('date',None);b.pop('date',None)
  if kind=='erc':assert a==b
  else:
   assert a['violations']==b['violations'];assert len(a['unconnected_items'])==90 and len(b['unconnected_items'])==84
  checks[kind+'_no_new_violations']=True
 rejected=[]
 bad=copy.deepcopy(fb);pads=v.children(bad['Q1'],'pad');v.field(pads[0],'net')[1]='"GND"'
 try:check_pads(bad)
 except AssertionError:rejected.append('wrong_MOSFET_gate_net')
 else:raise AssertionError('Wrong gate net escaped')
 bad=copy.deepcopy(fb);v.field(v.children(bad['D333'],'pad')[0],'drill')[1]='0.8'
 try:check_pads(bad)
 except AssertionError:rejected.append('undersized_diode_hole')
 else:raise AssertionError('Wrong drill escaped')
 report=dict(passed=True,checks=checks,new_tracks=sum(x[0]=='segment' for x in new),new_vias=sum(x[0]=='via' for x in new),negative_controls_rejected=rejected,source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [CIR,SCH,PCB]},native_erc_existing_violations=1,control_existing_drc_violations=13,control_unconnected_items=84,fabrication_ready=False)
 (OUT/'native-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
