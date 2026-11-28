"""CB-020. Exercise both independent shunt paths and their single-short controls."""
import json
import multiprocessing
import sys
from itertools import product
from unittest.mock import patch

import qualify_bridge
from dual_bridge import dual_bridge
from retuned_shunt import NETWORK
from sic_shunt import MODEL_SHA


def case(args):
    path,kind,value,corner,a,b,late,skew,opposed=args
    def pair(**settings):
        del settings['held_V']
        return dual_bridge(a,b,mirrored=opposed,second_diode=(45,50,.8),late_channel=late,skew_ns=skew,**settings)
    with patch.object(qualify_bridge,'bridge',pair):
        row=qualify_bridge.case((path,kind,value,corner,a,30,25,1.2,True))
    return dict(row,bias_A_V=a,bias_B_V=b,late_channel=late,skew_ns=skew,mirrored=opposed)


if __name__=='__main__':
    path=sys.argv[1]
    configurations=[(2,2,None,0),(0,2,None,0),(2,0,None,0),(0,1.5,'B',20),(1.5,0,'A',20),(0,0,None,0)]
    cases=[(path,'quiet',v,None,a,b,leg,skew,False) for (a,b,leg,skew),v in product(configurations,(-160,0,160))]
    cases += [(path,'playing',p,s,a,b,leg,skew,False) for (a,b,leg,skew),p,s in product(configurations,(0,90,180,270),(-1,1))]
    cases += [(path,'tone',v,h,2,2,None,0,False) for v,h in product((.135,4.27,13.5,22,42.7,85,135),(False,True))]
    cases += [(path,'quiet',v,None,0,2,None,0,True) for v in (-160,0,160)]
    with multiprocessing.get_context('spawn').Pool(5,maxtasksperchild=1) as pool:
        rows=pool.map(case,cases,chunksize=1)
    (qualify_bridge.gain.MODULE/'results/dual-bridge.json').write_text(json.dumps(
        dict(model_sha256=MODEL_SHA,network=NETWORK,second_diode=dict(Cjo_pF=45,transit_ns=50,ratio=.8),rows=rows),
        indent=1,default=float)+'\n')
