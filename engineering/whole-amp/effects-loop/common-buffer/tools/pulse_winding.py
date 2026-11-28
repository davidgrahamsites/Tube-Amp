"""CB-009 check. Winding terminal-to-terminal pulse voltage in the CB-008 delay network.

Reuses the CB-008 fast-fault, handover and audio fixtures unchanged. Only the delay
network text is replaced, and extra probes record the voltage across every winding.
Arithmetic and simulation only. No winding is qualified by this file.
"""
from contextlib import ExitStack, contextmanager
from unittest.mock import patch

import numpy as np

import guard_audio
import guard_handover
import sudden_guard
from sudden_guard import MODULE, sp

STATE = dict(spec=None, corner={}, probe=None, seen=None)


def delay_line(start, end, scale=1, winding_pF=18, shunt_pF=220, mid_pF=330, end_pF=270, start_pF=220):
    """Same interface as sudden_guard.delay_line. Coils and taps come from STATE['spec'].

    CB-008 corner arguments keep their meaning: scale multiplies every inductance,
    winding_pF/18 multiplies every winding capacitance and mid_pF/330 every tap capacitor.
    """
    spec, corner = STATE['spec'], STATE['corner']
    coils, taps = spec['coils'], spec['taps']
    assert len(taps) == len(coils) - 1 and taps.count('mid') == 1
    nodes = [start] + ['mid8' if t == 'mid' else f'g9n{i}' for i, t in enumerate(taps)] + [end]
    cap_scale = mid_pF / 330
    out = [f'CENTRY8 {start} 0 {start_pF}p']
    names = []
    for i, c in enumerate(coils):
        a, b = nodes[i], nodes[i + 1]
        name = 'l8a' if i == 0 else 'l8b' if i == len(coils) - 1 else f'l9n{i}'
        names.append(name)
        mismatch = corner.get('l_mismatch', [1] * len(coils))[i]
        resistance = c['dcr'] * corner.get('r_scale', 1)
        winding = c['cw_pF'] * winding_pF / 18 * corner.get('c_scales', [1]*len(coils))[i]
        out += [f'RW{name} {a} w{name} {resistance}',
                f'{name} w{name} {b} {c["L"] * scale * mismatch}',
                f'CW{name} {a} {b} {winding}p']
        if i < len(taps):
            value = mid_pF if taps[i] == 'mid' else taps[i] * cap_scale * corner.get('tap_scale', 1)
            out.append(f'CTAP9{i} {b} 0 {value}p' if taps[i] != 'mid' else f'CMID8 {b} 0 {value}p')
    if corner.get('k'):
        out += [f'K9{i} {names[i]} {names[i + 1]} {corner["k"]}' for i in range(len(names) - 1)]
    out += [f'CLOCAL8 {end} 0 {end_pF}p', f'CGUARD8 {end} 0 {shunt_pF}p']
    STATE['probe'] = dict(nodes=[n.lower() for n in nodes], coils=names)
    return '\n'.join(out) + '\n'


_cmd = sp.cmd


def cmd(text):
    """Add winding probes to each saved transient and read them before the plot is destroyed."""
    probe = STATE['probe']
    if probe and text.startswith('save '):
        text += ' ' + ' '.join([f'v({n})' for n in probe['nodes']] + [f'i({n})' for n in probe['coils']]
                              )
    if probe and text == 'destroy all':
        t = np.asarray(sp.vector('time'))
        v = [np.asarray(sp.vector(f'v({n})')) for n in probe['nodes']]
        rows = []
        for k, name in enumerate(probe['coils']):
            across = v[k] - v[k + 1]
            current = np.asarray(sp.vector(f'i({name})'))
            j = int(np.argmax(abs(across)))
            above = abs(across) >= abs(across[j]) / 2
            lo = j
            while lo > 0 and above[lo - 1]:
                lo -= 1
            hi = j
            while hi < len(t) - 1 and above[hi + 1]:
                hi += 1
            row = dict(coil=name, peak_V=float(abs(across[j])), at_s=float(t[j]),
                       half_width_us=float((t[hi] - t[lo]) * 1e6),
                       max_dv_dt_V_per_us=float(max(abs(np.diff(across) / np.maximum(np.diff(t), 1e-15))) * 1e-6),
                       peak_A=float(max(abs(current))), end_node_peak_to_ground_V=float(max(max(abs(v[k])), max(abs(v[k + 1])))))
            rows.append(row)
        STATE['seen'] = rows
    _cmd(text)


@contextmanager
def instrument():
    """Restore all original factories and the simulator command on fixture exit."""
    with ExitStack() as stack:
        stack.enter_context(patch.object(sp, 'cmd', cmd))
        for module in (sudden_guard, guard_handover, guard_audio):
            stack.enter_context(patch.object(module, 'delay_line', delay_line))
        yield


def with_coils(result):
    result = dict(result)
    result['windings'] = STATE['seen']
    return result
