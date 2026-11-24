"""Two-injection AC measurement at an explicitly split return wire.

No native files or model generation. Inputs are SPICE decks and port names;
outputs are arrays and operating points. Caller owns evidence and acceptance.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
import spice_runtime as sp


def append_elements(text, elements):
    lines = text.splitlines()
    lines[lines.index('.end'):lines.index('.end')] = elements
    return '\n'.join(lines) + '\n'


def run_ac(text, nodes, branches=(), sweep='dec 120 .1 10000000'):
    sp.load(text)
    sp.cmd('op')
    op = {n: float(sp.vector(f'v({n})')[-1]) for n in nodes}
    sp.cmd('ac ' + sweep)
    vectors = {n: np.array(sp.vector(f'v({n})')) for n in nodes}
    vectors.update({b: np.array(sp.vector(f'i({b})')) for b in branches})
    frequency = np.real(sp.vector('frequency'))
    sp.cmd('destroy all')
    return np.array(frequency), vectors, op


def injections(text, receiver='OT_4', source='TX_TAP'):
    """Caller zeros all ordinary AC sources. Probe keeps DC wire intact.

    VPROBE is receiver->source; IPROBE injects ground->receiver.
    Paper's if is the negative of the simulator's VPROBE branch current.
    """
    return {
        kind: append_elements(text, [
            f'VPROBE {receiver} {source} DC 0 AC {int(kind == "voltage")}',
            f'IPROBE 0 {receiver} DC 0 AC {int(kind == "current")}',
        ]) for kind in ('voltage', 'current')
    }


def return_ratio(voltage, current, receiver='OT_4'):
    A, B = -current['vprobe'], -voltage['vprobe']
    C, D = current[receiver], voltage[receiver]
    numerator = 2 * (A * D - B * C) - A + D
    denominator = 1 - numerator
    return numerator / denominator


def admittance_probe(text, bias, receiver='OT_4', source='TX_TAP'):
    """Independent AC-clamped-port Y-matrix cross-check, at matched DC bias.

    In the bilateral return-wire model T=(Y12+Y21)/(Y11+Y22).
    Clamps are for this independent check, never a transient fixture.
    """
    columns = []
    for port in (0, 1):
        deck = append_elements(text, [
            f'VEPORT {receiver} 0 DC {bias} AC {int(port == 0)}',
            f'VFPORT {source} 0 DC {bias} AC {int(port == 1)}',
        ])
        _, v, _ = run_ac(deck, [receiver, source], ['veport', 'vfport'])
        columns.append((-v['veport'], -v['vfport']))
    y11, y21 = columns[0]
    y12, y22 = columns[1]
    return (y12 + y21) / (y11 + y22)
