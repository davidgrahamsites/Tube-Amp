"""CB-013 audio, pulse and mismatch checks. Run with KiCad Python and model path."""
import json
import sys
from contextlib import contextmanager
from itertools import product
from unittest.mock import patch

import assembled_return as assembly
import fixed_gain as gain
import guard_audio
import local_reservoir
import relay_margin
import sic_shunt
from cutoff_guard_model import HOT_LOW

NETWORK=dict(assembly.NETWORK,feedback=40600,name='CB-013')


@contextmanager
def peaks():
    original=gain.sp.cmd
    traces={}
    def capture(command):
        names=['v(gate13)','v(island13)','v(mix)']
        if command.startswith('save '):
            command+=' '+' '.join(names[:2])
        if command=='destroy all':
            gate,island,mix=[gain.np.asarray(gain.sp.vector(n)) for n in names]
            vgs=gate-island
            traces.update(external_gate_min_V=min(vgs),external_gate_max_V=max(vgs),mixer_peak_V=max(abs(mix)))
        original(command)
    with patch.object(gain.sp,'cmd',capture):
        yield traces


def switching(model):
    rows=[]
    cases=[(-10,1),(-6,.75),(-14,1.25)]
    cases += list(product((-10.25,-9.75),(.9,1.1)))
    for (vth,cap),step in product(cases,(-160,0,160)):
        with sic_shunt.installed(model,threshold=vth,cap_scale=cap),peaks() as traces:
            gain.guard_injection.run(step,1,18)
        rows.append(dict(ground_leg_Vto=vth,ground_leg_Miller_scale=cap,step_V=step,**traces))
    return rows


def faults(model):
    rows=[]
    for (vth,k,wire),sign,phase in product([(-10,1,0),(-9.75,1.1,4)],(-1,1),(None,0,90,180,270)):
        row=dict(ground_leg_Vto=vth,ground_leg_Miller_scale=k,wire_ohm=wire,sign=sign,phase_deg=phase)
        for refined in (False,True):
            try:
                with sic_shunt.installed(model,threshold=vth,cap_scale=k,wire_ohm=wire),peaks() as traces:
                    r=gain.sudden_guard.fault('JFET pulse',live_phase=phase,sign=sign,fine=refined)
                keys=['post_switch_peak_V','peak_shunt_A','shunt_energy_uJ','timestep_ns','reached_s']
                row.update(completed=True,**{key:r[key] for key in keys},**traces)
                break
            except AssertionError:
                # Retain a stopped transient. Never extract a peak as a pass from that trace.
                time=gain.sp.vector('time')
                row.setdefault('incomplete_attempts',[]).append(dict(max_step_ns=1 if refined else 4,
                      reached_s=float(time[-1]),diagnostic=gain.sp.logs[-8:]))
                gain.pulse_winding._cmd('destroy all')
                row['completed']=False
        rows.append(row)
        print('fault',sign,phase,wire,row['completed'],flush=True)
    return rows


def audio(model):
    def rail(raw,ctr,th,cap,bypass,leak):
        return relay_margin.rail.variant(raw,ctr,th,local_reservoir.CMIN,bypass,None,**relay_margin.rail.CAND)
    bands,full=[],[]
    with relay_margin.supply_path(2.,HOT_LOW),patch.object(guard_audio,'regulator',rail),sic_shunt.installed(model):
        for h,o,t,l,k in product((0,500),(30,150),(25,85),(.9,1.1),(.977,1.023)):
            args=(20000,h,1,o,False,t,310,True,l)
            r=gain.audio(args,cap_scale=k,ac_only=True)['small_signal']
            band=r['band_min_max_dB']+[r['gain_dB']['20'],r['gain_dB']['20000']]
            bands.append(dict(args=args,cap_scale=k,low_dB=min(band),high_dB=max(band)))
        extremes=[min(bands,key=lambda r:r['low_dB']),max(bands,key=lambda r:r['high_dB'])]
        for case in extremes:
            r=gain.audio(case['args'],cap_scale=case['cap_scale'],raw=340)
            full.append(dict(case=case,**{k:r[k] for k in ['gain_dB','thd_pct','peak_V','rail_min_V','chip_W','windings']}))
    return dict(bands=bands,full_level=full)


if __name__=='__main__':
    group,path=sys.argv[1:]
    run={'switching':switching,'faults':faults,'audio':audio}[group]
    model=sic_shunt.spice_model(path)
    with gain.fixture():
        gain.STATE['net']=NETWORK
        receipt=dict(model_sha256=sic_shunt.MODEL_SHA,group=group,network=NETWORK,results=run(model))
    (gain.MODULE/f'results/sic-{group}.json').write_text(json.dumps(receipt,indent=1,default=float)+'\n')
