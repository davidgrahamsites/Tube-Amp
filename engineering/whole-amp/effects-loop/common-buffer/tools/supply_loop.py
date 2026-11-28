"""CB-007. Check the proposed analog regulator independently of the audio model."""
import json
import numpy as np
from supply_trial import MODULE, regulator, sp


def probe(raw, bypass, ctr, cap, original=False):
    net = regulator(raw, ctr, 4, cap, bypass, 1.208)
    if original:
        net=net.replace('CFB7 drive7 comp7 100n\nRCOMP7 comp7 inv7 100k', 'CFB7 drive7 inv7 10n')
    # Insert a series AC test source at the ideal, low-impedance error output.
    net = net.replace('BDRIVE drive7 0', 'VINJ drive7 ctrl7 dc 0 ac 1\nBDRIVE ctrl7 0')
    # Keep the local op-amp feedback closed; break only the outer optical loop.
    net = net.replace('RFB7 drive7', 'RFB7 ctrl7').replace('CFB7 drive7','CFB7 ctrl7')
    sp.load('Regulator return ratio\n'+net+'RLOAD supply 0 60k\n.end')
    sp.cmd('ac dec 80 .1 10meg')
    freq=np.real(sp.vector('frequency'))
    gain=-np.array(sp.vector('v(ctrl7)'))/np.array(sp.vector('v(drive7)'))
    phase=np.unwrap(np.angle(gain))*180/np.pi
    level=np.log(np.maximum(abs(gain),1e-25))
    crossings=[]
    for i in np.where(np.diff(level>0))[0]:
        fraction=level[i]/(level[i]-level[i+1])
        crossings.append(dict(hz=freq[i]*(freq[i+1]/freq[i])**fraction,
                              margin_deg=180+phase[i]+fraction*(phase[i+1]-phase[i])))
    sp.cmd('destroy all')
    return dict(raw_V=raw,bypass=bypass,CTR=ctr,cap_uF=cap,dc_gain_dB=20*level[0]/np.log(10),crossings=crossings)


def transient(raw, bypass, ctr, cap, sustained=False):
    net=regulator(raw,ctr,4,cap,bypass,1.208)
    net=net.replace(f'VRAW raw7 0 {raw}',f'VRAW raw7 0 SIN({raw+5} 5 100)')
    pulse_width=1.5 if sustained else .1
    end=1.5 if sustained else .4
    sp.load('Load step and raw ripple\n'+net+f'ILOAD supply 0 PULSE(.002 .008 .1 .0001 .0001 {pulse_width} 3)\n.end')
    sp.cmd(f'tran .0001 {end} 0 .0001')
    t=np.array(sp.vector('time'))
    assert t[-1] >= end-1e-7, sp.logs[-6:]
    rail=np.array(sp.vector('v(supply)'))
    sp.cmd('destroy all')
    return dict(raw_trough_V=raw, bypass=bypass, CTR=ctr, cap_uF=cap,
                rail_min_V=min(rail),rail_max_V=max(rail),end_V=rail[-1],reached_s=t[-1])


if __name__=='__main__':
    cases=[(340,True,.4,17.6),(390,True,1,44),(440,False,2,35.2),(440,True,2,52.8)]
    out=dict(initial_10nF=[probe(*c,original=True) for c in cases],loop=[probe(*c) for c in cases], load_step=[transient(*c) for c in cases])
    # Compare the initial bypass rule with a closed bypass at intermediate line.
    out['transition_load_step']=[transient(raw,bypass,.4,35.2) for raw in [400,405,410,415,420]
                                 for bypass in [False,True]]
    out['sustained_load']=[transient(raw,bypass,.4,35.2,True) for raw in [400,410,420,430,440]
                           for bypass in [False,True]]
    (MODULE/'results/supply-loop.json').write_text(json.dumps(out,indent=2)+'\n')
