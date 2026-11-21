"""Match board metadata and pin partitions to native exported schematics."""
from pathlib import Path
import pcbnew as p,xml.etree.ElementTree as E,json,collections
R=Path(__file__).resolve().parents[1];reports={}
for name in ['Main','Power','Control']:
 path=R/'pcb'/name/('Renegade_'+name+'.kicad_pcb');b=p.LoadBoard(str(path));xml=E.parse(R/'validation'/(name+'-netlist.xml')).getroot()
 parts={c.attrib['ref']:c for c in xml.findall('./components/comp')};expected={}
 for n in xml.findall('./nets/net'):
  for q in n.findall('node'):
   if not q.attrib['ref'].startswith('#'):expected[(q.attrib['ref'],q.attrib['pin'])]=n.attrib['name']
 mapping=collections.defaultdict(set);actual=set();nc=[]
 for f in b.GetFootprints():
  ref=f.GetReference();c=parts[ref];fp=c.findtext('footprint');lib,fn=fp.split(':');f.SetFPID(p.LIB_ID(lib,fn));f.SetValue(c.findtext('value'));f.SetAttributes((f.GetAttributes() & ~p.FP_EXCLUDE_FROM_BOM) | (p.FP_THROUGH_HOLE if ref.startswith('J') else 0));f.SetField('Datasheet',c.findtext('datasheet') or '')
  f.SetPath(p.KIID_PATH(c.find('sheetpath').attrib['tstamps'].rstrip('/')+'/'+c.findtext('tstamps').split()[0]))
  for fld in c.findall('./fields/field'):
   if fld.attrib['name'] not in ['Footprint','Description']:f.SetField(fld.attrib['name'],fld.text or '')
  for fld in f.GetFields():
   if fld.GetName()!='Reference':fld.SetVisible(False)
  for pad in f.Pads():
   key=(ref,pad.GetNumber())
   if not pad.GetNumber():continue
   if key in expected:
    actual.add(key)
    if pad.GetNetCode():mapping[pad.GetNetCode()].add(expected[key])
    else:nc.append((pad,expected[key]))
  xy=f.GetPosition()
  if ref.startswith('J'):
   f.Reference().SetPosition(p.VECTOR2I(xy.x,xy.y+p.FromMM(-3.3 if p.ToMM(xy.y)<15 else 3.3)))
   f.Reference().SetTextSize(p.VECTOR2I(p.FromMM(.9),p.FromMM(.9)))
  if ref.startswith('H'):f.Reference().SetPosition(p.VECTOR2I(xy.x,xy.y+p.FromMM(4.2 if p.ToMM(xy.y)<15 else -4.2)))
 assert actual==set(expected),(name,actual-set(expected),set(expected)-actual)
 assert all(len(v)==1 for v in mapping.values()),mapping
 for code,names in mapping.items():b.FindNet(code).SetNetname(next(iter(names)))
 for pad,n in nc:
  net=b.FindNet(n)
  if not net:net=p.NETINFO_ITEM(b,n);b.Add(net)
  pad.SetNet(net)
 p.SaveBoard(str(path),b);reports[name]={'pin_partition_matched':True,'pads':len(actual),'nc_assigned':len(nc)}
(R/'validation/pin-partition.json').write_text(json.dumps(reports,indent=2));print(reports)
