"""Prove the declared PE/GND bond with native baseline and cut-wire netlists.
Read-only to active CAD. Writes fixed-name review evidence, never changes earth wiring.
Run with ordinary Python and installed KiCad CLI; negative control lives in temp storage.
"""
from pathlib import Path
from collections import defaultdict
import hashlib,json,shutil,subprocess,sys,tempfile,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]; CAD=ROOT/'cad'
sys.path.insert(0,str(ROOT.parents[1]/'updated-schematic/tools'))
from kicad_factory import parse,serialize,children,child
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def partition(pins):
    grouped=defaultdict(set)
    for endpoint,net in pins.items():grouped[net].add(endpoint)
    return {frozenset(g) for g in grouped.values()}
def native_pins(path):
    root=ET.parse(path).getroot(); pins={}
    for net in root.findall('./nets/net'):
        if net.attrib['name'].startswith('unconnected-'):continue
        for p in net.findall('node'):
            if not p.attrib['ref'].startswith('#'):pins[p.attrib['ref'],p.attrib['pin']]=net.attrib['name']
    return pins

def main():
    contract_path=ROOT/'grounding-contract.json';contract=json.loads(contract_path.read_text())
    parts=json.loads((ROOT/'circuit.json').read_text())['components']
    expected={(c['reference'],pin):net for c in parts if not c['reference'].startswith('#') for pin,net in c['pins'].items() if net is not None}
    pe={k for k,n in expected.items() if n==contract['safety_net']}
    assert pe=={tuple(p) for p in contract['safety_earth_endpoints']},'PE endpoint inventory changed'
    bond=contract['bond']; assert bond['allowed_net_equivalence']==['GND','PE']
    hashes={p.name:digest(p) for p in CAD.glob('*.kicad_sch')}
    board_dir=ROOT.parent/'pcb-measured-r/boards';boards={p.name:digest(p) for p in board_dir.glob('*.kicad_pcb')}
    tree=parse((CAD/bond['native_sheet']).read_text())
    wires=[w for w in children(tree,'wire') if child(w,'uuid')[1]==bond['native_wire_uuid']]
    assert len(wires)==1,'Missing/duplicate declared bond wire'
    coords=[[float(v) for v in xy[1:]] for xy in children(child(wires[0],'pts'),'xy')]
    assert coords==bond['native_wire_endpoints_mm'],'Declared wire geometry changed'
    outputs=ROOT/'review';baseline=outputs/'grounding-native.xml'
    commands=[]
    def export(source,out):
        cmd=[CLI,'sch','export','netlist','--format','kicadxml','-o',str(out),str(source)]
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=60);commands.append(dict(command=cmd,returncode=r.returncode,stderr=r.stderr))
        assert r.returncode==0,r.stderr
    export(CAD/'Renegade_220V_Reverb.kicad_sch',baseline)
    full=native_pins(baseline)
    aliased={k:('GND' if n=='PE' else n) for k,n in expected.items()}
    tests={'baseline_endpoint_inventory':set(full)==set(expected),
           'baseline_exact_declared_bond_partition':partition(full)==partition(aliased),
           'unqualified_no_alias_comparison_fails':partition(full)!=partition(expected)}
    with tempfile.TemporaryDirectory(prefix='renegade-earth-cut-') as tmp:
        temp=Path(tmp)
        for path in CAD.iterdir():
            if path.suffix in ['.kicad_sch','.kicad_pro'] or path.name=='sym-lib-table':shutil.copy2(path,temp/path.name)
        (temp/'libraries').symlink_to(CAD/'libraries',target_is_directory=True)
        tree.remove(wires[0]);(temp/bond['native_sheet']).write_text(serialize(tree)+'\n')
        cut=temp/'cut.xml';export(temp/'Renegade_220V_Reverb.kicad_sch',cut);opened=native_pins(cut)
        tests['cut_endpoint_inventory']=set(opened)==set(expected)
        tests['cut_exact_original_partition']=partition(opened)==partition(expected)
        tests['cut_PE_isolated_from_every_signal_ground_endpoint']=all(opened[p]!=opened[g] for p in pe for g,n in expected.items() if n=='GND')
        cut_groups=sorted([sorted([list(e) for e in group]) for group in partition(opened)])
    tests['active_schematic_hashes_preserved']=hashes=={p.name:digest(p) for p in CAD.glob('*.kicad_sch')}
    tests['active_board_hashes_preserved']=boards=={p.name:digest(p) for p in board_dir.glob('*.kicad_pcb')}
    report=dict(scope='Logical/native bond topology; not physical bonding or current capacity qualification',
        passed=all(tests.values()),checks=tests,contract_sha256=digest(contract_path),circuit_sha256=digest(ROOT/'circuit.json'),
        schematic_sha256=hashes,board_sha256=boards,native_xml_sha256=digest(baseline),commands=commands,
        bond=bond,safety_earth_endpoints=sorted([list(p) for p in pe]),cut_endpoint_partitions=cut_groups,
        physical_qualified=False,fabrication_ready=False)
    (outputs/'grounding-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'checks':tests},indent=2));assert report['passed']
if __name__=='__main__':main()
