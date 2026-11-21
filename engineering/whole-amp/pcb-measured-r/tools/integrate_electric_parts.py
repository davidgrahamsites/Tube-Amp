"""Apply November21 exact packages to the existing draft; preserve pad nets.
Pre-edit native revision is tracked in Git7116898. Do not rerun after edits.
"""
from pathlib import Path
import hashlib
import json
import pcbnew as p

ROOT=Path(__file__).resolve().parents[1]
SEL=ROOT.parents[1]/'component-selection'
LIB=SEL/'footprints/Renegade_Selected.pretty'
MAPPING={
 'C301':'KNSCHA_MEB105J63V82CB0235','C311':'KNSCHA_MEB105J63V82CB0235',
 'C351':'KNSCHA_MEB104J63V82CB0236','C352':'KNSCHA_MEB104J63V82CB0236','C353':'KNSCHA_MEB104J63V82CB0236',
 'R1':'Tyohm_RN_halfWS_68K_P10.16','R43':'Yageo_HHV1WS_10M_P17.78','R24':'Yageo_HHV1WS_10M_P17.78',
 'R38':'Vishay_PR01_22K_P12.7','C505':'Aishi_EGW2CM470G16OT_D10.5_P5','D7':'Onsemi_1N4007RLG_P10.16'}
selected={r:c['selected_mpn'] for c in json.loads((SEL/'coverage.json').read_text()) if c.get('selected_mpn') for r in c['refs']}
KEEP=[];io=p.PCB_IO_KICAD_SEXPR();reports={};changed=set()
out=ROOT/'review/electric-package-integration.json'
assert not out.exists(),'Already integrated; preserve later native edits'
for name in ['Main','Power','Control']:
 path=ROOT/f'boards/Renegade_{name}.kicad_pcb'
 before=hashlib.sha256(path.read_bytes()).hexdigest()
 b=p.LoadBoard(str(path));KEEP.append(b);fps=list(b.GetFootprints());KEEP.extend(fps)
 changes=[];affected=set()
 for old in fps:
  ref=old.GetReference()
  if ref not in MAPPING:continue
  f=io.FootprintLoad(str(LIB),MAPPING[ref]);KEEP.append(f)
  oldpads={q.GetNumber():q for q in old.Pads()};newpads={q.GetNumber():q for q in f.Pads()}
  assert set(oldpads)==set(newpads)=={'1','2'}
  f.SetReference(ref);f.SetValue(old.GetValue());f.SetPosition(old.GetPosition());f.SetOrientationDegrees(old.GetOrientationDegrees());f.SetPath(old.GetPath())
  f.SetFPID(p.LIB_ID('Renegade_Selected',MAPPING[ref]));f.SetField('Selected_MPN',selected[ref]);f.SetField('Status','DRAFT: native DRC and assembled fit required')
  f.Value().SetVisible(False)
  for fld in f.GetFields():
   if fld.GetName() not in ['Reference','Value']:fld.SetVisible(False)
  for num,pad in newpads.items():pad.SetNet(oldpads[num].GetNet());affected.add(oldpads[num].GetNetCode())
  changes.append({'ref':ref,'mpn':selected[ref],'from':str(old.GetFPID()),'to':MAPPING[ref]})
  b.Remove(old);b.Add(f);changed.add(ref)
 tracks=list(b.GetTracks());KEEP.extend(tracks);removed=0
 for t in tracks:
  if t.GetNetCode() in affected:b.Remove(t);removed+=1
 p.SaveBoard(str(path),b)
 reports[name]={'before_sha256':before,'after_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'changes':changes,'removed_affected_track_items':removed,'unreleased':True}
assert changed==set(MAPPING),(changed,set(MAPPING)-changed)
out.write_text(json.dumps({'baseline_git':'7116898','scope':'Exact packages on current incomplete outlines; neither completed routing nor cabinet-fit approval','boards':reports},indent=2)+'\n')
print('Integrated',len(changed),'exact packages; reroute and DRC required.')
