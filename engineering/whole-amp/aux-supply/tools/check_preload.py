"""Independent scoped native-preservation, package and minimum-load checks."""
import copy,hashlib,json,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2];OUT=M/'results/preload'
sys.path.insert(0,str(M.parent/'tools'))
import native_sexpr as v
def load_bounds(c):
 delta=max(abs(t-c['reference_temperature_C']) for t in c['screen_temperature_C'])*c['tcr_per_C']
 tol=c['initial_tolerance_fraction']+delta+c['environmental_allowance_fraction']
 lo=c['value_ohm']*(1-tol)-c['environmental_allowance_absolute_ohm'];hi=c['value_ohm']*(1+tol)+c['environmental_allowance_absolute_ohm']
 minimum=c['rail_V'][0]/hi;maximum=c['rail_V'][1]/lo;power=c['rail_V'][1]**2/lo
 derated=c['power_W_at_70C']*(155-max(c['screen_temperature_C']))/(155-70)
 assert minimum>c['minimum_regulator_load_A']
 assert power<derated/2,'Require at least2x derated power margin for this preload'
 assert c['finished_hole_mm']-c['finished_hole_tolerance_mm']-c['lead_max_diameter_mm']>=0.2
 return dict(resistance_min_ohm=lo,resistance_max_ohm=hi,minimum_current_A=minimum,maximum_current_A=maximum,maximum_power_W=power,derated_power_at_125C_W=derated,minimum_diametric_hole_clearance_mm=c['finished_hole_mm']-c['finished_hole_tolerance_mm']-c['lead_max_diameter_mm'])
