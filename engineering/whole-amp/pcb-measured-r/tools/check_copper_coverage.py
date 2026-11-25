"""Independently compare audit pad coverage with native KiCad syntax."""
import hashlib
import json
import sys
from pathlib import Path

M = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(M.parent / 'tools'))
import native_sexpr as v

audit_path = M / 'review/copper-audit.json'
audit = json.loads(audit_path.read_text())
summary = {}
for name, row in audit['boards'].items():
    path = M / 'boards' / ('Renegade_' + name + '.kicad_pcb')
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
    board = v.parse(path.read_text()); pads = {}
    for ref, fp in v.fps(board).items():
        for pad in v.children(fp, 'pad'):
            net = v.children(pad, 'net')
            if net and net[0][1].strip('"'):
                pads.setdefault(net[0][1].strip('"'), []).append({'reference': ref, 'pad': pad[1].strip('"')})
    assert set(pads).issubset(row['nets'])
    for net, connections in pads.items():
        assert sorted(connections, key=lambda r:(r['reference'], r['pad'])) == row['nets'][net]['pad_connections']
    summary[name] = {
        'board_net_entries': len(row['nets']),
        'with_routed_copper': sum(r['has_routed_copper'] for r in row['nets'].values()),
        'right_angle_branch_candidates_outside_pads_vias': sum(r['right_angle_pair_present'] and not r['in_pad'] and not r['at_via'] for r in row['junctions_for_visual_review'])
    }
result = dict(native_pad_coverage_verified=True, boards=summary,
    audit_sha256=hashlib.sha256(audit_path.read_bytes()).hexdigest(),
    current_capacity_qualified=False, fabrication_ready=False)
(M / 'review/copper-coverage-checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(summary, indent=2))
