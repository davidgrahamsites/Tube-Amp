"""Small shared gate: permit a named external bond only with current native proof.
No generic PE-to-GND alias. A changed contract, schematic or netlist invalidates proof.
"""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def verified_aliases(native_xml):
    contract=ROOT/'grounding-contract.json';report=json.loads((ROOT/'review/grounding-audit.json').read_text())
    required={'baseline_endpoint_inventory','baseline_exact_declared_bond_partition',
              'unqualified_no_alias_comparison_fails','cut_endpoint_inventory',
              'cut_exact_original_partition','cut_PE_isolated_from_every_signal_ground_endpoint',
              'active_schematic_hashes_preserved','active_board_hashes_preserved'}
    assert report['passed'] and set(report['checks'])==required and all(report['checks'].values()),'Ground-bond proof incomplete'
    assert report['contract_sha256']==digest(contract),'Ground-bond contract changed: rerun check_grounding.py'
    assert report['circuit_sha256']==digest(ROOT/'circuit.json'),'Circuit changed: rerun check_grounding.py'
    assert report['native_xml_sha256']==digest(Path(native_xml)),'Use current grounding-native.xml or rerun check_grounding.py'
    current={p.name:digest(p) for p in (ROOT/'cad').glob('*.kicad_sch')}
    assert current==report['schematic_sha256'],'Native schematic changed: rerun check_grounding.py'
    bond=json.loads(contract.read_text())['bond']
    assert bond['id']=='GB1' and bond['allowed_net_equivalence']==['GND','PE'] and bond['native_net_name']=='GND'
    return {'PE':'GND'}
