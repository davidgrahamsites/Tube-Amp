"""Explicit experiment deltas; no changes to native circuit or tube coefficients.
Public seam: apply_experiment(deck, options), screen_resistances(deck).
"""
import math
import re

def screen_resistances(text):
    result = {}
    for ref, side in [('R41', 'A'), ('R42', 'B')]:
        match = re.findall(rf'^{ref} B_SCREEN EL34_S{side} ([\d.eE+\-]+)$', text, re.M)
        if len(match) != 1 or not math.isfinite(float(match[0])) or float(match[0]) <= 0:
            raise ValueError('Unexpected screen-resistor interface: '+ref)
        result[side] = float(match[0])
    return result

def apply_experiment(text, options):
    if set(options) - {'screen_ohm', 'solver', 'rails_V'}:
        raise ValueError('Unknown protection experiment')
    screen_resistances(text)
    if 'screen_ohm' in options:
        value = float(options['screen_ohm'])
        if not math.isfinite(value) or value <= 0:raise ValueError('Invalid resistance')
        for ref,side in [('R41','A'),('R42','B')]:
            text, count = re.subn(rf'^{ref} B_SCREEN EL34_S{side} [\d.eE+\-]+$',
                                  f'{ref} B_SCREEN EL34_S{side} {value}', text, flags=re.M)
            assert count == 1
    for source, value in options.get('rails_V', {}).items():
        if source not in {'VMAIN','VSCREEN','VBIAS','VEARLY','VPRE'} or not math.isfinite(value):
            raise ValueError('Invalid rail experiment')
        if (value >= 0) == (source == 'VBIAS'):raise ValueError('Wrong rail polarity')
        text,count=re.subn(rf'^({source} \S+ 0) [\d.eE+\-]+$',rf'\g<1> {value}',text,flags=re.M)
        assert count == 1
    if options.get('solver') == 'iterations':
        text = text.replace('.end\n', '.options itl1=500 itl4=500\n.end\n')
    elif options.get('solver') == 'trap':
        text = text.replace('method=gear maxord=2', 'method=trap maxord=2')
    elif options.get('solver') is not None:
        raise ValueError('Unknown solver experiment')
    return text
