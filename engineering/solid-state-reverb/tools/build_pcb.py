"""Low-voltage daughterboard, explicit placements and native pad/net mapping.
Routing is a separate checked operation. No mains/HV copper permitted.
"""
import pcbnew as pcb,json,sys,math
from pathlib import Path
if (Path(__file__).resolve().parents[1]/'NATIVE_EDIT_GUARD').exists():
 raise SystemExit('Preserve native edits: initial generator disabled for completed v0.4 CAD. Copy/reconcile into a new revision instead.')

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'pcb';OUT.mkdir(exist_ok=True)
LIB=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
spec=json.loads((ROOT/'design-connectivity.json').read_text())
cs={}
for c in spec['components']:
 if not c['sheet'].startswith(('07a','07b','07c')):continue
 r=c['reference']
 if r not in cs:cs[r]={**c,'pins':{}}
 cs[r]['pins'].update(c['pins'])
# Coordinates mm, origin top left viewed from component side. Positive y down.
pos={
'JR1':(8,15,0),'C601':(16,15,0),'R601':(38,15,0),'R602':(28,26,0),
'U10':(49,26,0),'D601':(38,37,0),'D602':(38,44,0),'C602':(61,16,0),
'RV601':(76,22,0),'R603':(61,41,0),'R604':(61,33,0),'R605':(78,41,0),
'C603':(91,41,0),'JR2':(104,41,0),
'JR3':(8,62,0),'C604':(17,62,0),'R606':(17,73,0),'U11':(40,61,0),
'R607':(28,84,0),'R608':(53,72,0),'C605':(53,81,0),'C606':(55,61,0),
'JR4':(73,61,0),'R609':(68,77,0),'R610':(80,86,0),'R611':(93,86,0),
'R612':(104,57,0),'U12':(117,66,0),'R613':(104,78,0),
'R614':(131,80,90),'R615':(141,80,90),'R616':(131,60,0),'C607':(133,49,0),
'R617':(133,39,0),'JR5':(148,49,0),
'JR6':(148,10,0),'K3':(114,17,0),
'C610':(62,24,0),'C611':(43,52,0),'C612':(51,54,0),'C613':(35,77,0),
'C614':(130,64,0),'C615':(111,89,0),'C616':(137,15,0),'C617':(137,26,0)
}
assert set(pos)==set(cs),(set(pos)-set(cs),set(cs)-set(pos))
b=pcb.BOARD();b.SetCopperLayerCount(2)
nets={}
for n in sorted({n for c in cs.values() for n in c['pins'].values() if n}):
 ni=pcb.NETINFO_ITEM(b,n);b.Add(ni);nets[n]=ni
assert not any(n.startswith(('MAINS','B_','HV_','HEAT')) for n in nets)
for r,c in cs.items():
 lib,name=c['footprint'].split(':');f=pcb.FootprintLoad(str(LIB/(lib+'.pretty')),name)
 assert f,r+' missing footprint';f.SetReference(r);f.SetValue(c['value']);f.SetFPID(pcb.LIB_ID(lib,name));x,y,ang=pos[r]
 f.SetPosition(pcb.VECTOR2I(pcb.FromMM(x),pcb.FromMM(y)));f.SetOrientationDegrees(ang)
 f.Reference().SetTextSize(pcb.VECTOR2I(pcb.FromMM(1),pcb.FromMM(1)));f.Reference().SetTextThickness(pcb.FromMM(.15));f.Value().SetVisible(False)
 # Clear generic value text to assembly only; exact values stay in footprint properties/BOM.
 b.Add(f)
 physical={p.GetNumber() for p in f.Pads() if p.GetNumber()}
 assert physical==set(c['pins']),(r,physical,c['pins'])
 for p in f.Pads():
  n=c['pins'].get(p.GetNumber())
  if n:p.SetNet(nets[n])
for i,(x,y) in enumerate([(5,5),(155,5),(5,95),(155,95)],1):
 f=pcb.FootprintLoad(str(LIB/'MountingHole.pretty'),'MountingHole_3.2mm_M3');f.SetReference('H'+str(i));f.SetPosition(pcb.VECTOR2I(pcb.FromMM(x),pcb.FromMM(y)));f.Value().SetVisible(False);b.Add(f)
for a,z in [((0,0),(160,0)),((160,0),(160,100)),((160,100),(0,100)),((0,100),(0,0))]:
 s=pcb.PCB_SHAPE();s.SetShape(pcb.SHAPE_T_SEGMENT);s.SetStart(pcb.VECTOR2I(*[pcb.FromMM(v) for v in a]));s.SetEnd(pcb.VECTOR2I(*[pcb.FromMM(v) for v in z]));s.SetLayer(pcb.Edge_Cuts);s.SetWidth(pcb.FromMM(.05));b.Add(s)
def label(txt,x,y):
 t=pcb.PCB_TEXT(b);t.SetText(txt);t.SetPosition(pcb.VECTOR2I(pcb.FromMM(x),pcb.FromMM(y)));t.SetTextSize(pcb.VECTOR2I(pcb.FromMM(1),pcb.FromMM(1)));t.SetTextThickness(pcb.FromMM(.15));t.SetLayer(pcb.F_SilkS);b.Add(t)
label('RENEGADE SPRING v0.4 / LV ONLY',78,96)
label('FX IN',12,9);label('TANK RETURN',19,55);label('PANEL REVERB',76,55);label('TANK DRIVE',100,34)
label('+15 GND -15 +12 COIL',134,7)
path=OUT/'Renegade_Reverb.kicad_pcb';pcb.SaveBoard(str(path),b)
# Portable native project rules. Conservative low-voltage spacing, not mains insulation.
project={'meta':{'filename':'Renegade_Reverb.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_clearance':.25,'min_track_width':.3,'min_via_diameter':.8,'min_through_hole_diameter':.4,'min_hole_clearance':.25,'min_copper_edge_clearance':1.0}}},'net_settings':{'classes':[{'name':'Default','clearance':.25,'track_width':.3,'via_diameter':.8,'via_drill':.4,'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.3,'diff_pair_gap':.25,'diff_pair_via_gap':.25,'nets':list(nets)}]}}
(OUT/'Renegade_Reverb.kicad_pro').write_text(json.dumps(project,indent=2))
(OUT/'Renegade_Reverb.kicad_dru').write_text('(version 1)\n(rule "LV copper clearance" (constraint clearance (min 0.25mm)))\n(rule "Trace width" (constraint track_width (min 0.30mm)))\n(rule "Board edge" (constraint edge_clearance (min 1.0mm)))\n')
(ROOT/'validation/pcb-components.json').write_text(json.dumps({'board_mm':[160,100],'parts':cs,'placements':pos,'pads':sum(len(c['pins']) for c in cs.values()),'nets':list(nets)},indent=2))
print('Created',len(cs),'components',len(nets),'nets',path)
