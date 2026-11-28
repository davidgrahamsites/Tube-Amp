"""CB-016. Run one fresh ngspice process per candidate and fault or tone."""
import json
import multiprocessing
import sys
from itertools import product
from unittest.mock import patch

import numpy as np

import fixed_gain as gain
from receiver_filter import receiver_filter
from retuned_shunt import NETWORK
from sic_shunt import MODEL_SHA, installed, spice_model
from sic_signal_levels import point
from steered_bias import branch


def quiet(step):
    original = gain.sp.cmd
    row = {}

    def capture(command):
        if command.startswith('save '):
            command += ' v(fast16) v(island13)'
        if command == 'destroy all':
            time = np.asarray(gain.sp.vector('time'))
            mix = np.asarray(gain.sp.vector('v(mix)'))
            island = np.asarray(gain.sp.vector('v(island13)'))
            edge = 2.40e-6
            base = np.interp(edge, time, mix)
            window = (time >= edge) & (time <= edge + 200e-9)
            peak = np.argmax(abs(mix))
            row.update(mixer_peak_V=abs(mix[peak]), signed_peak_V=mix[peak], peak_us=time[peak]*1e6,
                       precommand_peak_V=max(abs(mix[time < edge])), gate_start_V=base,
                       gate_window_change_V=max(abs(mix[window]-base)),
                       gate_start_source_V=np.interp(edge, time, island), stop_us=time[-1]*1e6)
        original(command)

    with patch.object(gain.sp, 'cmd', capture):
        gain.guard_injection.run(step, 1, 18.5)
    return row


def case(args):
    path, diodes, split, vth, miller, edge, kind, value, condition = args
    row = dict(diodes=diodes, split=split, ground_threshold_V=vth, ground_charge_scale=miller,
               edge_ns=edge, kind=kind, value=value, condition=condition)
    attempts = [('trap', None), ('gear', None)]
    if kind == 'tone':
        attempts += [('trap', -11.), ('gear', -9.)]
    for method, seed in attempts:
        try:
            with receiver_filter(diodes, split=split, method=method), branch(seed=seed):
                if kind == 'tone':
                    result = point((path, value, condition))
                else:
                    with gain.fixture(), installed(spice_model(path), off=18.5, driver_ohm=3, edge_ns=edge,
                            threshold=vth, cap_scale=miller, isol_pF=12, fault_edge_ns=edge, wire_ohm=4):
                        gain.STATE['net'] = NETWORK
                        if kind == 'quiet':
                            result = quiet(value)
                        else:
                            fault = gain.sudden_guard.fault('receiver filter', live_phase=value, sign=condition)
                            result = {key:fault[key] for key in ('post_switch_peak_V', 'peak_shunt_A', 'reached_s')}
            return dict(row, completed=True, method=method, released_guess_V=seed, **result)
        except AssertionError:
            row.setdefault('stopped', []).append(dict(method=method, released_guess_V=seed, diagnostic=gain.sp.logs[-3:]))
            gain.pulse_winding._cmd('destroy all')
    return dict(row, completed=False)


if __name__ == '__main__':
    path = sys.argv[1]
    cases = [(path,n,False,-9.75,1.1,40,'quiet',v,None) for n,v in product((1,2,3),(-160,0,160))]
    cases += [(path,n,False,-9.75,1.1,40,'live',phase,1) for n,phase in product((1,2,3),(90,270))]
    cases += [(path,2,True,t,k,e,'quiet',v,None) for t,k,e,v in
              product((-10.25,-9.75),(.9,1.1),(25,40,50),(-160,0,160))]
    cases += [(path,2,True,t,k,40,'live',p,s) for (t,k),p,s in
              product(((-10.25,.9),(-9.75,1.1)),(0,90,180,270),(-1,1))]
    # The integrated PA audio fixture uses the nominal pair, shared 2 ohm PLAY driver and 18 V bias.
    cases += [(path,2,True,-10,1,None,'tone',v,h) for v,h in
              product((.135,4.27,13.5,22,42.7,85,135),(False,True))]
    with multiprocessing.get_context('spawn').Pool(5, maxtasksperchild=1) as pool:
        rows = pool.map(case, cases, chunksize=1)
    out = dict(model_sha256=MODEL_SHA, previous_network=NETWORK, diode_model='behavioral', rows=rows)
    (gain.MODULE/'results/receiver-filter.json').write_text(json.dumps(out, indent=1, default=float)+'\n')
