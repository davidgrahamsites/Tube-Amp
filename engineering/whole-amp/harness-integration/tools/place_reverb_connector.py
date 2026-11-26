#!/usr/bin/env python3
"""Create one current connector candidate; never overwrite an active native board."""
import hashlib,json,shutil,sys,tempfile,uuid
from pathlib import Path
import wx
APP=wx.App(False)
import pcbnew as p
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2]
sys.path.insert(0,str(M.parent/'pcb-measured-r/tools'))
from integrate_socket_footprints import spans
import native_sexpr as v
from integrate_drivers import emit,prop

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def uid(label):return str(uuid.uuid5(uuid.NAMESPACE_URL,'renegade/HI-008/'+label))
def main():
 c=json.loads((M/'reverb-connector-placement.json').read_text());h=json.loads((M/'connector-contract.json').read_text())['candidate'];src=ROOT/c['baseline_board']
 assert sha(src)==c['baseline_sha256'],'Board changed; rebase this candidate deliberately'
 out=M/'results/reverb-connector-candidate';out.mkdir(exist_ok=True)
 b=p.LoadBoard(str(src));old=next(f for f in b.GetFootprints() if f.GetReference()==c['reference'])
 assert {q.GetNumber():q.GetNetname() for q in old.Pads()}=={k:n for k,n in c['cavity_nets'].items() if n}
 f=p.FootprintLoad(h['native_library'],h['footprint']);assert f
 f.SetReference(c['reference']);f.SetValue(h['header']);f.SetUuid(old.m_Uuid);f.SetPath(old.GetPath())
 f.SetPosition(p.VECTOR2I(*[p.FromMM(x) for x in c['position_mm']]));f.SetOrientationDegrees(c['angle_deg'])
 f.Reference().SetPosition(p.VECTOR2I(p.FromMM(71.5),p.FromMM(84)));f.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
 f.Value().SetVisible(False)
 for q in f.Pads():
  q.SetUuid(p.KIID(uid('pad/'+q.GetNumber())))
  net=c['cavity_nets'].get(q.GetNumber());q.SetNet(b.FindNet(net) if net else b.FindNet(0))
 for i,g in enumerate(f.GraphicalItems()):g.SetUuid(p.KIID(uid('graphic/'+str(i))))
 b.Remove(old);b.Add(f)
 with tempfile.TemporaryDirectory(prefix='renegade-jr4-') as td:
  saved=Path(td)/src.name;p.SaveBoard(str(saved),b);serialized=saved.read_text()
  replacements=[serialized[a:z] for a,z in spans(serialized,'footprint') if prop(v.parse(serialized[a:z]),'Reference')[2]==json.dumps(c['reference'])]
  assert len(replacements)==1;new_fp=replacements[0]
 original=src.read_text();edits=[];removed=[];widened=[]
 for a,z in spans(original,'footprint'):
  if prop(v.parse(original[a:z]),'Reference')[2]==json.dumps(c['reference']):edits.append((a,z,new_fp))
 for a,z in spans(original,'segment'):
  node=v.parse(original[a:z]);u=v.field(node,'uuid')[1].strip('"')
  if u in c['remove_segments']:removed.append(u);edits.append((a,z,''))
  elif v.field(node,'net')[1].strip('"') in c['existing_net_widths_mm']:
   v.field(node,'width')[1]=str(c['existing_net_widths_mm'][v.field(node,'net')[1].strip('"')]);edits.append((a,z,emit(node)));widened.append(u)
 assert sorted(removed)==sorted(c['remove_segments'])
 for a,z in spans(original,'gr_text'):
  node=v.parse(original[a:z])
  if node[1]=='"PANEL REVERB"':
   node[1]='"REVERB POT"';v.field(node,'at')[1:3]=['53','94'];edits.append((a,z,emit(node)))
  elif node[1]=='"RENEGADE 600R-1 / DRAFT"':
   v.field(node,'at')[1:3]=['32','96'];edits.append((a,z,emit(node)))
 assert len(edits)==11+len(widened),'Expected only declared footprint, track and label edits'
 text=original
 for a,z,new in sorted(edits,reverse=True):text=text[:a]+new+text[z:]
 added=[]
 for i,r in enumerate(c['routes']):
  for j,(a,z) in enumerate(zip(r['points'],r['points'][1:])):
   dx,dy=abs(z[0]-a[0]),abs(z[1]-a[1]);assert dx==0 or dy==0 or abs(dx-dy)<1e-9
   added.append(emit(['segment',['start',*map(str,a)],['end',*map(str,z)],['width',str(r['width_mm'])],['layer',json.dumps(r['layer'])],['net',json.dumps(r['net'])],['uuid',json.dumps(uid(f'route/{i}/{j}'))]]))
 for i,q in enumerate(c['vias']):
  added.append(emit(['via',['at',*map(str,q['at_mm'])],['size',str(q['size_mm'])],['drill',str(q['drill_mm'])],['layers','"F.Cu"','"B.Cu"'],['net',json.dumps(q['net'])],['uuid',json.dumps(uid(f'via/{i}'))]]))
 index=text.rfind(')');text=text[:index]+'\n'+'\n'.join(added)+'\n'+text[index:]
 # Nominal stackup is distinct from the contractual minimum finished thickness.
 nominal=c['construction']['outer_copper_nominal_um']/1000
 core=c['construction']['board_nominal_mm']-2*nominal
 stack=emit(['stackup',['layer','"F.Cu"',['type','"copper"'],['thickness',str(nominal)]],['layer','"dielectric 1"',['type','"core"'],['thickness',str(core)],['material','"FR4"']],['layer','"B.Cu"',['type','"copper"'],['thickness',str(nominal)]]])
 text=text.replace('(setup','(setup\n'+stack,1)
 target=out/src.name;target.write_text(text);p.LoadBoard(str(target))
 for ext in ('.kicad_pro','.kicad_dru'):shutil.copyfile(src.with_suffix(ext),target.with_suffix(ext))
 dru=target.with_suffix('.kicad_dru')
 dru.write_text(dru.read_text()+'\n(rule "HI008 wet signal width" (condition "A.NetName == \'WET_TOP\' || A.NetName == \'WET_W\'") (constraint track_width (min 0.60mm)))\n')
 table=(src.parent/'fp-lib-table').read_text().replace('${KIPRJMOD}/../../../component-selection','${KIPRJMOD}/../../../../component-selection').replace('${KIPRJMOD}/../../libraries','${KIPRJMOD}/../../../libraries')
 (out/'fp-lib-table').write_text(table)
 print(target)
 assert sha(src)==c['baseline_sha256']
if __name__=='__main__':main()
