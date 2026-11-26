"""Independent native pin partitions, exact deltas, geometry and drill acceptance."""
from pathlib import Path
import collections,copy,hashlib,json,math,re,subprocess,sys,xml.etree.ElementTree as E
import pymupdf
M=Path(__file__).resolve().parents[1];ROOT=M.parents[3];D=M/'results'
sys.path.insert(0,str(ROOT/'engineering/whole-amp/tools'));import native_sexpr as n

def props(x):return {p[1].strip('"'):p for p in n.children(x,'property')}
def ref(x):return props(x)['Reference'][2].strip('"')
def objects(x,kind):return {n.field(p,'uuid')[1].strip('"'):p for p in n.children(x,kind)}
def groups(path):return {frozenset((p.get('ref'),p.get('pin')) for p in net.findall('node')) for net in E.parse(path).findall('nets/net') if not net.get('name').startswith('unconnected-')}
def holes(folder):
 out=collections.Counter()
 for p in folder.glob('*.drl'):
  sizes={};t=None
  for line in p.read_text().splitlines():
   m=re.fullmatch(r'T(\d+)C([\d.]+)',line)
   if m:sizes[m[1]]=float(m[2]);continue
   m=re.fullmatch(r'T(\d+)',line)
   if m:t=m[1];continue
   m=re.fullmatch(r'X([\d.-]+)Y([\d.-]+)',line)
   if m:out[(sizes[t],float(m[1]),float(m[2]))]+=1
 return out

