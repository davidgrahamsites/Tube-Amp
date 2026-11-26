"""Independent explicit-delta check of native connectivity, geometry and drills."""
from pathlib import Path
import collections,copy,hashlib,json,re,subprocess,sys,xml.etree.ElementTree as E
import pymupdf
M=Path(__file__).resolve().parents[1];ROOT=M.parents[3];D=M/'results'
sys.path.insert(0,str(ROOT/'engineering/whole-amp/tools'));import native_sexpr as n

def props(x):return {p[1].strip('"'):p for p in n.children(x,'property')}
def ref(x):return props(x)['Reference'][2].strip('"')
def objects(x,kind):return {n.field(p,'uuid')[1]:p for p in n.children(x,kind)}
def netpins(path):return {net.get('name'):{(x.get('ref'),x.get('pin')) for x in net.findall('node')} for net in E.parse(path).findall('nets/net')}
def identities(path):return {x.get('ref'):(x.findtext('value'),tuple(sorted(x.find('libsource').attrib.items())),tuple(y.text for y in x.findall('tstamps/tstamp'))) for x in E.parse(path).findall('components/comp')}
def holes(folder):
 hits=[]
 for p in folder.glob('*.drl'):
  tools={};tool=None
  for line in p.read_text().splitlines():
   m=re.fullmatch(r'T(\d+)C([\d.]+)',line)
   if m:tools[m[1]]=float(m[2]);continue
   m=re.fullmatch(r'T(\d+)',line)
   if m:tool=m[1];continue
   if line.startswith('X'):hits.append((p.name.split('-')[-1],tools[tool],line))
 return collections.Counter(hits)
