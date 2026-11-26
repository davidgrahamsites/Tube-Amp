#!/usr/bin/env python3
"""Recompute source-bounded loads and check complete candidate supply-net copper."""
import json,math
from pathlib import Path
from check_candidate_copper import M,ROOT,H,C,p,mm,rho_at,resistance,sha
from analyze import calculate,scalar,measurement_sha

def main():
 spec=json.loads((M/'supply-copper.json').read_text());placement=json.loads(C.read_text());construction=placement['construction'];legacy=json.loads((M/'contract.json').read_text())
 source=ROOT/legacy['source'];components=json.loads(source.read_text())['components'];parts={q['reference']:q for q in components}
 checks={'passive_values_and_pins_match':all(all(parts[r].get(k)==v for k,v in e.items()) for r,e in legacy['expected_parts'].items())}
 for ref,pins in spec['opamp_combined_pins'].items():
  units=[q for q in components if q['reference']==ref];merged={k:v for q in units for k,v in q['pins'].items()}
  checks[ref+'_identity_and_complete_pin_map']=len(units)==3 and all(q['value']=='OPA2134PA' for q in units) and merged==pins
 checks['rail_shunts']=parts['R619']['value']==parts['R620']['value']=='10k' and parts['R619']['pins']=={'1':'+15V','2':'GND'} and parts['R620']['pins']=={'1':'GND','2':'-15V'}
 checks['pots']=all(parts[r]['value'].startswith('100k ') for r in ['RV601','RV602'])
 assert all(checks.values()),checks
 measured=json.loads((ROOT/legacy['tank_source']).read_text())['tank_received']['electrical_measurements']
 values={r:scalar(parts[r]['value']) for r in legacy['expected_parts']}
 loads=calculate(legacy,values,measured);max_load=max(q['each_rail_conditional_A'] for q in loads['cases']);current=spec['screen_current_A'];temperature=spec['copper_temperature_C'];limit=spec['track_via_drop_limit_V'];margin=spec['minimum_finished_width_margin']
 checks['recomputed_diagnostic_load_covered']=max_load<=current
 # Independent series-RLC resonance check on all cases, without trusting a green old receipt.
 checks['resonance_maxima']=all(math.isclose(q['tank']['rms_A'],q['output_peak_V']/((values['R605']*(1-legacy['resistor_low_fraction'])+measured['input_DC_resistance_ohm']*(1-legacy['driver_Rdc_low_fraction_screen']))*math.sqrt(2)),rel_tol=1e-10) for q in loads['cases'])
 candidate=H/'results/reverb-connector-candidate/Renegade_Reverb.kicad_pcb';b=p.LoadBoard(str(candidate));factor=1-construction['negative_width_tolerance_fraction'];thick=construction['outer_copper_minimum_finished_um_required'];plate=construction['via_barrel_minimum_um_required']/1000;results={}
 for net in spec['nets']:
  tracks=[t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetNetname()==net];vias=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()==net]
  lengths=[mm(t.GetLength()) for t in tracks];widths=[mm(t.GetWidth()) for t in tracks];length=sum(lengths);via_r=0
  for v in vias:
   d=mm(v.GetDrillValue())-.08;area=math.pi*((d/2+plate)**2-(d/2)**2);via_r+=rho_at(temperature)*.00176/(area*1e-6)
  remaining_r=limit/current-via_r;assert remaining_r>0
  required_finished_mm=rho_at(temperature)*length*1e-3/(thick*1e-6*remaining_r)*1000
  ratio=min(widths)*factor/required_finished_mm
  r=sum(resistance(l,w*factor,thick,temperature) for l,w in zip(lengths,widths))+via_r
  comparisons=[{'drawn_width_mm':w,'track_via_drop_V':current*(resistance(length,w*factor,thick,temperature)+via_r),'finished_width_margin':w*factor/required_finished_mm} for w in [.3,.6,.8,1.0]]
  checks[net+'_native_width']=all(math.isclose(w,placement['existing_net_widths_mm'][net]) for w in widths)
  checks[net+'_drop']=r*current<=limit
  checks[net+'_finished_width_margin']=ratio>=margin
  results[net]={'track_count':len(tracks),'via_count':len(vias),'track_length_sum_mm':length,'drawn_widths_mm':sorted(set(widths)),'via_resistance_sum_ohm':via_r,'minimum_finished_width_from_drop_mm':required_finished_mm,'minimum_drawn_width_with_margin_mm':required_finished_mm*margin/factor,'actual_finished_width_margin':ratio,'track_via_resistance_sum_ohm':r,'track_via_drop_V':current*r,'track_via_loss_W_at_screen_current':current**2*r,'comparisons':comparisons}
 controls={'old_0p3mm_rejected':all(q['comparisons'][0]['track_via_drop_V']>limit for q in results.values()),'0p6mm_fails_margin_on_at_least_one_rail':any(q['comparisons'][1]['finished_width_margin']<margin for q in results.values()),'narrow_arc_rejected':.3*factor/results['+15V']['minimum_finished_width_from_drop_mm']<margin,'halved_thickness_rejected':all(current*(resistance(q['track_length_sum_mm'],.8*factor,thick/2,temperature)+q['via_resistance_sum_ohm'])>limit for q in results.values())}
 drc=H/'results/reverb-connector-candidate/drc.json';d=json.loads(drc.read_text());checks['native_drc_zero']=not d['violations'] and not d['unconnected_items']
 inputs=[M/'supply-copper.json',M/'contract.json',C,candidate,source,M/'tools/analyze.py',M/'tools/check_candidate_copper.py',Path(__file__),drc]
 output={'id':'CU-002','input_hashes':{str(x.relative_to(ROOT)):sha(x) for x in inputs},'load_rebase':{'method':'Recomputed current source passive values, complete opamp pin maps and measured tank seam using the retained pure model; old whole-source SHA is historical.','old_contract_whole_source_matches':sha(source)==legacy['source_sha256'],'tank_measurement_sha256':measurement_sha(measured),'cases':loads['case_count'],'each_rail_max_A_by_output':{str(v):max(q['each_rail_conditional_A'] for q in loads['cases'] if q['output_peak_V']==v) for v in legacy['opamp_output_peak_V']},'maximum_KCL_residual_A_per_V':loads['maximum_KCL_residual_A_per_V']},'conditions':spec,'rails':results,'checks':checks,'controls':controls,'evidence_checks_pass':all(checks.values()) and all(controls.values()),'rejected_width_trial':{'drawn_width_mm':1.0,'straight_segments_only':True,'clearance_findings':10,'missed_arc_trial':{'count':4,'net':'+15V','drawn_width_mm':0.3,'detected_by':'Native width rule and independent whole-net minimum-width/margin checks; repaired before acceptance'},'note':'Initial temporary export also lacked its library table (41 configuration warnings); table restored before accepted0.8mm test. Neither kind of finding was waived.'},'thermal_fault_qualified':False,'fabrication_ready':False}
 (M/'results/supply-copper.json').write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps({'checks':checks,'controls':controls,'rails':{k:{x:v[x] for x in ['track_count','track_length_sum_mm','track_via_drop_V','minimum_drawn_width_with_margin_mm','actual_finished_width_margin']} for k,v in results.items()}},indent=2));assert output['evidence_checks_pass']
if __name__=='__main__':main()
