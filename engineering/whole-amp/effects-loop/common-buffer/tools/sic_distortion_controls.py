"""CB-015. Compare the intermediate-level distortion with a fixed capacitance and a finer timestep."""
import json
import multiprocessing
import sys
from unittest.mock import patch

import fixed_gain as gain
import guard_audio
import local_reservoir
import relay_margin
from cutoff_guard_model import HOT_LOW
from retuned_shunt import NETWORK
from sic_shunt import installed, spice_model, MODEL_SHA
import numpy as np


def point(args):
    path,target,mode,factor=args
    model=spice_model(path)
    def rail(raw,ctr,th,cap,bypass,leak):
        return relay_margin.rail.variant(raw,ctr,th,local_reservoir.CMIN,bypass,None,**relay_margin.rail.CAND)
    with gain.fixture(),relay_margin.supply_path(2.,HOT_LOW),patch.object(guard_audio,'regulator',rail),installed(model):
        gain.STATE['net']=NETWORK
        original_deck,original_cmd=guard_audio.deck,gain.sp.cmd
        captures={}
        def source(f,reference,*rest):
            return original_deck(f,target,*rest)
        def metrics(cmd):
            if cmd.startswith('tran '):
                _,step,end,zero,maximum=cmd.split()
                cmd=f'tran {float(step)/factor} {end} {zero} {float(maximum)/factor}'
            if cmd.startswith('save '):
                cmd+=' v(input6) v(low) v(driver8)'
                if mode=='JFET':
                    cmd+=' v(island13) v(gate13)'
            if cmd=='destroy all':
                t=np.asarray(gain.sp.vector('time'))
                f=20000
                samples=t[-1]+(np.arange(8192)/819.2-10)/f
                for n in ['input6','low','preout','driver8','fx_return']:
                    v=np.interp(samples,t,gain.sp.vector(f'v({n})'))
                    harm=2*abs(np.fft.rfft(v)/len(v))[np.arange(1,11)*10]
                    captures[n]=dict(fund_Vpk=harm[0],THD_pct=100*np.linalg.norm(harm[1:])/harm[0],
                                     harmonics_Vpk=harm.tolist())
                if mode=='JFET':
                    island=np.interp(samples,t,gain.sp.vector('v(island13)'))
                    captures['island_range_V']=[min(island),max(island)]
            original_cmd(cmd)
        with patch.object(guard_audio,'deck',source),patch.object(gain.sp,'cmd',metrics):
            r=gain.audio((20000,0,300,30,False,25,310,mode=='JFET',1.1),raw=340)
        return dict(target_Vpk=target,shunt=mode,step_refinement=factor,mixer_thd_pct=r['thd_pct'],probes=captures)


if __name__=='__main__':
    args=[(sys.argv[1],amplitude,mode,factor) for amplitude in (.135,13.5) for mode in ('JFET','fixed 300 pF') for factor in (1,2)]
    with multiprocessing.get_context('spawn').Pool(4,maxtasksperchild=1) as pool:
        rows=pool.map(point,args,chunksize=1)
    (gain.MODULE/'results/sic-distortion-controls.json').write_text(json.dumps(dict(model_sha256=MODEL_SHA,
            network=NETWORK,rows=rows),indent=1,default=float)+'\n')
