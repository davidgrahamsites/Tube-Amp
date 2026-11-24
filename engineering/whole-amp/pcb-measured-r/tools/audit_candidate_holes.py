"""Read-only active/candidate hole and pad-net audit. KiCad Python required.
Usage: audit_candidate_holes.py CANDIDATE_DIR NATIVE_XML OUTPUT_PREFIX
Does not certify component lead tolerances or fabrication readiness.
"""
from pathlib import Path
from collections import Counter
import csv, hashlib, json, sys, xml.etree.ElementTree as ET
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]; WHOLE=ROOT.parent
candidate=Path(sys.argv[1]); native=Path(sys.argv[2]); output=Path(sys.argv[3])
sys.path.insert(0,str(WHOLE/'reverb-600/tools'))
from grounding_contract import verified_aliases
aliases=verified_aliases(native)
parts={}
for c in json.loads((WHOLE/'reverb-600/circuit.json').read_text())['components']:
 if not c['reference'].startswith('#'):parts.setdefault(c['reference'],{}).update(c['pins'])
selection={r:c for c in json.loads((WHOLE.parent/'component-selection/coverage.json').read_text()) for r in c['refs']}
xml=ET.parse(native).getroot(); nativepins={}
for net in xml.findall('./nets/net'):
 for node in net.findall('node'):nativepins[(node.attrib['ref'],node.attrib['pin'])]=net.attrib['name']
# Compare endpoint sets; humanized schematic may use auto-generated local names.
contract_groups={}; native_groups={}
for ref,pins in parts.items():
 for pin,net in pins.items():
  if net is not None:
   contract_groups.setdefault(aliases.get(net,net),set()).add((ref,pin))
   if (ref,pin) in nativepins:native_groups.setdefault(nativepins[ref,pin],set()).add((ref,pin))
