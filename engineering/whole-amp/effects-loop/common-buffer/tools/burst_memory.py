"""CB-017. Measure the mute pulse after a four-cycle 20 kHz burst ends at zero."""
import json
import multiprocessing
import sys
from itertools import product
from unittest.mock import patch

import numpy as np

import fixed_gain as gain
from retuned_shunt import NETWORK
from sic_shunt import MODEL_SHA, installed, spice_model
from steered_bias import branch


def burst(args, shunt_context=branch, reference_node='bias15x'):
    path, amplitude, delay_us, bleed_M, dynamic, threshold, scale = args
    end = 200e-6
    command = end + delay_us*1e-6
    stop = command + 2e-6
    row = dict(amplitude_Vpk=amplitude, quiet_us=delay_us, bleed_Mohm=bleed_M,
               dynamic_reference=dynamic, ground_threshold_V=threshold, ground_charge_scale=scale)
    for method, max_step_ns, marker_ns in [('trap',25,1),('gear',25,1),('gear',10,.5)]:
        original = gain._load

        def load(deck):
            lines = deck.splitlines()
            for i,line in enumerate(lines):
                if line.startswith('VS src '):
                    lines[i] = f'Bburst17 src 0 V={amplitude}*sin(2*pi*20000*time)*ternary_fcn(time<{end},1,0)'
                elif line.startswith('Vctl13 '):
                    phase=f'min(1,max(0,(time-{command:.12g})/40n))'
                    lines[i]=f'Bctl17 cmd13 island13 V=-18.5+18.5*ease17({phase})'
                elif dynamic and line.startswith('R15biasA '):
                    # Ideal full-wave level pickup from the upstream source. This is a feasibility bound.
                    lines[i] = ('Brect17 demand17 0 V=min(12,3*abs(v(src)))\n'
                                'Battack17 0 env17 I=max(0,v(demand17,env17))/100\n'
                                'Chold17 env17 0 10n\nRdecay17 env17 0 10k\n'
                                'Btap17 target17 0 V=-v(env17)\nR15biasA target17 bias15x 47k')
                elif dynamic and line.startswith('R15biasB '):
                    lines[i] = '* 47k Thevenin resistance at controlled tap'
            extra = [f'.options method={method} maxord=2', '.func ease17(x) {x*x*(3-2*x)}']
            if bleed_M:
                extra.append(f'R17reset island13 bias15x {bleed_M}meg')
            # Force local breakpoints around closure while permitting larger steps in the silent wait.
            points = ' '.join(f'{command+i*marker_ns*1e-9:.12g} {i%2}' for i in range(-5,int(206/marker_ns)))
            extra.append(f'Vtiming17 timing17 0 PWL(0 0 {points})')
            lines[lines.index('.end'):lines.index('.end')] = extra
            original('\n'.join(lines))

        with patch.object(gain,'_load',load), shunt_context(), gain.fixture(), installed(spice_model(path),
                off=18.5,driver_ohm=3,edge_ns=40,threshold=threshold,cap_scale=scale,isol_pF=12):
            gain.STATE['net'] = NETWORK
            old = gain.sp.cmd

            def capture(cmd):
                if cmd.startswith('save '):
                    cmd=f'save v(mix) v(gate13) v(island13) v({reference_node})'
                if cmd.startswith('tran '):
                    cmd=f'tran {max_step_ns}n {stop} 0 {max_step_ns}n'
                if cmd == 'destroy all':
                    t=np.asarray(gain.sp.vector('time'))
                    assert t[-1]>=stop*(1-1e-9)
                    mix=np.asarray(gain.sp.vector('v(mix)'))
                    src=np.asarray(gain.sp.vector('v(island13)'))
                    tap=np.asarray(gain.sp.vector(f'v({reference_node})'))
                    before=np.interp(command,t,mix)
                    event=(t >= command-1e-15) & (t <= command + 200e-9)
                    after=t >= command + 100e-9
                    row.update(completed=True,method=method,marker_ns=marker_ns,max_step_ns=max_step_ns,stop_us=t[-1]*1e6,precommand_mix_V=before,
                            island_before_V=np.interp(command,t,src),tap_before_V=np.interp(command,t,tap),
                            playing_peak_V=max(abs(mix[t<end])),event_peak_V=max(abs(mix[event])),
                            event_change_V=max(abs(mix[event]-before)),post_100ns_V=max(abs(mix[after])))
                old(cmd)
            with patch.object(gain.sp,'cmd',capture):
                try:
                    gain.guard_injection.run(0,1,18.5)
                    return row
                except AssertionError:
                    trace=np.asarray(gain.sp.vector('time'))
                    attempt=dict(method=method,marker_ns=marker_ns,max_step_ns=max_step_ns,diagnostic=gain.sp.logs[-3:])
                    if len(trace) and trace[-1] >= command-1e-9:
                        attempt.update(reached_us=trace[-1]*1e6,
                            precommand_source_V=np.interp(command-1e-9,trace,gain.sp.vector('v(island13)')),
                            precommand_mix_V=np.interp(command-1e-9,trace,gain.sp.vector('v(mix)')))
                    row.setdefault('stopped',[]).append(attempt)
                    gain.pulse_winding._cmd('destroy all')
    return dict(row,completed=False)


if __name__ == '__main__':
    path=sys.argv[1]
    args=[(path,a,d,b,y,t,k) for (a,d),(b,y),(t,k) in product(
          [(0,100),(13.5,100),(135,100),(135,1000),(135,10000)],
          [(None,False),(None,True),(1,True)],[(-10.25,.9),(-9.75,1.1)])]
    with multiprocessing.get_context('spawn').Pool(5,maxtasksperchild=1) as pool:
        rows=pool.map(burst,args,chunksize=1)
    (gain.MODULE/'results/burst-memory.json').write_text(json.dumps(dict(model_sha256=MODEL_SHA,
          command='40 ns smoothstep; 1 ns local time markers or 0.5 ns on refinement',source_ohm=NETWORK['isolation']*.95,simulation='controlled full-wave reference and finite-source burst',
          rows=rows),indent=1,default=float)+'\n')
