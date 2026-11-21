from pathlib import Path
import json,xml.etree.ElementTree as E,collections
R=Path(__file__).resolve().parents[1]
spec=json.loads((R/'design-connectivity.json').read_text())['components'];actual=E.parse(R/'validation/netlist.xml').getroot();pins={};expected={};errors=[]
for n in actual.findall('./nets/net'):
 for p in n.findall('node'):
  if not p.attrib['ref'].startswith('#') and not n.attrib['name'].startswith('unconnected-'):pins[(p.attrib['ref'],p.attrib['pin'])]=n.attrib['name']
for c in spec:
 if c['reference'].startswith('#'):continue
 for p,n in c['pins'].items():
  k=(c['reference'],p)
  if n is None:
   if k in pins:errors.append(['NC connected',k,pins[k]])
  else:expected[k]='GND' if n=='PE' else n
for k,n in expected.items():
 if k not in pins:errors.append(['missing pin',k,n])
exp_to_act=collections.defaultdict(set);act_to_exp=collections.defaultdict(set)
for k,n in expected.items():
 if k in pins:exp_to_act[n].add(pins[k]);act_to_exp[pins[k]].add(n)
for n,v in exp_to_act.items():
 if len(v)>1:errors.append(['split',n,sorted(v)])
for n,v in act_to_exp.items():
 if len(v)>1:errors.append(['short',n,sorted(v)])
extra=set(pins)-set(expected)
if extra:errors.append(['extra pins',sorted(extra)])
out={'passed':not errors,'components':len(actual.findall('./components/comp')),'mapped_pins':len(expected),'errors':errors}
(R/'validation/connectivity.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert not errors
