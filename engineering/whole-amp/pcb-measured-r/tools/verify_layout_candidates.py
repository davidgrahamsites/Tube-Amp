"""Verify a bounded candidate against active source before adoption.

Run with KiCad Python and the candidate directory after native DRC and visual
review. This checks geometry/interface preservation and known connection counts;
it does not qualify the whole layout or permit fabrication.
"""
from pathlib import Path
import json, importlib.util, hashlib, sys
import pcbnew as p
root=Path(__file__).resolve().parents[1]
out=Path(sys.argv[1])
spec=importlib.util.spec_from_file_location('copper',root/'tools/audit_copper.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
manifest=json.loads((out/'manifest.json').read_text());keep=[]
def fp(b):
 return sorted((f.GetReference(),f.GetFPID().GetUniStringLibId(),f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees(),tuple(sorted((q.GetNumber(),q.GetNetname(),q.GetPosition().x,q.GetPosition().y,q.GetSize().x,q.GetSize().y,q.GetDrillSize().x,q.GetDrillSize().y) for q in f.Pads()))) for f in b.GetFootprints())
def outline(b):
 return sorted((x.GetShapeStr(),x.GetStart().x,x.GetStart().y,x.GetEnd().x,x.GetEnd().y) for x in b.GetDrawings() if x.GetLayer()==p.Edge_Cuts)
for name,r in manifest['boards'].items():
 a=p.LoadBoard(str(root/'boards'/f'Renegade_{name}.kicad_pcb'));b=p.LoadBoard(str(out/f'Renegade_{name}.kicad_pcb'));keep +=[a,b]
 assert fp(a)==fp(b),name
 assert outline(a)==outline(b),name
 assert hashlib.sha256((root/'boards'/f'Renegade_{name}.kicad_dru').read_bytes()).hexdigest()==hashlib.sha256((out/f'Renegade_{name}.kicad_dru').read_bytes()).hexdigest()
 d=json.loads((out/f'{name}-drc.json').read_text())
 assert all(v['type']=='missing_courtyard' for v in d['violations'])
 assert len(d['unconnected_items'])=={'Main':105,'Power':39,'Control':99,'Reverb':0}[name]
 c=m.inspect_board(out/f'Renegade_{name}.kicad_pcb');assert not c['simple_bends_over_45_degrees']
 r['verification']={'footprints_pads_positions_unchanged':True,'outline_unchanged':True,'custom_rules_unchanged':True,'simple_bend_findings':0,'unconnected_items':len(d['unconnected_items']),'missing_courtyards':len(d['violations']),'detail_visual_review':'REQUIRED before adoption' if name!='Reverb' else 'unchanged board'}
manifest['fabrication_ready']=False
(out/'verified-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:r['verification'] for k,r in manifest['boards'].items()},indent=2))
