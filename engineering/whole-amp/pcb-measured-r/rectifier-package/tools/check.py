"""Independently check the complete declared source, placement, route and drill delta."""
import collections,copy,json,math,re,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
import pymupdf
from prepare import M,ROOT,n,props,sha

def old(p,c):return subprocess.check_output(['git','show',c['baseline_commit']+':'+p],cwd=ROOT,text=True)
def drill(path):
 tools={};active=None;hits=collections.Counter()
 for line in path.read_text().splitlines():
  m=re.fullmatch(r'(T\d+)C([\d.]+)',line)
  if m:tools[m[1]]=float(m[2])
  elif re.fullmatch(r'T\d+',line):active=line
  elif line.startswith('X'):
   m=re.fullmatch(r'X(-?[\d.]+)Y(-?[\d.]+)',line);assert m,line
   hits[(tools[active],float(m[1]),float(m[2]))]+=1
 return hits

def holes(f):
 at=list(map(float,n.field(f,'at')[1:]));theta=math.radians(at[2] if len(at)>2 else 0);out=collections.Counter()
 for p in n.children(f,'pad'):
  x,y=map(float,n.field(p,'at')[1:3]);d=n.field(p,'drill');assert len(d)==2
  out[(float(d[1]),round(at[0]+x*math.cos(theta)+y*math.sin(theta),3),round(-(at[1]-x*math.sin(theta)+y*math.cos(theta)),3))]+=1
 return out

def normalize_findings(items):
 return sorted((x['type'],x['severity'],x['description'],tuple(sorted(i['uuid'] for i in x['items']))) for x in items)

