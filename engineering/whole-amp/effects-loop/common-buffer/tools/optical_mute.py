"""CB-007 optical mute. Measure capacitive transfer during a bounded 160 V upset."""
import json
from pathlib import Path

import numpy as np
from supply_trial import MODULE, sp


def kick(name, lead, pF, stuck=False, shunt_R=4.7):
    # All timing includes detector + driver allocations, not hot part guarantees.
    # Both shunts become conductive by 3ms; series switch opens after 0.25ms.
    opened=.00025 if not stuck else 1
    rise=.000001
    net=f"""CB-007 mute isolation stress
VUP src 0 PWL(0 0 {lead} 0 {lead+rise} 160)
RISO src a 3300
COUT a common 1.1u
RB common 0 1meg
RLOAD mixer 0 100k
CH mixer 0 500p
VCONTROL c 0 PWL(0 1 {opened} 1 {opened+1e-7} 0)
SPLAY common mixer c 0 playing
CFEED common mixer {pF}p
.model playing sw(ron=30 roff=300meg vt=.5 vh=.01)
VSH s 0 PWL(0 0 .003 0 .0030001 1)
SPRE common pre s 0 shunt
RPRE pre 0 10k
SSH mixer ret s 0 shunt
RSH ret 0 {shunt_R}
.model shunt sw(ron=50 roff=30meg vt=.5 vh=.01)
.end"""
    sp.load(net)
    sp.cmd('tran .2u .008 0 .2u')
    t=sp.vector('time')
    assert t[-1]>=.008-1e-10
    peak=max(abs(np.array(sp.vector('v(mixer)'))))
    sp.cmd('destroy all')
    return dict(case=name,advance_ms=lead*1000,feedthrough_pF=pF,series_stuck_on=stuck,
                receiver_resistor_ohm=shunt_R,step_V=160,edge_us=rise*1e6,peak_mixer_V=peak)


if __name__=='__main__':
    rows=[kick('initial 100 ohm',.005,150,shunt_R=100),kick('loss at command',1e-7,150),kick('qualified lead',.005,30),
          kick('large capacitance',.005,150),kick('failed series contact',.005,150,True)]
    (MODULE/'results/supply-optical-mute.json').write_text(json.dumps(rows,indent=2)+'\n')
