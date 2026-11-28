"""CB-008 passive delay and fast receiver shunt, with CB-007 optical handover."""
import hashlib
import json
from pathlib import Path

import numpy as np
from supply_trial import MODULE, sp

# Coilcraft RFC1010B-475KE and -106KE. Use maximum room-temperature DCR.
def delay_line(start, end, scale=1, winding_pF=18, shunt_pF=220, mid_pF=330, end_pF=270, start_pF=220):
    return f"""CENTRY8 {start} 0 {start_pF}p
RWD1 {start} w8a 7
L8A w8a mid8 {4.7e-3*scale}
CW1 {start} mid8 {winding_pF}p
CMID8 mid8 0 {mid_pF}p
RWD2 mid8 w8b 15.5
L8B w8b {end} {.010*scale}
CW2 mid8 {end} {winding_pF}p
CLOCAL8 {end} 0 {end_pF}p
CGUARD8 {end} 0 {shunt_pF}p
"""


def fault(label, sign=1, delay_us=.5, rise_us=1., wire_pF=500, bypass_pF=.35,
          shunt_ohm=10, scale=1, winding_pF=18, live_phase=None, fine=False, current_limit=None, **line):
    t0=(4+live_phase/360)/20000 if live_phase is not None else 1e-6
    t1=t0+rise_us*1e-6
    onset=t0+delay_us*1e-6
    stop=t0+max(30,rise_us+10,delay_us+5)*1e-6
    if live_phase is None:
        source=f'VFAULT src 0 PWL(0 0 {t0} 0 {t1} {sign*160})'
    else:
        source=f'BFAULT src 0 V=135*sin(2*pi*20000*time)+{sign*160}*max(0,min(1,(time-{t0})/{t1-t0}))'
    net=f"""CB008 sudden fault
{source}
RISO src cap8 {3300*.95}
CBLOCK cap8 common 1.1u
RKEEP common 0 1meg
RSER common play 30
{delay_line('play','mix',scale,winding_pF,**line)}
CBYP src mix {bypass_pF}p
CH mix 0 {max(wire_pF,.001)}p
RMIX mix 0 100k
VTRIP cmd 0 PWL(0 0 {onset} 0 {onset+10e-9} 1)
SSH mix imon cmd 0 guard
VMON imon 0 0
.model guard sw(ron={shunt_ohm} roff=1e9 vt=.5 vh=.01)
.end"""
    if current_limit:
        net=net.replace('SSH mix imon','SSH limited8 imon').replace(f'ron={shunt_ohm} ', 'ron=.01 ')
        net=net.replace('VMON imon',f'BLIM mix limited8 i={current_limit}*tanh(v(mix,limited8)/{current_limit*shunt_ohm})\nVMON imon')
    sp.load(net)
    sp.cmd('save v(mix) i(vmon) i(l8a) i(l8b) v(src)')
    dt=1e-9 if fine else 4e-9
    sp.cmd(f'tran {dt} {stop} 0 {dt}')
    t=np.asarray(sp.vector('time'))
    assert t[-1]>=stop*(1-1e-9)
    use=t>=t0
    mix=np.asarray(sp.vector('v(mix)'))[use]
    current=np.asarray(sp.vector('i(vmon)'))[use]
    post=t[use]>=onset+.1e-6
    r=dict(case=label,sign=sign,delay_us=delay_us,rise_us=rise_us,harness_pF=wire_pF,
           line_caps_pF=line,feedthrough_pF=bypass_pF,shunt_ohm=shunt_ohm,inductance_scale=scale,
           current_limit_A=current_limit,winding_pF=winding_pF,phase_deg=live_phase,timestep_ns=dt*1e9,
           peak_mixer_V=max(abs(mix)),post_switch_peak_V=max(abs(mix[post])),
           peak_shunt_A=max(abs(current)),shunt_energy_uJ=np.trapezoid(mix*current,t[use])*1e6,
           max_coil_A=max(max(abs(np.asarray(sp.vector(n)))) for n in ['i(l8a)','i(l8b)']),
           reached_s=t[-1],deck_sha256=hashlib.sha256(net.encode()).hexdigest())
    sp.cmd('destroy all')
    return r


if __name__=='__main__':
    rows=[fault('nominal'),fault('negative',-1),fault('fast edge',rise_us=.05),
          fault('short harness corner',wire_pF=0,scale=.9,winding_pF=30,shunt_pF=80),
          fault('short harness fast edge',rise_us=.05,wire_pF=0,scale=.9,winding_pF=30,shunt_pF=80),
          fault('unshielded 2pF',bypass_pF=2,rise_us=.05,wire_pF=0,scale=.9,winding_pF=30,shunt_pF=80),
          fault('late detector',delay_us=2),fault('missed detector',delay_us=25),
          fault('hot shunt',shunt_ohm=18),fault('stray feedthrough',bypass_pF=15),
          fault('refined nominal',fine=True),
          fault('combined quiet corner',rise_us=.05,wire_pF=0,scale=.9,winding_pF=30,shunt_pF=50,
                end_pF=256.5,mid_pF=313.5,start_pF=209,shunt_ohm=18,fine=True)]
    rows.extend(fault('playing',sign=s,live_phase=p) for s in (-1,1) for p in (0,90,180,270))
    rows.extend(fault('playing current limited',sign=s,live_phase=p,current_limit=3) for s in (-1,1) for p in (0,90,180,270))
    (MODULE/'results/sudden-guard.json').write_text(json.dumps(rows,indent=2)+'\n')
    print([(r['case'],round(r['peak_mixer_V'],3),round(r['peak_shunt_A'],2)) for r in rows])
