"""CB-018. Four-diode signal bridge with one normally-on SiC switch across its DC terminals."""
from contextlib import contextmanager
from unittest.mock import patch

import fixed_gain as gain


@contextmanager
def bridge(held_V=1.8, terminal_pF=270, pedestal=True, junction_pF=30, transit_ns=25,
           mismatch=1.2, method='trap'):
    original = gain._load

    def add(net):
        lines = net.splitlines()
        first = next(i for i,line in enumerate(lines) if line.startswith('X13A '))
        second = next(i for i,line in enumerate(lines) if line.startswith('X13B '))
        signal, tail = lines[first].split()[1], lines[second].split()[1]
        lines[first]='X13A plus18 gate13 island13 UJ3N065080K3S'
        # Current in either signal direction flows through the switch from drain to source.
        lines[second]=f'''D18a {signal} plus18 bridge18a
D18b {tail} plus18 bridge18b
D18c minus18 {signal} bridge18b
D18d minus18 {tail} bridge18a
Vhold18 minus18 rail18 {held_V}
Rlimit18 rail18 island13 2.2
Rleak18 plus18 minus18 22meg
Cterminal18 {signal} 0 {terminal_pF}p
.model bridge18a D(is=5n n=1.65 rs=.2 cjo={junction_pF}p m=.4 tt={transit_ns}n bv=400 ibv=10u)
.model bridge18b D(is={5*mismatch}n n=1.65 rs=.2 cjo={junction_pF*mismatch}p m=.4 tt={transit_ns}n bv=400 ibv=10u)'''
        extra=[f'.options method={method} maxord=2']
        if pedestal:
            # The protected PA fixture already contains the audio rails.
            for name,voltage in [('pos15',15),('neg15',-15)]:
                if not any(l.lower().startswith('v') and l.lower().split()[1:3] == [name,'0'] for l in lines):
                    extra.append(f'V18{name} {name} 0 {voltage}')
            extra.extend(['Rhi18 pos15 high18 150k', 'Rhi018 high18 0 100k',
                          'Rpa18 high18 an18 39k', 'Dparkp18 an18 plus18 park18',
                          'Rlo18 neg15 low18 150k', 'Rlo018 low18 0 100k',
                          'Rna18 ca18 low18 39k', 'Dparkn18 minus18 ca18 park18',
                          '.model park18 D(is=1n n=1.5 cjo=2p rs=2 tt=25n)'])
        lines[lines.index('.end'):lines.index('.end')]=extra
        original('\n'.join(lines))

    with patch.object(gain,'_load',add):
        yield
