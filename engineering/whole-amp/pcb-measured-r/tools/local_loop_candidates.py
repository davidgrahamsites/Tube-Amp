"""Create a fresh, reviewable local-bypass/relay candidate from bf98485 CAD.

Never overwrites active boards. Run with KiCad Python and a NEW output folder.
Rules/project files are copied byte for byte; adoption is a separate operation.
"""
from pathlib import Path
import hashlib, json, shutil, sys
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT.parents[1] / 'component-selection/footprints/Renegade_Selected.pretty'
SYSTEM = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
OUT = Path(sys.argv[1]); OUT.mkdir(exist_ok=False)
EXPECTED = {'Main':'baf16ec240e19c16b2b545a8bc78375e55ba3348d51e2ab014543ad07b714a51',
 'Power':'95d326c677cafc0bb6c6e2896320e32cb2eb4b116ae5e6ea8058efdcc735c810',
 'Control':'57b6fca66783e43059bd2070076fd4ef319179d17e7e38c6e768850e4c7ff15c',
 'Reverb':'d504b26a4a76971c1e9ba0939e9bce23933df0f0b174de679f211cfd2432be03'}
KEEP=[]; boards={}; report={}; io=p.PCB_IO_KICAD_SEXPR()
def vec(x,y): return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def xy(item): return tuple(round(v,6) for v in p.ToMM(item.GetPosition()))
def fp(b,ref): return next(f for f in b.GetFootprints() if f.GetReference()==ref)
def pad(b,ref,num): return next(q for q in fp(b,ref).Pads() if q.GetNumber()==num)
def load(lib,name):
 f=io.FootprintLoad(str(lib),name); KEEP.append(f); return f
def install(b,old,lib,name,library,at,angle,mpn):
 f=load(lib,name); f.SetReference(old.GetReference()); f.SetValue(old.GetValue())
 f.SetPath(old.GetPath()); f.SetPosition(vec(*at)); f.SetOrientationDegrees(angle)
 f.SetFPID(p.LIB_ID(library,name)); f.SetField('Selected_MPN',mpn)
 for q in f.Pads(): q.SetNet(next(o for o in old.Pads() if o.GetNumber()==q.GetNumber()).GetNet())
 f.Value().SetVisible(False)
 for fld in f.GetFields():
  if fld.GetName() not in ['Reference','Value']: fld.SetVisible(False)
 b.Remove(old); b.Add(f); return f
def route(b,net,points,layer=p.F_Cu,width=.3):
 for a,z in zip(points,points[1:]):
  if a==z: continue
  t=p.PCB_TRACK(b);t.SetStart(vec(*a));t.SetEnd(vec(*z));t.SetWidth(p.FromMM(width));t.SetLayer(layer)
  t.SetNet(b.FindNet(net));b.Add(t)
def elbow(a,z):
 dx=z[0]-a[0];dy=z[1]-a[1];d=min(abs(dx),abs(dy))
 return [a,(a[0]+(d if dx>=0 else -d),a[1]+(d if dy>=0 else -d)),z]
for name,h in EXPECTED.items():
 src=ROOT/f'boards/Renegade_{name}.kicad_pcb';assert hashlib.sha256(src.read_bytes()).hexdigest()==h,name
 b=p.LoadBoard(str(src));KEEP.append(b);boards[name]=b
 report[name]={'before_sha256':h}

b=boards['Control']
# These nets have no existing copper following the previous package integration.
assert not any(t.GetNetname() in ['+5V','GND'] for t in b.GetTracks())
for ref,at,angle in [('C351',(85.2,22.825),270),('C352',(16.9,40.5),180),('C353',(29.8,40.5),180)]:
 install(b,fp(b,ref),SYSTEM/'Capacitor_SMD.pretty','C_0805_2012Metric','Capacitor_SMD',at,angle,'CC0805KRX7R9BB104')
# Cap pad1 is supply, pad2 return. Supply and return both reach the local IC.
route(b,'+5V',elbow(xy(pad(b,'C351','1')),xy(pad(b,'U1','14'))))
route(b,'GND',elbow(xy(pad(b,'C351','2')),xy(pad(b,'U1','13'))))
# Supply pin is at one end of the DIP; its ground pin is at the opposite end.
# Use an adjacent supply/return pair under the package, not a long board-wide loop.
route(b,'+5V',elbow(xy(pad(b,'C352','1')),xy(pad(b,'U2','14'))))
g=xy(pad(b,'C352','2'))
route(b,'GND',[g,(17,41.55),(17,56),(13.855,59.145),(13.085,59.145)])
route(b,'+5V',elbow(xy(pad(b,'C353','1')),xy(pad(b,'U3','6'))))
route(b,'GND',[xy(pad(b,'C353','2')),(26.0,40.5),(25.3,41.2),(25.3,43.8),(25.75,44.25),(26.7175,44.25)])
# Finish the U1 local ground return on the underside, avoiding DIP input pads.
route(b,'GND',[(82.3797,24.095),(80.8,25.6747),(80.8,34.5),(78.505,36.795),(74.7597,36.795)],p.B_Cu)
# Drop the old diode branches only; preserve driver-to-harness routing on B.Cu.
for t in list(b.GetTracks()):
 if t.GetLayer()==p.F_Cu and t.GetNetname() in ['COIL_CH','COIL_REV']: b.Remove(t)
