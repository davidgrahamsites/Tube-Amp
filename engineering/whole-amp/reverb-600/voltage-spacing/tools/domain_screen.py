#!/usr/bin/env python3
"""Rebase clamp-domain evidence and test stricter spacing without editing native CAD."""
import hashlib,importlib.util,itertools,json,math,re,shutil,subprocess,tempfile
from pathlib import Path
import numpy as np
import wx
APP=wx.App(False)
import pcbnew as p
M=Path(__file__).resolve().parents[1];ROOT=M.parents[3];O=M/'results';CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def scalar(s):
 n,k=re.fullmatch(r'([\d.]+)([Mkunp]?)',s).groups();return float(n)*{'':1,'M':1e6,'k':1e3,'u':1e-6,'n':1e-9,'p':1e-12}[k]
def main():
 c=json.loads((M/'domain-screen.json').read_text());source=ROOT/c['source'];target=ROOT/c['candidate'];parts={q['reference']:q for q in json.loads(source.read_text())['components']}
 checks={'candidate_revision':sha(target)==c['candidate_sha256'],'current_values_and_pin_maps':all(all(parts[r][k]==val for k,val in fields.items()) for r,fields in c['expected_parts'].items())};assert all(checks.values())
 factory=M.parent/'wet-protection/tools/analyze.py';spec=importlib.util.spec_from_file_location('wet_domain_model',factory);model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
 values={r:scalar(parts[r]['value']) for r in c['expected_parts'] if r[0] in 'RC'};refs=['R7','R43','R612','R24','R618','R617'];rows=[];errors=[]
 for signs in itertools.product([-1,1],repeat=6):
  r={**values,**{ref:values[ref]*(1+s*c['resistor_fraction']) for ref,s in zip(refs,signs)}}
  for supply,threshold in itertools.product(c['supply_V'],[None,*c['clamp_threshold_V']]):
   q=model.dc(r,supply,threshold,c['clamp_slope_ohm']);g={k:1/r[k] for k in refs}
   # Independent three-node KCL; active clamp branch adds conductance and threshold source.
   active=threshold is not None and model.dc(r,supply,None,c['clamp_slope_ohm'])['wet_V']>threshold;gc=1/c['clamp_slope_ohm'] if active else 0
   a=np.array([[g['R7']+g['R43']+g['R612'],-g['R612'],0],[-g['R612'],g['R612']+g['R24']+g['R618'],-g['R618']],[0,-g['R618'],g['R618']+g['R617']+gc]])
   v=np.linalg.solve(a,np.array([supply*g['R7'],0,gc*(threshold or 0)]));errors.append(max(abs(v[i]-q[k]) for i,k in enumerate(['fx_V','mix_V','wet_V'])))
   rows.append({'supply_V':supply,'signs':signs,'threshold_V':threshold,**q})
 clamped=[q for q in rows if q['threshold_V'] is not None];maxima={k:max(q[k] for q in clamped) for k in ['fx_V','mix_V','wet_V','R618_V']}
 checks['1024_cases']=len(rows)==1024;checks['independent_KCL']=max(errors)<1e-8
 checks['wet_to_minus15_below63V_screen']=maxima['wet_V']+15<63
 checks['dry_nodes_below400V_screen']=maxima['fx_V']<400 and maxima['mix_V']<400
 board=p.LoadBoard(str(target));pad=next(q for f in board.GetFootprints() if f.GetReference()=='C607' for q in f.Pads() if q.GetNumber()=='2')
 track=next(t for t in board.GetTracks() if t.m_Uuid.AsString()==c['local_repair']['items'][0])
 gap=abs(p.ToMM(track.GetStart().x-pad.GetPosition().x))-p.ToMM(pad.GetSize().x)/2-p.ToMM(track.GetWidth())/2
 checks['C607_gap_geometry']=pad.GetShape()==p.PAD_SHAPE_CIRCLE and track.GetStart().x==track.GetEnd().x and min(track.GetStart().y,track.GetEnd().y)<=pad.GetPosition().y<=max(track.GetStart().y,track.GetEnd().y) and math.isclose(gap,c['local_repair']['nominal_gap_mm'])
 checks['C607_nominal_gap_exceeds_wet_screen']=gap>=c['wet_clearance_mm']
 native=list((M.parent/'cad').glob('*.kicad_sch'))+list((M.parent.parent/'pcb-measured-r/boards').glob('*.kicad_pcb'));before={str(q.relative_to(ROOT)):sha(q) for q in native}
 base=target.with_suffix('.kicad_dru').read_text()
 def rule(name,nets,gap):
  condition=' || '.join(f"{side}.NetName == '{net}'" for side in ['A','B'] for net in nets)
  return f'\n(rule "{name}" (condition "{condition}") (constraint clearance (min {gap}mm)))\n'
 # KiCad evaluates later matching constraints first: stronger dry rule MUST be last.
 added=rule('VS002 protected wet screen',c['wet_nets'],c['wet_clearance_mm'])+rule('VS002 dry tube screen',c['dry_nets'],c['dry_clearance_mm'])
 (O/'domain-screen.kicad_dru').write_text(base+added)
 commands=[]
 prior=subprocess.check_output(['git','show',c['pre_repair_commit']+':'+c['candidate']],cwd=ROOT)
 checks['prior_candidate_revision']=hashlib.sha256(prior).hexdigest()==c['pre_repair_candidate_sha256']
 with tempfile.TemporaryDirectory(prefix='renegade-domain-screen-') as td:
  tmp=Path(td)
  for suffix in ['.kicad_pcb','.kicad_pro']:shutil.copyfile(target.with_suffix(suffix),tmp/(target.stem+suffix))
  table=(target.parent/'fp-lib-table').read_text();(tmp/'fp-lib-table').write_text(table.replace('${KIPRJMOD}',str(target.parent)))
  for name,rules in [('domain-before',base+added),('current',base),('domain',base+added)]:
   (tmp/target.name).write_bytes(prior if name=='domain-before' else target.read_bytes())
   (tmp/(target.stem+'.kicad_dru')).write_text(rules);cmd=[CLI,'pcb','drc','--format','json','--severity-all','--all-track-errors','-o',str(O/(name+'-screen-drc.json')),str(tmp/target.name)]
   run=subprocess.run(cmd,capture_output=True,text=True,timeout=180);assert run.returncode==0,run.stderr;commands.append({'command':cmd,'stdout':run.stdout,'stderr':run.stderr})
  checks['temporary_board_preserved']=sha(tmp/target.name)==sha(target)
 baseline=json.loads((O/'current-screen-drc.json').read_text());d=json.loads((O/'domain-screen-drc.json').read_text());checks['current_rule_receipt_zero']=not baseline['violations'] and not baseline['unconnected_items'];checks['domain_receipt_no_opens']=not d['unconnected_items']
 previous=json.loads((O/'domain-before-screen-drc.json').read_text())
 wet_findings=lambda report:[q for q in report['violations'] if 'VS002 protected wet screen' in q['description']]
 checks['local_wet_screen_findings_removed']=len(wet_findings(previous))==2 and not wet_findings(d)
 groups={};pairs=set()
 for q in d['violations']:
  name=q['description'].split("'")[1];groups[name]=groups.get(name,0)+1;pairs.add((q['type'],tuple(sorted(t['uuid'] for t in q['items']))))
 # Regression guard: a lower wet rule must not override dry/wet separation.
 protected_pair={'0ccc9b82-9394-44af-8c80-65721b6d6fea','6ab4ba42-b73a-4d00-9f91-932c25613662'}
 hits=[q for q in d['violations'] if {t['uuid'] for t in q['items']}==protected_pair]
 checks['stronger_dry_wet_pair_rule_wins']=len(hits)==1 and 'VS002 dry tube screen' in hits[0]['description'] and '2.5000 mm' in hits[0]['description']
 checks['native_files_unchanged']=all(sha(ROOT/p)==h for p,h in before.items());checks['candidate_unchanged']=sha(target)==c['candidate_sha256']
 outputs=[O/'domain-before-screen-drc.json',O/'current-screen-drc.json',O/'domain-screen-drc.json',O/'domain-screen.kicad_dru'];inputs=[M/'domain-screen.json',source,target,target.with_suffix('.kicad_dru'),target.with_suffix('.kicad_pro'),target.parent/'fp-lib-table',factory,Path(__file__)]
 result={'id':'VS-002','date':'2026-11-26','input_hashes':{str(q.relative_to(ROOT)):sha(q) for q in inputs},'output_hashes':{str(q.relative_to(ROOT)):sha(q) for q in outputs},'native_hashes':before,'checks':{k:bool(v) for k,v in checks.items()},'evidence_checks_pass':all(checks.values()),'maximum_KCL_error_V':max(errors),'clamped_node_maxima_V':maxima,'unclamped_wet_max_V':max(q['wet_V'] for q in rows if q['threshold_V'] is None),'cases':rows,'counts':{'reports':len(d['violations']),'unique_typed_pairs':len(pairs),'opens':len(d['unconnected_items']),'by_rule':groups},'commands':commands,'spacing_screen_pass':not d['violations'],'insulation_qualified':False,'native_adopted':False,'fabrication_ready':False}
 (O/'domain-screen.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['checks','clamped_node_maxima_V','counts','spacing_screen_pass']},indent=2));assert result['evidence_checks_pass']
if __name__=='__main__':main()
