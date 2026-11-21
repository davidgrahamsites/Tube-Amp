"""Reconcile native PCB nets/metadata with exported native schematic, without rerouting."""
import pcbnew as p,xml.etree.ElementTree as E,json,collections
from pathlib import Path
R=Path(__file__).resolve().parents[1];path=R/'pcb/Renegade_Reverb.kicad_pcb';b=p.LoadBoard(str(path));root=E.parse(R/'validation/board-netlist.xml').getroot()
expected={};part={c.attrib['ref']:c for c in root.findall('./components/comp')}
for n in root.findall('./nets/net'):
 for q in n.findall('node'):
  if not n.attrib['name'].startswith('unconnected-'):expected[(q.attrib['ref'],q.attrib['pin'])]=n.attrib['name']
mapping=collections.defaultdict(set);actual=set()
for f in b.GetFootprints():
 ref=f.GetReference();c=part[ref]
 for pad in f.Pads():
  k=(ref,pad.GetNumber());n=pad.GetNetCode()
  if n:assert k in expected,k;mapping[n].add(expected[k]);actual.add(k)
 assert c.findtext('value')==f.GetValue(),ref
 fp=c.findtext('footprint');lib,name=fp.split(':');f.SetFPID(p.LIB_ID(lib,name))
 f.SetAttributes(f.GetAttributes() & ~p.FP_EXCLUDE_FROM_BOM)
 for fld in c.findall('./fields/field'):
  name=fld.attrib['name'];value=fld.text or ''
  if name in ('Footprint','Datasheet','Description'):continue
  f.SetField(name,value)
 f.SetPath(p.KIID_PATH(c.find('sheetpath').attrib['tstamps'].rstrip('/')+'/'+c.findtext('tstamps').split()[0]))
 if ref=='C614':f.Reference().SetPosition(p.VECTOR2I(p.FromMM(132.5),p.FromMM(67.5)))
assert actual==set(expected),(actual-set(expected),set(expected)-actual)
assert all(len(v)==1 for v in mapping.values()),mapping
assert len({next(iter(v)) for v in mapping.values()})==len(mapping),'Unexpected short/split'
for code,names in mapping.items():b.FindNet(code).SetNetname(next(iter(names)))
# A plated component hole already connects both layers; remove redundant colocated vias.
centers={(pad.GetPosition().x,pad.GetPosition().y,pad.GetNetCode()) for f in b.GetFootprints() for pad in f.Pads() if pad.GetDrillSize().x>0}
removed=[]
for t in list(b.GetTracks()):
 if isinstance(t,p.PCB_VIA) and (t.GetPosition().x,t.GetPosition().y,t.GetNetCode()) in centers:removed.append(str(t.m_Uuid.AsString()));b.Remove(t)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
report={'passed':True,'native_schematic_connected_pads':len(expected),'native_board_connected_pads':len(actual),'one_to_one_net_partition':True,'renamed_nets':{str(k):next(iter(v)) for k,v in mapping.items()},'redundant_vias_removed':removed}
(R/'validation/board-parity.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