def main():
 c=json.loads((M/'contract.json').read_text());receipt=json.loads((D/'integration.json').read_text());parts=c['parts'];protected=0;addedtracks=[]
 for path,h in c['native_sha256'].items():
  raw=(ROOT/path).read_bytes();assert hashlib.sha256(raw).hexdigest()==receipt['after_sha256'].get(path,h),path
  old=subprocess.check_output(['git','show',c['baseline_commit']+':'+path],cwd=ROOT).decode()
  if path.endswith('.json'):
   a,b=json.loads(old),json.loads(raw);aa={(r['reference'],r['unit']):r for r in a['components']};bb={(r['reference'],r['unit']):r for r in b['components']}
   assert set(bb)-set(aa)=={('D603',1),('D604',1)} and not set(aa)-set(bb)
   for k,v in aa.items():
    if k[0] not in ['R616','R618']:assert bb[k]==v,k
    else:assert bb[k]['pins']==v['pins'] and bb[k]['value']==v['value']
   for r,p in parts.items():
    v=bb[r,1];assert all(v[k]==p[k] for k in ['pins','value','footprint','rating','datasheet']);assert v['selected_mpn']==p['mpn']
  elif path.endswith('.kicad_sch'):
   a,b=n.parse(old),n.parse(raw.decode());aa,bb=objects(a,'symbol'),objects(b,'symbol');assert not set(aa)-set(bb)
   for u,s in aa.items():
    if ref(s) in ['R616','R618']:
     # Changes confined to exact-part properties; all instance pins/placement retained.
     omit={'Footprint','Rating','Datasheet','MPN','Supplier_SKU','Part_source','Price_stock_observed','Part_status'}
     norm=lambda o:[x for x in o if not(isinstance(x,list) and x[0]=='property' and x[1].strip('"') in omit)]
     assert norm(s)==norm(bb[u])
    else:assert s==bb[u],ref(s)
   assert {ref(bb[u]) for u in set(bb)-set(aa)}=={'D603','D604','#PWR9910'}
   for r in parts:
    s=next(x for x in n.children(b,'symbol') if ref(x)==r);p=props(s)
    assert p['MPN'][2].strip('"')==parts[r]['mpn']
    assert p['Supplier_SKU'][2].strip('"')==parts[r]['supplier_sku']
   for kind in ['wire','junction','label','global_label','hierarchical_label','no_connect','text']:
    aa,bb=objects(a,kind),objects(b,kind);assert not set(aa)-set(bb)
    for u,x in aa.items():
     if x==bb[u]:continue
     assert kind=='wire' and n.field(x,'pts')[1:]==[['xy','266.7','90.17'],['xy','304.8','90.17']]
     assert n.field(bb[u],'pts')[1:]==[['xy','266.7','90.17'],['xy','285.75','90.17']]
  else:
   a,b=n.parse(old),n.parse(raw.decode());fa={ref(x):x for x in n.children(a,'footprint')};fb={ref(x):x for x in n.children(b,'footprint')};assert set(fb)-set(fa)=={'D603','D604'} and not set(fa)-set(fb)
   for r,f in fa.items():
    if r not in ['R616','R618']:assert fb[r]==f,r
    else:
     for k in ['uuid','path']:assert n.field(f,k)==n.field(fb[r],k)
     assert {p[1]:n.field(p,'net') for p in n.children(f,'pad')}=={p[1]:n.field(p,'net') for p in n.children(fb[r],'pad')}
     if r=='R618':
      assert n.field(f,'at')==n.field(fb[r],'at') and n.children(f,'pad')==n.children(fb[r],'pad')
   for r,p in parts.items():
    f=fb[r];assert f[1].strip('"')==p['footprint'];assert props(f)['Selected_MPN'][2].strip('"')==p['mpn']
    assert {x[1].strip('"'):n.field(x,'net')[1].strip('"') for x in n.children(f,'pad')}==p['pins']
    drill=.8 if r=='R618' else .9
    for pad in n.children(f,'pad'):assert n.field(pad,'drill')[1:]==[str(drill)] and pad[2:4]==['thru_hole','circle']
   for kind in ['segment','arc','via','zone','gr_line','gr_rect','gr_arc','gr_circle','gr_text']:
    aa,bb=objects(a,kind),objects(b,kind);assert not set(aa)-set(bb)
    for u,x in aa.items():
     if x==bb[u]:continue
     assert kind=='segment' and u=='49624d20-7c0a-4f6d-8e89-93f111a3b6ef'
     z=copy.deepcopy(bb[u]);n.field(z,'start')[1:]=['131.0','60.0'];assert z==x
    if kind=='segment':addedtracks=[bb[u] for u in set(bb)-set(aa)]
    else:assert set(bb)==set(aa)
   assert len(addedtracks)==8
   for t in addedtracks:
    ds=[abs(float(x)-float(y)) for x,y in zip(n.field(t,'start')[1:],n.field(t,'end')[1:])];assert min(ds)==0 or abs(ds[0]-ds[1])<1e-8
    assert n.field(t,'width')[1]=='0.4'
   omit={'footprint','segment'};assert [x for x in a if not isinstance(x,list) or x[0] not in omit]==[x for x in b if not isinstance(x,list) or x[0] not in omit]
 # Manufacturer-derived hole/package acceptance; no nominal-lead shortcut.
 for name,g in c['hole_geometry'].items():
  f=n.parse((ROOT/'engineering/component-selection/footprints/Renegade_Selected.pretty'/(name+'.kicad_mod')).read_text())
  pp=n.children(f,'pad');assert len(pp)==2
  assert float(n.field(pp[1],'at')[1])==g['pitch']
  for pad in pp:
   assert pad[2:4]==['thru_hole','circle'] and float(n.field(pad,'drill')[1])==g['drill']
   assert list(map(float,n.field(pad,'size')[1:]))==[g['pad'],g['pad']]
  assert g['drill']-c['finished_hole_tolerance_provisional_mm']-g['lead_max']>=.16
  body=next(o for o in n.children(f,'fp_rect') if n.field(o,'layer')[1]=='"F.Fab"')
  delta=[float(b)-float(a) for a,b in zip(n.field(body,'start')[1:],n.field(body,'end')[1:])]
  assert abs(delta[0]-g['body_length_max'])<1e-9 and abs(delta[1]-g['body_diameter_max'])<1e-9
 # Protect every other active sheet/board byte-for-byte against the commit.
 for directory,pattern in [('engineering/whole-amp/reverb-600/cad','*.kicad_sch'),('engineering/whole-amp/pcb-measured-r/boards','*.kicad_pcb')]:
  for p in (ROOT/directory).glob(pattern):
   if str(p.relative_to(ROOT)) in receipt['changed_paths']:continue
   assert p.read_bytes()==subprocess.check_output(['git','show',c['baseline_commit']+':'+str(p.relative_to(ROOT))],cwd=ROOT);protected+=1
 before,after=groups(D/'before.xml'),groups(D/'after.xml');expected=set()
 for g in before:
  if ('C607','2') in g:g=g|{('D603','1')}
  if ('K3','11') in g:g=g|{('D604','1')}
  expected.add(g)
 expected.add(frozenset({('D603','2'),('D604','2')}));assert after==expected
 # Negative control: an antiparallel diode error must fail the same partition comparison.
 wrong=set(after);g=next(x for x in wrong if ('D603','1') in x);wrong.remove(g);wrong.add((g-{('D603','1')})|{('D603','2')});assert wrong!=expected
 erc=lambda p:[v for s in json.loads(p.read_text())['sheets'] for v in s['violations']]
 assert erc(D/'before-erc.json')==erc(D/'after-erc.json');drc=json.loads((D/'after-drc.json').read_text());assert not drc['violations'] and not drc['unconnected_items']
 a,b=pymupdf.open(D/'before.pdf'),pymupdf.open(D/'after.pdf');assert len(a)==len(b)==18
 same=[i+1 for i in range(18) if a[i].get_pixmap().samples==b[i].get_pixmap().samples];assert same==[i for i in range(1,19) if i!=13]
 ha,hb=holes(D/'drill-before'),holes(D/'drill-after');removed=ha-hb;added=hb-ha
 assert removed==collections.Counter({(.8,131.,-60.):1,(.8,141.16,-60.):1}),removed
 wanted=collections.Counter({(.9,128.46,-60.):1,(.9,141.16,-60.):1,(.9,120.5,-42.5):1,(.9,133.2,-42.5):1,(.9,120.5,-46.5):1,(.9,133.2,-46.5):1});assert added==wanted,added
 out={'passed':True,'protected_other_native_files':protected,'native_connected_net_partitions':len(after),'explicit_delta_only':True,'antiparallel_negative_control_detected':True,'ERC_findings_unchanged':len(erc(D/'after-erc.json')),'Reverb_DRC':0,'Reverb_opens':0,'pixel_identical_pages':same,'unchanged_drill_hits':sum((ha&hb).values()),'new_round_diode_holes':4,'resized_round_resistor_holes':2,'added_45_style_tracks':len(addedtracks),'all_mounting_holes_outline_preserved':True,'native_integrated':True,'voltage_spacing_qualified':False,'fabricator_tolerance_confirmed':False,'hardware_qualified':False,'all_six_complete':False}
 out['artifact_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/x for x in receipt['changed_paths']]+[D/'after.xml',D/'after.pdf',D/'after-drc.json']}
 (D/'checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='artifact_sha256'},indent=2))
if __name__=='__main__':main()
