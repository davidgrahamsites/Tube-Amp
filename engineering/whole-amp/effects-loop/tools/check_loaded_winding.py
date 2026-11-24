"""Independent impedance/ratio/DC tests of the emitted tapped transformer."""
import hashlib
import json
from pathlib import Path

import numpy as np

from fixture import ROOT
from loaded_feedback_model import build, TAP_FRACTION
from loop_probe import sp

ELEMENTS = {'RPA', 'RPB', 'LPA', 'LPB', 'LSLOW', 'LSHIGH', 'KOT',
            'VSLOW', 'VSHIGH', 'RSLOW', 'RSHIGH'}


def main():
    rows = []
    for load8, load4 in [(8, 1e12), (1e12, 4), (8, 4)]:
        elements = [x for x in build(dict(leakage_H=0, primary_cap_F=0, secondary_ohm=0)).splitlines()
                    if x.split(' ')[0] in ELEMENTS]
        text = '\n'.join(['Reciprocal winding terminal test',
                          'VDRIVE OT_PA OT_PB DC 0 AC 1', 'RCT B_MAIN 0 1gig',
                          *elements, f'RL8 SPEAKER 0 {load8}', f'RL4 OT_4 0 {load4}', '.end', ''])
        sp.load(text)
        sp.cmd('ac lin 1 1000 1000')
        z = 1 / -sp.vector('i(vdrive)')[0]
        ratio = sp.vector('v(ot_4)')[0] / sp.vector('v(speaker)')[0]
        reflected = 1 / (1 / (950*load8) + 1 / (1900*load4))
        expected = 200 + 1 / (1/reflected + 1/(2j*np.pi*1000*40))
        rows.append(dict(test='AC terminals', load8_ohm=load8, load4_ohm=load4,
                         impedance_relative_error=float(abs(z/expected-1)),
                         tap_ratio_error=float(abs(ratio-TAP_FRACTION))))
        sp.cmd('destroy all')
    for copper in (.2, 1):
        elements = [x for x in build(dict(leakage_H=0, primary_cap_F=0, secondary_ohm=copper)).splitlines()
                    if x.split(' ')[0] in ELEMENTS]
        for node, expected in [('speaker', copper), ('ot_4', copper*TAP_FRACTION)]:
            text = '\n'.join(['Winding DC resistance test', 'RCT B_MAIN 0 1gig',
                              *elements, f'VDRIVE {node} 0 DC 1', '.end', ''])
            sp.load(text)
            sp.cmd('op')
            measured = 1 / -sp.vector('i(vdrive)')[0]
            rows.append(dict(test='DC continuity', node=node, expected_ohm=expected,
                             measured_ohm=measured, relative_error=abs(measured/expected-1)))
            sp.cmd('destroy all')
    passed = all(r.get('impedance_relative_error', 0) < 1e-6 and r.get('tap_ratio_error', 0) < 1e-6
                 and r.get('relative_error', 0) < 1e-6 for r in rows)
    files = [Path(__file__), Path(__file__).with_name('loaded_feedback_model.py')]
    result = dict(scope='Reciprocal transformer equations and terminal continuity; no physical part qualification',
                  rows=rows, factory_hashes={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}, passed=passed)
    (ROOT/'results/loaded-winding-checks.json').write_text(json.dumps(result, indent=2)+'\n')
    assert passed, rows
    print(len(rows), 'loaded-winding terminal checks PASS')


if __name__ == '__main__':
    main()
