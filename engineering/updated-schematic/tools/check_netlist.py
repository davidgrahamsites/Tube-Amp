"""Compare native-exported pin connectivity against the explicit design register."""
from pathlib import Path
import collections,hashlib,json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
spec=json.loads((ROOT/'design-connectivity.json').read_text());results=[]
for project,filename in [('Renegade_Source_Baseline','baseline-netlist.xml'),('Renegade_220V_Reverb','revised-netlist.xml')]:
 actual=ET.parse(ROOT/'validation'/filename).getroot();pin_actual={};net_expected={};nc=set();errors=[]
 for n in actual.findall('./nets/net'):
  nodes=n.findall('node')
  if n.attrib['name'].startswith('unconnected-') and len(nodes)==1:continue
  for p in nodes:pin_actual[(p.attrib['ref'],p.attrib['pin'])]=n.attrib['name']
 for c in spec['components']:
  if c['project']!=project or c['reference'].startswith('#'):continue
  for pin,net in c['pins'].items():
   key=(c['reference'],pin)
   if net is None:nc.add(key);continue
   if net=='PE':net='GND'
   if project.endswith('Baseline') and net=='B_RAW':net='B_MAIN'
   net_expected.setdefault(net,set()).add(key)
 for net,pins in net_expected.items():
  missing=pins-pin_actual.keys()
  if missing:errors.append({'net':net,'missing_pins':sorted(missing)})
  exported={pin_actual[p] for p in pins if p in pin_actual}
  if len(exported)!=1:errors.append({'net':net,'unexpected_split':sorted(exported)})
 inverse=collections.defaultdict(set)
 for net,pins in net_expected.items():
  for p in pins:
   if p in pin_actual:inverse[pin_actual[p]].add(net)
 for net,names in inverse.items():
  if len(names)>1:errors.append({'actual_net':net,'unexpected_short':sorted(names)})
 for pin in nc:
  if pin in pin_actual:errors.append({'no_connect_pin_connected':pin,'net':pin_actual[pin]})
 known={p for ps in net_expected.values() for p in ps}|nc
 extra=set(pin_actual)-known
 if extra:errors.append({'unexpected_pins':sorted(extra)})
 result={'project':project,'native_components':len(actual.findall('./components/comp')),'native_nets':len(actual.findall('./nets/net')),'mapped_connected_pins':sum(map(len,net_expected.values())),'explicit_no_connect_pins':len(nc),'errors':errors,'passed':not errors,'netlist_sha256':hashlib.sha256((ROOT/'validation'/filename).read_bytes()).hexdigest()};results.append(result)
(ROOT/'validation'/'connectivity-check.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
assert all(r['passed'] for r in results)
