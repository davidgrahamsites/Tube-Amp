"""CB-011. Test DC reverse bias on the fast shunt against both gain and mute injection."""
import itertools
import json
from unittest.mock import patch

import assembled_return as assembly
import fixed_gain as gain


def screen(bias, resistance, leakage_mA):
    source=gain.sp.load

    def with_bias(net):
        for marker,node in (('RISO8 island8 0 1gig','island8'),('CGISE island 0 6p','island')):
            if marker in net:
                branch=f'VBIAS11 bias11 0 {-bias}\nRBIAS11 {node} bias11 {resistance}\nILEAK11 0 {node} {leakage_mA}m\n'
                net=net.replace(marker,branch+marker)
        source(net)

    band=[]
    with patch.object(gain.sp,'load',with_bias):
        for h,o,t,l in itertools.product((0,500),(30,150),(25,85),(.9,1.1)):
            row=gain.audio((20000,h,2600,o,False,t,310,True,l),ac_only=True)['small_signal']
            band.extend(row['band_min_max_dB']+[row['gain_dB']['20000']])
        injection=max(gain.guard_injection.run(v,m,6.2,cscale=k)['peak_V']
                      for v,m,k in itertools.product((-160,0,160),(.5,2),(1,4)))
    return dict(negative_bias_V=bias,series_ohm=resistance,leakage_mA=leakage_mA,
                AC_range_dB=[float(min(band)),float(max(band))],switch_peak_V=float(injection))


def main():
    with gain.fixture():
        gain.STATE['net']=assembly.NETWORK
        rows=[screen(b,r,i) for b,r,i in itertools.product((4.5,6.,17.5),(47e3,100e3),(0,.02,.1))]
    passing=[r for r in rows if max(map(abs,r['AC_range_dB']))<=.5 and r['switch_peak_V']<.7]
    common=[(b,r) for b,r in itertools.product((4.5,6.,17.5),(47e3,100e3))
            if all(row in passing for row in rows if (row['negative_bias_V'],row['series_ohm'])==(b,r))]
    out=dict(evidence='Behavioral body-junction and switching surrogates; no measured capacitance curve.',
             bias_passes_all_leakages=common,rows=rows)
    (gain.MODULE/'results/shunt-bias-trade.json').write_text(json.dumps(out,indent=1)+'\n')
    print(common)


if __name__=='__main__':
    main()
