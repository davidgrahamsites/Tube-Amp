"""CB-015. One-way common-source bias derived from the negative 15 V audio rail."""
from contextlib import contextmanager
from unittest.mock import patch

import fixed_gain as gain


@contextmanager
def branch(negative_V=15,leak_uA=0,diode_pF=2,seed=None):
    original=gain._load
    def add(net):
        marker='Risol13 island13 0 1gig'
        if marker in net:
            # The audio fixture already has VNEG; independent guard fixtures use its stated nominal value.
            if 'VNEG neg15 0 -15' in net and negative_V==15:
                supply='neg15'
                source=''
            else:
                supply='minus15test'
                source=f'Vs15bias {supply} 0 {-negative_V}\n'
            circuit=source+f'''R15biasA {supply} bias15x 59k
R15biasB bias15x 0 237k
D15steer island13 bias15x steering15
.model steering15 D(is=1n n=1.5 cjo={diode_pF}p vj=.7 m=.4 rs=2 tt=25n)
I15leak 0 island13 {leak_uA}u
'''
            if seed is not None:
                circuit+=f'.nodeset v(island13)={seed} v(gate13)={seed-18} v(bias15x)={seed-.5}\n'
            net=net.replace(marker,circuit+marker)
        original(net)
    with patch.object(gain,'_load',add):
        yield
