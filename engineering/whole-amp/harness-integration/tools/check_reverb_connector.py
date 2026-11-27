#!/usr/bin/env python3
"""Check a candidate's native delta, DRC and nominal plug reserve; never release it."""
import collections,hashlib,json,math,subprocess,sys
from pathlib import Path
import wx
APP=wx.App(False)
import pcbnew as p
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2];O=M/'results/reverb-connector-candidate'
sys.path.insert(0,str(M.parent/'pcb-measured-r/tools'))
from integrate_socket_footprints import spans
import native_sexpr as v
from integrate_drivers import prop
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def xy(a):return [round(p.ToMM(a.x),6),round(p.ToMM(a.y),6)]
def atoms(path,kind):
 text=path.read_text();return [text[a:z] for a,z in spans(text,kind)]
def uid(raw):return v.field(v.parse(raw),'uuid')[1].strip('"')
def named(path,kind):return {uid(raw):raw for raw in atoms(path,kind)}
def ref(raw):return prop(v.parse(raw),'Reference')[2].strip('"')
def close(a,b):return abs(a-b)<1e-6

def main():
 c=json.loads((M/'reverb-connector-placement.json').read_text());h=json.loads((M/'mating-geometry.json').read_text());w=json.loads((M/'wire-dressing.json').read_text());src=ROOT/c['baseline_board'];target=O/src.name
 checks={};checks['source_revision']=sha(src)==c['baseline_sha256']
 for kind in ['footprint','gr_text','segment','arc','via']:
  a,b=named(src,kind),named(target,kind)
  changed={u for u in a if u not in b or a[u]!=b[u]}
  if kind=='footprint':expected={u for u,raw in a.items() if ref(raw)==c['reference']}
  elif kind=='gr_text':expected={u for u,raw in a.items() if v.parse(raw)[1] in ['"PANEL REVERB"','"RENEGADE 600R-1 / DRAFT"']}
  elif kind in ['segment','arc']:expected=(set(c['remove_segments']) if kind=='segment' else set())|{u for u,raw in a.items() if v.field(v.parse(raw),'net')[1].strip('"') in c['existing_net_widths_mm']}
  else:expected=set()
  checks[kind+'_only_declared_existing_changes']=changed<=expected if kind in ['segment','arc'] else changed==expected
  if kind in ['footprint','gr_text']:checks[kind+'_identities_preserved']=set(a)==set(b)
  else:checks[kind+'_new_count']=len(set(b)-set(a))==(sum(len(r['points'])-1 for r in c['routes']) if kind=='segment' else len(c['vias']) if kind=='via' else 0)
 def new_atoms(kind):
  old,new=named(src,kind),named(target,kind)
  return [v.parse(new[u]) for u in set(new)-set(old)]
 def point(n,key):return tuple(float(x) for x in v.field(n,key)[1:3])
 actual_segments=collections.Counter((v.field(n,'net')[1].strip('"'),v.field(n,'layer')[1].strip('"'),float(v.field(n,'width')[1]),point(n,'start'),point(n,'end')) for n in new_atoms('segment'))
 expected_segments=collections.Counter((r['net'],r['layer'],r['width_mm'],tuple(a),tuple(z)) for r in c['routes'] for a,z in zip(r['points'],r['points'][1:]))
 checks['native_routes_match_specification']=actual_segments==expected_segments
 actual_vias=collections.Counter((v.field(n,'net')[1].strip('"'),point(n,'at'),float(v.field(n,'size')[1]),float(v.field(n,'drill')[1]),tuple(v.field(n,'layers')[1:])) for n in new_atoms('via'))
 expected_vias=collections.Counter((q['net'],tuple(q['at_mm']),q['size_mm'],q['drill_mm'],('"F.Cu"','"B.Cu"')) for q in c['vias'])
 checks['native_vias_match_specification']=actual_vias==expected_vias
 a,b=v.parse(src.read_text()),v.parse(target.read_text());excluded={'footprint','gr_text','segment','arc','via','setup'}
 checks['other_board_data_unchanged']=[n for n in a[1:] if n[0] not in excluded]==[n for n in b[1:] if n[0] not in excluded]
 checks['project_preserved']=src.with_suffix('.kicad_pro').read_bytes()==target.with_suffix('.kicad_pro').read_bytes()
 expected_rule='\n(rule "HI008 wet signal width" (condition "A.NetName == \'WET_TOP\' || A.NetName == \'WET_W\'") (constraint track_width (min 0.60mm)))\n(rule "CU002 supply width" (condition "A.NetName == \'+15V\' || A.NetName == \'-15V\'") (constraint track_width (min 0.80mm)))\n'
 for rule in c.get('additional_width_rules',[]):
  condition=' || '.join("A.NetName == '"+net+"'" for net in rule['nets'])
  expected_rule+=f'(rule "{rule["name"]}" (condition "{condition}") (constraint track_width (min {rule["minimum_mm"]:.2f}mm)))\n'
 checks['existing_custom_rules_preserved']=target.with_suffix('.kicad_dru').read_text()==src.with_suffix('.kicad_dru').read_text()+expected_rule
 sa,sb=v.field(a,'setup'),v.field(b,'setup');stack=v.field(sb,'stackup')
 checks['other_setup_preserved']=sa==[sb[0]]+[n for n in sb[1:] if n[0]!='stackup']
 layers=[n for n in stack[1:] if n[0]=='layer'];cu=[n for n in layers if n[1] in ('"F.Cu"','"B.Cu"')]
 checks['nominal_stackup']=len(cu)==2 and all(close(float(v.field(n,'thickness')[1]),c['construction']['outer_copper_nominal_um']/1000) for n in cu) and close(sum(float(v.field(n,'thickness')[1]) for n in layers),1.6)
 # Permit declared widths, segment endpoints and arc control points; preserve other fields.
 oldseg={**named(src,'segment'),**named(src,'arc')};newseg={**named(target,'segment'),**named(target,'arc')}
 overrides=c.get('existing_item_overrides',{})
 checks['overrides_reference_retained_items']=set(overrides)<=set(oldseg)-set(c['remove_segments'])
 width_only=True
 for u,raw in oldseg.items():
  if u in c['remove_segments']:continue
  oldnode=v.parse(raw);newnode=v.parse(newseg[u]);net=v.field(oldnode,'net')[1].strip('"')
  if net in c['existing_net_widths_mm']:
   change=overrides.get(u,{})
   v.field(oldnode,'width')[1]=str(change.get('width_mm',c['existing_net_widths_mm'][net]))
   for key in ['start','mid','end']:
    if key+'_mm' in change:v.field(oldnode,key)[1:3]=list(map(str,change[key+'_mm']))
   width_only &= oldnode==newnode
 checks['existing_routes_only_declared_width_and_endpoint_changes']=width_only
 arc_translations=[]
 for u,change in overrides.items():
  if 'mid_mm' not in change:continue
  node=v.parse(oldseg[u]);deltas=[tuple(change[key+'_mm'][i]-float(v.field(node,key)[i+1]) for i in [0,1]) for key in ['start','mid','end']]
  arc_translations.append(node[0]=='arc' and all(close(d[i],deltas[0][i]) for d in deltas for i in [0,1]))
 checks['moved_arcs_preserve_shape_by_translation']=all(arc_translations)
 board=p.LoadBoard(str(target));original=p.LoadBoard(str(src));fp=next(f for f in board.GetFootprints() if f.GetReference()==c['reference']);pad_data={q.GetNumber():{'xy_mm':xy(q.GetPosition()),'net':q.GetNetname(),'drill_mm':xy(q.GetDrillSize()),'shape':int(q.GetDrillShape())} for q in fp.Pads()}
 circuit_path=M.parent/'reverb-600/circuit.json'
 components=json.loads(circuit_path.read_text())['components'];source_jr4=next(q for q in components if q['reference']=='JR4')
 checks['circuit_terminal_parity']=source_jr4['pins']=={k:q['net'] for k,q in pad_data.items() if k and q['net']}
 checks['pot_nets_preserved']={k:q['net'] for k,q in pad_data.items() if k}=={k:n or '' for k,n in c['cavity_nets'].items()}
 checks['position_and_orientation']=xy(fp.GetPosition())==c['position_mm'] and close(fp.GetOrientationDegrees(),c['angle_deg'])
 spec=json.loads((M/'connector-contract.json').read_text())['candidate']
 checks['contact_positions_match_rotation']=all(pad_data[k]['xy_mm']==[c['position_mm'][0]-pos[0],c['position_mm'][1]-pos[1]] for k,pos in spec['contact_xy_mm'].items())
 checks['header_identity']=fp.GetValue()==spec['header']
 checks['four_round_contact_drills']=all(q['drill_mm']==[spec['contact_holes_nominal_mm']]*2 and q['shape']==int(p.PAD_DRILL_SHAPE_CIRCLE) for k,q in pad_data.items() if k)
 checks['round_locator_drill']=pad_data['']['drill_mm']==[spec['locator_hole_nominal_mm']]*2 and pad_data['']['shape']==int(p.PAD_DRILL_SHAPE_CIRCLE)
 checks['requested_route_style']=all((a[0]==z[0] or a[1]==z[1] or close(abs(a[0]-z[0]),abs(a[1]-z[1]))) for r in c['routes'] for a,z in zip(r['points'],r['points'][1:]))
 checks['new_trace_width_requirement']=all(r['width_mm']>=.6 for r in c['routes'])
 checks['declared_native_widths_and_necks']=all(close(p.ToMM(t.GetWidth()),overrides.get(t.m_Uuid.AsString(),{}).get('width_mm',c['existing_net_widths_mm'][t.GetNetname()])) for t in board.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetNetname() in c['existing_net_widths_mm'] and t.m_Uuid.AsString() in oldseg)
 checks['detours_use_45_degree_or_orthogonal_segments']=all(q['start_mm'][0]==q['end_mm'][0] or q['start_mm'][1]==q['end_mm'][1] or close(abs(q['start_mm'][0]-q['end_mm'][0]),abs(q['start_mm'][1]-q['end_mm'][1])) for q in overrides.values() if 'start_mm' in q and 'mid_mm' not in q)
 rules=json.loads(src.with_suffix('.kicad_pro').read_text())['board']['design_settings']['rules']
 checks['via_project_minimum']=all(q['size_mm']>=rules['min_via_diameter'] and q['drill_mm']>=rules['min_through_hole_diameter'] for q in c['vias'])
 # Exact 180 degree proposal: transform local negative-y plug exit to positive board-y.
 assert c['angle_deg']==180
 cy=c['position_mm'][1];front=h['header']['peg_y_mm']-h['header']['front_to_peg_nominal_mm'];rear=front+h['header']['front_to_rear_body_nominal_mm'];exit_y=rear-h['mate']['right_angle_mated_length_mm']
 edge_points=[]
 for raw in atoms(src,'gr_line'):
  n=v.parse(raw)
  if v.field(n,'layer')[1]=='"Edge.Cuts"':
   edge_points.extend([[float(t) for t in v.field(n,k)[1:3]] for k in ['start','end']])
 bounds=[[min(t[i] for t in edge_points),max(t[i] for t in edge_points)] for i in [0,1]]
 checks['rectangular_board_datum']=bounds==[[0.,160.],[0.,100.]]
 edge=bounds[1][1];peg=pad_data['']['xy_mm'][1];wire_exit=cy-exit_y;restraint=wire_exit+w['planning_policy']['axial_reservation_mm']
 geometry={'frame':'PCB component side; upper-left edge origin, x right, y down, z above component surface; nominal only','board_size_mm':[160,100],'pad1_xy_mm':c['position_mm'],'peg_xy_mm':pad_data['']['xy_mm'],'edge_to_peg_mm':round(edge-peg,6),'header_front_y_mm':round(cy-front,6),'header_rear_y_mm':round(cy-rear,6),'mated_wire_exit_y_mm':round(wire_exit,6),'first_restraint_y_min_mm':round(restraint,6),'wire_exit_beyond_edge_mm':round(wire_exit-edge,6),'restraint_beyond_edge_mm':round(restraint-edge,6),'mated_height_mm':h['mate']['right_angle_mated_height_mm'],'latching_height_callout_mm':h['mate']['latching_height_callout_mm'],'fit_approved':False,'bend_radius_mm':None,'withdrawal_mm':None,'finger_space_mm':None}
 checks['nominal_mating_edge_rule']=0<=edge-peg<=h['header']['edge_to_peg_max_mm']
 # Explicitly reject treating the courtyard/board boundary as the complete service volume.
 controls={'tie_at_limit':restraint>=wire_exit+12.7-1e-9,'tie_one_mm_early_rejected':not(restraint-1>=wire_exit+12.7),'board_edge_not_wire_exit':edge<wire_exit,'header_front_not_restraint':cy-front<restraint}
 def lengths(b):
  d=collections.defaultdict(float)
  for t in b.GetTracks():
   if not isinstance(t,p.PCB_VIA):d[t.GetNetname()]+=p.ToMM(t.GetLength())
  return d
 before,after=lengths(original),lengths(board);delta={net:round(after[net]-before[net],6) for net in sorted(set(before)|set(after)) if not close(before[net],after[net])}
 checks['only_declared_net_lengths_changed']=set(delta)<={'WET_TOP','WET_W','GND','+12V'}
 drc_path=O/'drc.json';run=subprocess.run([CLI,'pcb','drc','--format','json','--severity-all','--all-track-errors','--output',str(drc_path),str(target)],capture_output=True,text=True);assert run.returncode==0,run.stderr
 d=json.loads(drc_path.read_text());checks['zero_DRC_violations']=not d['violations'];checks['zero_open_connections']=not d['unconnected_items']
 inputs=[circuit_path,M/'reverb-connector-placement.json',M/'connector-contract.json',M/'mating-geometry.json',M/'wire-dressing.json',src,target,Path(__file__),M/'tools/place_reverb_connector.py']
 result={'id':'HI-008','date':'2026-11-26','kicad':subprocess.check_output([CLI,'version'],text=True).strip(),'input_hashes':{str(q.relative_to(ROOT)):sha(q) for q in inputs},'checks':checks,'controls':controls,'pads':pad_data,'geometry':geometry,'route_length_delta_mm':delta,'drc':{'violations':len(d['violations']),'unconnected':len(d['unconnected_items']),'sha256':sha(drc_path)},'evidence_checks_pass':all(checks.values()) and all(controls.values()),'native_adoption':False,'electrical_parasitics_qualified':False,'fabrication_ready':False,'holds':c['holds']}
 (O/'checks.json').write_text(json.dumps(result,indent=2)+'\n');(O/'service-geometry.json').write_text(json.dumps(geometry,indent=2)+'\n')
 print(json.dumps({'checks':checks,'controls':controls,'geometry':geometry,'route_length_delta_mm':delta},indent=2));assert result['evidence_checks_pass']
if __name__=='__main__':main()
