"""Independent preservation checks against the immutable pre-package checkpoint."""
import copy,json,re,subprocess,xml.etree.ElementTree as ET,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5];MOD=Path(__file__).resolve().parents[1];OUT=MOD/'results';BASE='3efa8d9b53ab95ab312d7110e59168276e5308b3'
def old(path):return subprocess.check_output(['/usr/bin/git','show',BASE+':'+str(path.relative_to(ROOT))],cwd=ROOT).decode()
def parse(text):
 stack=[];root=[]
 for t in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',text):
  if t=='(':
   n=[]
   if stack:stack[-1].append(n)
   else:root.append(n)
   stack.append(n)
  elif t==')':stack.pop()
  else:stack[-1].append(t)
 assert not stack;return root[0]
def children(a,kind):return [x for x in a if isinstance(x,list) and x[0]==kind]
def field(a,kind):return children(a,kind)[0]
def fps(a):return {next(x[2].strip('"') for x in children(f,'property') if x[1]=='"Reference"'):f for f in children(a,'footprint')}
def nets(root):return {n.get('name'):sorted(tuple(sorted(x.attrib.items())) for x in n.findall('node')) for n in root.findall('./nets/net')}
def main():
 spec=json.loads((MOD/'package-contract.json').read_text());mapping={r:a for a in spec['parts'] for r in a['refs']};checks={}
 before=ET.parse(OUT/'before.xml').getroot();after=ET.parse(OUT/'after.xml').getroot()
 checks['native_named_nets_and_pins_identical']=nets(before)==nets(after)
 restored=copy.deepcopy(after);bc={x.get('ref'):x for x in before.findall('./components/comp')}
 for node in restored.findall('./components/comp'):
  ref=node.get('ref')
  if ref in mapping:
   assert node.findtext('footprint')=='Renegade_Selected:'+mapping[ref]['footprint']
   node.find('footprint').text=bc[ref].findtext('footprint')
   node.find('./fields/field[@name="Footprint"]').text=bc[ref].find('./fields/field[@name="Footprint"]').text
 checks['native_components_only_seven_footprints_changed']=ET.tostring(restored.find('components'))==ET.tostring(before.find('components'))
 source=ROOT/'engineering/whole-amp/reverb-600/circuit.json';a=json.loads(old(source));b=json.loads(source.read_text());prior={x['reference']:x for x in a['components']}
 for c in b['components']:
  if c['reference'] in mapping:
   assert c['footprint']=='Renegade_Selected:'+mapping[c['reference']]['footprint'];c['footprint']=prior[c['reference']]['footprint']
 checks['source_only_seven_footprint_fields_changed']=a==b
 for sheet in ['08_control_supply','07c_reverb_output']:
  path=source.parent/f'cad/{sheet}.kicad_sch';aa=parse(old(path));bb=parse(path.read_text())
  def syms(x):return {next(p[2].strip('"') for p in children(s,'property') if p[1]=='"Reference"'):s for s in children(x,'symbol')}
  aa_s=syms(aa);bb_s=syms(bb)
  for ref in mapping.keys() & bb_s.keys():
   af=next(p for p in children(aa_s[ref],'property') if p[1]=='"Footprint"');bf=next(p for p in children(bb_s[ref],'property') if p[1]=='"Footprint"');bf[2]=af[2]
  checks[sheet+'_only_hidden_footprints_changed']=aa==bb
 repair=json.loads((ROOT/'engineering/whole-amp/pcb-measured-r/review/panasonic-fr-route-repair.json').read_text());allowed={x['uuid']:x for x in repair['changes']}
 for name in ['Control','Reverb']:
  path=ROOT/f'engineering/whole-amp/pcb-measured-r/boards/Renegade_{name}.kicad_pcb';a=parse(old(path));b=parse(path.read_text());fa=fps(a);fb=fps(b)
  checks[name+'_same_references']=set(fa)==set(fb)
  checks[name+'_unaffected_footprints_exact']=all(fa[r]==fb[r] for r in fa if r not in mapping)
  for ref in mapping.keys() & fa.keys():
   aa=fa[ref];bb=fb[ref];s=mapping[ref]
   assert bb[1]=='"Renegade_Selected:'+s['footprint']+'"'
   assert field(aa,'at')==field(bb,'at') and field(aa,'path')==field(bb,'path')
   ap={x[1]:x for x in children(aa,'pad')};bp={x[1]:x for x in children(bb,'pad')};assert set(ap)==set(bp)=={'"1"','"2"'}
   for n,pad in bp.items():
    assert field(ap[n],'net')==field(pad,'net')
    assert float(field(pad,'drill')[1])==s['finished_hole_mm']
    assert float(field(pad,'at')[1])==(0 if n=='"1"' else s['pitch_mm'])
   checks[ref+'_position_polarity_pitch_drill']=True
  sa={field(t,'uuid')[1].strip('"'):t for t in children(a,'segment')};sb={field(t,'uuid')[1].strip('"'):t for t in children(b,'segment')};assert set(sa)==set(sb)
  changed=[]
  for key in sa:
   if sa[key]!=sb[key]:
    changed.append(key);assert key in allowed
    t=copy.deepcopy(sb[key]);coords=allowed[key]['after_mm']
    for kind,coord in zip(['start','end'],coords):
     f=field(t,kind);assert [float(x) for x in f[1:]]==coord;f[:]=field(sa[key],kind)
    assert t==sa[key]
  checks[name+'_only_reviewed_six_segment_endpoints_changed']=set(changed)==(set(allowed) if name=='Control' else set())
  checks[name+'_all_other_board_data_exact']=[x for x in a if not isinstance(x,list) or x[0] not in ['footprint','segment']]==[x for x in b if not isinstance(x,list) or x[0] not in ['footprint','segment']]
  for ext in ['.kicad_pro','.kicad_dru']:checks[name+ext+'_unchanged']=path.with_suffix(ext).read_text()==old(path.with_suffix(ext))
 before_d=json.loads((OUT/'before-native-summary.json').read_text());after_d=json.loads((OUT/'after-native-summary.json').read_text())
 for name in ['Control','Reverb']:
  checks[name+'_drc_no_regression']=before_d[name]['violations']==after_d[name]['violations'] and before_d[name]['unconnected']==after_d[name]['unconnected']
 a=json.loads((OUT/'before-erc.json').read_text());b=json.loads((OUT/'after-erc.json').read_text());a.pop('date',None);b.pop('date',None);checks['erc_unchanged']=a==b
 result=dict(baseline_commit=BASE,checks=checks,passed=all(checks.values()),current_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),fabrication_ready=False,limits=['234 existing unconnected items across four boards','68 missing wire courtyards','Socket choice, bypass loop placement and assembled chassis fit remain unqualified','No new electrical values or topology; package tests are not simulations'])
 (OUT/'integration-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert result['passed']
if __name__=='__main__':main()
