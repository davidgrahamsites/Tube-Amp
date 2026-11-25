"""Create one native plane candidate outside active board storage."""
from pathlib import Path
import hashlib,json,math,shutil,sys
import wx
APP=wx.App(False)
import pcbnew as p
M=Path(__file__).resolve().parents[1];ROOT=M.parents[3]
c=json.loads((M/'contract.json').read_text());src=ROOT/c['target']
assert hashlib.sha256(src.read_bytes()).hexdigest()==c['native_sha256'][c['target']], 'baseline changed'
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False);dst=out/src.name
for ext in ['.kicad_pro','.kicad_dru']:shutil.copy2(src.with_suffix(ext),dst.with_suffix(ext))
(out/'fp-lib-table').write_text((src.parent/'fp-lib-table').read_text().replace('${KIPRJMOD}',str(src.parent)))
b=p.LoadBoard(str(src));keep=[b];assert not list(b.Zones());mm=p.FromMM
z=p.ZONE(b);keep.append(z);z.SetLayer(p.B_Cu);z.SetNetCode(b.FindNet('GND').GetNetCode());z.SetZoneName('GND return plane - held voltage-domain candidate')
q=c['zone'];z.SetLocalClearance(mm(q['clearance_mm']));z.SetMinThickness(mm(q['min_thickness_mm']));z.SetPadConnection(p.ZONE_CONNECTION_THERMAL);z.SetThermalReliefGap(mm(q['thermal_gap_mm']));z.SetThermalReliefSpokeWidth(mm(q['thermal_spoke_mm']));z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
poly=z.Outline();poly.NewOutline()
for x,y in q['outline_mm']:poly.Append(mm(x),mm(y))
b.Add(z)
for ref in c['mounts']['refs']:
 f=b.FindFootprintByReference(ref);keep.append(f);pos=f.GetPosition();cx,cy=p.ToMM(pos.x),p.ToMM(pos.y)
 a=p.ZONE(b);keep.append(a);a.SetLayer(p.B_Cu);a.SetIsRuleArea(True);a.SetZoneName(ref+' isolated mounting copper clearance');a.SetDoNotAllowZoneFills(True);a.SetDoNotAllowTracks(False);a.SetDoNotAllowVias(False);a.SetDoNotAllowPads(False);a.SetDoNotAllowFootprints(False)
 polygon=a.Outline();polygon.NewOutline();radius=c['mounts']['minimum_copper_exclusion_radius_mm']/math.cos(math.pi/16)
 for i in range(16):polygon.Append(mm(cx+radius*math.cos(i*math.pi/8)),mm(cy+radius*math.sin(i*math.pi/8)))
 b.Add(a)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(dst),b)
# Saving a full board rounds pre-existing arc coordinates. Transplant only
# API-generated zone nodes into the exact original text; leave all old atoms.
sys.path.insert(0,str(ROOT/'engineering/whole-amp/tools'));import native_sexpr as native
zones=native.children(native.parse(dst.read_text()),'zone')
def emit(x):return '('+' '.join(emit(y) if isinstance(y,list) else y for y in x)+')'
raw=src.read_text();end=raw.rfind(')');dst.write_text(raw[:end]+'\n'+'\n'.join(emit(x) for x in zones)+'\n'+raw[end:])
check=p.LoadBoard(str(dst));keep.append(check);assert len(list(check.Zones()))==5
print(str(dst))
