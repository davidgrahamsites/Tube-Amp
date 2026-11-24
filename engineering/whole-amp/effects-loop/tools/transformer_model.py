"""Linear coupled-winding experiment; parameters are assumptions, not a part model.
Public seam: winding_lines() and integrated_deck(). Existing ideal decks unchanged.
"""
import math
from fixture import deck

RATIO = math.sqrt(7600 / 8)  # Full-primary to secondary, from original design basis.

def winding_lines(half_primary_H=10, coupling=1, secondary_ohm=0, polarity=1):
    if not half_primary_H > 0 or not 0 < coupling <= 1 or secondary_ohm < 0 or polarity not in [-1, 1]:
        raise ValueError('Invalid linear-transformer experiment parameters')
    secondary_H = half_primary_H / (RATIO / 2)**2
    node = 'SEC_W' if secondary_ohm else 'SPEAKER'
    terminals = f'{node} 0' if polarity == 1 else f'0 {node}'
    lines = [f'LPA PA_W B_MAIN {half_primary_H}',
             f'LPB B_MAIN PB_W {half_primary_H}',
             f'LS {terminals} {secondary_H}', f'KOT LPA LPB LS {coupling}']
    if secondary_ohm:
        lines.append(f'RSEC {node} SPEAKER {secondary_ohm}')
    return lines

def integrated_deck(transformer=None, **config):
    text, inventory = deck(**config)
    lines = text.splitlines()
    remove = ('EPA ', 'EPB ', 'FSA ', 'FSB ')
    found = [line for line in lines if line.startswith(remove)]
    if len(found) != 4:
        raise ValueError('Ideal transformer interface changed; review substitution')
    lines = [line for line in lines if not line.startswith(remove)]
    lines[0] = 'Renegade coupled-winding sensitivity experiment; NOT selected magnetics'
    index = lines.index('.end')
    lines[index:index] = winding_lines(**(transformer or {}))
    return '\n'.join(lines) + '\n', inventory
