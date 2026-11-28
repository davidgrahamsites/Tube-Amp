"""CB-012. Compare the measured-curve estimates with the audio and mute limits."""
import json
from itertools import product

import assembled_return as assembly
import fixed_gain as gain
from shunt_curve import FIGURE, device, device_caps, switch_charge


def calibration():
    # Probe differential current with the gate fixed 6.2 V below the source.
    import math
    rows = []
    for volts, expected, reverse in FIGURE:
        cap = device_caps('drain','0','gate','test',1,6.2)
        gain.sp.load(f"charge calibration\nVdrain drain 0 {volts} ac 1\nVgate gate 0 -6.2\n{cap}\n.end")
        gain.sp.cmd('ac lin 1 100000 100000')
        actual = -gain.sp.vector('i(vdrain)')[0].imag*1e12/(2*math.pi*1e5)
        miller = gain.sp.vector('i(vgate)')[0].imag*1e12/(2*math.pi*1e5)
        gain.sp.cmd('destroy all')
        assert abs(actual-expected)<.5 and abs(miller-reverse)<.5, (volts,actual,miller)
        rows.append(dict(V=volts,expected_Coss_pF=expected,ngspice_Coss_pF=actual,
                         expected_Crss_pF=reverse,ngspice_Crss_pF=miller))
    return rows


def main():
    check=calibration()
    bands, transitions, faults = [], [], []
    with gain.fixture():
        gain.STATE['net']=assembly.NETWORK
        for bias,th,m,step in product((0,12),[(-3,-3),(-2,-4.5),(-4.5,-2)],(.5,1,2),(-160,0,160)):
            with switch_charge(bias,47000,0,1,6.2,*th):
                peak=gain.guard_injection.run(step,m,6.2)['peak_V']
                transitions.append(dict(bias_V=bias,Vth_V=list(th),Crss_ratio=m,step_V=step,mixer_V=peak))
        for ohm,limit in ((5.4,6),(9,3),(13.4,3),(18,3),(18,1.5)):
            for sign,phase in product((-1,1),(None,0,90,180,270)):
                r=gain.sudden_guard.fault('bounded current',sign=sign,live_phase=phase,
                      current_limit=limit,shunt_ohm=ohm,shunt_pF=600,wire_pF=500)
                faults.append({k:r[k] for k in ('sign','phase_deg','current_limit_A','shunt_ohm',
                    'peak_shunt_A','post_switch_peak_V','peak_mixer_V','deck_sha256')})
        for bias,leak in [(0,0),(12,0),(12,100)]:
            for cs,os in product((.75,1,1.25),(6.2,10)):
                with device(bias,47000,leak,cs,os):
                    values = []
                    for h,o,t,l,k in product((0,500),(30,150),(25,85),(.9,1.1),(.977,1.023)):
                        band=gain.audio((20000,h,1,o,False,t,310,True,l),cap_scale=k,ac_only=True)['small_signal']
                        limits=band['band_min_max_dB']+[band['gain_dB']['20'],band['gain_dB']['20000']]
                        values.append(dict(harness_pF=h,contact_pF=o,temp_C=t,L_scale=l,cap_scale=k,
                                           low_dB=min(limits),high_dB=max(limits)))
                    bands.append(dict(bias_V=bias,leak_uA=leak,charge_scale=cs,gate_axis_V=os,
                                      worst_low=min(values,key=lambda r:r['low_dB']),
                                      worst_high=max(values,key=lambda r:r['high_dB']),corners=len(values)))
            print('gain',bias,leak,flush=True)
    out=dict(calibration=check,bands=bands,transitions=transitions,faults=faults,
             scope='Typical curve, behavioral gate switching and independent current limited fault fixture. No measured unit.')
    (gain.MODULE/'results/shunt-device-curve.json').write_text(json.dumps(out,indent=1,default=float)+'\n')
    print('transitions',max(r['mixer_V'] for r in transitions),'faults',len(faults),flush=True)


if __name__=='__main__':
    main()
