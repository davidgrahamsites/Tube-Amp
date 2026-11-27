#!/usr/bin/env python3
"""Measure declared broadening; compare copper resistance without claiming capacity."""
import collections,json,math
from check_candidate_copper import M,ROOT,H,C,p,mm,resistance,sha

def inventory(board,nets,construction):
 out={};factor=1-construction['negative_width_tolerance_fraction'];thick=construction['outer_copper_minimum_finished_um_required']
 for net in nets:
  ts=[t for t in board.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetNetname()==net]
  out[net]={'segments_and_arcs':len(ts),'length_sum_mm':sum(mm(t.GetLength()) for t in ts),'drawn_widths_mm':sorted(set(round(mm(t.GetWidth()),6) for t in ts)),'track_resistance_sum_ohm':sum(resistance(mm(t.GetLength()),mm(t.GetWidth())*factor,thick,70) for t in ts)}
 return out

def main():
 c=json.loads(C.read_text());src=ROOT/c['baseline_board'];target=H/'results/reverb-connector-candidate'/src.name
 nets=['+12V','COIL_REV','DRIVER','DRIVE_CAP','TANK_IN','SEND_BUF','REC_OUT','WET_BUF','SUM_INV','OUT_BUF','OUT_AC','GND']
 before=inventory(p.LoadBoard(str(src)),nets,c['construction']);after=inventory(p.LoadBoard(str(target)),nets,c['construction'])
 checks={'source_revision':sha(src)==c['baseline_sha256'],'coverage':set(before)==set(after)==set(nets)}
 for n in nets:checks[n+'_lower_track_resistance_sum']=after[n]['track_resistance_sum_ohm']<before[n]['track_resistance_sum_ohm']
 circuit=M.parent.parent/'reverb-600/circuit.json';parts=json.loads(circuit.read_text())['components']
 # Identify driven audio nodes from actual op-amp output pins, not their names.
 output_nets={q['pins'][pin] for q in parts if q['reference'] in ['U10','U11','U12'] for pin in ['1','7'] if pin in q['pins']}
 checks['widened_direct_audio_nodes_are_opamp_outputs']=set(['DRIVER','SEND_BUF','REC_OUT','WET_BUF','SUM_INV','OUT_BUF'])<=output_nets
 expected_R616=next(q for q in parts if q['reference']=='R616')
 checks['OUT_AC_is_series_output']=expected_R616['pins']=={'1':'OUT_BUF','2':'OUT_AC'} and expected_R616['value']=='100'
 audit=H/'results/reverb-connector-candidate/checks.json';native=json.loads(audit.read_text())
 checks['native_receipt_current']=native['input_hashes'][str(target.relative_to(ROOT))]==sha(target) and native['input_hashes'][str(C.relative_to(ROOT))]==sha(C)
 checks['native_delta_and_drc_pass']=native['evidence_checks_pass']
 # Independent geometric tolerance arithmetic, not a predicted temperature rise.
 controls={'twice_width_halves_R':math.isclose(resistance(10,.8,30,70)*2,resistance(10,.4,30,70)), 'thin_foil_raises_R':resistance(10,.8,15,70)>resistance(10,.8,30,70),'short_45_degree_length':math.isclose(math.hypot(.5,.5),math.sqrt(.5))}
 rows={n:{'before':before[n],'after':after[n],'reduction_percent':100*(1-after[n]['track_resistance_sum_ohm']/before[n]['track_resistance_sum_ohm'])} for n in nets}
 result={'id':'CU-003','date':'2026-11-26','input_hashes':{str(q.relative_to(ROOT)):sha(q) for q in [src,target,C,circuit,audit,Path(__file__),M/'tools/check_candidate_copper.py']},'conditions':{'copper_temperature_C_assumed':70,'finished_foil_minimum_um_required':c['construction']['outer_copper_minimum_finished_um_required'],'negative_width_tolerance_fraction':c['construction']['negative_width_tolerance_fraction'],'same_construction_for_both_boards':True},'nets':rows,'local_necks':c['existing_item_overrides'],'checks':checks,'controls':controls,'evidence_checks_pass':all(checks.values()) and all(controls.values()),'thermal_fault_qualified':False,'fabrication_ready':False,'limits':['Resistance is the sum of every track on each net, not a solved source-to-load or shared-ground transfer impedance.','Vias, pad rings, connector contacts, harnesses and return-loop interactions are excluded here; rail/wet calculations retain their own scopes.','These widths add geometric margin; this comparison does not establish maximum continuous, peak, startup or fault current.','Sensitive input/feedback and tube-interface routes remain for separate clearance/loading review.','The 70 C calculation temperature is assumed, not predicted or measured.']}
 (M/'results/broad-copper.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'checks':checks,'controls':controls,'reductions_percent':{n:round(v['reduction_percent'],2) for n,v in rows.items()}},indent=2));assert result['evidence_checks_pass']
if __name__=='__main__':
 from pathlib import Path
 main()
