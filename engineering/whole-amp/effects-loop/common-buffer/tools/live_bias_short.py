"""CB-020. Close a local short across a charged bank during the mute transition."""
import json
import multiprocessing
import sys
from itertools import product
from unittest.mock import patch

import numpy as np
import fixed_gain as gain
from dual_bridge import dual_bridge
from retuned_shunt import NETWORK
from sic_shunt import MODEL_SHA, installed, spice_model


def case(args):
    path,channel,kind,sign,phase,offset_ns,coupling,step_ns=args
    playing=kind=='playing'
    onset=(4+phase/360)/20000+.5e-6 if playing else 2.40e-6
    failure=onset+offset_ns*1e-9
    suffix='' if channel=='A' else 'B20'
    original=gain._load
    row=dict(shorted=channel,kind=kind,source_sign=sign,phase_deg=phase,offset_ns=offset_ns,
             coupling=coupling,timestep_ns=step_ns)
    def insert(net):
        tag='Vhold18'+suffix
        lines=net.splitlines()
        i=next(i for i,s in enumerate(lines) if s.startswith(tag+' '))
        top,ref=lines[i].split()[1:3]
        # Keep a zero-volt current probe in series with the remaining bridge circuit.
        lines[i]=f'''{tag} {top} bankport20 0
Vcharger20 ch20 {ref} 2
Rcharge20 ch20 bankport20 10
Lneck20 bankport20 caps20 .25n
Lbulk20 caps20 bulkL20 10n
Rbulk20 bulkL20 bulk20 .018
Cbulk20 bulk20 {ref} 2640u
Lcer20 caps20 ceramicL20 .25n
Rcer20 ceramicL20 ceramic20 .00375
Ccer20 ceramic20 {ref} 8u
Lfault20 bankport20 fault20 4n
Bshort20 fault20 {ref} I=v(fault20,{ref})*(1e-9+20*v(close20))
Vshort20 close20 0 PWL(0 0 {failure:.14g} 0 {failure+10e-9:.14g} 1)
Lreturn20 common20 0 4n'''
        if coupling:
            lines[i]+=f'\nKfault20 Lfault20 Lreturn20 {coupling}'
        # Two independent return wires meet the reference at one modeled inductance.
        names=('VMON',) if playing else ('RSH','RSHB20')
        for name in names:
            j=next(j for j,l in enumerate(lines) if l.startswith(name+' '))
            fields=lines[j].split()
            assert fields[2]=='0'
            fields[2]='common20'
            lines[j]=' '.join(fields)
        deck='\n'.join(lines)
        original(deck.replace(f'.options method={method} maxord=2',f'.options method={method} maxord={maxord} itl4=100'))
    for method,maxord in [('gear',2),('trap',2),('gear',1)]:
        with patch.object(gain,'_load',insert),dual_bridge(2,2,second_diode=(45,50,.8),method=method),gain.fixture(),installed(
                spice_model(path),off=18.5,driver_ohm=3,edge_ns=40,isol_pF=12,wire_ohm=4,fault_edge_ns=40):
            gain.STATE['net']=NETWORK
            previous=gain.sp.cmd
            def capture(cmd):
                if cmd.startswith('save '):
                    cmd+=f' i(lfault20) v(minus18{suffix}) v(rail18{suffix}) v(common20)'
                if cmd.startswith('tran '):
                    f=cmd.split()
                    cmd=f'tran {step_ns}n {f[2]} 0 {step_ns}n'
                if cmd=='destroy all':
                    time=np.asarray(gain.sp.vector('time'))
                    mix=np.asarray(gain.sp.vector('v(mix)'))
                    current=np.asarray(gain.sp.vector('i(lfault20)'))
                    v=np.asarray(gain.sp.vector(f'v(minus18{suffix})'))-np.asarray(gain.sp.vector(f'v(rail18{suffix})'))
                    after=time>=failure
                    row.update(completed=True,method=method,maxord=maxord,stop_us=time[-1]*1e6,
                               pre_short_V=np.interp(failure,time,v),terminal_end_V=v[-1],
                               short_peak_A=max(abs(current[after])),return_peak_V=max(abs(np.asarray(gain.sp.vector('v(common20)'))[after])),
                               short_i2r_uJ=np.trapezoid(current[after]**2*.05,time[after])*1e6,
                               post100_V=max(abs(mix[time>=onset+100e-9])))
                    if not playing:
                        row.update(quiet_peak_V=max(abs(mix)),peak_us=time[np.argmax(abs(mix))]*1e6)
                previous(cmd)
            with patch.object(gain.sp,'cmd',capture):
                try:
                    if playing:
                        gain.sudden_guard.fault('charged bridge short',sign=sign,live_phase=phase)
                    else:
                        gain.guard_injection.run(sign*160,1,18.5)
                    return row
                except AssertionError:
                    row.setdefault('stopped',[]).append(dict(method=method,maxord=maxord,log=gain.sp.logs[-4:]))
                    gain.pulse_winding._cmd('destroy all')
    return dict(row,completed=False)


if __name__=='__main__':
    path=sys.argv[1]
    cases=[(path,ch,'quiet',s,None,d,0,1) for ch,s,d in product('AB',(-1,0,1),(-400,0,30,120))]
    cases += [(path,ch,'playing',s,p,0,0,1) for ch,s,p in product('AB',(-1,1),(0,90,180,270))]
    cases += [(path,'A','quiet',s,None,30,k,1) for s,k in product((-1,0,1),(-.25,.25))]
    cases += [(path,'A','playing',s,p,30,k,1) for s,p,k in product((-1,1),(90,270),(-.25,.25))]
    with multiprocessing.get_context('spawn').Pool(5,maxtasksperchild=1) as pool:
        rows=pool.map(case,cases,chunksize=1)
    (gain.MODULE/'results/charged-bias-short.json').write_text(json.dumps(dict(model_sha256=MODEL_SHA,
        short_R_ohm=.05,short_L_nH=4,return_L_nH=4,short_close_ns=10,healthy_bias_V=2,
        bulk_uF=2640,local_uF=8,charger_ohm=10,rows=rows),indent=1,default=float)+'\n')
