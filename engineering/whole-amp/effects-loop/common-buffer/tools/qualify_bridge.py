"""CB-018. Check simultaneous audio and protection on the bridge candidate."""
import json
import multiprocessing
import sys
from itertools import product
from unittest.mock import patch

import numpy as np
import fixed_gain as gain
from bridge_shunt import bridge
from retuned_shunt import NETWORK
from sic_shunt import MODEL_SHA, installed, spice_model
from sic_signal_levels import point


def case(args):
    path,kind,value,corner,held,cj,tt,ratio,park=args
    row=dict(kind=kind,value=value,corner=corner,held_V=held,Cjo_pF=cj,transit_ns=tt,ratio=ratio,pedestal=park)
    for method in ('trap','gear'):
        try:
            with bridge(held_V=held,junction_pF=cj,transit_ns=tt,mismatch=ratio,pedestal=park,method=method):
                if kind=='tone':
                    data=point((path,value,corner))
                else:
                    with gain.fixture(),installed(spice_model(path),off=18.5,driver_ohm=3,edge_ns=40,
                            isol_pF=12,wire_ohm=4,fault_edge_ns=40):
                        gain.STATE['net']=NETWORK
                        original=gain.sp.cmd
                        data={}
                        def capture(command):
                            if command.startswith('save '):
                                command+=' i(vhold18) v(plus18) v(minus18) v(gate13) v(island13)'
                            if command=='destroy all':
                                t=np.asarray(gain.sp.vector('time'))
                                mix=np.asarray(gain.sp.vector('v(mix)'))
                                current=np.asarray(gain.sp.vector('i(vhold18)'))
                                gate=np.asarray(gain.sp.vector('v(gate13)'))-np.asarray(gain.sp.vector('v(island13)'))
                                data.update(hold_peak_A=max(abs(current)),hold_final_A=current[-1],
                                    gate_min_V=min(gate),gate_max_V=max(gate),stop_s=t[-1])
                                if kind=='quiet':
                                    at=np.argmax(abs(mix))
                                    data.update(peak_us=t[at]*1e6,precommand_V=np.interp(2.4e-6,t,mix),
                                                signed_peak_V=mix[at])
                            original(command)
                        with patch.object(gain.sp,'cmd',capture):
                            if kind=='quiet':
                                data['peak_V']=gain.guard_injection.run(value,1,18.5)['peak_V']
                            else:
                                fault=gain.sudden_guard.fault('single switch bridge',live_phase=value,sign=corner)
                                data.update(residual_V=fault['post_switch_peak_V'],signal_shunt_A=fault['peak_shunt_A'])
            return dict(row,completed=True,method=method,**data)
        except AssertionError:
            row.setdefault('stopped',[]).append(dict(method=method,diagnostic=gain.sp.logs[-5:]))
            gain.pulse_winding._cmd('destroy all')
    return dict(row,completed=False)


if __name__=='__main__':
    path=sys.argv[1]
    corners=[(15,10,.8),(30,25,1.2),(45,50,1.2)]
    cases=[(path,'quiet',s,None,h,c,t,r,True) for s,h,(c,t,r) in
           product((-160,0,160),(0,1.5,1.8),corners)]
    cases += [(path,'playing',p,s,h,30,25,1.2,True) for p,s,h in
              product((0,90,180,270),(-1,1),(0,1.5,1.8))]
    cases += [(path,'tone',a,h,1.8,30,25,1.2,True) for a,h in
              product((.135,4.27,13.5,22,42.7,85,135),(False,True))]
    cases += [(path,'tone',.135,True,1.8,30,25,1.2,False)]
    with multiprocessing.get_context('spawn').Pool(5,maxtasksperchild=1) as pool:
        rows=pool.map(case,cases,chunksize=1)
    out=dict(model_sha256=MODEL_SHA,network=NETWORK,local_additional_pF=270,rows=rows)
    (gain.MODULE/'results/bridge-shunt.json').write_text(json.dumps(out,indent=1,default=float)+'\n')
