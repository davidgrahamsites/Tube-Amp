"""Check continuous rail demand after the new load has depleted the reservoir."""
import json
from supply_trial import MODULE, regulator, sp


def screen(trough, load_A):
    net=regulator(trough,.4,5,17.6,True,1.208)
    net=net.replace(f'VRAW raw7 0 {trough}',f'VRAW raw7 0 SIN({trough+5} 5 100)')
    sp.load('CB008 sustained guard load\n'+net+f'ILOAD supply 0 PULSE(.002 {load_A} .1 .0001 .0001 2 4)\n.end')
    sp.cmd('tran .00005 1.5 0 .00005')
    t=sp.vector('time')
    assert t[-1]>=1.5-1e-8
    rail=sp.vector('v(supply)')
    settled=[v for time,v in zip(t,rail) if time>1.4]
    sp.cmd('destroy all')
    return dict(raw_trough_V=trough,load_mA=load_A*1000,settled_min_V=min(settled),settled_max_V=max(settled))


if __name__=='__main__':
    rows=[screen(raw,load) for raw in (340,350,390) for load in (.014,.0165)]
    (MODULE/'results/guard-sustained.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(rows)