def main():
 workspace=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT
 c=json.loads((M/'contract.json').read_text());r=json.loads((workspace/'receipt.json' if workspace!=ROOT else M/'results/integration.json').read_text());refs=set(c['references']);moves=set(c['supporting_moves']);paths=list(c['input_sha256'])
 for p,h in r['after_sha256'].items():assert sha(workspace/p)==h,p
 for p,h in c['protected_native_sha256'].items():assert sha(ROOT/p)==h,p
 assert sha(ROOT/c['datasheet_path'])==c['datasheet_sha256']
 for p in paths[:2]:
  a=json.loads(old(p,c));b=json.loads((workspace/p).read_text())
  for x,y in zip(a['components'],b['components']):
   if x['reference'] in refs:
    assert y['selected_mpn']==c['mpn'] and y['value']==c['display_value'] and y['footprint']==c['footprint']
    for k in ['value','selected_mpn','footprint','datasheet','rating','selection_evidence','status']:x.pop(k,None);y.pop(k,None)
  assert a==b,p
 a=n.parse(old(paths[2],c));b=n.parse((workspace/paths[2]).read_text())
 def strip_sch(x):
  x=copy.deepcopy(x)
  for s in n.children(x,'symbol'):
   if props(s)['Reference'][2].strip('"') in refs:
    for p in list(n.children(s,'property')):
     if p[1].strip('"') in {'Value','Selected_MPN','Footprint','Datasheet','Rating'}:s.remove(p)
  return x
 assert strip_sch(a)==strip_sch(b),'Schematic wiring, position or unrelated change'
 ba=n.parse(old(paths[3],c));bb=n.parse((workspace/paths[3]).read_text());fa=n.fps(ba);fb=n.fps(bb);assert set(fa)==set(fb)
 removed=collections.Counter();added=collections.Counter()
 for ref in refs|moves:
  removed.update(holes(fa[ref]));added.update(holes(fb[ref]))
  if ref in moves:
   q=copy.deepcopy(fb[ref]);assert list(map(float,n.field(q,'at')[1:]))==c['supporting_moves'][ref]
   n.field(q,'at')[1:]=n.field(fa[ref],'at')[1:];assert q==fa[ref]
  else:
   f=fb[ref];assert f[1].strip('"')==c['footprint'] and props(f)['Selected_MPN'][2].strip('"')==c['mpn']
   assert list(map(float,n.field(f,'at')[1:]))==c['placements'][ref]
   assert n.field(f,'uuid')==n.field(fa[ref],'uuid') and n.field(f,'path')==n.field(fa[ref],'path')
   op={p[1]:p for p in n.children(fa[ref],'pad')}
   assert len(n.children(f,'pad'))==2
   body=next(x for x in n.children(f,'fp_rect') if n.field(x,'layer')[1]=='"F.Fab"')
   start=list(map(float,n.field(body,'start')[1:]));end=list(map(float,n.field(body,'end')[1:]))
   assert math.isclose(end[0]-start[0],c['body_length_max_mm']) and math.isclose(end[1]-start[1],c['body_diameter_max_mm'])
   assert math.isclose((end[0]+start[0])/2,c['pitch_mm']/2)
   for p in n.children(f,'pad'):
    assert n.field(p,'net')==n.field(op[p[1]],'net') and n.field(p,'uuid')==n.field(op[p[1]],'uuid')
    assert p[2]=='thru_hole' and float(n.field(p,'drill')[1])==c['drill_mm']
    assert list(map(float,n.field(p,'size')[1:]))==[c['pad_mm']]*2
    assert float(n.field(p,'at')[1])==(0 if p[1]=='"1"' else c['pitch_mm'])
   assert holes(f)==collections.Counter({(c['drill_mm'],c['placements'][ref][0],-130.5):1,(c['drill_mm'],c['placements'][ref][0],-160.98):1})
 def strip_board(x):
  return [v for v in x if not(isinstance(v,list) and ((v[0]=='footprint' and props(v)['Reference'][2].strip('"') in refs|moves) or (v[0] in ['segment','arc'] and n.field(v,'net')[1].strip('"') in c['nets'])))]
 assert strip_board(ba)==strip_board(bb),'Undeclared board change'
 actual=[]
 for s in n.children(bb,'segment'):
  net=n.field(s,'net')[1].strip('"')
  if net in c['nets']:actual.append((net,n.field(s,'layer')[1].strip('"'),tuple(map(float,n.field(s,'start')[1:])),tuple(map(float,n.field(s,'end')[1:])),float(n.field(s,'width')[1])))
 expected=[(net,layer,tuple(a),tuple(b),c['route_width_mm']) for net,layer,pts in c['routes'] for a,b in zip(pts,pts[1:])]
 assert sorted(actual)==sorted(expected)
 assert not [s for s in n.children(bb,'arc') if n.field(s,'net')[1].strip('"') in c['nets']]
 for _,_,a,b,_ in actual:
  dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1]);assert dx==0 or dy==0 or math.isclose(dx,dy,abs_tol=1e-8),'Non-45 degree route'
 d=M/'results';db=drill(d/'before/Renegade_Power.drl');da=drill(d/'after/Renegade_Power.drl')
 assert db-da==removed-added and da-db==added-removed,'Drill delta'
 xa=ET.parse(d/'before/netlist.xml').getroot();xb=ET.parse(d/'after/netlist.xml').getroot();assert n.nets(xa)==n.nets(xb),'Changed endpoint partitions'
 for x in xb.findall('components/comp'):
  if x.get('ref') in refs:assert x.findtext('value')==c['display_value'] and x.findtext('footprint')==c['footprint']
 erc=lambda p:[v for s in json.load(open(p))['sheets'] for v in s['violations']]
 assert erc(d/'before/erc.json')==erc(d/'after/erc.json')
 daj=json.load(open(d/'after/drc.json'));dbj=json.load(open(d/'before/drc.json'))
 assert normalize_findings(daj['violations'])==normalize_findings(dbj['violations'])
 assert len(daj['unconnected_items'])==len(dbj['unconnected_items'])
 pa=pymupdf.open(d/'before/schematics.pdf');pb=pymupdf.open(d/'after/schematics.pdf');assert len(pa)==len(pb)
 changed_pages=[]
 for i,(a,b) in enumerate(zip(pa,pb)):
  if a.get_pixmap().samples!=b.get_pixmap().samples:changed_pages.append(i+1)
 assert changed_pages==[8]
 assert c['drill_mm']-c['finished_hole_tolerance_mm']-c['lead_diameter_max_mm']>=c['minimum_diametral_allowance_mm']
 result={'passed':True,'references':sorted(refs),'supporting_moves':sorted(moves),'net_partitions_preserved':len(n.nets(xa)),'native_DRC_findings':len(daj['violations']),'new_DRC_findings':0,'unconnected_items':len(daj['unconnected_items']),'changed_schematic_pages':changed_pages,'other_pages_pixel_identical':len(pa)-1,'protected_native_files':len(c['protected_native_sha256']),'drill_hits_total':sum(da.values()),'changed_drill_hits':sum((added-removed).values()),'rectifier_holes_resized':8,'source_and_native_changes':r['after_sha256'],'diametral_allowance_mm':round(c['drill_mm']-c['finished_hole_tolerance_mm']-c['lead_diameter_max_mm'],6),'annular_ring_before_registration_mm':(c['pad_mm']-c['drill_mm']-c['finished_hole_tolerance_mm'])/2,'maximum_installed_height_proposal_mm':c['body_standoff_proposal_mm']+c['body_diameter_max_mm'],'whole_amp_qualified':False,'fabrication_ready':False}
 (d/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='source_and_native_changes'},indent=2))
 envelopes=[]
 for ref in sorted(refs):
  x,y,angle=c['placements'][ref];center_y=y-c['pitch_mm']/2*math.sin(math.radians(angle))
  envelopes.append({'reference':ref,'body_center_xy_mm':[x,round(center_y,6)],'maximum_body_xy_mm':[c['body_diameter_max_mm'],c['body_length_max_mm']],'body_standoff_proposal_mm':c['body_standoff_proposal_mm'],'installed_height_proposal_mm':result['maximum_installed_height_proposal_mm'],'thermal_clearance_qualified':False})
 for ref in ['R501','R502']:
  x,y=c['supporting_moves'][ref]
  envelopes.append({'reference':ref,'body_center_xy_mm':[x+7.62,y],'maximum_body_xy_mm':[9.5,4.2],'body_standoff_proposal_mm':None,'installed_height_proposal_mm':None,'thermal_clearance_qualified':False,'geometry_source':'../fmp200-holes/contract.json'})
 (d/'package-envelopes.json').write_text(json.dumps({'board_sha256':sha(workspace/paths[3]),'frame':'Native Power PCB XY; Z above PCB top','components':envelopes,'fabrication_ready':False},indent=2)+'\n')

if __name__=='__main__':main()
