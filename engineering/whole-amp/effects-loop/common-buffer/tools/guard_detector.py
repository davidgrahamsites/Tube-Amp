"""Sense rail loss with physical dividers and compare edge timing to receiver trips."""
import json
import math
import numpy as np
from sudden_guard import MODULE, fault, sp


# The floating receiver drive and the digital latch share a time allocation.
AFTER_CROSSING_US=.40
RAILS={'hv':310.,'pos':15.,'neg':-15.,'five':5.,'twelve':12.}


def measure(rail, edge_us, pin_us, sign, parasitic_pF=7, droop=False, ripple=0):
    origin=2e-6 if sign else 0.
    def ramp(name, initial, final, duration):
        return f'V{name} {name} 0 PWL(0 {initial} {origin} {initial} {origin+duration*1e-6} {final})'
    sources=[ramp(n,v,0,pin_us) if rail in (n,'all') else f'V{n} {n} 0 {v}' for n,v in RAILS.items()]
    if ripple:
        sources=[f'V{n} {n} 0 SIN({v} {ripple*(.06 if n=="hv" else .02)} 100000)' for n,v in RAILS.items()]
    sources.append(ramp('out',0,sign*160,edge_us) if sign else 'Vout out 0 SIN(0 135 20000)')
    net='CB008 compensated pin divider and independent bipolar slew detector\n'+'\n'.join(sources)+f'''
VREF ref 0 2.5
RED sense ref 10k
CED out sense 2.2p
CINPUT sense ref {parasitic_pF}p
DP sense upper clampd
DN lower sense clampd
VUP upper 0 4.65
VLOW lower 0 .35
.model clampd d(is=1n n=1)
RH hv sh 307.2k
RL sh 0 2.49k
CH hv sh 4.7p
CL sh 0 580p
'''
    # Comparator input and routing capacitance are included in the shunt C.
    for n in ['pos','neg','five','twelve']:
        ref='ref' if n in ('pos','neg') else '0'
        low=10 if ref=='ref' else 33
        net+=f'RT{n} {n} s{n} 100k\nRB{n} s{n} {ref} {low}k\nCT{n} {n} s{n} 10p\nCB{n} s{n} {ref} {1000/low}p\n'
    if droop:
        for n in RAILS:
            # AC pin monitor for early loss. The separate DC window still covers a slow sag.
            cap=22 if n=='hv' else 1000
            net+=f'CD{n} {n} ac{n} {cap}p\nRD{n} ac{n} hp{n} 1k\nRBHP{n} hp{n} ref 10k\n'
            net+=f'CBHP{n} hp{n} ref 7p\nDHP{n} hp{n} upper clampd\nDLP{n} lower hp{n} clampd\n'
    net+='.end'
    sp.load(net)
    sp.cmd('save v(sense) v(sh) v(spos) v(sneg) v(sfive) v(stwelve)'+(' '+' '.join(f'v(hp{n})' for n in RAILS) if droop else ''))
    stop=55e-6 if not sign else origin+max(3,pin_us,edge_us)*1e-6
    sp.cmd(f'tran 2n {stop} 0 2n')
    t=np.array(sp.vector('time'))
    assert t[-1]>=stop*(1-1e-8)
    def trace(n):return np.array(sp.vector('v('+n+')'))
    ed=trace('sense')
    thresholds={'edge':abs(ed-2.5)>.7,'hv':trace('sh')<290*2.49/(307.2+2.49),
                'pos':trace('spos')<(13.5+25)/11,'neg':trace('sneg')>(-13.5+25)/11,
                'five':trace('sfive')<4.5*33/133,'twelve':trace('stwelve')<10.8*33/133}
    if droop:
        for n in RAILS:
            change=trace('hp'+n)-2.5
            threshold=.35 if n=='hv' else .06
            thresholds['droop_'+n]=(change if n=='neg' else -change)>threshold
    crossings={k:float((t[np.flatnonzero(a)[0]]-origin)*1e6) for k,a in thresholds.items() if np.any(a)}
    sp.cmd('destroy all')
    arrival=min(crossings.values())+AFTER_CROSSING_US if crossings else None
    row=dict(lost_pin=rail,output_sign=sign,edge_us=edge_us,pin_fall_us=pin_us,
             healthy_ripple_scale=ripple,early_droop_enabled=droop,input_parasitic_pF=parasitic_pF,crossing_from_fault_us=crossings,
             detector_excursion_V=max(abs(ed-2.5)),assumed_downstream_us=AFTER_CROSSING_US,closed_us=arrival)
    if sign and arrival is not None:
        r=fault('linked detector',sign=sign,delay_us=arrival,rise_us=edge_us,
                wire_pF=0,winding_pF=30,shunt_pF=80,scale=.9,shunt_ohm=18)
        row['mixer_peak_V']=r['peak_mixer_V']
    return row


if __name__=='__main__':
    rows=[measure(rail,rise,.5,s) for rail in RAILS for rise in (.05,1.) for s in (-1,1)]
    rows+=[measure(None,1,1,s) for s in (-1,1)]
    rows+=[measure(None,20,1,1),measure(None,1,1,0),* [measure(n,20,4,1) for n in RAILS]]
    (MODULE/'results/guard-detector.json').write_text(json.dumps(rows,indent=2)+'\n')
    print([(r['lost_pin'],r['edge_us'],r['closed_us'],r.get('mixer_peak_V')) for r in rows])