def main():
 c=json.loads((M/'preload-contract.json').read_text());checks={};bounds=load_bounds(c)
 before=ET.parse(OUT/'before.xml').getroot();after=ET.parse(OUT/'after.xml').getroot();a=v.nets(before);b=v.nets(after)
 r=next(x for x in after.findall('./components/comp') if x.get('ref')=='R215');assert r.findtext('value')=='820'
 after.find('components').remove(r);checks['all_prior_exported_components_unchanged']=ET.tostring(before.find('components'))==ET.tostring(after.find('components'))
 changed={n for n in b if a.get(n)!=b[n]};assert changed=={'+5V','GND'}
 for n,pin in [('+5V','1'),('GND','2')]:
  added=[dict(x) for x in b[n] if x not in a[n]];assert len(added)==1 and added[0]['ref']=='R215' and added[0]['pin']==pin
  b[n]=[x for x in b[n] if dict(x).get('ref')!='R215']
 checks['native_only_new_pins_R215_1_to_5V_2_to_GND']=a==b
 def old(p):return subprocess.check_output(['/usr/bin/git','show',c['baseline_commit']+':'+p],cwd=ROOT).decode()
 p='engineering/whole-amp/reverb-600/circuit.json';source=json.loads((ROOT/p).read_text());prior=json.loads(old(p));row=source['components'].pop();assert row['reference']=='R215' and row['pins']=={'1':'+5V','2':'GND'};checks['source_only_R215_added']=source==prior
 p='engineering/whole-amp/pcb-measured-r/boards/Renegade_Control.kicad_pcb';aa=v.parse(old(p));bb=v.parse((ROOT/p).read_text());fa=v.fps(aa);fb=v.fps(bb);assert set(fb)-set(fa)=={'R215'}
 checks['all_prior_footprints_unchanged']=all(fa[k]==fb[k] for k in fa)
 prior_other=[x for x in aa[1:] if not isinstance(x,list) or x[0]!='footprint'];new_other=[x for x in bb[1:] if not isinstance(x,list) or x[0]!='footprint'];checks['all_prior_board_data_unchanged']=new_other[:len(prior_other)]==prior_other
 tracks=new_other[len(prior_other):];assert len(tracks)==6 and all(x[0]=='segment' for x in tracks)
 for t in tracks:
  p1=list(map(float,v.field(t,'start')[1:]));p2=list(map(float,v.field(t,'end')[1:]));dx,dy=[abs(x-y) for x,y in zip(p1,p2)]
  assert min(dx,dy)<1e-8 or abs(dx-dy)<1e-8
  assert float(v.field(t,'width')[1])==0.4
 # Every new pad is physically connected to its corresponding U5 pad by new copper.
 for net,start,end in [('"+5V"',(196.654,75.5),(196.654,68.125)),('"GND"',(209.354,75.5),(194.114,68.125))]:
  edges=[(tuple(map(float,v.field(t,'start')[1:])),tuple(map(float,v.field(t,'end')[1:]))) for t in tracks if v.field(t,'net')[1]==net];seen={start}
  for _ in range(len(edges)):
   for x,y in edges:
    if x in seen:seen.add(y)
    if y in seen:seen.add(x)
  assert end in seen
 checks['new_tracks_connect_to_U5_and_use_HV45']=True
 for pad,net in zip(v.children(fb['R215'],'pad'),['"+5V"','"GND"']):assert v.field(pad,'net')[1]==net and float(v.field(pad,'drill')[1])==0.9 and pad[2:4]==['thru_hole','circle']
 checks['R215_two_round_PTH_0p9mm']=True
 for kind in ['erc','drc']:
  a=json.loads((OUT/f'before-{kind}.json').read_text());b=json.loads((OUT/f'after-{kind}.json').read_text());a.pop('date',None);b.pop('date',None)
  if kind=='erc':checks['erc_unchanged']=a==b
  else:
   checks['drc_existing_violations_unchanged']=a['violations']==b['violations'];checks['unconnected_count_unchanged']=len(a['unconnected_items'])==len(b['unconnected_items'])==90
 # The old native schematic tree must survive exactly, with one library symbol and seven objects added.
 p='engineering/whole-amp/reverb-600/cad/08_control_supply.kicad_sch';sa=v.parse(old(p));sb=v.parse((ROOT/p).read_text());sb=copy.deepcopy(sb)
 libs=v.field(sb,'lib_symbols');newlib=next(x for x in v.children(libs,'symbol') if x[1]=='"Renegade_Draft:Device_R"');libs.remove(newlib)
 assert sb[:len(sa)]==sa,'Existing schematic tree changed'
 assert len(sb)-len(sa)==7
 checks['existing_schematic_geometry_and_metadata_unchanged']=True
 raw=json.loads((OUT/'raw-screen.json').read_text());base=json.loads((M/'results/envelope/screen.json').read_text())
 assert len(raw['cases'])==72 and len(raw['refinements'])>=2
 assert raw['circuit_sha256']==hashlib.sha256((M.parent/'reverb-600/circuit.json').read_bytes()).hexdigest()
 assert raw['preload_contract_sha256']==hashlib.sha256((M/'preload-contract.json').read_bytes()).hexdigest()
 for prior,current in zip(base['cases'],raw['cases']):
  expected=copy.deepcopy(prior['case']);expected['id']+='-R215';expected['load']['logic_5V_A']+=bounds['maximum_current_A']
  assert current['case']==expected
  assert current['completed_time_s']>=.6-1e-9 and current['kcl_max_error_A']<1e-5
  assert 'U5_below_minimum_regulation_load' not in current['screen_flags']
  assert hashlib.sha256(raw['decks'][expected['id']].encode()).hexdigest()==current['deck_sha256']
 for r in raw['refinements']:assert r['positive_min_delta_V']<.01 and r['winding_rms_relative_delta']<.005
 checks['72_updated_raw_supply_runs_and_refinements_checked']=True
 # Meaningful negative controls: wrong resistor and undersized finished hole must fail.
 rejected=[]
 for label,key,value in [('1k_insufficient_load','value_ohm',1000),('hole_too_small','finished_hole_mm',0.7)]:
  bad=copy.deepcopy(c);bad[key]=value
  try:load_bounds(bad)
  except AssertionError:rejected.append(label)
  else:raise AssertionError(label+' escaped')
 assert all(checks.values()),checks
 report=dict(passed=True,checks=checks,bounds=bounds,negative_controls_rejected=rejected,circuit_sha256=hashlib.sha256((M.parent/'reverb-600/circuit.json').read_bytes()).hexdigest(),fabrication_ready=False)
 (OUT/'checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
