"""Read-only inventory of every active board, including parts old pad checks skip.

Run with KiCad Python. Facts are not ratings or an assembly qualification.
Public output: review/native-requirements-facts.json. Does not save native CAD.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import math
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT.parent
parts = {}
for c in json.loads((WHOLE / 'reverb-600/circuit.json').read_text())['components']:
    if not c['reference'].startswith('#'):
        parts.setdefault(c['reference'], {}).update(c['pins'])
plan = json.loads((WHOLE / 'board-plan.json').read_text())
selection = {r: c for c in json.loads((WHOLE.parent / 'component-selection/coverage.json').read_text()) for r in c['refs']}
def xy(v):
    return [round(p.ToMM(v.x), 4), round(p.ToMM(v.y), 4)]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

result = {'scope': 'All four active boards; source hashes, exhaustive reference coverage, geometry and rule inventory. No physical fit/current/EMC certification.', 'boards': {}}
keep, seen = [], Counter()
for name in ['Main', 'Power', 'Control', 'Reverb']:
    path = ROOT / 'boards' / f'Renegade_{name}.kicad_pcb'
    b = p.LoadBoard(str(path)); keep.append(b)
    project = json.loads(path.with_suffix('.kicad_pro').read_text())
    dru = path.with_suffix('.kicad_dru').read_text()
    rows, errors, nc = [], [], []
    for f in sorted(b.GetFootprints(), key=lambda f: f.GetReference()):
        ref = f.GetReference(); seen[ref] += 1
        pads = [{'number': q.GetNumber(), 'net': q.GetNetname(), 'at_mm': xy(q.GetPosition()), 'size_mm': xy(q.GetSize()), 'drill_mm': xy(q.GetDrillSize()), 'attribute': int(q.GetAttribute())} for q in f.Pads()]
        expected = parts.get(ref)
        if expected is not None:
            nums = [q['number'] for q in pads if q['number']]
            if set(nums) != set(expected): errors.append({'ref': ref, 'pad_set': nums, 'expected': sorted(expected)})
            for q in pads:
                if not q['number']: continue
                want = expected.get(q['number']); actual = q['net']
                if want is None and actual in ['', f"unconnected-({ref}-Pad{q['number']})"]:
                    nc.append([ref, q['number']])
                elif want != actual: errors.append({'ref': ref, 'pad': q['number'], 'expected': want, 'actual': actual})
        courtyards = [g for g in f.GraphicalItems() if g.GetLayer() in [p.F_CrtYd, p.B_CrtYd]]
        sel = selection.get(ref, {})
        rows.append({'ref': ref, 'value': f.GetValue(), 'footprint': f.GetFPID().GetUniStringLibId(), 'at_mm': xy(f.GetPosition()), 'pads': pads, 'courtyard_graphics': len(courtyards), 'selected_mpn': sel.get('selected_mpn'), 'selection_status': sel.get('status'), 'contract_member': expected is not None, 'model_count': len(list(f.Models()))})
    actual_refs = {r['ref'] for r in rows}
    ports = [r for r in rows if not r['contract_member'] and not r['ref'].startswith('H')]
    port_errors = []
    if name != 'Reverb':
        if sorted(r['value'] for r in ports) != sorted(plan['boards'][name]['ports']):
            port_errors.append('Wire-port value inventory differs from board plan')
        for r in ports:
            if len(r['pads']) != 1 or r['pads'][0]['number'] != '1' or r['pads'][0]['net'] != r['value']:
                port_errors.append(r['ref'] + ': wire-port pad/net mismatch')
    # Straight-line pad separation is a LOWER BOUND, not routed loop length.
    bypass = []
    caps = [r for r in rows if r['ref'].startswith('C') and r['value'].lower() in ['100n', '330n', '100nf', '330nf']]
    for r in rows:
        if not r['ref'].startswith('U'): continue
        for q in r['pads']:
            if q['net'] not in ['+5V', '+12V', '+15V', '-15V', 'CTRL_RAW']: continue
            choices = [(math.dist(q['at_mm'], s['at_mm']), c['ref']) for c in caps
                       if any(t['net'] == 'GND' for t in c['pads'])
                       for s in c['pads'] if s['net'] == q['net']]
            if choices:
                distance, cap = min(choices)
                bypass.append({'ref': r['ref'], 'pin': q['number'], 'net': q['net'], 'nearest_100n_or_330n': cap, 'pad_distance_lower_bound_mm': round(distance, 3)})
    box = b.GetBoardEdgesBoundingBox()
    settings = project.get('board', {}).get('design_settings', {})
    result['boards'][name] = {
        'sha256': sha(path), 'project_sha256': sha(path.with_suffix('.kicad_pro')), 'rules_sha256': sha(path.with_suffix('.kicad_dru')),
        'outline_bbox_mm': {'origin': xy(box.GetOrigin()), 'size': xy(box.GetSize())},
        'copper_layers': b.GetCopperLayerCount(), 'zone_count': len(list(b.Zones())),
        'track_items': len(list(b.GetTracks())), 'footprints': rows,
        'missing_courtyards': [r['ref'] for r in rows if not r['courtyard_graphics']],
        'missing_models': [r['ref'] for r in rows if not r['model_count']],
        'not_in_circuit_contract': [r for r in rows if not r['contract_member']],
        'planned_board_refs_absent': sorted(set(plan['boards'][name]['refs']) - actual_refs),
        'wire_port_errors': port_errors, 'wire_port_count': len(ports),
        'bypass_lower_bounds': bypass,
        'pad_net_errors': errors, 'explicit_no_connects': nc,
        'rules': settings.get('rules', {}), 'ignored_checks': [k for k,v in settings.get('rule_severities', {}).items() if v == 'ignore'],
        'drc_exclusions': settings.get('drc_exclusions', []),
        'net_settings': project.get('net_settings', {}),
        'custom_rules': dru, 'stackup': project.get('board', {}).get('stackup'),
        'native_explicit_stackup': '(stackup' in path.read_text(),
        'paired_schematic_exists': path.with_suffix('.kicad_sch').exists()}
result['cross_board_duplicate_refs'] = {k:v for k,v in seen.items() if v > 1}
result['circuit_refs_absent_from_all_boards'] = [{'ref': r, 'disposition': plan['chassis_parts'].get(r, 'UNACCOUNTED in historical board plan'), 'pins': parts[r]} for r in sorted(set(parts) - set(seen))]
result['contract_reference_count'] = len(parts)
result['unique_native_references'] = len(seen)
(ROOT / 'review/native-requirements-facts.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({n:{'footprints':len(v['footprints']), 'missing_courtyards':v['missing_courtyards'], 'missing_models':len(v['missing_models']), 'zone_count':v['zone_count'], 'extra_refs':[r['ref'] for r in v['not_in_circuit_contract']], 'planned_refs_absent':v['planned_board_refs_absent'], 'pad_errors':v['pad_net_errors']} for n,v in result['boards'].items()}, indent=2))
print('Absent circuit references:', len(result['circuit_refs_absent_from_all_boards']))
