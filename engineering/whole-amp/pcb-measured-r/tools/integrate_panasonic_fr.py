"""Guarded one-time exact FR-A footprint integration, preserving circuit/geometry outside seven parts."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
import pcbnew as p
ROOT=Path(__file__).resolve().parents[4]
MODULE=ROOT/'engineering/whole-amp/pcb-measured-r'
PKG=ROOT/'engineering/component-selection/footprints/panasonic-fr'
LIB=PKG.parent/'Renegade_Selected.pretty'
BASE='3efa8d9b53ab95ab312d7110e59168276e5308b3'
OUT=MODULE/'review/panasonic-fr-integration.json'
PATHS=['engineering/whole-amp/reverb-600/circuit.json','engineering/whole-amp/reverb-600/cad/08_control_supply.kicad_sch','engineering/whole-amp/reverb-600/cad/07c_reverb_output.kicad_sch']
def baseline(path):return subprocess.check_output(['/usr/bin/git','show',BASE+':'+str(path.relative_to(ROOT))],cwd=ROOT)
def digest(data):return hashlib.sha256(data).hexdigest()
def symbol_spans(text):
 # Track native S-expressions without reformatting factory or hand-edited sheets.
 depth=0;quoted=False;escaped=False;start=None
 for i,ch in enumerate(text):
  if quoted:
   if escaped:escaped=False
   elif ch=='\\':escaped=True
   elif ch=='"':quoted=False
  elif ch=='"':quoted=True
  elif ch=='(':
   if depth==1 and text.startswith('(symbol ',i):start=i
   depth+=1
  elif ch==')':
   depth-=1
   if depth==1 and start is not None:
    yield start,i+1;start=None

def restore_unaffected_footprints(path, baseline_text, targets):
 # pcbnew serializes defaults/reorders paths even on untouched footprints.
 # Retain their original native bytes so this package wave has a narrow delta.
 def blocks(text):
  depth=0;quoted=False;escaped=False;start=None
  for i,ch in enumerate(text):
   if quoted:
    if escaped:escaped=False
    elif ch=='\\':escaped=True
    elif ch=='"':quoted=False
   elif ch=='"':quoted=True
   elif ch=='(':
    if depth==1 and text.startswith('(footprint ',i):start=i
    depth+=1
   elif ch==')':
    depth-=1
    if depth==1 and start is not None:
     block=text[start:i+1];ref=re.search(r'\(property\s+"Reference"\s+"([^"]+)"',block).group(1)
     yield ref,start,i+1,block;start=None
 originals={r:b for r,_,_,b in blocks(baseline_text)};text=path.read_text()
 for ref,start,end,block in reversed(list(blocks(text))):
  if ref not in targets:text=text[:start]+originals[ref]+text[end:]
 path.write_text(text)

def main():
 assert sys.argv[1:]==['--apply'] and not OUT.exists(),'One-time guarded application only'
 specs=json.loads((PKG/'package-contract.json').read_text());mapping={ref:a for a in specs['parts'] for ref in a['refs']}
 paths=[ROOT/x for x in PATHS]+[MODULE/f'boards/Renegade_{n}.kicad_pcb' for n in ['Control','Reverb']]
 originals={x:x.read_bytes() for x in paths}
 for x,data in originals.items():assert data==baseline(x),f'Unexpected edits: {x}'
 modified={};c=json.loads(originals[paths[0]])
 for row in c['components']:
  if row['reference'] in mapping:row['footprint']='Renegade_Selected:'+mapping[row['reference']]['footprint']
 modified[paths[0]]=json.dumps(c,indent=2)+'\n'
 found=set()
 for path in paths[1:3]:
  text=originals[path].decode();replacements=[]
  for start,end in symbol_spans(text):
   block=text[start:end];ref=re.search(r'\(property "Reference" "([^"]+)"',block)
   if not ref or ref.group(1) not in mapping:continue
   name=ref.group(1);fp='Renegade_Selected:'+mapping[name]['footprint']
   block,count=re.subn(r'(\(property "Footprint" )"[^"]*"',lambda m:m.group(1)+json.dumps(fp),block)
   assert count==1,(name,count);replacements.append((start,end,block));found.add(name)
  for start,end,block in reversed(replacements):text=text[:start]+block+text[end:]
  modified[path]=text
 assert found==set(mapping),found
 keep=[];changes=[];boards=[]
 for path in paths[3:]:
  board=p.LoadBoard(str(path));keep.append(board);boards.append((path,board))
  for old in list(board.GetFootprints()):
   ref=old.GetReference()
   if ref not in mapping:continue
   a=mapping[ref];new=p.FootprintLoad(str(LIB),a['footprint']);keep.extend([old,new])
   new.SetReference(ref);new.SetValue(old.GetValue());new.SetPosition(old.GetPosition());new.SetOrientationDegrees(old.GetOrientationDegrees());new.SetPath(old.GetPath());new.SetFPID(p.LIB_ID('Renegade_Selected',a['footprint']))
   new.Reference().SetPosition(old.Reference().GetPosition());new.Reference().SetTextAngle(old.Reference().GetTextAngle());new.Reference().SetTextSize(old.Reference().GetTextSize())
   new.SetField('Selected_MPN',a['mpn']);new.Value().SetVisible(False)
   for field in new.GetFields():
    if field.GetName() not in ['Reference','Value']:field.SetVisible(False)
   op={q.GetNumber():q for q in old.Pads()};np={q.GetNumber():q for q in new.Pads()};assert set(op)==set(np)=={'1','2'}
   endpoints=0;pads=[]
   for num,pad in np.items():
    prev=op[num];pad.SetNet(prev.GetNet())
    if pad.GetPosition()!=prev.GetPosition():
     for track in board.GetTracks():
      if track.GetNetCode()!=prev.GetNetCode():continue
      if track.GetStart()==prev.GetPosition():track.SetStart(pad.GetPosition());endpoints+=1
      if track.GetEnd()==prev.GetPosition():track.SetEnd(pad.GetPosition());endpoints+=1
    pads.append(dict(number=num,net=pad.GetNetname(),before_mm=[p.ToMM(prev.GetPosition().x),p.ToMM(prev.GetPosition().y)],after_mm=[p.ToMM(pad.GetPosition().x),p.ToMM(pad.GetPosition().y)],drill_mm=p.ToMM(pad.GetDrillSize().x)))
   changes.append(dict(reference=ref,board=path.name,old_footprint=str(old.GetFPID().GetLibItemName()),new_footprint=a['footprint'],pads=pads,track_endpoints_adjusted=endpoints))
   board.Remove(old);board.Add(new)
 assert {x['reference'] for x in changes}==set(mapping)
 json.dumps(changes) # validate receipt fields before any mutation
 for path,text in modified.items():path.write_text(text)
 for path,board in boards:
  project=path.with_suffix('.kicad_pro');data=project.read_bytes();p.SaveBoard(str(path),board);project.write_bytes(data)
  restore_unaffected_footprints(path,originals[path].decode(),set(mapping))
 OUT.write_text(json.dumps(dict(baseline_commit=BASE,kicad=p.Version(),changes=changes,before_sha256={str(x.relative_to(ROOT)):digest(b) for x,b in originals.items()},after_sha256={str(x.relative_to(ROOT)):digest(x.read_bytes()) for x in paths},fabrication_ready=False,scope='Exact footprint assignments only; preserve positions and circuits. Bypass proximity/loops and sockets pending.'),indent=2)+'\n')
 print('Integrated seven selected FR-A packages on Control/Reverb and source/native sheets')
if __name__=='__main__':main()
