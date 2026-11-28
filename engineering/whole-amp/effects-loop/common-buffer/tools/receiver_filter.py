"""CB-016 receiver filter and source-referenced gate resistors for the archived SiC pair."""
from contextlib import contextmanager
from unittest.mock import patch

import fixed_gain as gain


@contextmanager
def receiver_filter(series_diodes, *, split=False, method='trap'):
    """Keep the cable, winding and mute on the input side. Sense the downstream mixer."""
    original = gain._load

    def connect(net):
        lines = net.splitlines()
        end = next(line.split()[1] for line in lines if line.startswith('X13A '))
        upstream = {'l8b', 'cwl8b', 'x13a', 'ch', 'charness', 'clocal8', 'cguard8',
                    'cnc2', 'rno7', 'rplaymix'}
        for index, line in enumerate(lines):
            fields = line.split()
            if fields and fields[0].lower() in upstream:
                lines[index] = ' '.join('fast16' if token.lower() == end.lower() else token for token in fields)
            if split and line.startswith('X13B '):
                fields[2] = 'groundgate16'
                lines[index] = ' '.join(fields)
            if split and line.startswith('Rgate13 '):
                lines[index] = (f'Rdriver16 cmd13 fork16 {fields[-1]}\n'
                                'Rsignal16 fork16 gate13 1\nRground16 fork16 groundgate16 .1')
        # Direct PA-to-mixer stray remains on the protected side.
        components = [f'Rpass16 fast16 {end} {3300 if split else 1800}', f'Cpass16 {end} 0 220p',
                      '.model proxy16 d(is=2n n=1.7 rs=1 cjo=2p tt=4n)',
                      f'.options method={method} maxord=2']
        for tag, start, stop in [('up', 'fast16', end), ('down', end, 'fast16')]:
            nodes = [start] + [f'{tag}16{i}' for i in range(1, series_diodes)] + [stop]
            components.extend(f'D{tag}16{i} {a} {b} proxy16' for i, (a, b) in enumerate(zip(nodes, nodes[1:])))
            if split:
                components.extend([f'D{tag}slow16 {start} {tag}R16 proxy16', f'R{tag}slow16 {tag}R16 {stop} 100'])
        idx = lines.index('.end')
        lines[idx:idx] = components
        probe = gain.pulse_winding.STATE['probe']
        if probe and probe['nodes'][-1] == end.lower():
            probe['nodes'][-1] = 'fast16'
        original('\n'.join(lines))

    with patch.object(gain, '_load', connect):
        yield
