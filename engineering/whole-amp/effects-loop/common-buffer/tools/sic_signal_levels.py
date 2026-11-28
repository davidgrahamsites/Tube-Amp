"""Test finite-amplitude distortion between the quiet and overload limits."""
from itertools import product
import json
import math
import sys
from unittest.mock import patch

import fixed_gain as gain
import guard_audio
import local_reservoir
import relay_margin
from cutoff_guard_model import HOT_LOW
from retuned_shunt import NETWORK
from sic_shunt import MODEL_SHA, installed, spice_model


def point(args):
    path,amplitude,heavy=args
    model=spice_model(path)
    def rail(raw,ctr,th,cap,bypass,leak):
        return relay_margin.rail.variant(raw,ctr,th,local_reservoir.CMIN,bypass,None,**relay_margin.rail.CAND)
    harness,contact,temp,L=(500,150,85,.9) if heavy else (0,30,25,1.1)
    with gain.fixture(),relay_margin.supply_path(2.,HOT_LOW),patch.object(guard_audio,'regulator',rail),installed(model):
        gain.STATE['net']=NETWORK
        source=guard_audio.deck
        def level(f,target,*rest):
            return source(f,amplitude,*rest)
        with patch.object(guard_audio,'deck',level):
            r=gain.audio((20000,harness,1,contact,False,temp,310,True,L),raw=340)
    return dict(target_Vpk=amplitude,harness_pF=harness,contact_pF=contact,temp_C=temp,L_scale=L,
                mixer_Vpk=r['peak_V'],gain_dB=r['gain_dB']+20*math.log10(135/amplitude),
                thd_pct=r['thd_pct'],rail_min_V=r['rail_min_V'],chip_W=r['chip_W'])


if __name__=='__main__':
    args=product([sys.argv[1]],(.135,4.27,13.5,42.7,85,135),(False,True))
    # Fresh ngspice process for each loaded tone. Each run has a separate circuit state.
    import multiprocessing
    with multiprocessing.get_context('spawn').Pool(4,maxtasksperchild=1) as pool:
        rows=pool.map(point,args,chunksize=1)
    (gain.MODULE/'results/sic-signal-levels.json').write_text(json.dumps(dict(network=NETWORK,
           model_sha256=MODEL_SHA,frequency_Hz=20000,raw_V=340,rows=rows),indent=1,default=float)+'\n')
