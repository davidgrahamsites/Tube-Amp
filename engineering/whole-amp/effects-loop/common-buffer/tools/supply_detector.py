"""CB-007 independent OV detector using the TI comparator model and a pass short."""
import hashlib
import json
from pathlib import Path
import numpy as np
from supply_trial import MODULE, sp

MODEL=MODULE.parents[2]/'component-selection/heater-divider-rating/sources/LM2903B.lib'


def fault(name, corner, delay, broken_sense=False):
    # Bias/offset error extremes are applied separately in supply_faults.py.
    rt, rb, ref=(328000*1.004,2490*.996,2.5*1.009) if corner else (328000,2490,2.5)
    if broken_sense:
        rt=1e12
    macro=MODEL.read_text().replace('TC=0,0','')
    net=f"""CB-007 440V pass-short comparator trial
.func if(c,a,b) {{c ? a : b}}
{macro}
VRAW raw 0 PWL(0 310 1m 310 1.0001m 440)
RFIX raw feed 1729
SSER feed hv drive 0 relay7
.model relay7 sw(ron=.01 roff=1gig vt=2.5 vh=.001)
CPOST hv 0 17.6u
RBLEED hv 0 360k
RSENSE hv sense {rt}
RBOT sense 0 {rb}
CSENSE sense 0 1n
VREF ref 0 {ref}
VLOGIC logic 0 5
XCOMP ref sense logic 0 comp LM2903B
RPULL logic comp 4.7k
CLOAD comp 0 100p
SCLR latch 0 logic comp clear7
.model clear7 sw(ron=2 roff=1e15 vt=2.5 vh=.001)
RLATCH logic latch 1g
CLATCH latch 0 100n
EBUF buff 0 latch 0 1
RDELAY buff drive 1k
CDELAY drive 0 {delay/(1000*np.log(2))}
.options method=gear
.end"""
    sp.cmd('set ngbehavior=psa')
    sp.load(net)
    sp.cmd('save v(hv) v(comp) v(latch) v(drive) v(sense)')
    sp.cmd('tran 1u 40m 0 1u')
    t=np.array(sp.vector('time'))
    assert t[-1]>=.04-1e-10, sp.logs[-5:]
    hv, cmp, drive, sense=[np.array(sp.vector(f'v({x})')) for x in ['hv','comp','drive','sense']]
    def crossing(mask):
        return t[np.flatnonzero(mask)[0]] if mask.any() else None
    a,b,c=crossing(sense>=ref),crossing(cmp<2.5),crossing(drive<2.5)
    row=dict(case=name,cap_uF=17.6,peak_V=max(hv),initial_V=hv[0],reached_s=t[-1],
             sense_s=a,clear_s=b,disconnect_s=c,latch_final_V=sp.vector('v(latch)')[-1],
             timing_surrogate_ms=delay*1000,deck_sha256=hashlib.sha256(net.encode()).hexdigest())
    sp.cmd('destroy all')
    return row


if __name__=='__main__':
    tests=[('nominal trip',False,.0019),('high threshold',True,.0019),
           ('extended actuation',True,.010),('top divider open',False,.0019,True)]
    out=dict(model_sha256=hashlib.sha256(MODEL.read_bytes()).hexdigest(),runs=[fault(*t) for t in tests])
    (MODULE/'results/supply-detector.json').write_text(json.dumps(out,indent=2)+'\n')
