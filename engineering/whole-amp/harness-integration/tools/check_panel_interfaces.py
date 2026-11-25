#!/usr/bin/env python3
"""Read-only panel interface audit; run with the installed KiCad Python."""
import copy
import csv
import hashlib
import json
from pathlib import Path
import pcbnew

MODULE = Path(__file__).resolve().parents[1]
WHOLE = MODULE.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_mapping(rows, components, contract):
    assert set(r['pot'] for r in rows) == set(contract['panel_pots'])
    assert len(rows) == 30
    assert len({(r['pot'], r['terminal']) for r in rows}) == 30
    for row in rows:
        assert row['block'] == contract['panel_pots'][row['pot']]
        assert row['net'] == components[row['pot']]['pins'][row['terminal']]
        assert row['cavity'] == row['terminal']
        assert row['reserved_cavity4'] == 'UNASSIGNED'


def wire_range_compatible(awg, minimum_od, maximum_od, limits):
    return (awg in limits['awg'] and minimum_od <= maximum_od
            and limits['insulation_diameter_min_mm'] <= minimum_od
            and maximum_od <= limits['insulation_diameter_max_mm'])


def main():
    contract_path = MODULE / 'connector-contract.json'
    circuit_path = WHOLE / 'reverb-600/circuit.json'
    contract = json.loads(contract_path.read_text())
    source = json.loads(circuit_path.read_text())
    components = {}
    for component in source['components']:
        ref = component['reference']
        if ref in contract['panel_pots']:
            assert ref not in components, 'Duplicate panel reference'
            assert set(component['pins']) == {'1', '2', '3'}
            components[ref] = component

    board_paths = sorted((WHOLE / 'pcb-measured-r/boards').glob('*.kicad_pcb'))
    assert len(board_paths) == 4
    hashes = {str(p.relative_to(WHOLE)): digest(p) for p in board_paths}
    native = {}
    wire_pads = {}
    for path in board_paths:
        board = pcbnew.LoadBoard(str(path))
        name = path.stem.removeprefix('Renegade_')
        native[name] = {}
        wire_pads[name] = []
        for footprint in board.GetFootprints():
            ref = footprint.GetReference()
            item = str(footprint.GetFPID().GetLibItemName())
            if ref.startswith('JM'):
                wire_pads[name].append({'reference': ref, 'footprint': item})
            for pad in footprint.Pads():
                net = pad.GetNetname()
                if net:
                    native[name].setdefault(net, []).append(ref + '.' + pad.GetNumber())
        for endpoints in native[name].values():
            endpoints.sort()

    rows = []
    for ref, block in contract['panel_pots'].items():
        for pin in ('1', '2', '3'):
            net = components[ref]['pins'][pin]
            endpoints = native[block].get(net, [])
            rows.append(dict(pot=ref, block=block, terminal=pin, cavity=pin, net=net,
                             reserved_cavity4='UNASSIGNED',
                             native_endpoints=';'.join(endpoints),
                             migration='JOIN_EXISTING_NET' if endpoints else 'ADD_BOARD_NODE_FOR_EXISTING_CIRCUIT_NET'))
    validate_mapping(rows, components, contract)
    negatives = {}
    for label, alter in (
        ('terminal_swap', lambda r: r[0].update(net=r[1]['net'])),
        ('implicit_shield_ground', lambda r: r[0].update(reserved_cavity4='GND')),
        ('omitted_duplicate_terminal', lambda r: r.pop(4)),
    ):
        bad = copy.deepcopy(rows)
        alter(bad)
        try:
            validate_mapping(bad, components, contract)
        except AssertionError:
            negatives[label] = 'rejected'
        else:
            raise AssertionError('Negative control accepted: ' + label)
    limits = contract['wire_tool_limits']
    wire_checks = {name: wire_range_compatible(*values, limits) for name, values in {
        'synthetic_24awg_1.50_to_1.70': (24, 1.50, 1.70),
        'too_thin_24awg_1.10_to_1.20': (24, 1.10, 1.20),
        'too_thick_22awg_2.30_to_2.50': (22, 2.30, 2.50),
        'wrong_contact_26awg': (26, 1.50, 1.70),
    }.items()}
    assert list(wire_checks.values()) == [True, False, False, False]

    wire_path = MODULE / 'wire-candidates.json'
    wire_data = json.loads(wire_path.read_text())
    tolerance = wire_data['outside_diameter_tolerance_mm']
    wire_candidates = []
    for wire in wire_data['candidates']:
        low = round(wire['nominal_od_mm'] - tolerance, 6)
        high = round(wire['nominal_od_mm'] + tolerance, 6)
        compatible = wire_range_compatible(wire['awg'], low, high, limits)
        assert compatible == wire['expected_dimension_screen'], wire['id']
        wire_candidates.append({'id': wire['id'], 'awg': wire['awg'],
            'od_range_mm': [low, high], 'contact_tool_dimension_screen': compatible,
            'lower_limit_margin_mm': round(low - limits['insulation_diameter_min_mm'], 6),
            'upper_limit_margin_mm': round(limits['insulation_diameter_max_mm'] - high, 6),
            'qualified_crimp': False, 'purchase_ready': False})
    assert wire_data['selected_wire'] is None

    candidate = contract['candidate']
    library = Path(candidate['native_library'])
    fp_path = library / (candidate['footprint'] + '.kicad_mod')
    footprint = pcbnew.FootprintLoad(str(library), candidate['footprint'])
    assert footprint is not None
    actual_pads = []
    for pad in footprint.Pads():
        number = pad.GetNumber()
        xy = [pcbnew.ToMM(pad.GetPosition().x), pcbnew.ToMM(pad.GetPosition().y)]
        drill = [pcbnew.ToMM(pad.GetDrillSize().x), pcbnew.ToMM(pad.GetDrillSize().y)]
        expected_xy = candidate['contact_xy_mm'][number] if number else candidate['locator_xy_mm']
        expected_drill = candidate['contact_holes_nominal_mm'] if number else candidate['locator_hole_nominal_mm']
        assert all(abs(a-b) < 1e-6 for a,b in zip(xy, expected_xy))
        assert all(abs(d-expected_drill) < 1e-6 for d in drill)
        assert pad.GetDrillShape() == pcbnew.PAD_DRILL_SHAPE_CIRCLE
        assert pad.GetAttribute() == (pcbnew.PAD_ATTRIB_PTH if number else pcbnew.PAD_ATTRIB_NPTH)
        actual_pads.append({'number': number, 'xy_mm': xy, 'drill_mm': drill,
                            'plated': bool(number), 'shape': 'round'})
    assert len(actual_pads) == 5 and {p['number'] for p in actual_pads} == {'','1','2','3','4'}
    assert hashes == {str(p.relative_to(WHOLE)): digest(p) for p in board_paths}
    gaps = sorted({r['net'] for r in rows if not r['native_endpoints']})
    output = MODULE / 'results'
    with (output / 'pot-connectors.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    report = {
        'scope': 'Ten external panel pots; existing circuit retained; native CAD not modified',
        'inputs_sha256': {**hashes, 'reverb-600/circuit.json': digest(circuit_path),
                          'connector-contract.json': digest(contract_path),
                          'wire-candidates.json': digest(wire_path),
                          'candidate_installed_footprint': digest(fp_path),
                          'factory': digest(Path(__file__))},
        'panel_pots': len(components), 'terminal_assignments': len(rows),
        'circuit_mapping': 'PASS', 'native_cad_preserved': True,
        'existing_circuit_nets_needing_board_nodes': gaps,
        'main_existing_JM_footprints': sorted(wire_pads['Main'], key=lambda x:x['reference']),
        'candidate_nominal_footprint': {'result':'PASS', 'pads': sorted(actual_pads, key=lambda x:x['number']),
            'limitation':'Nominal installed footprint comparison only. Full drawing visual/tolerance, mated geometry and fabricator finished-hole capabilities remain pending.'},
        'negative_controls': negatives, 'wire_dimension_controls': wire_checks,
        'published_wire_candidate_screens': wire_candidates,
        'selected_wire': None, 'native_connector_adoption': False,
        'purchase_ready': False, 'manufacturing_ready': False, 'holds': contract['release_holds']
    }
    (output / 'checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['panel_pots','terminal_assignments','circuit_mapping','existing_circuit_nets_needing_board_nodes','native_cad_preserved','purchase_ready','manufacturing_ready']}, indent=2))


if __name__ == '__main__':
    main()
