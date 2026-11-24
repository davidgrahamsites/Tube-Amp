"""Guarded one-time electrical checkpoint; refuses to overwrite adopted values.
Requires completed protection audit. Does not route or release boards.
"""
from pathlib import Path
import sys,json,hashlib,copy
root=Path(__file__).resolve().parents[4];eng=root/'engineering';mod=eng/'whole-amp/effects-loop'
sys.path.insert(0,str(eng/'updated-schematic/tools'))
from kicad_factory import parse,serialize,children
assert json.loads((mod/'results/protection-audit.json').read_text())['passed']
contract=eng/'whole-amp/reverb-600/circuit.json';sheet=contract.parent/'cad/04_output.kicad_sch'
oldtext=sheet.read_text();tree=parse(oldtext);assert serialize(tree)+'\n'==oldtext
spec=json.loads(contract.read_text());before={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [contract,sheet]}
values={'Value':'4.7k','Rating':'10 W minimum; exact part, derating, pulse and thermal qualification pending','Design_status':'Output protection engineering revision 2026-11-24; finite stress matrix only'}
changes=[]
for sym in children(tree,'symbol'):
 props={v[1]:v for v in children(sym,'property')};ref=props['Reference'][2]
 if ref not in ['R41','R42']:continue
 assert props['Value'][2]=='1k'
 row={'reference':ref,'before':{},'after':values}
 for k,v in values.items():row['before'][k]=props[k][2];props[k][2]=v
 changes.append(row)
assert len(changes)==2
# Reverse-delta proof catches any unintended native-field or geometry edit.
check=copy.deepcopy(tree)
for sym in children(check,'symbol'):
 props={v[1]:v for v in children(sym,'property')}
 for r in changes:
  if props['Reference'][2]==r['reference']:
   for k,v in r['before'].items():props[k][2]=v
assert serialize(check)+'\n'==oldtext
for c in spec['components']:
 if c['reference'] in ['R41','R42']:
  assert c['value']=='1k';c['value']=values['Value'];c['rating']=values['Rating'];c['status']=values['Design_status']
sheet.write_text(serialize(tree)+'\n');contract.write_text(json.dumps(spec,indent=2)+'\n')
plan=eng/'whole-amp/board-plan.json';d=json.loads(plan.read_text())
for ref in ['R41','R42']:
 d['chassis_parts'][ref]=d['chassis_parts'][ref].replace('1k/5W','4.7k / minimum 10W')+' Finite stress matrix: effects-loop/protection-review.md. Exact supported package and hot-enclosure derating remain release gates.'
plan.write_text(json.dumps(d,indent=2)+'\n')
cov=eng/'component-selection/coverage.json';d=json.loads(cov.read_text())
for c in d:
 if c['id']=='P040':
  c['value']='4.7k';c['requirement']=values['Rating'];c['status']='4.7k/minimum10W integrated in circuit and native schematic; exact MPN not selected; qualified thermal/voltage/pulse/fit still pending'
  c['candidate_mpns']=['EWWR0010J4K70T9','SQP10AJB-4K7']
cov.write_text(json.dumps(d,indent=2)+'\n')
record={'scope':'Two screen resistor values and engineering fields only; pins, wires and boards preserved','baseline_commit':'fea220801c9c5204e2b5ff21307464ff6c3eb09c','before_hashes':before,'after_hashes':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [contract,sheet]},'changes':changes,'native_reverse_delta_exact':True,'native_connectivity_comparison':'pending','fabrication_ready':False}
(mod/'results/protection-native-integration.json').write_text(json.dumps(record,indent=2)+'\n')
print('Adopted two socket-side protection values; no native geometry or board changes.')
