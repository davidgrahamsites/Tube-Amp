"""Synchronize adopted film identities without moving symbols or changing wiring."""
import copy,hashlib,json,sys
from pathlib import Path
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2]
sys.path.insert(0,str(ROOT/'engineering/whole-amp/tools'));import native_sexpr as v
Q=json.dumps
CIR='engineering/whole-amp/reverb-600/circuit.json'
def spans(text):
 depth=0;quoted=False;escape=False;start=None
 for i,ch in enumerate(text):
  if quoted:
   if escape:escape=False
   elif ch=='\\':escape=True
   elif ch=='"':quoted=False
  elif ch=='"':quoted=True
  elif ch=='(':
   if depth==1 and text.startswith('(symbol ',i):start=i
   depth+=1
  elif ch==')':
   depth-=1
   if depth==1 and start is not None:yield start,i+1;start=None

def emit(x):return '('+' '.join(emit(t) if isinstance(t,list) else t for t in x)+')'
def props(x):return {p[1].strip('"'):p for p in v.children(x,'property')}
def desired(row,contract):
 return {'Footprint':row['footprint'],'Datasheet':contract['parts'][row['mpn']]['datasheet'],'Selected_MPN':row['mpn'],'Selection_evidence':'VAL-057; selected hardware identity, system qualification pending'}
def main():
 assert sys.argv[1:]==['--apply']
 c=json.loads((M/'contract.json').read_text());rows={x['reference']:x for x in c['adopted_board_parts']}
 for p,h in c['native_sha256'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 source=json.loads((ROOT/CIR).read_text());seen=set()
 for x in source['components']:
  r=x['reference']
  if r not in rows:continue
  row=rows[r];assert x['value']==row['value'];seen.add(r)
  x.update(footprint=row['footprint'],selected_mpn=row['mpn'],datasheet=c['parts'][row['mpn']]['datasheet'],selection_evidence='engineering/component-selection/film-parity/review.md',selection_status='adopted hardware identity synchronized; system qualification pending')
 assert seen==set(rows)
 changes={CIR:json.dumps(source,indent=2)+'\n'};seen=set()
 for path in (ROOT/'engineering/whole-amp/reverb-600/cad').glob('*.kicad_sch'):
  text=path.read_text();edits=[]
  for a,b in spans(text):
   s=v.parse(text[a:b]);pr=props(s);r=pr['Reference'][2].strip('"')
   if r not in rows:continue
   assert r not in seen;seen.add(r);assert pr['Value'][2]==Q(rows[r]['value'])
   for name,value in desired(rows[r],c).items():
    if name not in pr:
     field=copy.deepcopy(pr['Footprint']);field[1]=Q(name);s.append(field);pr[name]=field
    pr[name][2]=Q(value);assert 'hide' in v.field(pr[name],'effects')
   edits.append((a,b,emit(s)))
  if edits:
   for a,b,new in reversed(edits):text=text[:a]+new+text[b:]
   v.parse(text);changes[str(path.relative_to(ROOT))]=text
 assert seen==set(rows)
 for p,t in changes.items():(ROOT/p).write_text(t)
 (M/'results/integration.json').write_text(json.dumps({'changed_paths':list(changes),'references':sorted(rows),'after_sha256':{p:hashlib.sha256(t.encode()).hexdigest() for p,t in changes.items()},'boards_changed':False,'electrical_change':False,'fabrication_ready':False},indent=2)+'\n');print('Synchronized',len(seen),'references in',len(changes)-1,'sheets; source updated; boards preserved.')
if __name__=='__main__':main()
