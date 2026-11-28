"""CB-019. Disconnect the 1.8 V charger and run the bridge through optical handover."""
import json
import multiprocessing
import re
import sys
from itertools import product
from unittest.mock import patch

import numpy as np

import fixed_gain as gain
from bridge_shunt import bridge
from retuned_shunt import NETWORK
from sic_shunt import MODEL_SHA, installed, spice_model


def trial(args):
    path, count, local, common_nH, sign, phase, marker_ns, start_V = args
    t0=(4+phase/360)/20000
    onset=t0+.5e-6
    stop=onset+.003013
    row=dict(start_V=start_V,bulk_count=count,local_count=local,common_nH=common_nH,sign=sign,phase_deg=phase,marker_ns=marker_ns)
    original=gain._load
    def add(deck):
        old='Vhold18 minus18 rail18 1.8'
        assert old in deck
        # A conductance ramp removes a pre-existing charger before the PA pin fault.
        # The open charger and the charged capacitor are distinct faults.
        sub=f'''Vhold18 minus18 top19 0
Vchg19 charger19 rail18 {start_V}
Bcharge19 charger19 top19 I=v(charger19,top19)*(1e-10+2*v(ready19))
Vready19 ready19 0 PWL(0 1 {t0-4e-6:.12g} 1 {t0-2e-6:.12g} 0)
Lcommon19 top19 bank19 {common_nH}n
Lbulk19 bank19 l19 {10/count}n
Rbulk19 l19 c19 {.018/count}
Cbulk19 c19 rail18 {2640*count}u
Rleak19 c19 rail18 {1.8/(count*.00033)}
'''
        if local:
            sub+=f'Llocal19 bank19 b19 {2/local}n\nRlocal19 b19 d19 {.03/local}\nClocal19 d19 rail18 {local}u\n'
        # Put the resolution breakpoints in the real command source. A second PWL
        # source can create almost-coincident events at millisecond absolute times.
        samples=[]
        for i in range(-5,int(150/marker_ns)+1):
            u=min(1,max(0,i*marker_ns/40))
            samples.append(f'{onset+i*marker_ns*1e-9:.14g} {u*u*(3-2*u):.12g}')
        trip='VTRIP cmd 0 PWL(0 0 '+' '.join(samples)+')'
        deck,n=re.subn(r'^VTRIP cmd 0 PWL\(.+\)$',trip,deck,flags=re.M)
        assert n==1
        if method=='backward-euler':
            deck=deck.replace('.options method=gear maxord=2','.options method=gear maxord=1')
        if extended:
            deck=deck.rsplit('.end',1)[0]+'.options itl4=150 reltol=.0005 trtol=3 chgtol=1e-15\n.end'
        original(deck.replace(old,sub))
    for method,max_step_ns,extended in [('gear',10,False),('trap',10,False),('gear',7,False),('trap',8,False),
                                         ('gear',7,True),('trap',6,True),('backward-euler',5,True)]:
        with patch.object(gain,'_load',add),bridge(method='gear' if method=='backward-euler' else method),gain.fixture(),installed(spice_model(path),
                off=18.5,driver_ohm=3,edge_ns=40,isol_pF=12,wire_ohm=4,fault_edge_ns=40):
            gain.STATE['net']=NETWORK
            old_cmd=gain.sp.cmd
            def capture(cmd):
                if cmd.startswith('save '):
                    cmd+=' v(top19) v(c19) v(rail18) i(vhold18)'
                if cmd.startswith('tran '):
                    cmd=f'tran {max_step_ns}n {stop} 0 {max_step_ns}n'
                if cmd=='destroy all':
                    t=np.asarray(gain.sp.vector('time'))
                    assert t[-1]>=stop*(1-1e-9)
                    mix=np.asarray(gain.sp.vector('v(mix)'))
                    ref=np.asarray(gain.sp.vector('v(rail18)'))
                    terminal=np.asarray(gain.sp.vector('v(top19)'))-ref
                    bulk=np.asarray(gain.sp.vector('v(c19)'))-ref
                    current=np.asarray(gain.sp.vector('i(vhold18)'))
                    use=t>=onset
                    row.update(completed=True,method=method,max_step_ns=max_step_ns,extended_iterations=extended,stop_s=t[-1],reservoir_final_V=bulk[-1],
                               terminal_min_V=min(terminal[use]),terminal_max_V=max(terminal[use]),
                               mixer_residual_V=max(abs(mix[t>=onset+100e-9])),
                               peak_A=max(abs(current[use])),charge_uC=-np.trapezoid(current[use],t[use])*1e6)
                old_cmd(cmd)
            with patch.object(gain.sp,'cmd',capture):
                try:
                    gain.sudden_guard.fault('bridge reserve',live_phase=phase,sign=sign)
                    return row
                except AssertionError:
                    row.setdefault('stopped',[]).append(dict(method=method,max_step_ns=max_step_ns,extended_iterations=extended,diagnostic=gain.sp.logs[-4:]))
                    gain.pulse_winding._cmd('destroy all')
    return dict(row,completed=False)


if __name__=='__main__':
    p=sys.argv[1]
    configs=[(1,0,.25),(1,1,.25),(1,4,.25),(1,8,.25),(2,8,.25),(1,8,1)]
    cases=[(p,n,l,h,s,phase,1,1.8) for (n,l,h),s,phase in product(configs,(-1,1),(90,270))]
    cases += [(p,1,8,.25,s,phase,.25,1.8) for s,phase in product((-1,1),(90,270))]
    cases += [(p,1,8,.25,s,phase,marker,2.) for s,phase,marker in product((-1,1),(90,270),(1,.25))]
    with multiprocessing.get_context('spawn').Pool(4,maxtasksperchild=1) as pool:
        rows=pool.map(trial,cases,chunksize=1)
    out=dict(model_sha256=MODEL_SHA,command="40 ns smoothstep sampled in the gate source",bulk_part='Panasonic EEUFR1A332',bulk_min_uF=2640,bulk_assumed_ESL_nH=10,
             bulk_assumed_ESR_ohm=.018,local_effective_uF=1,local_assumed_ESL_nH=2,local_assumed_ESR_ohm=.03,
             rows=rows)
    (gain.MODULE/'results/bridge-reservoir.json').write_text(json.dumps(out,indent=1,default=float)+'\n')