partition_errors=[{'contract_net':n,'pins':sorted(g),'native_net_names':sorted({nativepins.get(t,'MISSING') for t in g})} for n,g in contract_groups.items() if not any(g==h for h in native_groups.values())]
root_uuid='97ca3088-a174-52f9-956d-0a38bb8e2f56'
paths={c.attrib['ref']:'/'+root_uuid+c.find('sheetpath').attrib['tstamps']+c.findtext('tstamps').split()[0] for c in xml.findall('./components/comp')}
def xy(v):return [round(p.ToMM(v.x),5),round(p.ToMM(v.y),5)]
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
rows=[]; report={'declared_external_bond':'GB1; current native cut-wire proof required','scope':'Every drilled footprint pad and via on all four active and candidate boards. Nominal CAD geometry only; no lead fit, manufacturing tolerance, assembled fit or release claim.','native_xml_sha256':sha(native),'circuit_sha256':sha(WHOLE/'reverb-600/circuit.json'),'boards':{},'fabrication_ready':False,'native_contract_endpoint_partition_errors':partition_errors,'native_contract_expected_nets':len(contract_groups),'native_contract_observed_nets':len(native_groups)}; keep=[]
for variant,directory in [('active',ROOT/'boards'),('candidate',candidate)]:
 for name in ['Main','Power','Control','Reverb']:
  file=directory/f'Renegade_{name}.kicad_pcb'; b=p.LoadBoard(str(file));keep.append(b)
  errors=[];native_errors=[];path_errors=[];courtyard=[];checked=0;drilled=0;vias=0
  for f in b.GetFootprints():
   ref=f.GetReference();sel=selection.get(ref,{});expected=parts.get(ref)
   if not any(g.GetLayer() in [p.F_CrtYd,p.B_CrtYd] for g in f.GraphicalItems()):courtyard.append({'reference':ref,'footprint':f.GetFPID().GetUniStringLibId(),'value':f.GetValue(),'selected_mpn':sel.get('selected_mpn')})
   if expected is not None:
    pads={q.GetNumber():q for q in f.Pads() if q.GetNumber()}
    if set(pads)!=set(expected):errors.append({'ref':ref,'pad_set_mismatch':True})
    if f.GetPath().AsString()!=paths.get(ref):path_errors.append({'ref':ref,'actual':f.GetPath().AsString(),'expected':paths.get(ref)})
    for num,q in pads.items():
     checked+=1;actual=q.GetNetname();want=expected.get(num)
     if not(want==actual or want is None and (not actual or actual.startswith('unconnected-'))):errors.append({'ref':ref,'pad':num,'expected':want,'actual':actual})
     actualnative=nativepins.get((ref,num))
     if not(actualnative==actual or want is None and (not actual or actual.startswith('unconnected-'))):native_errors.append({'ref':ref,'pad':num,'native':actualnative,'actual':actual})
   for q in f.Pads():
    drill=xy(q.GetDrillSize())
    if max(drill)<=0:continue
    drilled+=1;size=xy(q.GetSize());offset=xy(q.GetOffset());plated=q.GetAttribute()!=p.PAD_ATTRIB_NPTH
    # Simple axis edge margin for centred circular/oval/rectangle pads only.
    margin=[round((size[i]-drill[i])/2-abs(offset[i]),5) for i in [0,1]] if plated and q.GetShape() in [p.PAD_SHAPE_CIRCLE,p.PAD_SHAPE_OVAL,p.PAD_SHAPE_RECT] else None
    mpn=next((fld.GetText() for fld in f.GetFields() if fld.GetName()=='Selected_MPN'),sel.get('selected_mpn',''))
    gap='Exact lead maximum dimensions, finished-hole tolerance and insertion allowance not qualified by this inventory'
    if ref.startswith('J') and expected is None:gap='Generic wire port; actual connector/terminal, wire gauge, strain relief and courtyard unselected'
    if not plated:gap='Fastener, washer, tool approach and finished-hole tolerance require mechanical qualification'
    rows.append(dict(variant=variant,board=name,reference=ref,pad=q.GetNumber(),net=q.GetNetname(),footprint=f.GetFPID().GetUniStringLibId(),selected_mpn=mpn,plated=plated,drill_shape='oval_slot' if q.GetDrillShape()==p.PAD_DRILL_SHAPE_OBLONG else 'round',drill_x_mm=drill[0],drill_y_mm=drill[1],pad_shape=int(q.GetShape()),pad_x_mm=size[0],pad_y_mm=size[1],offset_mm=offset,pad_orientation_deg=q.GetOrientationDegrees(),minimum_nominal_axis_edge_margin_mm=min(margin) if margin else '',position_mm=xy(q.GetPosition()),source='Embedded native footprint; coverage register for MPN',evidence_gap=gap))
  for t in b.GetTracks():
   if isinstance(t,p.PCB_VIA):
    vias+=1;d=p.ToMM(t.GetDrillValue());s=p.ToMM(t.GetWidth(p.F_Cu))
    rows.append(dict(variant=variant,board=name,reference='VIA',pad=str(vias),net=t.GetNetname(),footprint='',selected_mpn='',plated=True,drill_shape='round',drill_x_mm=d,drill_y_mm=d,pad_shape='circle',pad_x_mm=s,pad_y_mm=s,offset_mm=[0,0],pad_orientation_deg=0,minimum_nominal_axis_edge_margin_mm=(s-d)/2,position_mm=xy(t.GetPosition()),source='Native via',evidence_gap='Fabricator drill/plating/annulus tolerances and current qualification pending'))
  report['boards'][variant+'_'+name]={'sha256':sha(file),'pads_checked':checked,'contract_errors':errors,'native_net_label_differences':native_errors,'native_path_errors':path_errors,'drilled_footprint_pads':drilled,'via_count':vias,'missing_courtyards':courtyard}
report['inventory_rows']=len(rows);report['drill_shapes']=dict(Counter(r['drill_shape'] for r in rows))
output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
with output.with_suffix('.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
print(json.dumps({k:{'contract':len(v['contract_errors']),'native_labels_different':len(v['native_net_label_differences']),'native_paths':len(v['native_path_errors']),'drills':v['drilled_footprint_pads'],'vias':v['via_count']} for k,v in report['boards'].items()},indent=2))
