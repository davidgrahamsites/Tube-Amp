"""Conservative isolated-event PR01 pulse screen; no contact-life claim."""
import json
import math
from analyze import M, sha, inputs


def main():
    c,r=inputs();a=json.loads((M/'results/analytic.json').read_text())
    voltage=a['contact']['voltage_V']
    # Proposed 5% stocked family member; include 250ppm/K across -25..70C.
    rmin=r['R616']*.95*(1-250e-6*50)
    rmax=r['R616']*1.05*(1+250e-6*50)
    peak=voltage**2/rmin
    tau=rmax*r['C607']*1.1
    tail=peak*math.exp(-2*.001/tau)
    out=dict(candidate='PR01000101000JA500',manufacturer='Vishay',R_ohm=100,tolerance=.05,
             R_min_ohm=rmin,R_max_ohm=rmax,peak_W=peak,C607_branch_peak_A=voltage/rmin,
             worst_RC_s=tau,upper_power_after_1ms_W=tail,
             rectangular_screen=dict(duration_s=.001,peak_W=20,peak_V=50,period_s=1,
                                     added_tail_W=1e-6,ambient_max_C=70),
             manufacturer_curve=dict(document='sources/Vishay-PR01.pdf',revision='08-Jul-2025',page=9,
                evidence='Visually inspected PR01 curve at1ms,tp/ti1000. Adopt50W as deliberately rounded-down screen; curve is about100W. Voltage curve1000V.',
                conservative_power_W=50,voltage_V=1000),
             passed=bool(peak<20 and voltage<50 and tail<1e-6),
             limits=['Not a qualification of arbitrary repeated operation or relay bounce',
                     'Different tolerance from native1%; full output-buffer stability and exact footprint not yet integrated',
                     'Procurement is an indexed Chinese listing, not verified live stock'],
             source_sha256=c['source_sha256'],inputs_sha256={str(p.relative_to(M)):sha(p) for p in [M/'results/analytic.json',M/'sources/Vishay-PR01.pdf',M/'tools/pulse_budget.py']})
    assert out['passed']
    (M/'results/pulse-budget.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__': main()
