"""Audit the original electric input against a fresh KiCad XML export.

Usage: python3 tools/check_electric_input.py /path/to/fresh-netlist.xml
Produces bounded small-signal loading evidence, not a tube/pickup simulation.
"""
import hashlib
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
netlist = Path(sys.argv[1])
tree = ET.parse(netlist).getroot()
values = {c.attrib['ref']: c.findtext('value')
          for c in tree.findall('./components/comp')}
pins = {}
for net in tree.findall('./nets/net'):
    for node in net.findall('node'):
        pins[(node.attrib['ref'], node.attrib['pin'])] = net.attrib['name']
groups = [
    [('J1', 'T'), ('R1', '1')],
    [('R1', '2'), ('K1', '4')],
    [('K1', '6'), ('R2', '1'), ('V1', '2')],
    [('K1', '8'), ('R10', '1'), ('V2', '2')],
    [('R2', '2'), ('R10', '2'), ('J1', 'S'), ('J1', 'TN')],
]
checks = {f'connected_group_{i}': len({pins.get(p) for p in group}) == 1
          and all(p in pins for p in group)
          for i, group in enumerate(groups, 1)}
checks['distinct_input_and_grid_nodes'] = len({pins[p] for p in
    [('J1', 'T'), ('K1', '4'), ('V1', '2'), ('V2', '2')]}) == 4
checks['R1_68k'] = values['R1'] == '68k'
checks['grid_leaks_1M'] = values['R2'] == values['R10'] == '1M'
checks['first_tubes_12AX7'] = all('12AX7' in values[r] for r in ['V1', 'V2'])
spec = json.loads((ROOT / 'circuit.json').read_text())['components']
checks['contract_input_values'] = all(
    next(c['value'] for c in spec if c['reference'] == ref) == val
    for ref, val in [('R1', '68k'), ('R2', '1M'), ('R10', '1M')])

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

rows = []
for rs in [0, 6000, 20000, 100000]:
    transfer = 1e6 / (rs + 68e3 + 1e6)
    rows.append({'illustrative_source_resistance_ohm': rs,
                 'grid_voltage_over_thevenin_source_voltage': transfer,
                 'gain_dB': 20 * math.log10(transfer)})
result = {
    'scope': 'Original electric input, 600R-1; both steady relay positions',
    'passed': all(checks.values()), 'checks': checks,
    'netlist_export_tool': tree.findtext('./design/tool'),
    'netlist_sha256': sha(netlist),
    'input_hashes': {str(p.relative_to(ROOT)): sha(p) for p in
        [ROOT / 'circuit.json', *sorted((ROOT / 'cad').glob('*.kicad_sch'))]},
    'low_frequency_jack_resistance_ohm': 1068000,
    'voltage_divider_cases': rows,
    'assumptions': [
        'J1 plug inserted; normal grounding contact opens.',
        'K1 common pin4 selects pin6 OR pin8; relay operation is not simulated.',
        'Small signal: negligible grid conduction, capacitance neglected.',
        'Source resistances are illustrations, not pickup models or DCR-based guitar classifications.'
    ],
    'limits': [
        'Not an AC impedance sweep: pickup inductance, guitar controls, cable and Miller capacitance matter.',
        'No overload, bias, relay transient, noise, RFI, hardware or exact tube validation.',
        'Do not interpret 1.068 Mohm as frequency-independent impedance.'
    ]
}
out = ROOT / 'review/electric-input-loading-2026-11-21.json'
out.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'passed': result['passed'], 'checks': len(checks),
                  'resistance_ohm': 1068000, 'cases': rows}, indent=2))
assert result['passed'], checks
