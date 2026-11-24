"""Reciprocal tapped-secondary experiment; not a selected transformer model.

Public seam: build(params, **fixture_config) -> SPICE deck.
Retains original Output/Presence interfaces. Existing fixtures are unchanged.
"""
import math

from feedback_model import DEFAULTS, build as baseline

TAP_FRACTION = 1 / math.sqrt(2)


def build(params=None, **config):
    p = dict(DEFAULTS, **(params or {}))
    if p.get('legacy_transformer') is not None:
        raise ValueError('This experiment requires independent magnetic parameters')
    if config.get('feedback_phase', 1) != 1:
        raise ValueError('Reverse winding polarity requires an explicit winding model')
    damping = p.get('damping_RC')
    if damping is not None and (len(damping) != 2 or min(damping) <= 0):
        raise ValueError('Damping branch requires positive series R and C')
    text = baseline(p, 'closed', **config)
    lines = text.splitlines()
    secondary_H = p['magnetizing_H'] / (7600 / 8)
    lower = secondary_H * TAP_FRACTION**2
    upper = secondary_H * (1 - TAP_FRACTION)**2
    copper = p['secondary_ohm']
    # The shorting links are voltage sources at zero resistance, avoiding
    # illegal zero-valued resistors and preserving exact no-loss test limits.
    windings = [
        f'LSLOW TAP_CORE 0 {lower}',
        f'LSHIGH SEC_HIGH OT_4 {upper}',
        'KOT LPA LPB LSLOW LSHIGH 1',
        f'RSLOW TAP_CORE OT_4 {copper*TAP_FRACTION}' if copper else 'VSLOW TAP_CORE OT_4 0',
        f'RSHIGH SEC_HIGH SPEAKER {copper*(1-TAP_FRACTION)}' if copper else 'VSHIGH SEC_HIGH SPEAKER 0',
    ]
    removed = ('LS ', 'KOT ', 'RSEC ', 'ENFB ')
    assert sum(x.startswith('LS ') for x in lines) == 1
    assert sum(x.startswith('ENFB ') for x in lines) == 1
    lines = [x for x in lines if not x.startswith(removed)]
    if damping:
        windings += [f'RDAMP SPEAKER DAMP_MID {damping[0]}',
                     f'CDAMP DAMP_MID 0 {damping[1]}']
    lines[0] = 'Renegade reciprocal tapped-secondary experiment; NOT selected magnetics'
    lines[lines.index('.end'):lines.index('.end')] = windings
    return '\n'.join(lines) + '\n'


def split_probe(text):
    """Separate the physical tap from R31/optional CFB receiver at OT_4.

    Returns a deck with open ports OT_4 (receiver) and TX_TAP (transformer).
    Only emitted secondary components are edited; the native block is intact.
    """
    lines = []
    for line in text.splitlines():
        if line.startswith(('LSHIGH ', 'RSLOW ', 'VSLOW ')):
            line = line.replace(' OT_4 ', ' TX_TAP ')
        lines.append(line)
    assert sum('TX_TAP' in x for x in lines) == 2
    return '\n'.join(lines) + '\n'
