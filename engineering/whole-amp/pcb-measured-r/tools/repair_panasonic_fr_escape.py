"""One-time repair for C212 changed pitch/rectangular positive pad, all segments H/V/45deg."""
from pathlib import Path
import json,hashlib,sys
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1];path=ROOT/'boards/Renegade_Control.kicad_pcb';out=ROOT/'review/panasonic-fr-route-repair.json'
assert sys.argv[1:]==['--apply'] and not out.exists()
assert hashlib.sha256(path.read_bytes()).hexdigest()=='d6647bc457e3bb9260ffcccf3c90ce962a2b84d682ca015baae4eeff503c9b18'
coords={
 'ead77f28-5022-48a1-a5c0-5e55cd32ffe7':[(97.765,66.325),(97.765,78.5)],
 '8fc36d2f-f641-49b8-aa10-ce7bde61d48d':[(97.765,78.5),(110.5983,91.3333)],
 '8f91a821-e867-44a1-abf4-a18ce97f1c48':[(110.5983,91.3333),(112.3955,91.3333)],
 '082044ca-d3e2-4dd6-b882-6fd035195f68':[(112.3955,91.3333),(114.2038,89.525)],
 '9d7d8a14-f5b8-4c67-b408-5dab80178abf':[(123.9429,85.6961),(118.0327,85.6961)],
 'dc3cc4a8-0886-41d9-b7bb-98d5b12ae878':[(118.0327,85.6961),(114.2038,89.525)]}
b=p.LoadBoard(str(path));seen=set();records=[]
for t in b.GetTracks():
 key=t.m_Uuid.AsString()
 if key not in coords:continue
 assert t.GetNetname()=='NEG_RAW' and abs(p.ToMM(t.GetWidth())-.4)<1e-6
 before=[[p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y)],[p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y)]]
 a,z=coords[key];dx=abs(z[0]-a[0]);dy=abs(z[1]-a[1]);assert min(dx,dy)<1e-9 or abs(dx-dy)<1e-9
 t.SetStart(p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1])));t.SetEnd(p.VECTOR2I(p.FromMM(z[0]),p.FromMM(z[1])))
 seen.add(key);records.append(dict(uuid=key,before_mm=before,after_mm=[a,z],net='NEG_RAW',width_mm=.4))
assert seen==set(coords)
pro=path.with_suffix('.kicad_pro');keep=pro.read_bytes();p.SaveBoard(str(path),b);pro.write_bytes(keep)
out.write_text(json.dumps(dict(changes=records,after_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),scope='Retain six segment identities, layers, net and width; adjust joins to correct clearance and H/V/45deg style',fabrication_ready=False),indent=2)+'\n')
print('Adjusted six C212 NEG_RAW segments; fresh DRC required')
