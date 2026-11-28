"""Repeat the CB-017 history on the single-switch bridge."""
import json
import multiprocessing
import sys
from functools import partial
from itertools import product

import fixed_gain as gain
from bridge_shunt import bridge
from burst_memory import burst
from sic_shunt import MODEL_SHA


def run(args):
    path,level,quiet_us,ratio=args
    row=burst((path,level,quiet_us,None,False,-10,1),
              shunt_context=partial(bridge,mismatch=ratio), reference_node='plus18')
    if row['completed']:
        row['bridge_positive_before_V']=row.pop('tap_before_V')
    for key in ('dynamic_reference','bleed_Mohm','ground_threshold_V','ground_charge_scale'):
        del row[key]
    return dict(row,diode_ratio=ratio)


if __name__=='__main__':
    cases=[(sys.argv[1],level,delay,ratio) for (level,delay),ratio in
           product([(0,100),(13.5,100),(135,100),(135,1000),(135,10000)],(.8,1.2))]
    with multiprocessing.get_context('spawn').Pool(4,maxtasksperchild=1) as pool:
        rows=pool.map(run,cases,chunksize=1)
    (gain.MODULE/'results/bridge-burst.json').write_text(json.dumps(dict(model_sha256=MODEL_SHA,
           held_V=1.8,rows=rows),indent=1,default=float)+'\n')
