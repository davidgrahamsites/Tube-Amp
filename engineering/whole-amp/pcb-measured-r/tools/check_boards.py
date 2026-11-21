"""Read-only native pad/net audit against the current electrical contract.

This is not KiCad paired-schematic parity or an assembled fit check.
"""
from pathlib import Path
import hashlib
import json
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT.parent
contract_path = WHOLE / 'reverb-600/circuit.json'
parts = {}
for c in json.loads(contract_path.read_text())['components']:
    if not c['reference'].startswith('#'):
        parts.setdefault(c['reference'], {}).update(c['pins'])
integration = json.loads((ROOT / 'review/integration.json').read_text())
report = {'circuit_sha256': hashlib.sha256(contract_path.read_bytes()).hexdigest(),
          'scope': 'Native pad/net contract; no assembly schematic parity or cabinet fit claim',
          'boards': {}}
KEEP = []
for name in ['Main', 'Power', 'Control', 'Reverb']:
    path = ROOT / 'boards' / f'Renegade_{name}.kicad_pcb'
    b = p.LoadBoard(str(path))
    KEEP.append(b)
    checked, mismatches, nc = 0, [], []
    for f in b.GetFootprints():
        ref = f.GetReference()
        if ref not in parts:
            continue
        pads = {q.GetNumber(): q for q in f.Pads() if q.GetNumber()}
        if set(pads) != set(parts[ref]):
            mismatches.append({'reference': ref, 'pad_set_mismatch': True})
        for num, pad in pads.items():
            checked += 1
            expected, actual = parts[ref].get(num), pad.GetNetname()
            if expected is None and actual in ['', f'unconnected-({ref}-Pad{num})']:
                nc.append([ref, num])
            elif actual != expected:
                mismatches.append({'reference': ref, 'pad': num, 'expected': expected, 'actual': actual})
    d = json.loads((ROOT / f'review/{name}-drc.json').read_text())
    source = WHOLE / integration['boards'][name]['source']
    preserved = hashlib.sha256(source.read_bytes()).hexdigest() == integration['boards'][name]['source_sha256']
    report['boards'][name] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'source_unchanged': preserved, 'pad_checks': checked, 'mismatches': mismatches,
        'explicit_no_connect_pads': nc, 'track_items': len(list(b.GetTracks())),
        'drc_violations': len(d['violations']), 'unconnected_items': len(d['unconnected_items'])}
report['all_pad_maps_pass'] = all(not r['mismatches'] and r['source_unchanged'] for r in report['boards'].values())
report['fabrication_ready'] = False
(ROOT / 'review/final-checks.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
assert report['all_pad_maps_pass']
