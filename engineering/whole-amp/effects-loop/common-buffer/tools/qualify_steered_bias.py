"""CB-015. Compare the steered source-bias candidate in PLAY and MUTE."""
import json
import multiprocessing
import sys
from itertools import product

import fixed_gain as gain
from qualify_sic_shunt import peaks
from retuned_shunt import NETWORK
from sic_shunt import MODEL_SHA, installed, spice_model
from sic_signal_levels import point
from steered_bias import branch


def tone(args):
    failures=[]
    for seed in (None,-11.,-9.):
        with branch(seed=seed):
            try:
                row=point(args)
                return dict(completed=True,released_guess_V=seed,incomplete_attempts=failures,**row)
            except AssertionError:
                failures.append(dict(seed_V=seed,diagnostic=gain.sp.logs[-3:]))
                gain.pulse_winding._cmd('destroy all')
    return dict(completed=False,target_Vpk=args[1],harness_pF=500 if args[2] else 0,incomplete_attempts=failures)


def pulses(model):
    rows=[]
    with gain.fixture():
        gain.STATE['net']=NETWORK
        for (threshold,cap),source in product([(-10,1),(-9.75,1.1),(-10.25,.9),(-10.25,1.1)],(-160,0,160)):
            row=dict(threshold_V=threshold,charge_scale=cap,source_V=source)
            with branch(),installed(model,off=18.5,driver_ohm=3,edge_ns=40,threshold=threshold,
                                    cap_scale=cap,isol_pF=12),peaks() as traces:
                try:
                    gain.guard_injection.run(source,1,18.5)
                except AssertionError:
                    row['stop_s']=float(gain.sp.vector('time')[-1])
                    gain.pulse_winding._cmd('destroy all')
                else:
                    row.update(traces)
            rows.append(row)
    return rows


if __name__=='__main__':
    path=sys.argv[1]
    with multiprocessing.get_context('spawn').Pool(4,maxtasksperchild=1) as pool:
        tones=pool.map(tone,product([path],(.135,4.27,13.5,42.7,85,135),(False,True)),chunksize=1)
    steps=pulses(spice_model(path))
    (gain.MODULE/'results/sic-steered-bias.json').write_text(json.dumps(dict(model_sha256=MODEL_SHA,
            network=NETWORK,tones=tones,pulses=steps),indent=1,default=float)+'\n')
