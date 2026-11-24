"""Linear output-transformer/feedback experiments, never a selected part model.
Public seam: build(params, state, **fixture_config) -> SPICE text.
Lm and leakage are independently primary-referred; capacitance is one lump.
"""
import math
from transformer_model import integrated_deck

DEFAULTS = dict(magnetizing_H=40., leakage_H=.02, primary_cap_F=250e-12,
                secondary_ohm=.2, load_ohm=8., load_cap_F=0., presence=.5, pi_cap_F=None, feedback_cap_F=0.)

def build(params=None, state='closed', **config):
    p = dict(DEFAULTS, **(params or {}))
    if state not in ('closed', 'open', 'injection'): raise ValueError(state)
    if not 0 <= p['presence'] <= 1 or p['load_ohm'] <= 0: raise ValueError(p)
    if any(p[k] < 0 for k in ('leakage_H','primary_cap_F','secondary_ohm','load_cap_F')) or p['magnetizing_H'] <= 0: raise ValueError(p)
    legacy = p.get('legacy_transformer')
    tx = legacy if legacy is not None else dict(half_primary_H=p['magnetizing_H']/4,
                  coupling=1, secondary_ohm=p['secondary_ohm'])
    text, _ = integrated_deck(tx, **dict(dict(mode='return-drive', amp=0, guard_pentode_power=True), **config))
    lines = text.splitlines(); extra=[]
    if legacy is None and p['leakage_H']:
        # Symmetric series leakage; each half sums to full-primary Lsc.
        lines = [x.replace('LPA PA_W ', 'LPA PA_CORE ').replace('LPB B_MAIN PB_W ', 'LPB B_MAIN PB_CORE ') for x in lines]
        extra += [f'LLA PA_W PA_CORE {p["leakage_H"]/2}', f'LLB PB_CORE PB_W {p["leakage_H"]/2}']
    if legacy is None and p['primary_cap_F']: extra += [f'CPR PA_W PB_W {p["primary_cap_F"]}']
    if p['feedback_cap_F']: extra += [f'CFB OT_4 NFB_NODE {p["feedback_cap_F"]}']
    if p['load_cap_F']: extra += [f'CLOAD SPEAKER 0 {p["load_cap_F"]}']
    out=[]
    for x in lines:
        if x.startswith('C22 ') and p['pi_cap_F'] is not None: x=f'C22 PI_P1 PI_P2 {p["pi_cap_F"]}'
        if x.startswith('RLOAD '): x=f'RLOAD SPEAKER 0 {p["load_ohm"]}'
        if x.startswith('RV9A '): x=f'RV9A PRES_TOP 0 {max(1,25000*(1-p["presence"]))}'
        if x.startswith('VSOURCE '): x=x.replace(' AC 1',' AC 0')
        if x.startswith('VTEST ') and state=='injection': x=x.replace(' AC 1',' AC 0')
        if x.startswith('ENFB ') and state!='closed': x=f'VNFB OT_4 0 DC 0 AC {1 if state=="injection" else 0}'
        if x=='.end': out.extend(extra)
        out.append(x)
    return '\n'.join(out)+'\n'

def legacy_inductances(half, k):
    # From three-winding inductance matrix with every pair sharing k.
    return dict(open_primary_H=2*half*(1+k),
                shorted_secondary_primary_H=2*half*(1+k-2*k*k))
