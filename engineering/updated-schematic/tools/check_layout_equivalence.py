"""Compare fresh native-exported physical pin partitions and values to v0.2."""
from pathlib import Path
import hashlib,json,zipfile,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
with zipfile.ZipFile(ROOT/'validation/label-layout-v0.2.zip') as z:
 old_bytes=z.read('validation/revised-netlist.xml')
new_bytes=(ROOT/'validation/revised-netlist.xml').read_bytes()
def read(data):
 x=ET.fromstring(data)
 components={c.attrib['ref']:c.findtext('value') for c in x.findall('./components/comp')}
 nets={frozenset((n.attrib['ref'],n.attrib['pin']) for n in net.findall('node')) for net in x.findall('./nets/net')}
 return components,nets
old,nets_old=read(old_bytes);new,nets_new=read(new_bytes)
report={'baseline_revision':'0.2-DRAFT','presentation_revision':'0.3 DRAFT','physical_components':len(new),'native_nets':len(nets_new),'same_component_references':old.keys()==new.keys(),'same_component_values':old==new,'same_pin_partitions':nets_old==nets_new,'previous_netlist_sha256':hashlib.sha256(old_bytes).hexdigest(),'current_netlist_sha256':hashlib.sha256(new_bytes).hexdigest()}
report['passed']=all(report[k] for k in ['same_component_references','same_component_values','same_pin_partitions'])
(ROOT/'validation/layout-equivalence.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2));assert report['passed'],report
