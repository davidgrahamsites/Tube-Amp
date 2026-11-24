"""Compare ALL native connected-pin partitions and changed values to the contract."""
from pathlib import Path
from collections import defaultdict
import argparse,json,re,xml.etree.ElementTree as ET
from grounding_contract import verified_aliases
ROOT=Path(__file__).resolve().parents[1]
spec=json.loads((ROOT/'circuit.json').read_text())['components']
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--netlist',type=Path,default=ROOT/'review/grounding-native.xml');args=parser.parse_args()
aliases=verified_aliases(args.netlist)
actual=ET.parse(args.netlist).getroot()
pins={};expected={};errors=[]
for net in actual.findall('./nets/net'):
    for pin in net.findall('node'):
        if not pin.attrib['ref'].startswith('#') and not net.attrib['name'].startswith('unconnected-'):
            pins[(pin.attrib['ref'],pin.attrib['pin'])]=net.attrib['name']
for c in spec:
    if c['reference'].startswith('#'):continue
    for p,n in c['pins'].items():
        key=(c['reference'],p)
        if n is None:
            if key in pins:errors.append(['NC connected',key,pins[key]])
        else:expected[key]=aliases.get(n,n)
for key,n in expected.items():
    if key not in pins:errors.append(['missing pin',key,n])
e2a=defaultdict(set);a2e=defaultdict(set)
for key,n in expected.items():
    if key in pins:e2a[n].add(pins[key]);a2e[pins[key]].add(n)
for n,v in e2a.items():
    if len(v)>1:errors.append(['split',n,sorted(v)])
for n,v in a2e.items():
    if len(v)>1:errors.append(['short',n,sorted(v)])
if set(pins)-set(expected):errors.append(['extra pins',sorted(set(pins)-set(expected))])
vals={c.attrib['ref']:c.findtext('value') for c in actual.findall('./components/comp')}
for c in spec:
    if c['sheet'].startswith('07') and vals.get(c['reference'])!=c['value']:
        errors.append(['value',c['reference'],vals.get(c['reference']),c['value']])
# The electrical fixture and native circuit must agree on every modeled R/C
# value and endpoint; decouplers are explicitly omitted with ideal supplies.
nodes=dict(zip('GND FX_RETURN IN_AC SEND_IN SEND_BUF SEND_TOP SEND_W DRV_FB DRIVER DRIVE_CAP TANK_IN TANK_OUT REC_IN REC_FB REC_OUT WET_TOP WET_W WET_BUF WET_MUTE SUM SUM_INV OUT_FB OUT_BUF OUT_AC WET_AC MIX_OUT'.split(),
               '0 fx acin dryin drybuf sendtop sendw drvfb driver drivecap tankin tankout recin recfb recout wettop wetw wetbuf wetmute sum suminv outfb outbuf outac wetac mix'.split()))
deck=ROOT/'simulation/dry-rs100000-knob1-muteFalse.cir'
elements={x[0]:x for l in deck.read_text().splitlines() if (x:=l.split()) and re.fullmatch(r'[RC]6\d\d',x[0])}
def numeric(s):
    s=s.replace('M','meg').lower();m=re.fullmatch(r'([0-9.]+)(meg|[kmunp]?)',s)
    return float(m[1])*{'':1,'k':1e3,'meg':1e6,'m':1e-3,'u':1e-6,'n':1e-9,'p':1e-12}[m[2]]
for ref,e in elements.items():
    c=next(c for c in spec if c['reference']==ref)
    if numeric(e[3])!=numeric(c['value']):errors.append(['SPICE value',ref,e[3],c['value']])
    if {e[1],e[2]}!={nodes[n] for n in c['pins'].values()}:errors.append(['SPICE endpoints',ref,e[1:3],c['pins']])
out={'declared_external_bond':'GB1 (native cut-wire proof in grounding-audit.json)','passed':not errors,'native_components':len(vals),'mapped_connected_pins':len(expected),'errors':errors}
out['modeled_RC_elements_compared']=len(elements)
(ROOT/'review/connectivity.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2));assert not errors