def main():
 c=json.loads((M/'contract.json').read_text());receipt=json.loads((D/'integration.json').read_text());board=None;added_tracks=[]
 for path,h in c['native_sha256'].items():
  current=(ROOT/path).read_bytes();assert hashlib.sha256(current).hexdigest()==receipt['after_sha256'].get(path,h),path
  if path not in receipt['changed_paths']:continue
  old=subprocess.check_output(['git','show',c['baseline_commit']+':'+path],cwd=ROOT).decode()
  if path.endswith('.json'):
   a,b=json.loads(old),json.loads(current);ar={(x['reference'],x['unit']):x for x in a['components']};br={(x['reference'],x['unit']):x for x in b['components']}
   assert set(br)-set(ar)=={('R619',1),('R620',1)}
   for key,val in ar.items():
    if key!=('R601',1):assert br[key]==val,key
    else:
     assert br[key]['pins']==val['pins'] and br[key]['value']==val['value']
     assert br[key]['selected_mpn']==c['R601_mpn'] and br[key]['footprint']==c['resistor_footprint']
   for r,row in c['loads'].items():assert br[r,1]['pins']==row['pins'] and br[r,1]['value']=='10k' and br[r,1]['selected_mpn']==c['load_mpn']
  elif path.endswith('.kicad_sch'):
   a,b=n.parse(old),n.parse(current.decode());aa=objects(a,'symbol');bb=objects(b,'symbol')
   assert not set(aa)-set(bb)
   for uid,obj in aa.items():
    if ref(obj)=='R601':
     fixed=copy.deepcopy(bb[uid])
     for k in ['Footprint','Datasheet','Rating','Part_status']:props(fixed)[k][2]=props(obj)[k][2]
     assert fixed==obj
    else:assert bb[uid]==obj,ref(obj)
   # All existing local wires/labels/NCs/pins remain exactly as captured.
   for kind in ['wire','label','global_label','hierarchical_label','junction','no_connect','text']:
    aa,bb=objects(a,kind),objects(b,kind)
    for uid,obj in aa.items():assert bb[uid]==obj,(path,kind,uid)
  else:
   a,b=n.parse(old),n.parse(current.decode());board=b;fa={ref(x):x for x in n.children(a,'footprint')};fb={ref(x):x for x in n.children(b,'footprint')}
   assert set(fb)-set(fa)=={'R619','R620'} and not set(fa)-set(fb)
   for r,f in fa.items():
    if r!='R601':assert fb[r]==f,r
    else:
     for k in ['uuid','at','path']:assert n.field(f,k)==n.field(fb[r],k)
     pa,pb=n.children(f,'pad'),n.children(fb[r],'pad')
     for p,q in zip(pa,pb):
      for k in ['at','drill','net','uuid','size']:assert n.field(p,k)==n.field(q,k)
   for r in ['R601','R619','R620']:
    f=fb[r];assert f[1].strip('"')==c['resistor_footprint']
    for p in n.children(f,'pad'):assert n.field(p,'drill')[1:]==['0.8'] and p[2]=='thru_hole' and p[3]=='circle'
   for r,row in c['loads'].items():
    f=fb[r];assert list(map(float,n.field(f,'at')[1:]))==c['board_positions'][r]
    assert {p[1].strip('"'):n.field(p,'net')[1].strip('"') for p in n.children(f,'pad')}==row['pins']
   for kind in ['segment','arc','via','zone','gr_line','gr_rect','gr_arc','gr_circle']:
    aa,bb=objects(a,kind),objects(b,kind)
    for uid,obj in aa.items():assert bb[uid]==obj,(kind,uid)
    if kind=='segment':added_tracks=[bb[u] for u in set(bb)-set(aa)]
    else:assert set(bb)==set(aa),kind
   # Guard board setup, layers, outline, exclusions and all non-routing objects.
   omit={'footprint','segment','gr_text'}
   assert [x for x in a if not isinstance(x,list) or x[0] not in omit]==[x for x in b if not isinstance(x,list) or x[0] not in omit]
   ta,tb=objects(a,'gr_text'),objects(b,'gr_text');assert set(ta)==set(tb)
   changed=[u for u in ta if ta[u]!=tb[u]];assert len(changed)==1
   before_text,after_text=ta[changed[0]],tb[changed[0]]
   assert before_text[1]=='"+15 GND -15 +12 COIL"' and after_text[1]=='"JR6: +15 GND -15 +12 COIL"'
   copied=copy.deepcopy(after_text);copied[1]=before_text[1];n.field(copied,'at')[1:]=n.field(before_text,'at')[1:];assert copied==before_text
   assert len(added_tracks)==10
   for t in added_tracks:
    x,y=n.field(t,'start')[1:],n.field(t,'end')[1:];dx,dy=[abs(float(v)-float(w)) for v,w in zip(x,y)]
    assert dx==0 or dy==0 or abs(dx-dy)<1e-8
    assert n.field(t,'width')[1]=='0.3' and n.field(t,'net')[1] in ['"+15V"','"-15V"','"GND"']
   assert not n.children(b,'zone')
 before,after=netpins(D/'before.xml'),netpins(D/'after.xml');expected=copy.deepcopy(before)
 for r,row in c['loads'].items():
  for pin,net in row['pins'].items():expected[net].add((r,pin))
 assert after==expected
 corrupted=copy.deepcopy(after);corrupted['+15V'].remove(('R619','1'));corrupted['GND'].add(('R619','1'));assert corrupted!=expected
 ba,bb=identities(D/'before.xml'),identities(D/'after.xml');assert set(bb)-set(ba)=={'R619','R620'}
 assert all(bb[r]==v for r,v in ba.items())
 for r in c['loads']:assert bb[r][0]=='10k'
 erc=lambda p:[v for s in json.loads(p.read_text())['sheets'] for v in s['violations']]
 assert erc(D/'before-erc.json')==erc(D/'after-erc.json')
 drc=json.loads((D/'after-drc.json').read_text());assert not drc['violations'] and not drc['unconnected_items']
 a,b=pymupdf.open(D/'before.pdf'),pymupdf.open(D/'after.pdf');assert len(a)==len(b)==18
 same=[i+1 for i in range(18) if a[i].get_pixmap().samples==b[i].get_pixmap().samples];assert same==[i for i in range(1,19) if i!=13]
 ha,hb=holes(D/'drill-before'),holes(D/'drill-after');assert not ha-hb
 expectedholes=collections.Counter({('Renegade_Reverb.drl',.8,f'X{x}Y-{y}'):1 for x,y in [('125.5','5.0'),('135.66','5.0'),('125.5','9.0'),('135.66','9.0')]});assert hb-ha==expectedholes,hb-ha
 result={'passed':True,'existing_component_identities_preserved':len(ba),'added_components':2,'net_count':len(after),'explicit_net_delta_only':True,'negative_control_caught_wrong_rail':True,'pixel_identical_pages':same,'ERC_findings_unchanged':len(erc(D/'after-erc.json')),'Reverb_DRC':0,'Reverb_opens':0,'existing_drill_hits_unchanged':sum(ha.values()),'new_round_0_8mm_PTH':4,'unchanged_existing_tracks':len(n.children(board,'segment'))-10,'added_45_style_tracks':10,'provisional_finished_hole_min_mm':.7,'lead_max_mm':.6,'minimum_diametral_fit_allowance_mm':.1,'fabricator_tolerance_confirmed':False,'voltage_spacing_qualified':False,'whole_amp_qualified':False}
 result['artifact_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/x for x in receipt['changed_paths']]+[D/'after.xml',D/'after.pdf',D/'after-drc.json']}
 (D/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='artifact_sha256'},indent=2))
if __name__=='__main__':main()
