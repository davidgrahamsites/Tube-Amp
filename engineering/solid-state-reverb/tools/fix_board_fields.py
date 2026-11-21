from pathlib import Path
import pcbnew as p,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[1];path=R/'pcb/Renegade_Reverb.kicad_pcb';b=p.LoadBoard(str(path));root=E.parse(R/'validation/board-netlist.xml').getroot();parts={c.attrib['ref']:c for c in root.findall('./components/comp')}
for f in b.GetFootprints():
 c=parts[f.GetReference()]
 for fld in c.findall('./fields/field'):
  name=fld.attrib['name']
  if name not in ('Footprint','Description'):f.SetField(name,fld.text or '')
 for fld in f.GetFields():
  if fld.GetName()!='Reference':fld.SetVisible(False)
for n in root.findall('./nets/net'):
 name=n.attrib['name']
 if name.startswith('unconnected-'):
  ni=p.NETINFO_ITEM(b,name);b.Add(ni)
  for q in n.findall('node'):
   for f in b.GetFootprints():
    if f.GetReference()==q.attrib['ref']:
     for pad in f.Pads():
      if pad.GetNumber()==q.attrib['pin']:pad.SetNet(ni)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
print('Metadata hidden; explicit isolated pad nets assigned')
