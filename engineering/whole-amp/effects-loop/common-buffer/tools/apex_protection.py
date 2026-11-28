"""CB-006 follow-up. Inspect return ratio, short losses and a soft supply."""
import json
import numpy as np
from apex_return import M, deck, sp


def fixture(rail=310,pf=500,temp=25,short=False,cc=4.7):
    return deck(20000,135,pf,rail,3300,cc,short,temp,False,'PA340',True,True)


def margin(pf, temp, stray):
    net=fixture(pf=pf,temp=temp)
    net=net.replace('ac 1 SIN','ac 0 SIN').replace('RF1 preout rfmid','VLOOP inject preout DC 0 AC 1\nRF1 inject rfmid')
    if stray:
        net=net.replace('RF2 rfmid minus',f'CSTRAY inject minus {stray}p\nRF2 rfmid minus')
    sp.load(net)
    sp.cmd('ac dec 100 1 100meg')
    f=np.real(sp.vector('frequency'))
    t=-np.array(sp.vector('v(preout)'))/np.array(sp.vector('v(inject)'))
    phase=np.unwrap(np.angle(t))*180/np.pi
    mag=np.log(abs(t))
    idx=np.where(np.diff(mag>0))[0]
    margins=[]
    for i in idx:
        frac=mag[i]/(mag[i]-mag[i+1])
        margins.append(dict(hz=f[i]*(f[i+1]/f[i])**frac,deg=180+phase[i]+frac*(phase[i+1]-phase[i])))
    sp.cmd('destroy all')
    return dict(pF=pf,temp_C=temp,feedback_stray_pF=stray,crossings=margins)


def load_test(rail, short, soft, temp):
    net=fixture(rail=rail,short=short,temp=temp)
    if soft:
        net=net.replace('VREC supply 0','RSOURCE6 rawhv supply 600\nCRES supply 0 4.7u\nVREC rawhv 0')
    sp.load(net)
    sp.cmd('save v(preout) v(coupling) v(fx_return) v(supply) v(plus) i(vrec) i(vchip) i(vmon)')
    step=1/20000/320
    end=.006
    sp.cmd(f'tran {step} {end} 0 {step}')
    t=np.array(sp.vector('time'))
    assert t[-1]>=end*(1-1e-8)
    points=end+(np.arange(4096)/409.6-10)/20000
    def v(name): return np.interp(points,t,sp.vector(name))
    out, coupling, port, supply, plus, src, chip, port_i=map(v,
        ['v(preout)','v(coupling)','v(fx_return)','v(supply)','v(plus)','i(vrec)','i(vchip)','i(vmon)'])
    iso_i=(out-coupling)/3300
    # Capacitor ripple current has zero mean at settled DC. Direct chip power below uses stiff tests only.
    harm=2*abs(np.fft.rfft(port)/len(port))[np.arange(1,11)*10]
    row=dict(rail_V=rail,short=short,soft=soft,temp_C=temp,loaded_rail_min_V=min(supply),
             port_Vpk=harm[0],gain_error_dB=20*np.log10(harm[0]/135),thd_percent=100*np.linalg.norm(harm[1:])/harm[0],
             iso_peak_mA=1000*max(abs(iso_i)),chip_peak_mA=1000*max(abs(chip)),
             resistor_W=np.mean(iso_i**2)*3300, max_port_mA=max(abs(port_i))*1000)
    if not soft:row['chip_W']=np.mean(-supply*src-supply*(supply-plus)/470000-out*chip)
    sp.cmd('destroy all')
    return row


if __name__=='__main__':
    margins=[margin(p,t,c) for p,t,c in [(0,25,0),(500,25,0),(500,85,0),(500,85,1),(2000,85,1)]]
    runs=[load_test(*x) for x in [(310,False,True,25),(279,False,True,25),(320,True,False,85)]]
    (M/'results/apex-protection.json').write_text(json.dumps(dict(margins=margins,runs=runs),indent=2)+'\n')
