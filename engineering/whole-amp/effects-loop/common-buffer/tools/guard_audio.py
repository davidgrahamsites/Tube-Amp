"""Drive the CB-008 guard from the accepted Apex/TI fixture into the full mixer."""
import json
import numpy as np
from supply_trial import regulator
from apex_return import deck
from sudden_guard import delay_line, MODULE, sp


def audio(f, harness, shunt, series_off, short=False, temp=25, rail=310, nonlinear=False, scale=1, raw=None, feedback=39700):
    net=deck(f,135,harness,rail,3300,4.7,short,temp,False,'PA340',True,True)
    net=net.replace('RLOW2 low invlow 40200',f'RLOW2 low invlow {feedback}')
    net=net.replace('VMON port FX_RETURN 0',f'''VMON port driver8 0
RDRV driver8 line8 30
CNC1 port precharge8 {series_off}p
RPRE precharge8 0 10k
CNC2 FX_RETURN midsh8 {series_off}p
RSH8 midsh8 0 4.7
RNO7 FX_RETURN 0 1meg
RPORT7 port portref7 1meg
VPORTREF7 portref7 0 2.5
RBIAS7 preout 0 2meg
CSTRAY8 preout FX_RETURN .35p
'''+delay_line('line8','FX_RETURN',shunt_pF=shunt,scale=scale))
    if nonlinear:
        # Charge storage of two opposed drain/body junctions. Match 255 pF per drain at 25 V.
        # Common-source island can charge on signal peaks. Include isolated supply stray.
        net=net.replace(f'CGUARD8 FX_RETURN 0 {shunt}p',f'''D8A island8 FX_RETURN djunction8
D8B island8 0 djunction8
.model djunction8 D(is=1n n=1.4 cjo={shunt}p m=.5 vj=1 rs=.1)
CISO8 island8 0 6p
RISO8 island8 0 1gig''')
    net=net.replace('XPOWER plus minus supply 0', 'VHV8 supply chiprail8 0\nXPOWER plus minus chiprail8 0')
    if raw:
        net=net.replace(f'VREC supply 0 {rail}', regulator(raw,.4 if raw==340 else 1,5 if raw==340 else 4,17.6 if raw==340 else 44,True,1.208))
        net=net.replace('.end\n','.nodeset v(supply)=310 v(preout)=155 v(drive7)=2 v(mg7)=314\n.end\n')
    sp.load(net)
    sp.cmd('op')
    op=sp.vector('v(preout)')
    assert op, (f,harness,shunt,raw,sp.logs[-8:])
    bias=op[-1]
    assert abs(bias-rail/2)<5
    sp.cmd('ac dec 50 10 1000000')
    freq=np.real(sp.vector('frequency'))
    gain=20*np.log10(abs(np.asarray(sp.vector('v(fx_return)')))/100)
    idx=(freq>=20)&(freq<=20001)
    limits=[min(gain[idx]),max(gain[idx])]
    names=['v(preout)','v(supply)','i(vhv8)','i(vchip)','v(fx_return)']
    sp.cmd('save '+' '.join(names))
    stop=max(40/f,.006) if raw else 40/f
    dt=1/(f*320)
    sp.cmd(f'tran {dt} {stop} 0 {dt}')
    t=np.asarray(sp.vector('time'))
    assert t[-1]>=stop*(1-1e-8)
    points=stop+(np.arange(4096)/409.6-10)/f
    out,supply,irail,chip,port=[np.interp(points,t,sp.vector(n)) for n in names]
    h=2*abs(np.fft.rfft(port)/len(port))[np.arange(1,11)*10]
    result=dict(frequency_Hz=f,harness_pF=harness,fast_shunt_pF=shunt,open_optical_pF=series_off,
                feedback_ohm=feedback,raw_input_V=raw,rail_min_V=min(supply),rail_max_V=max(supply),mean_PA_rail_mA=1000*np.mean(irail),
                nonlinear=nonlinear,inductance_scale=scale,short=short,temp_C=temp,rail_V=rail,bias_V=bias,band_gain_min_max_dB=limits,
                peak_V=h[0],thd_pct=100*np.linalg.norm(h[1:])/h[0],gain_dB=20*np.log10(h[0]/135),
                peak_chip_mA=max(abs(chip))*1e3,chip_W=np.mean(supply*irail-out*chip))
    sp.cmd('destroy all')
    return result


if __name__=='__main__':
    cases=[(20000,0,80,30),(20000,500,220,30),(20000,500,600,150),
           (1000,500,220,30),(20,500,220,30),(20000,500,1000,150),
           (20000,500,220,30,True,85,320),
           (20000,500,1300,150,False,25,310,True),
           (20000,500,2600,150,False,85,310,True),
           (20000,0,80,30,False,25,310,False,1.1),
           (20000,500,600,150,False,85,310,False,.9),
           (20000,500,220,30,False,25,310,False,1,390),
           (20000,500,600,150,False,25,310,False,1,340),
           (20000,500,600,150,False,85,310,False,.9,None,40600),
           (20000,500,220,30,False,25,310,False,1.1,None,38300)]
    rows=[audio(*args) for args in cases]
    (MODULE/'results/guard-audio.json').write_text(json.dumps(rows,indent=2)+'\n')
    print([(r['frequency_Hz'],round(r['gain_dB'],2),round(r['thd_pct'],2),round(r['chip_W'],2)) for r in rows])
