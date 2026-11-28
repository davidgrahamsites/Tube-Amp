"""Differential feedthrough from a floating gate drive into the silent mixer."""
import json
import numpy as np
from sudden_guard import MODULE, delay_line, sp


def run(step, mismatch, off_V, reverse=False, slow=False, clamp=False, cscale=1):
    off=-off_V
    start,finish=(0,off) if reverse else (off,0)
    edge=20 if not slow else 6000
    net=f"""Gate-drive displacement current and winding network
VS src 0 PWL(0 0 2u 0 2.05u {step})
RISO src cap8 3135
CBLK cap8 play 1.1u
RKEEP play 0 1meg
RPLAY play line 30
{delay_line('line','mix',scale=.9,winding_pF=30,shunt_pF=.001)}
CBYP src mix .35p
RMIX mix 0 100k
RSH retour 0 6.8
CGISE island 0 6p
VDR gate island PWL(0 {start} 2.40u {start} {2.4+edge/1000}u {finish})
CGA gate mix {64*mismatch*cscale}p
CGB gate retour {64*cscale}p
CSA island mix {191*cscale}p
CSB island retour {191*cscale}p
DRA island mix db
DRB island retour db
.model db d(is=1n n=1.5)
SA mix island gate island dmos
SB retour island gate island dmos
.model dmos sw(ron=2 roff=100meg vt=-3 vh=.05)
RPLAYMIX mix 0 {54.7 if clamp else 1e9}
.end"""
    sp.load(net)
    sp.cmd('save v(mix) v(gate) v(island)')
    sp.cmd('tran 1n 15u 0 1n')
    t=np.array(sp.vector('time'))
    assert t[-1]>=14.999e-6
    v=np.array(sp.vector('v(mix)'))
    sp.cmd('destroy all')
    return dict(step_V=step,capacitance_scale=cscale,Crss_ratio=mismatch,off_bias_V=off,release=reverse,
                driver_transition_ns=edge,slow_optical_shunt_closed=clamp,peak_V=max(abs(v)))


if __name__=='__main__':
    rows=[run(step,m,b) for b in (12,6) for step in (0,-160,160) for m in (.5,1,2)]
    rows.extend(run(0,m,b,True,slow,clamp) for m in (.5,2) for b in (6,12)
                for slow,clamp in [(False,False),(True,True)])
    rows.extend(run(step,m,6.2,cscale=k) for step in (-160,0,160) for m in (.5,2) for k in (1,2,4))
    (MODULE/'results/guard-injection.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(rows)
