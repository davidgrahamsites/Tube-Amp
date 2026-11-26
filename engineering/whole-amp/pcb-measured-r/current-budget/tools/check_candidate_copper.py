#!/usr/bin/env python3
"""Audit native widths/thickness and calculate bounded wet-control DC losses."""
import collections,hashlib,json,math,sys
from pathlib import Path
import wx
APP=wx.App(False)
import pcbnew as p
M=Path(__file__).resolve().parents[1];ROOT=M.parents[3]
sys.path.insert(0,str(M.parent/'tools'))
from integrate_socket_footprints import spans
import native_sexpr as sx
H=M.parent.parent/'harness-integration';C=H/'reverb-connector-placement.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def mm(n):return p.ToMM(n)
def rho_at(temperature_C):
 return 1.724e-8*(1+.00393*(temperature_C-20))
def resistance(length_mm,width_mm,thickness_um,temperature_C):
 assert length_mm>=0 and width_mm>0 and thickness_um>0
 return rho_at(temperature_C)*length_mm*1e-3/(width_mm*1e-3*thickness_um*1e-6)
def main():
 c=json.loads(C.read_text());construction=c['construction'];candidate=H/'results/reverb-connector-candidate/Renegade_Reverb.kicad_pcb'
 circuit=ROOT/'engineering/whole-amp/reverb-600/circuit.json';parts={x['reference']:x for x in json.loads(circuit.read_text())['components']}
 old=json.loads((M/'contract.json').read_text());checks={'native_load_values_unchanged':all(all(parts[r].get(k)==v for k,v in a.items()) for r,a in old['expected_parts'].items()),'pot_value_and_map':parts['RV602']['value']=='100k LOG REVERB' and parts['RV602']['pins']=={'1':'WET_TOP','2':'WET_W','3':'GND'}}
 # A forced 18 V peak source and both shunts simultaneously at their lowest values
 # overbound the normal passive pot load. This is not a startup/short-circuit bound.
 shunt_peak=18/old['pot_total_low_ohm']+18/(1e6*(1-old['resistor_low_fraction']))
 screen_A=.00025;temperature_C=70;drop_limit_V=.0001
 checks['declared_current_covers_resistor_load']=shunt_peak<screen_A
 width_factor=1-construction['negative_width_tolerance_fraction'];thick=construction['outer_copper_minimum_finished_um_required']
 board=p.LoadBoard(str(candidate));nets={};all_tracks=list(board.GetTracks())
 for net,width in c['existing_net_widths_mm'].items():
  tracks=[t for t in all_tracks if not isinstance(t,p.PCB_VIA) and t.GetNetname()==net];vias=[t for t in all_tracks if isinstance(t,p.PCB_VIA) and t.GetNetname()==net]
  rows=[{'length_mm':mm(t.GetLength()),'drawn_width_mm':mm(t.GetWidth()),'layer':board.GetLayerName(t.GetLayer()),'resistance_ohm':resistance(mm(t.GetLength()),mm(t.GetWidth())*width_factor,thick,temperature_C)} for t in tracks]
  vr=[]
  for t in vias:
   d=mm(t.GetDrillValue())-.08;plate=construction['via_barrel_minimum_um_required']/1000
   area=math.pi*((d/2+plate)**2-(d/2)**2)
   r=rho_at(temperature_C)*(1.76e-3)/(area*1e-6)
   vr.append({'drill_nominal_mm':mm(t.GetDrillValue()),'finished_hole_minimum_assumed_mm':d,'barrel_area_mm2':area,'resistance_ohm':r})
  pads=[]
  for f in board.GetFootprints():
   for q in f.Pads():
    if q.GetNetname()!=net:continue
    drill=max(mm(q.GetDrillSize().x),mm(q.GetDrillSize().y));size=min(mm(q.GetSize().x),mm(q.GetSize().y))
    pads.append({'reference':f.GetReference(),'pin':q.GetNumber(),'pad_minimum_dimension_mm':size,'hole_nominal_mm':drill,'nominal_radial_ring_mm':(size-drill)/2 if drill else None,'qualified':False})
  total=sum(x['resistance_ohm'] for x in rows)+sum(x['resistance_ohm'] for x in vr)
  checks[net+'_all_segments_wide']=bool(rows) and all(abs(x['drawn_width_mm']-width)<1e-6 for x in rows)
  checks[net+'_track_via_drop_screen']=screen_A*total<=drop_limit_V
  nets[net]={'tracks':rows,'vias':vr,'pads':pads,'track_via_resistance_sum_ohm':total,'track_via_peak_drop_V':screen_A*total,'track_via_loss_W_at_screen_current':screen_A**2*total,'track_length_sum_mm':sum(x['length_mm'] for x in rows),'pad_contact_harness_resistance_included':False}
 inventory={}
 for path in sorted((M.parent/'boards').glob('*.kicad_pcb')):
  b=p.LoadBoard(str(path));data=collections.defaultdict(lambda:{'widths_mm':set(),'track_count':0,'via_count':0})
  for t in b.GetTracks():
   q=data[t.GetNetname()]
   if isinstance(t,p.PCB_VIA):q['via_count']+=1
   else:q['widths_mm'].add(round(mm(t.GetWidth()),6));q['track_count']+=1
  for f in b.GetFootprints():
   for pad in f.Pads():
    if pad.GetNetname():data[pad.GetNetname()]
  root=sx.parse(path.read_text());setup=sx.field(root,'setup');stack=next((n for n in setup[1:] if n[0]=='stackup'),None)
  inventory[path.stem]={'sha256':sha(path),'explicit_stackup_present':stack is not None,'nets':{n:{**q,'widths_mm':sorted(q['widths_mm']),'current_thermal_fault_qualification':'pending'} for n,q in sorted(data.items())}}
 controls={'double_width_halves_R':math.isclose(resistance(100,.6,30,70)*2,resistance(100,.3,30,70)), 'double_thickness_halves_R':math.isclose(resistance(100,.3,60,70)*2,resistance(100,.3,30,70)), '20_percent_narrowing_increases_R_25_percent':math.isclose(resistance(100,.24,30,70)/resistance(100,.3,30,70),1.25),'unit_reference':math.isclose(resistance(100,1,35,20),.04925714285714285),'thin_copper_failed_screen':all(screen_A*sum(resistance(x['length_mm'],x['drawn_width_mm']*width_factor,1,temperature_C) for x in n['tracks'])>drop_limit_V for n in nets.values())}
 inputs=[C,candidate,circuit,M/'contract.json',Path(__file__)]
 result={'id':'CU-001','scope':'HI-008 wet-control DC geometry screen plus all-active-board inventory','input_hashes':{str(x.relative_to(ROOT)):sha(x) for x in inputs},'construction':construction,'conditions':{'forced_source_peak_V':18,'resistor_load_bound_A':shunt_peak,'screen_current_A':screen_A,'temperature_C_assumed':temperature_C,'track_via_peak_drop_limit_V':drop_limit_V,'normal_bias_current_allowance_A':screen_A-shunt_peak,'thermal_rise_qualified':False,'fault_or_startup_bound':False},'candidate_nets':nets,'active_boards':inventory,'checks':checks,'controls':controls,'evidence_checks_pass':all(checks.values()) and all(controls.values()),'fab_confirmed':False,'fabrication_ready':False,'limits':['70 C is an assumed copper temperature for resistance, not a predicted operating temperature.','18 V peak is a diagnostic excitation, not guaranteed op-amp swing.','Minimum foil and barrel thickness need fabricator acceptance; JLC publishes average barrel thickness only.','Pad/contact/harness losses, mutual coupling, peak transients, shorts and thermal rise remain unqualified.','Net length sums overbound track resistance when branches are parallel; this is not source-to-load extraction.','Other nets and boards require their own budgets; no heater, supply or shared-return current qualification follows.']}
 (M/'results/candidate-copper.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'checks':checks,'controls':controls,'nets':{k:{f:q[f] for f in ('track_length_sum_mm','track_via_resistance_sum_ohm','track_via_peak_drop_V')} for k,q in nets.items()},'inventory_board_count':len(inventory)},indent=2));assert result['evidence_checks_pass']
if __name__=='__main__':main()
