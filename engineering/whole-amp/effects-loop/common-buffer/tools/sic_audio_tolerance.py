"""CB-014. Independent passive errors in the CB-013 quiet-signal band."""
from itertools import product
import json
import re
import sys
from unittest.mock import patch

import fixed_gain as gain
from qualify_sic_shunt import NETWORK
from retuned_shunt import NETWORK as REVISED
from sic_shunt import MODEL_SHA, installed, spice_model


def main(path, revised=False):
    # Two individual inductance and three capacitor extremes; two feedback ratios
    # use opposed 0.1% errors on the upper and lower arms of each feedback divider.
    model=spice_model(path)
    rows=[]
    winding=gain.pulse_winding.delay_line
    with gain.fixture(),installed(model):
        net=REVISED if revised else NETWORK
        gain.STATE['net']=net
        for la,lb,ca,cb,cc in product((.9,1.1),(.9,1.1),(.977,1.023),(.977,1.023),(.977,1.023)):
            def line(start,end,scale,pf,shunt,mid,tail,entry):
                gain.pulse_winding.STATE['corner']['l_mismatch']=[la,lb]
                return winding(start,end,scale,pf,shunt,mid*cb,tail*cc,entry*ca)
            with patch.object(gain.pulse_winding,'delay_line',line):
                for h,o,t,sgn in product((0,500),(30,150),(25,85),(-1,1)):
                    orig=gain.sp.load
                    net_feedback=net['feedback']
                    def dividers(net):
                        for key,val,sign in [('RLOW2 low invlow',net_feedback,1),('RLOW1 invlow 0',10000,-1),
                                ('RF1 preout rfmid',24000,1),('RF2 rfmid minus',24000,1),('RG minus cg',2000,-1)]:
                            # The two 24k arms are both in the same upper leg.
                            net,n=re.subn('^'+key+r' [^\n]+$',f'{key} {val*(1+.001*sgn*sign)}',net,flags=re.M)
                            assert n==1
                        orig(net)
                    with patch.object(gain.sp,'load',dividers):
                        r=gain.audio((20000,h,1,o,False,t,310,True,1),ac_only=True)['small_signal']
                    vals=r['band_min_max_dB']+[r['gain_dB']['20'],r['gain_dB']['20000']]
                    rows.append(dict(L=[la,lb],C=[ca,cb,cc],harness_pF=h,contact_pF=o,temp_C=t,
                                     ratio_sign=sgn,low_dB=min(vals),high_dB=max(vals)))
    out=dict(network=net,model_sha256=MODEL_SHA,cases=len(rows),worst_low=min(rows,key=lambda r:r['low_dB']),
             worst_high=max(rows,key=lambda r:r['high_dB']),violations=sum(1 for r in rows if max(-r['low_dB'],r['high_dB'])>.5),rows=rows)
    (gain.MODULE/('results/sic-retuned-tolerance.json' if revised else 'results/sic-audio-tolerance.json')).write_text(json.dumps(out,indent=1,default=float)+'\n')
    print(out['worst_low'],out['worst_high'],flush=True)


if __name__=='__main__':
    main(sys.argv[1],'--revised' in sys.argv[2:])
