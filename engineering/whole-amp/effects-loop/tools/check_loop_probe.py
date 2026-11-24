"""Validate injection polarities, loading and bilateral measurement analytically."""
import hashlib
import json
from pathlib import Path

import numpy as np

from loop_probe import injections, return_ratio, run_ac, admittance_probe

OUT = Path(__file__).resolve().parents[1] / 'results'


def main():
    rows = []
    for resistance in (10, 1000, 1e6):
        for reverse in (0, -.002, .003):
            text = '\n'.join([
                'Analytic bilateral return-wire control',
                f'RE OT_4 0 {resistance}', 'RF TX_TAP 0 1000',
                'CE OT_4 0 100p', 'CF TX_TAP 0 200p',
                'GF TX_TAP 0 OT_4 0 .01',
                f'GE OT_4 0 TX_TAP 0 {reverse}', '.end', '',
            ])
            for swapped in (False, True):
                receiver, source = ('TX_TAP', 'OT_4') if swapped else ('OT_4', 'TX_TAP')
                measured = {}
                for kind, deck in injections(text, receiver, source).items():
                    f, measured[kind], _ = run_ac(deck, [receiver, source], ['vprobe'])
                t = return_ratio(measured['voltage'], measured['current'], receiver)
                expected = (.01 + reverse) / (1 / resistance + .001 + 2j * np.pi * f * 300e-12)
                y = admittance_probe(text, 0, receiver, source)
                error = float(np.max(abs(t - expected) / np.maximum(abs(expected), 1e-12)))
                yerror = float(np.max(abs(t - y) / np.maximum(abs(t), 1e-12)))
                rows.append(dict(input_ohm=resistance, reverse_S=reverse, swapped=swapped,
                                 analytic_relative_error=error, independent_Y_error=yerror))
    result = dict(scope='Analytic probe validation, not amplifier acceptance', cases=rows,
                  factory_hashes={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in [Path(__file__), Path(__file__).with_name('loop_probe.py')]},
                  passed=all(r['analytic_relative_error'] < 1e-7 and r['independent_Y_error'] < 1e-7 for r in rows))
    (OUT / 'loaded-probe-checks.json').write_text(json.dumps(result, indent=2) + '\n')
    assert result['passed'], rows
    print(len(rows), 'analytic/bilateral/orientation checks PASS')


if __name__ == '__main__':
    main()
