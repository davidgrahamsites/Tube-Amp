"""Bias and capacitance of an opposed IXTP3N50D2 pair. CB-012 screening model."""
from contextlib import contextmanager
from unittest.mock import patch

import fixed_gain as gain

# Approximate graph readings, DS100148D, Fig. 13. Last two columns are pF.
# The 25 V point is from the table. Use a constant tail above 40 V as a sensitivity.
FIGURE = [(0, 2350, 1000), (1, 1690, 850), (3, 1170, 700), (5, 870, 570),
          (9, 630, 390), (10, 540, 315), (11, 435, 200), (12, 320, 102),
          (13, 235, 64), (15, 152, 43), (20, 118, 29), (25, 102, 24),
          (30, 92, 22), (40, 80, 18)]


def charge_expr(voltage, caps):
    """Integral of a piecewise linear differential capacitance. Constant at both ends."""
    # Integrate slopes using shifted squared ramps. Values are in pC before scaling.
    slopes = [(b-a)/(FIGURE[i+1][0]-FIGURE[i][0]) for i,(a,b) in enumerate(zip(caps,caps[1:]))]
    terms = [f'{caps[0]:.12g}*({voltage})']
    for (x,_,_), before, after in zip(FIGURE, [0.]+slopes, slopes+[0.]):
        if after != before:
            terms.append(f'({(after-before)/2:.12g})*max(({voltage})-({x}),0)^2')
    return '('+'+'.join(terms)+')'


def device_caps(drain,source,gate,tag,scale,offset):
    # Qgd uses Vdg minus an assumed gate-bias offset. Vgs=-offset puts both
    # curve arguments on the printed Vds axis. Vgs dependence is uncharacterized.
    ds = charge_expr(f'v({drain},{source})',[c-r for _,c,r in FIGURE])
    dg = charge_expr(f'v({drain},{gate})-{offset}',[r for _,_,r in FIGURE])
    return f'Cds{tag} {drain} {source} Q=\'{scale}p*{ds}\'\nCdg{tag} {drain} {gate} Q=\'{scale}p*{dg}\''


@contextmanager
def device(bias=0.,ohm=100000.,leak_uA=0.,scale=1.,offset=6.2):
    original = gain.sp.load
    def inject(net):
        if 'D8A island8' in net:
            old=net[net.index('D8A island8'):net.index('RISO8 island8 0 1gig')+len('RISO8 island8 0 1gig')]
            net=net.replace(old, '''D8A island8 FX_RETURN d12
D8B island8 0 d12
.model d12 D(is=1n n=1.4 rs=.1)
Vgate12 gate12 island8 -6.2
Ciso12 island8 0 6p
Rdrift12 island8 0 1gig
'''+device_caps('FX_RETURN','island8','gate12','a',scale,offset)+'\n'
                +device_caps('0','island8','gate12','b',scale,offset))
            if bias:
                net=net.replace('Rdrift12',f'Vbias12 b12 0 {-bias}\nRbias12 b12 island8 {ohm}\nIleak12 0 island8 {leak_uA}u\nRdrift12')
        original(net)
    with patch.object(gain.sp,'load',inject):
        yield


@contextmanager
def switch_charge(bias,ohm,leak_uA,scale,offset,first_threshold=-3,second_threshold=-3):
    """Replace the injection fixture's fixed charge by the same two drain laws."""
    original = gain.sp.load
    def inject(net):
        if 'CGA gate mix' in net:
            start, end = net.index('CGA gate mix'), net.index('DRA island mix')
            # The old fixture's ratio parameter scales just the signal-side Miller branch.
            mismatch=float(net[start:].splitlines()[0].split()[-1][:-1])/64
            a=device_caps('mix','island','gate','a',scale,offset)
            ds,dg=a.splitlines()
            dg=dg.replace(f'{scale}p*',f'{scale*mismatch}p*')
            parts=[ds,dg,device_caps('retour','island','gate','b',scale,offset)]
            if bias:
                parts += [f'Vbias12 b12 0 {-bias}', f'Rbias12 b12 island {ohm}',f'Ileak12 0 island {leak_uA}u']
            net=net[:start]+'\n'.join(parts)+'\n'+net[end:]
            net=net.replace('SB retour island gate island dmos','SB retour island gate island dmosB')
            net=net.replace('vt=-3 vh=.05)',f'vt={first_threshold} vh=.05)\n.model dmosB sw(ron=2 roff=100meg vt={second_threshold} vh=.05)')
        original(net)
    with patch.object(gain.sp,'load',inject):
        yield
