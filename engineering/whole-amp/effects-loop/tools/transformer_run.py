"""Bounded full-amplifier sensitivity experiment using linear coupled windings.
Owns execution and retained evidence, not transformer selection or CAD changes.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
from fixture import ROOT, WHOLE, fingerprint
from transformer_model import integrated_deck
from run import stats, NODES
sys.path.insert(0, str(WHOLE / 'tools'))
import spice_runtime as sp

OUT = ROOT / 'results'
EXTRA = ['B_SCREEN','EL34_SA','EL34_SB','K_A','K_B','OT_PA','OT_PB','xv5_3.cc','xv6_3.cc']

def worker(name, config, transformer, steps=96, experiment=None):
    paths=[Path(__file__), *[ROOT/'tools'/p for p in ['protection_model.py','transformer_model.py','fixture.py','run.py']], WHOLE/'tools/spice_runtime.py']
    factory_hashes={str(p.relative_to(WHOLE.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    source_hashes=fingerprint()
    text, _ = integrated_deck(transformer, **config)
    experiment = experiment or {}
    from protection_model import apply_experiment, screen_resistances
    text = apply_experiment(text, experiment)
    resistances = screen_resistances(text)
    (OUT / (name + '.cir')).write_text(text)
    sp.cmd('version'); version=list(sp.logs)
    sp.load(text); sp.cmd('op')
    op_speaker = sp.vector('v(speaker)')[-1]
    nodes = NODES + EXTRA
    sp.cmd('save ' + ' '.join('v('+n.lower()+')' for n in nodes) + ' i(vmain) i(vscreen)')
    f = config['freq']; end = max(.5, 30/f); step = min(20e-6,1/(f*steps))
    sp.cmd(f'tran {step} {end} {end-20/f} {step}')
    t = np.asarray(sp.vector('time'))
    if len(t) == 0 or t[-1] < end*(1-1e-8):raise RuntimeError('Transient stopped early')
    values = {n:np.asarray(sp.vector('v('+n.lower()+')')) for n in nodes}
    if not all(np.isfinite(v).all() for v in values.values()):raise RuntimeError('Nonfinite vectors')
    signals = {n:stats(t,values[n],f,end) for n in NODES}
    earlier = {n:stats(t,values[n],f,end-10/f) for n in NODES}
    settling = {n:abs(signals[n]['fundamental_Vpk']-earlier[n]['fundamental_Vpk']) / max(signals[n]['fundamental_Vpk'],1e-12) for n in NODES}
    times = np.linspace(end-10/f,end,10001)
    def average(values):return float(np.trapezoid(np.interp(times,t,values),times)/(times[-1]-times[0]))
    stress = {}
    for side,tube in [('A','5'),('B','6')]:
        resistance = resistances[side]
        screen_current = (values['B_SCREEN']-values['EL34_S'+side])/resistance
        plate_current = .00186*values['xv'+tube+'_3.cc']
        stress[side] = dict(screen_resistor_ohm=resistance, screen_resistor_W=average(screen_current**2*resistance),
            screen_W=average((values['EL34_S'+side]-values['K_'+side])*screen_current),
            plate_W=average((values['OT_P'+side]-values['K_'+side])*plate_current))
    row = dict(status='completed', config=config, transformer=transformer, steps_per_cycle=steps,
        end_s=float(t[-1]), max_step_s=step, op_speaker_DC_V=op_speaker, signals=signals,
        fundamental_load_W=signals['SPEAKER']['fundamental_Vpk']**2/16,
        total_load_W=average(values['SPEAKER']**2/8), stress=stress,
        main_supply_mean_A=-average(np.asarray(sp.vector('i(vmain)'))),
        screen_supply_mean_A=-average(np.asarray(sp.vector('i(vscreen)'))),
        settling_relative_fundamental=settling, simulator_version_log=version,
        experiment=experiment, source_hashes=source_hashes, factory_hashes=factory_hashes,
        deck_sha256=hashlib.sha256(text.encode()).hexdigest(), physical_qualified=False)
    assert fingerprint()==source_hashes, 'Source changed during worker'
    assert factory_hashes=={str(p.relative_to(WHOLE.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}, 'Factory changed during worker'
    (OUT / (name + '.json')).write_text(json.dumps(row,indent=2,allow_nan=False)+'\n')

def bounded(name, config, transformer, steps=96, experiment=None, timeout=60):
    start=time.monotonic()
    try:
        p=subprocess.run([sys.executable,__file__,'--worker',name,json.dumps(config),json.dumps(transformer),str(steps),json.dumps(experiment or {})],
            capture_output=True,text=True,timeout=timeout)
        row=json.loads((OUT/(name+'.json')).read_text()) if p.returncode == 0 else dict(status='failed',error=p.stderr[-2000:])
    except subprocess.TimeoutExpired:
        row=dict(status='timeout',error=f'Worker terminated at {timeout} seconds; no complete result')
    row.update(config=config,transformer=transformer,experiment=experiment or {},steps_per_cycle=steps,elapsed_s=time.monotonic()-start,wall_time_limit_s=timeout)
    (OUT/(name+'.json')).write_text(json.dumps(row,indent=2,allow_nan=False)+'\n')
    print(name,row['status'],flush=True)
    return dict(name=name,**row)

def ac_sensitivity():
    rows=[]
    for half in [2.5,10,40]:
        for k in [1,.999,.995]:
            transformer=dict(half_primary_H=half,coupling=k)
            text,_=integrated_deck(transformer,mode='return-drive',amp=0)
            name='magnetics-ac-'+str(half).replace('.','p')+'-'+str(k).replace('.','p')
            (OUT/(name+'.cir')).write_text(text)
            sp.load(text);sp.cmd('op');dc=sp.vector('v(speaker)')[-1]
            sp.cmd('ac dec 80 10 1000000')
            freq=np.real(sp.vector('frequency'));v=np.asarray(sp.vector('v(speaker)'))
            points={str(hz):dict(actual_Hz=float(freq[i]),gain=float(abs(v[i])),phase_deg=float(np.angle(v[i],deg=True)))
                for hz in [20,50,82.4,1000,5000,20000,100000] for i in [int(np.argmin(abs(freq-hz))) ]}
            i=int(np.argmax(abs(v)));rows.append(dict(name=name,transformer=transformer,
                op_speaker_DC_V=dc,points=points,peak_gain=float(abs(v[i])),peak_Hz=float(freq[i])))
            sp.cmd('destroy all')
    return rows

def main():
    hashes=fingerprint()
    config=dict(channel='clean',mode='native',freq=1000,amp=.00672,supply=278,volume=1,tone=.5,gain=.5,guard_pentode_power=True)
    result=dict(scope='Assumed linear magnetics sensitivity; not manufacturer or measured parameters',
        source_hashes=hashes,ac=ac_sensitivity(),transients=[],physical_qualified=False,fabrication_ready=False)
    cases=[('base-1k',config,{},96),('base-1k-refined',config,{},192),
           ('base-82',dict(config,freq=82.4),{},96),
           ('lowL-82',dict(config,freq=82.4),dict(half_primary_H=2.5),96),
           ('leakage-1k',config,dict(coupling=.999),96)]
    for label,cfg,tx,steps in cases:
        result['transients'].append(bounded('magnetics-'+label,cfg,tx,steps))
        (OUT/'magnetics-summary.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    assert fingerprint()==hashes,'Source changed during run'
    files=[Path(__file__),ROOT/'tools/transformer_model.py',ROOT/'tools/fixture.py',ROOT/'tools/run.py',WHOLE/'tools/spice_runtime.py']
    result['factory_hashes']={str(p.relative_to(WHOLE.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    (OUT/'magnetics-summary.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps([dict(name=r['name'],status=r['status'],W=r.get('fundamental_load_W'),speaker=r.get('signals',{}).get('SPEAKER'),stress=r.get('stress')) for r in result['transients']],indent=2))

if __name__ == '__main__':
    name = sys.argv[2] if '--worker' in sys.argv else 'magnetics-ac'
    try:
        if '--worker' in sys.argv:worker(name,json.loads(sys.argv[3]),json.loads(sys.argv[4]),int(sys.argv[5]),json.loads(sys.argv[6]) if len(sys.argv)>6 else {})
        else:main()
    finally:(OUT/(name+'.log')).write_text('\n'.join(x.rstrip() for x in sp.logs)+'\n')
