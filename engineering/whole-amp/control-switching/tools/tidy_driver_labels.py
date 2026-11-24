"""One-time visual corrections after inspecting the native PDF; no connectivity edits."""
from pathlib import Path
import hashlib,json,sys
import integrate_drivers as m
p=m.ROOT/'engineering/whole-amp/reverb-600/cad/09b_latches_drivers.kicad_sch'
def main():
 assert sys.argv[1:]==['--apply'] and not (m.M/'results/readability-correction.json').exists()
 old=p.read_text();text=old;replacements=[]
 for a,b in m.spans(old,'symbol'):
  x=m.v.parse(old[a:b]);ref=m.prop(x,'Reference')[2].strip('"')
  if ref in ['D333','D342','D332']:
   for name in ['Reference','Value']:m.v.field(m.prop(x,name),'at')[3]='90'
   replacements.append((a,b,m.emit(x)))
 for a,b in m.spans(old,'text'):
  x=m.v.parse(old[a:b]);pos=None
  if x[1].startswith('"D333 / D342:'):pos=['380','155','0']
  elif x[1].startswith('"D331: Main'):pos=['380','168','0']
  elif x[1].startswith('"Q-bar feeds'):pos=['380','115','0']
  if pos:m.v.field(x,'at')[1:]=pos;replacements.append((a,b,m.emit(x)))
 for a,b,t in sorted(replacements,reverse=True):text=text[:a]+t+text[b:]
 note=['text',m.Q('U3 reset replacement and removable carrier: PENDING.\nCurrent supervisor is not release-qualified.'),['at','380','300','0'],['effects',['font',['size','1.27','1.27']],['justify','left','top']],['uuid',m.UID('reset-status-note')]]
 text=text.rstrip()[:-1]+' '+m.emit(note)+')\n';m.v.parse(text);p.write_text(text)
 (m.M/'results/readability-correction.json').write_text(json.dumps(dict(before_sha256=hashlib.sha256(old.encode()).hexdigest(),after_sha256=hashlib.sha256(text.encode()).hexdigest(),scope='Label orientation and text-only positions; no symbol pin or wire changes'),indent=2)+'\n')
if __name__=='__main__':main()
