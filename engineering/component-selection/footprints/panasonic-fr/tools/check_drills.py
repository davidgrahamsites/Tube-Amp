"""Read native boards and exported Excellon; check the fourteen selected PTH hits."""
from pathlib import Path
import json,re,hashlib
import pcbnew as p
MOD=Path(__file__).resolve().parents[1];ROOT=MOD.parents[3]
def main():
 refs={r:a for a in json.loads((MOD/'package-contract.json').read_text())['parts'] for r in a['refs']};rows=[];hashes={}
 for name in ['Control','Reverb']:
  source=ROOT/f'engineering/whole-amp/pcb-measured-r/boards/Renegade_{name}.kicad_pcb';file=MOD/f'results/drill/Renegade_{name}-PTH.drl';text=file.read_text()
  assert 'METRIC' in text and 'absolute / metric / decimal' in text and 'FileFunction,Plated,1,2,PTH' in text
  tools={m[1]:float(m[2]) for m in re.finditer(r'^T(\d+)C([\d.]+)$',text,re.M)};hits=[];tool=None
  for line in text.splitlines():
   m=re.fullmatch(r'T(\d+)',line)
   if m:tool=m[1]
   m=re.fullmatch(r'X([-\d.]+)Y([-\d.]+)',line)
   if m:hits.append((float(m[1]),-float(m[2]),tools[tool]))
  board=p.LoadBoard(str(source))
  for f in board.GetFootprints():
   if f.GetReference() not in refs:continue
   a=refs[f.GetReference()]
   for pad in f.Pads():
    x=p.ToMM(pad.GetPosition().x);y=p.ToMM(pad.GetPosition().y)
    matching=[h for h in hits if abs(h[0]-x)<=.000501 and abs(h[1]-y)<=.000501]
    assert len(matching)==1 and matching[0][2]==a['finished_hole_mm'],(f.GetReference(),pad.GetNumber(),matching)
    rows.append(dict(reference=f.GetReference(),pad=pad.GetNumber(),xy_mm=[x,y],exported_finished_drill_mm=matching[0][2],plated=True,shape='round'))
  hashes[name]={'board':hashlib.sha256(source.read_bytes()).hexdigest(),'excellon':hashlib.sha256(file.read_bytes()).hexdigest()}
 assert len(rows)==14
 result=dict(passed=True,selected_holes=rows,source_sha256=hashes,scope='Only seven Panasonic positions; remaining component/mount/slot/hole qualification not implied',fabrication_ready=False)
 (MOD/'results/drill-checks.json').write_text(json.dumps(result,indent=2)+'\n');print('14 selected round PTH hits match native sizes, positions and plating')
if __name__=='__main__':main()