for ref in ['D331','D341']: b.Remove(fp(b,ref))

for name,ref,relay,at,angle in [('Main','D331','K1',(80,75.7625),90),('Main','D332','K2',(80,27.7625),90),('Reverb','D341','K3',(112.73,11.5),0)]:
 b=boards[name];f=load(LIB,'Onsemi_1N4007RLG_P10.16')
 f.SetReference(ref);f.SetValue('1N4007 flyback');f.SetFPID(p.LIB_ID('Renegade_Selected','Onsemi_1N4007RLG_P10.16'))
 f.SetPosition(vec(*at));f.SetOrientationDegrees(angle);f.SetField('Selected_MPN','1N4007RLG');f.Value().SetVisible(False)
 for fld in f.GetFields():
  if fld.GetName()!='Reference': fld.SetVisible(False)
 b.Add(f)
 for q in f.Pads(): q.SetNet(pad(b,relay,'1' if q.GetNumber()=='1' else '16').GetNet())
 for num,rnum in [('1','1'),('2','16')]: route(b,pad(b,relay,rnum).GetNetname(),elbow(xy(pad(b,ref,num)),xy(pad(b,relay,rnum))),width=.4)

# Manufacturer drill diameter, keeping all pad centres and contact copper intact.
for name,refs in [('Main',['K1','K2']),('Reverb',['K3'])]:
 for ref in refs:
  f=fp(boards[name],ref);f.SetFPID(p.LIB_ID('Renegade_Selected','Omron_G5V_2_H1_PTH1mm'))
  f.SetField('Selected_MPN','G5V-2-H1 DC12')
  for q in f.Pads(): q.SetDrillSize(vec(1,1));q.SetSize(vec(1.8,1.8))

b=boards['Reverb']
# Replace the remote 330p film placeholder with a C0G part beside recovery U11.
install(b,fp(b,'C605'),SYSTEM/'Capacitor_SMD.pretty','C_1206_3216Metric','Capacitor_SMD',(37.2,62.27),270,'CC1206JRNPO0BN331')
for t in list(b.GetTracks()):
 a=tuple(round(v,4) for v in p.ToMM(t.GetStart()));z=tuple(round(v,4) for v in p.ToMM(t.GetEnd()))
 if t.GetNetname() in ['REC_OUT','REC_FB'] and (a in [(53.,81.),(58.,81.)] or z in [(53.,81.),(58.,81.)]): b.Remove(t)
for t in list(b.GetTracks()):
 if t.GetNetname()=='REC_FB' and (tuple(round(v,4) for v in p.ToMM(t.GetStart()))==(58.2,72.0)): b.Remove(t)
route(b,'REC_OUT',elbow(xy(pad(b,'C605','1')),xy(pad(b,'U11','1'))))
route(b,'REC_FB',elbow(xy(pad(b,'C605','2')),xy(pad(b,'U11','2'))))

# Move reference labels clear of copper and component bodies.
for name,refs in {'Control':{'C351':(85.2,27),'C352':(16.9,38.5),'C353':(29.8,38.5),'U2':(16.9,61.5)},'Main':{'D331':(76.5,70.7),'D332':(76.5,22.7)},'Reverb':{'D341':(117.8,8.8),'C605':(33,62.27)}}.items():
 for ref,at in refs.items():
  f=fp(boards[name],ref);f.Reference().SetPosition(vec(*at));f.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
# Clear the corrected relay annular rings while retaining the existing routes.
b=boards['Main']
for t in b.GetTracks():
 if t.GetNetname()=='+12V' and t.GetLayer()==p.B_Cu:
  for get,setter in [(t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)]:
   a=tuple(round(v,4) for v in p.ToMM(get()))
   changes={(83.7719,65.0336):(83.7719,64.4),(86.2942,67.5559):(87,67.6281),(86.2942,69.0607):(87,69.1),(85.1425,70.2124):(85.1425,70.9575)}
   if a in changes: setter(vec(*changes[a]))
 if t.GetNetname()=='COIL_CH' and t.GetLayer()==p.B_Cu:
  for get,setter in [(t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)]:
   a=tuple(round(v,4) for v in p.ToMM(get()))
   changes={(83.9652,69.3198):(83.5,69.785),(83.9652,128.8223):(83.5,128.3571)}
   if a in changes: setter(vec(*changes[a]))
# Resolve project libraries for temporary review outside the workspace.
table=(ROOT/'boards/fp-lib-table').read_text().replace('${KIPRJMOD}',str((ROOT/'boards').resolve()))
(OUT/'fp-lib-table').write_text(table)
for name,b in boards.items():
 dst=OUT/f'Renegade_{name}.kicad_pcb';p.SaveBoard(str(dst),b)
 for ext in ['kicad_pro','kicad_dru']:shutil.copy2(ROOT/f'boards/Renegade_{name}.{ext}',OUT/f'Renegade_{name}.{ext}')
 report[name]['after_sha256']=hashlib.sha256(dst.read_bytes()).hexdigest()
(OUT/'candidate.json').write_text(json.dumps(report,indent=2)+'\n')
print(OUT)
