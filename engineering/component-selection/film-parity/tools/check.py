"""Complete metadata-only native delta, footprint geometry and page preservation gate."""
import copy,hashlib,json,math,subprocess,sys,xml.etree.ElementTree as E
from pathlib import Path
import pymupdf
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2];D=M/'results'
sys.path.insert(0,str(ROOT/'engineering/whole-amp/tools'));import native_sexpr as v
ALLOWED={'Footprint','Datasheet','Selected_MPN','Selection_evidence'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 c=json.loads((M/'contract.json').read_text());r=json.loads((D/'integration.json').read_text());rows={x['reference']:x for x in c['adopted_board_parts']};base=c['baseline_commit']
 for p,h in r['after_sha256'].items():assert sha(ROOT/p)==h,p
 for p,h in c['native_sha256'].items():
  if p not in r['changed_paths']:assert sha(ROOT/p)==h,p
 for x in c['parts'].values():assert sha(ROOT/x['retained_primary'])==x['primary_sha256']
 def net(path):
  a=E.parse(path).getroot();return a,{n.get('name'):sorted(tuple(sorted(p.attrib.items())) for p in n.findall('node')) for n in a.findall('nets/net')}
 before,nb=net(D/'before.xml');after,na=net(D/'after.xml');assert nb==na
 comps=lambda a:{x.get('ref'):x for x in a.findall('components/comp')}
 cb,ca=comps(before),comps(after);assert set(cb)==set(ca)
 def trim(x):
  x=copy.deepcopy(x)
  for node in list(x):
   if node.tag in ['footprint','datasheet'] or (node.tag=='property' and node.get('name') in ALLOWED):x.remove(node)
   elif node.tag=='fields':
    for f in list(node):
     if f.get('name') in ALLOWED:node.remove(f)
  return E.tostring(x)
 for ref,x in cb.items():
  y=ca[ref]
  if ref in rows:
   assert trim(x)==trim(y),ref
   assert y.findtext('footprint')==rows[ref]['footprint']
   assert y.find("property[@name='Selected_MPN']").get('value')==rows[ref]['mpn']
  else:assert E.tostring(x)==E.tostring(y),ref
 # Guard hidden-only schematic mutation, including symbol instance pin UUIDs.
 for p in r['changed_paths']:
  if not p.endswith('.kicad_sch'):continue
  old=v.parse(subprocess.check_output(['git','show',base+':'+p],cwd=ROOT,text=True));new=v.parse((ROOT/p).read_text())
  def strip(a):
   a=copy.deepcopy(a)
   for s in v.children(a,'symbol'):
    props={x[1].strip('"'):x for x in v.children(s,'property')};ref=props['Reference'][2].strip('"')
    if ref in rows:
     for key in ALLOWED:
      if key in props:
       assert 'hide' in v.field(props[key],'effects');s.remove(props[key])
   return a
  assert strip(old)==strip(new),p
 # Source values, pins, block ownership and all unrelated fields are identical.
 p='engineering/whole-amp/reverb-600/circuit.json';old=json.loads(subprocess.check_output(['git','show',base+':'+p],cwd=ROOT));new=json.loads((ROOT/p).read_text())
 for a,b in zip(old['components'],new['components']):
  if a['reference'] in rows:
   row=rows[a['reference']];assert b['footprint']==row['footprint'] and b['selected_mpn']==row['mpn']
   for key in ['footprint','selected_mpn','datasheet','selection_evidence','selection_status']:a.pop(key,None);b.pop(key,None)
 assert old==new
 geometry=[]
 for row in rows.values():
  board=v.parse((ROOT/row['board']).read_text());f=v.fps(board)[row['reference']];assert f[1]==json.dumps(row['footprint'])
  pads=v.children(f,'pad');assert len(pads)==2
  for p in pads:assert p[2:4]==['thru_hole','circle'] and float(v.field(p,'drill')[1])==.9 and list(map(float,v.field(p,'size')[1:]))==[1.8,1.8]
  xy=[list(map(float,v.field(p,'at')[1:3])) for p in pads];assert abs(math.dist(*xy)-5)<1e-9
  geometry.append({'ref':row['reference'],'pitch_mm':5,'round_finished_hole_nominal_mm':.9,'round_pad_mm':1.8,'annulus_nominal_mm':.45,'hole_tolerance_not_yet_fabricator_qualified':True})
 def erc(path):return [x for s in json.loads(path.read_text())['sheets'] for x in s['violations']]
 assert erc(D/'before-erc.json')==erc(D/'after-erc.json')
 pb=pymupdf.open(D/'before.pdf');pa=pymupdf.open(D/'after.pdf');assert len(pb)==len(pa);pixels=[]
 for i in range(len(pb)):
  x=pb[i].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5));y=pa[i].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5));assert (x.width,x.height,x.samples)==(y.width,y.height,y.samples),i
  pixels.append({'page':i+1,'width':x.width,'height':x.height,'raster_sha256':hashlib.sha256(x.samples).hexdigest(),'identical':True})
 output={'passed':True,'synchronized_references':sorted(rows),'net_count_preserved':len(nb),'component_count_preserved':len(cb),'protected_native_files':len(c['native_sha256'])-len(r['changed_paths']),'unchanged_board_count':4,'ERC_unchanged_count':len(erc(D/'after-erc.json')),'all_pages_pixel_identical':True,'page_count':len(pa),'page_rasters':pixels,'footprint_geometry':geometry,'conflicts_not_changed':c['conflicts_not_changed'],'all_parts_procurement_qualified':False,'shanghai_checkout_verified':False,'whole_amp_qualified':False,'fabrication_ready':False,'input_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),M/'contract.json',D/'before.xml',D/'after.xml',D/'integration.json',D/'before.pdf',D/'after.pdf',D/'sourcing.json']}}
 (D/'checks.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps({k:x for k,x in output.items() if k not in ['page_rasters','footprint_geometry','input_sha256','conflicts_not_changed']},indent=2))
if __name__=='__main__':main()
