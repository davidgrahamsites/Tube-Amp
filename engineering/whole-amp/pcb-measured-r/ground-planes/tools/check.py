"""Independent native atom preservation and result gate for one declared pour."""
from pathlib import Path
import hashlib,json,subprocess,sys
M=Path(__file__).resolve().parents[1];ROOT=M.parents[3]
sys.path.insert(0,str(ROOT/'engineering/whole-amp/tools'));import native_sexpr as v
c=json.loads((M/'contract.json').read_text());target=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/c['target']
old=v.parse(subprocess.check_output(['git','show',c['baseline_commit']+':'+c['target']],cwd=ROOT,text=True));new=v.parse(target.read_text())
assert not v.children(old,'zone');zones=v.children(new,'zone');assert len(zones)==5
# Exact token identity preserves every pre-existing track/arc/pad/net/hole/property.
assert [x for x in new if not(isinstance(x,list) and x[0]=='zone')]==old
for path,h in c['native_sha256'].items():
 if path!=c['target']:assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
planes=[z for z in zones if not v.children(z,'keepout')];assert len(planes)==1;z=planes[0]
assert v.field(z,'net')[1]=='"GND"' and v.field(z,'layer')[1]=='"B.Cu"'
q=c['zone'];assert float(v.field(z,'min_thickness')[1])==q['min_thickness_mm']
connect=v.field(z,'connect_pads');assert float(v.field(connect,'clearance')[1])==q['clearance_mm']
fill=v.field(z,'fill');assert float(v.field(fill,'thermal_gap')[1])==q['thermal_gap_mm'];assert float(v.field(fill,'thermal_bridge_width')[1])==q['thermal_spoke_mm']
assert len(v.children(z,'filled_polygon'))==1
for a in zones:
 if a is z:continue
 assert v.field(a,'layer')[1]=='"B.Cu"';assert v.field(v.field(a,'keepout'),'copperpour')[1]=='not_allowed'
report=json.loads((M/'results/fill.json').read_text());h=hashlib.sha256(target.read_bytes()).hexdigest();assert report['input_sha256']==h and report['filled'] and not report['floating_island']
run=json.loads((M/'results/native-run.json').read_text());assert run['target_sha256']==h and run['inputs_unchanged'];assert run['output_sha256']['reverb-candidate-drc.json']==hashlib.sha256((M/'results/reverb-candidate-drc.json').read_bytes()).hexdigest()
d=json.loads((M/'results/reverb-candidate-drc.json').read_text());assert not d['violations'] and not d['unconnected_items']
checks={'geometry_preservation_checks_passed':True,'adoption_allowed':c['qualification']['adoption_allowed'],'voltage_domains_qualified':c['qualification']['voltage_domains_qualified'],'baseline_commit':c['baseline_commit'],'target_sha256':h,'all_existing_native_atoms_preserved':True,'unchanged_companion_files':len(c['native_sha256'])-1,'all_mount_holes_and_component_drills_preserved':True,'added_vias':0,'added_parts':0,'added_ground_planes':1,'added_mount_copper_exclusions':4,'native_DRC_violations':0,'native_unconnected':0,'fill_area_mm2':report['filled_area_mm2'],'EMI_and_ampacity_qualified':False,'whole_amp_qualified':False,'fabrication_ready':False}
(M/'results/checks.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
