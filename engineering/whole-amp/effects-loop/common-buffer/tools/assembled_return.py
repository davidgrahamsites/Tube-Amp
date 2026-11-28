"""CB-011 full gain corners and pin-level short with the revised PA power path."""
import itertools
import json
from unittest.mock import patch

import fixed_gain as gain
import guard_audio
import hot_short_bias
import local_reservoir
import relay_margin
from cutoff_guard_model import HOT_LOW

NETWORK=dict(name='CB-011',isolation=3000,series=2.2,start=680,mid=220,end=180,feedback=40249)
# 1% C0G caps plus 1.3% independent allowance for temperature and aging.



def bands():
    rows=[]
    for h,s,o,temp,l,c in itertools.product((0,500),(80,220,600),(30,150),(25,85),(.9,1.1),(.977,1.023)):
        args=(20000,h,s,o,False,temp,310,False,l)
        r=gain.audio(args,cap_scale=c,ac_only=True)['small_signal']
        limits=r['band_min_max_dB']+[r['gain_dB']['20'],r['gain_dB']['20000']]
        rows.append(dict(args=list(args),cap_scale=c,band_dB=[float(min(limits)),float(max(limits))]))
    return rows


def main():
    def protected_rail(raw,ctr,threshold,cap,bypass,leak):
        return relay_margin.rail.variant(raw,ctr,threshold,local_reservoir.CMIN,bypass,None,**relay_margin.rail.CAND)
    with gain.fixture(), relay_margin.supply_path(2.,HOT_LOW), patch.object(guard_audio,'regulator',protected_rail):
        gain.STATE['net']=NETWORK
        b=bands()
        dark=min(b,key=lambda r:r['band_dB'][0])
        bright=max(b,key=lambda r:r['band_dB'][1])
        check=[('minimum',dark['args'],dark['cap_scale']),('maximum',bright['args'],bright['cap_scale']),
               ('heavy hot',gain.HOT,1.),('light ambient',gain.OPPOSITE,1.),
               ('charge-dependent', (20000,500,2600,150,False,85,310,True),1.),
               ('charge-dependent light',(20000,0,1300,30,False,25,310,True,1.1),1.),
               ('nominal midband',(1000,500,220,30),1.)]
        rows=[]
        for tag,args,scale in check:
            r=gain.audio(args,raw=340,cap_scale=scale)
            rows.append(dict(test=tag,result=r))
            print(tag,r['gain_dB'],r['thd_pct'],r['rail_min_V'],flush=True)
        with hot_short_bias.guide(16.5):
            short=gain.audio((20000,500,220,30,True,85,310),raw=440)
        print('short',gain.short_heat(short),flush=True)
        faults=gain.faults(True)
        out=dict(network=NETWORK,band_samples=b,voltage_extremes=[dark,bright],audio=rows,
                 hot_short=short,hot_short_heat=gain.short_heat(short),faults=faults,
                 limits=dict(band_dB=.5,thd_pct=1,short_case_C=76),
                 scope='Finite joint corners. Common capacitor and inductance scales; independent mismatches need a separate run.')
    (gain.MODULE/'results/assembled-return.json').write_text(json.dumps(out,indent=1,default=float)+'\n')


if __name__=='__main__':
    main()
