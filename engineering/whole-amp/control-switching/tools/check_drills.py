"""Compare temporary native Excellon exports against the pre-change board.

This verifies this correction's drill delta, not the complete amplifier's
manufacturing qualification. Temporary exports are removed on exit.
"""
import collections
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
ROOT = MODULE.parents[2]
BOARD = ROOT / 'engineering/whole-amp/pcb-measured-r/boards/Renegade_Control.kicad_pcb'
CLI = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'


def read_hits(text):
    assert 'METRIC' in text
    tools, hits, active = {}, collections.Counter(), None
    for line in text.splitlines():
        match = re.fullmatch(r'T(\d+)C([\d.]+)', line)
        if match:
            tools[match[1]] = float(match[2])
        match = re.fullmatch(r'T(\d+)', line)
        if match:
            active = match[1]
        match = re.fullmatch(r'X([\d.-]+)Y([\d.-]+)', line)
        if match:
            hits[(float(match[1]), float(match[2]), tools[active])] += 1
    return hits


def export(board, target):
    subprocess.run([CLI, 'pcb', 'export', 'drill', '--excellon-units', 'mm',
                    '--excellon-separate-th', '--output', str(target), str(board)],
                   check=True, capture_output=True, timeout=60)
    return {kind: (target / (board.stem + '-' + kind + '.drl')).read_text()
            for kind in ['PTH', 'NPTH']}


def main():
    base = json.loads((MODULE / 'contract.json').read_text())['baseline_commit']
    relative = str(BOARD.relative_to(ROOT))
    old = subprocess.check_output(['/usr/bin/git', 'show', base + ':' + relative], cwd=ROOT)
    with tempfile.TemporaryDirectory(prefix='renegade-local-clamp-drill-') as directory:
        temp = Path(directory)
        baseline = temp / 'baseline.kicad_pcb'
        baseline.write_bytes(old)
        before = export(baseline, temp / 'before')
        after = export(BOARD, temp / 'after')
        p0, p1 = read_hits(before['PTH']), read_hits(after['PTH'])
        # Only the old six TO92 pin holes may disappear.
        removed = p0 - p1
        expected_removed_positions = {(x, -45.105) for x in
                                      [111.955, 114.495, 117.035, 172.635, 175.175, 177.715]}
        assert sum(removed.values()) == 6, removed
        assert {(x, y) for x, y, diameter in removed} == expected_removed_positions
        # Q drain vias and four round local-diode PTHs replace those six hits.
        expected_added = collections.Counter({
            (117.035, -45.105, 0.4): 1, (177.715, -45.105, 0.4): 1,
            (128.0, -38.0, 1.2): 1, (117.84, -38.0, 1.2): 1,
            (185.68, -40.0, 1.2): 1, (175.52, -40.0, 1.2): 1})
        assert p1 - p0 == expected_added, p1 - p0
        assert read_hits(before['NPTH']) == read_hits(after['NPTH'])
        # Preserve routed/slot statements as well as round-hole coordinates.
        slot_lines = lambda s: [line for line in s.splitlines()
                                if 'G85' in line or line.startswith(('G00', 'G01', 'M15', 'M16'))]
        assert all(slot_lines(before[k]) == slot_lines(after[k]) for k in before)
        report = dict(
            passed=True, baseline_commit=base,
            scope='Only Q1/Q2 replacement and D333/D342 addition; not full-board release',
            removed_holes=[dict(x_mm=x, y_mm=y, diameter_mm=d, count=n)
                           for (x, y, d), n in removed.items()],
            added_holes=[dict(x_mm=x, y_mm=y, diameter_mm=d, count=n, shape='round', plated=True)
                         for (x, y, d), n in expected_added.items()],
            unrelated_round_drills_unchanged=True, slot_commands_unchanged=True,
            board_sha256=hashlib.sha256(BOARD.read_bytes()).hexdigest(),
            export_sha256={k: hashlib.sha256(t.encode()).hexdigest() for k, t in after.items()},
            fabrication_ready=False,
            limits='Final socket terminals, fab finished-hole tolerance, registration and actual leads remain separate checks.')
    (MODULE / 'results/drill-checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Verified scoped native drill delta; unrelated holes and slot commands preserved.')


if __name__ == '__main__':
    main()
