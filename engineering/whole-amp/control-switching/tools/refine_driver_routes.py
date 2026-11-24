"""One-time DRC-directed route refinement; preserves every baseline copper object."""
import hashlib,json,sys
from pathlib import Path
import integrate_drivers as m
v=m.v;ROOT=m.ROOT;M=m.M
p=ROOT/'engineering/whole-amp/pcb-measured-r/boards/Renegade_Control.kicad_pcb'
def main():
 assert sys.argv[1:]==['--apply'] and not (M/'results/route-refinement.json').exists()
 before=p.read_text();receipt=json.loads((M/'results/integration.json').read_text())
 assert hashlib.sha256(before.encode()).hexdigest()==receipt['after_sha256'][str(p.relative_to(ROOT))]
 oldids={m.UID('track'+str(i)) for i in range(receipt['added_track_count'])}|{m.UID('via'+str(i)) for i in range(receipt['added_via_count'])}
 changes=[]
 for kind in ['segment','via','footprint']:
  for start,end in m.spans(before,kind):
   x=v.parse(before[start:end])
   if kind=='footprint':
    if m.prop(x,'Reference')[2]=='"D333"':v.field(x,'at')[1:]=['128','38','180'];changes.append((start,end,m.emit(x)))
   elif v.field(x,'uuid')[1].strip('"') in oldids:changes.append((start,end,''))
 text=before
 for start,end,replacement in sorted(changes,reverse=True):text=text[:start]+replacement+text[end:]
 routes=[];vias=[]
 def route(layer,net,pts,width=.4):
  for a,b in zip(pts,pts[1:]):routes.append((layer,net,a,b,width))
 for dx,net,gate in [(0,'COIL_CH','CH_GATE'),(60.68,'COIL_REV','REV_GATE')]:
  vias.append((117.035+dx,45.105,net))
  route('F.Cu',net,[(114.495+dx,43.905),(115.835+dx,43.905),(117.035+dx,45.105)])
  if dx==0:route('F.Cu',net,[(114.495,43.905),(114.495,41.345),(117.84,38)])
  else:route('F.Cu',net,[(114.495+dx,43.905),(114.495+dx,40.345),(114.84+dx,40)])
  route('F.Cu',gate,[(89.535+dx,43.875),(95.685+dx,43.875)],.3)
  route('F.Cu',gate,[(95.685+dx,43.875),(95.685+dx,40.5),(96.685+dx,39.5),(110.545+dx,39.5),(111.545+dx,40.5),(111.545+dx,45.305),(112.545+dx,46.305),(113.545+dx,46.305)],.3)
  route('F.Cu','GND',[(105.845+dx,43.875),(105.845+dx,47.505),(106.845+dx,48.505),(114.445+dx,48.505),(115.445+dx,47.505),(115.445+dx,46.305)])
 route('F.Cu','+12V',[(128,38),(128,33),(129,32),(184.68,32),(185.68,33),(185.68,40)])
 route('B.Cu','+12V',[(185.68,40),(185.68,60),(182.104,63.576),(182.104,68.125)])
 add=[]
 for i,(layer,net,a,b,width) in enumerate(routes):add.append(f'(segment (start {a[0]:.6f} {a[1]:.6f}) (end {b[0]:.6f} {b[1]:.6f}) (width {width}) (layer "{layer}") (net "{net}") (uuid "{m.UID("refined-track"+str(i))}"))')
 for i,(x,y,net) in enumerate(vias):add.append(f'(via (at {x:.6f} {y:.6f}) (size .8) (drill .4) (layers "F.Cu" "B.Cu") (net "{net}") (uuid "{m.UID("refined-via"+str(i))}"))')
 text=text.rstrip()[:-1]+'\n'+'\n'.join(add)+')\n';v.parse(text);p.write_text(text)
 (M/'results/route-refinement.json').write_text(json.dumps(dict(before_sha256=hashlib.sha256(before.encode()).hexdigest(),after_sha256=hashlib.sha256(text.encode()).hexdigest(),removed_new_objects=len(oldids),added_tracks=len(routes),added_vias=len(vias),reason='DRC: gate tracks respect0.3mm rule and stay on front; move D333 clear of existing AC track; +12 return escapes on back',fabrication_ready=False),indent=2)+'\n')
 print('Refined only new objects; baseline tracks unchanged.')
if __name__=='__main__':main()
