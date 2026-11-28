"""Recover the load-only 2 mA crossing from the independent open-port probe."""
import hashlib
import json
import math
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
ROOT = MODULE.parents[3]
RESULTS = MODULE / 'results'


def main():
    receipt = json.loads((RESULTS / 'integrated-load.json').read_text())
    for name, expected in receipt['sources'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    probes = json.loads((MODULE.parent / 'results/return-port-summary.json').read_text())
    rows = receipt['cases']
    assert {(r['hz'],r['target_Vpk'],r['added_pF']) for r in rows} == {
        (f,v,c) for f,v in ((1000,4.27),(1000,135),(20000,135)) for c in (0,100,500)}
    assert len(rows) == 9 and len(probes['cases']) == 36
    crossings = {}
    for row in rows:
        frequency = row['hz']
        omega = 2 * math.pi * frequency
        for case in probes['cases']:
            z = complex(*case['measurements']['load-probe']['points'][str(frequency)]['FX_RETURN'])
            y = 1 / z
            extra = omega * row['added_pF'] * 1e-12
            target = row['target_Vpk'] * math.hypot(y.real, y.imag + extra)
            assert abs(target * 1000 / row['linear_target_current_mApk'] - 1) < .005
            limit = (math.sqrt((.002 / 135)**2 - y.real**2) - y.imag) / omega
            assert abs(135 * abs(y + 1j * omega * limit) - .002) < 1e-12
            crossings[frequency] = limit * 1e12
        if row['status'] == 'incomplete':
            assert row['reached_s'] < row['requested_end_s'] and row['solver_messages']
            continue
        assert row['port_current_mA'][0] < 0 < row['port_current_mA'][1]
    print('36 prior configurations x 9 load comparisons agree within 0.5%.')
    print('Ideal 135 V peak, 2 mA external-only crossing in pF:', crossings)


if __name__ == '__main__':
    main()
