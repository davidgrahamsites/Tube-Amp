"""HD-003: split-reference feasibility, with unchanged native circuits.

Seam: correction-contract.json -> correction-*.json/cir/log/csv.
Analytical reference screen and simulator adapters are independent functions.
"""
from pathlib import Path
import hashlib
import itertools
import json
import math
import subprocess
import sys
import time

M = Path(__file__).resolve().parents[1]
ROOT = M.parents[2]
OUT = M / 'results'
sys.path.insert(0, str(ROOT / 'engineering/whole-amp/effects-loop/tools'))
import numpy as np
from loaded_feedback_model import build
from run import sp, stats


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def analytic(c):
    """A bounded-input proof; no assumption that reference stays positive."""
    p = c['candidate']
    peak = p['heater_rms_diagnostic_max_V'] * math.sqrt(2) * (1 + p['midpoint_total_tolerance']) / 2
    midpoint_R_max = p['midpoint_R_ohm']*(1+p['midpoint_total_tolerance'])
    rows = []
    for signs in itertools.product([-1, 1], repeat=4):
        rt, rb = [p['divider_R_ohm'] * (1 + s * p['divider_R_total_tolerance']) for s in signs[:2]]
        ct, cb = [p['divider_C_F'] * (1 + s * p['divider_C_total_tolerance']) for s in signs[2:]]
        a0, ai = rb/(rt+rb), ct/(ct+cb)
        rth = rt*rb/(rt+rb)
        leak = p['total_leakage_budget_A'] * (rth+midpoint_R_max)
        bound = max(a0, ai, 1-a0, 1-ai)*p['preamp_ceiling_V'] + peak + leak
        rows.append(dict(rt=rt, rb=rb, ct=ct, cb=cb, a0=a0, ai=ai,
                         tau_s=rth*(ct+cb), rth_ohm=rth,
                         worst_hk_V=bound, margin_V=p['preamp_hk_limit_V']-bound,
                         supply_drop_undershoot_V=min(0,a0-ai)*p['preamp_ceiling_V'],
                         top_DC_W=p['preamp_ceiling_V']**2*rt/(rt+rb)**2,
                         bottom_DC_W=p['preamp_ceiling_V']**2*rb/(rt+rb)**2))
    # Single-fault voltage bounds. No component qualification is implied.
    faults = [dict(fault=f, possible_hk_V=v, passes=v<=p['preamp_hk_limit_V'])
              for f,v in [('top resistor open, steady rail',300+peak),
                          ('bottom resistor open, steady rail',300+peak),
                          ('top resistor short',300+peak),
                          ('bottom resistor short',300+peak),
                          ('top capacitor open, fast startup',300+peak),
                          ('bottom capacitor open, fast startup',300+peak),
                          ('top capacitor short',300+peak),
                          ('bottom capacitor short',300+peak)]]
    returns=[]
    for node,path in c['cathode_return_paths'].items():
        cathode=sum(value for ref,value in path)*(1+p['cathode_resistor_total_tolerance'])
        output=node in ['K_A','K_B']
        reference=0 if output else max(x['rth_ohm'] for x in rows)
        source_open_reference=0 if output else max(x['rb'] for x in rows)
        returns.append(dict(node=node,cathode_return_max_ohm=cathode,
                            total_reference_max_ohm=reference+midpoint_R_max+cathode,
                            source_open_reference_max_ohm=source_open_reference+midpoint_R_max+cathode,
                            limit_ohm=p['output_reference_R_limit_ohm'] if output else p['preamp_reference_R_limit_ohm']))
    return dict(corners=rows, faults=faults, heater_endpoint_peak_V=peak,
                worst_hk_V=max(x['worst_hk_V'] for x in rows),
                minimum_margin_V=min(x['margin_V'] for x in rows),
                reference_to_ground_R_max_ohm=max(x['rth_ohm'] for x in rows)+midpoint_R_max,
                output_reference_to_ground_R_max_ohm=midpoint_R_max,
                cathode_return_paths=returns,
                preamp_nominal_heater_A=4*.3, output_nominal_heater_A=2*1.5,
                native_supply_ceiling_implemented=False, single_fault_qualified=False)


def reference_sim(c, screen):
    """Exercise both fast/slow startup and shutdown against analytic transfer."""
    rows=[]
    # Sequential finite ramps, long holds and both polarities; initial B_PRE=0.
    knots=np.array([0,.01,.01001,.10,.10001,.2,.3,.4,.45,.45001,.46,.46001,.6])
    levels=np.array([0,0,300,300,0,0,300,300,0,300,300,0,0])
    for i,r in enumerate(screen['corners']):
        text=('HD-003 compensated heater reference; allocated values only\n'
              +'VB BPRE 0 PWL('+ ' '.join(f'{t} {v}' for t,v in zip(knots,levels))+')\n'
              +f'RT BPRE HREF {r["rt"]}\nRB HREF 0 {r["rb"]}\n'
              +f'CT BPRE HREF {r["ct"]}\nCB HREF 0 {r["cb"]}\n.end\n')
        path=OUT/f'correction-ref-{i:02}.cir';path.write_text(text)
        sp.load(text);sp.cmd('save v(bpre) v(href)');sp.cmd('tran 10u .6 0 10u')
        t=np.array(sp.vector('time'));u=np.array(sp.vector('v(bpre)'));y=np.array(sp.vector('v(href)'))
        assert t[-1]>=.6*(1-1e-8) and np.isfinite(y).all()
        # Exact linear-ramp propagation of low-pass state at simulator times.
        z=0.; prediction=[0.]
        for j in range(1,len(t)):
            dt=t[j]-t[j-1]; slope=(u[j]-u[j-1])/dt; e=math.exp(-dt/r['tau_s'])
            z=z*e+u[j-1]*(1-e)+slope*(dt-r['tau_s']*(1-e))
            prediction.append(r['ai']*u[j]+(r['a0']-r['ai'])*z)
        rows.append(dict(corner=i,max_error_V=float(np.max(abs(y-prediction))),
                         href_min_V=float(y.min()),href_max_V=float(y.max()),
                         worst_hk_without_leak_V=float(np.maximum(abs(y),abs(u-y)).max())+screen['heater_endpoint_peak_V'],
                         deck_sha256=sha(path)))
        sp.cmd('destroy all')
    return rows


def audio(case):
    text=build(mode='buffer',source_ohm=1000,supply=278,channel=case['channel'],
               amp=case['amp'],freq=1000,volume=1,tone=.5,gain=.5)
    assert text.count('VPRE B_PRE 0 313')==1
    text=text.replace('VPRE B_PRE 0 313',f'VPRE B_PRE 0 {case["pre_V"]}')
    # Only B_PRE changes. B_EARLY remains 278 V to isolate this interface.
    path=OUT/f'correction-{case["id"]}.cir';path.write_text(text)
    sp.load(text);sp.cmd('op')
    nodes=['FX_SEND','MIX_OUT','SPEAKER','DR_K3','DR_CF','PI_K']
    op={n:sp.vector('v('+n.lower()+')')[-1] for n in nodes}
    # feedback_model suppresses source AC; explicitly excite the input here.
    lines=text.splitlines()
    source=[x for x in lines if x.startswith('VSOURCE ')]
    assert len(source)==1 and ' AC 0' in source[0]
    ac_text=text.replace(source[0],source[0].replace(' AC 0',' AC 1'))
    sp.cmd('destroy all');sp.load(ac_text);sp.cmd('ac dec 48 20 20000')
    freq=np.real(sp.vector('frequency'));v=np.array(sp.vector('v(speaker)'))
    points={str(hz):dict(actual_Hz=float(freq[k]),gain=float(abs(v[k])),phase_deg=float(np.angle(v[k],deg=True)))
            for hz in [82.4,1000,5000,10000,20000] for k in [int(np.argmin(abs(freq-hz)))]}
    sp.cmd('destroy all');sp.load(text);sp.cmd('op')
    sp.cmd('save '+' '.join('v('+n.lower()+')' for n in nodes))
    step=1/(1000*96)/case.get('refine',1)
    sp.cmd(f'tran {step} .5 .48 {step}')
    t=np.array(sp.vector('time'));assert t[-1]>=.5*(1-1e-8)
    values={n:np.array(sp.vector('v('+n.lower()+')')) for n in nodes}
    assert all(np.isfinite(y).all() for y in values.values())
    metrics={n:stats(t,y,1000,.5) for n,y in values.items()}
    earlier={n:stats(t,y,1000,.49) for n,y in values.items()}
    sampled=np.arange(2560)/256000+.49
    np.savetxt(OUT/f'correction-{case["id"]}.csv',np.column_stack([sampled,*[np.interp(sampled,t,values[n]) for n in nodes]]),delimiter=',',header='time_s,'+','.join(nodes),comments='',fmt='%.12g')
    return dict(status='completed',case=case,op=op,ac=points,signals=metrics,
                fundamental_W=metrics['SPEAKER']['fundamental_Vpk']**2/16,
                settling_relative={n:abs(metrics[n]['fundamental_Vpk']-earlier[n]['fundamental_Vpk'])/max(metrics[n]['fundamental_Vpk'],1e-12) for n in nodes},
                deck_sha256=sha(path),step_s=step,end_s=float(t[-1]))


def main():
    c=json.loads((M/'correction-contract.json').read_text())
    for path,h in {**c['source_sha256'],**c['native_sha256']}.items():assert sha(ROOT/path)==h,path
    sp.cmd('version');a=analytic(c);ref=reference_sim(c,a)
    result=dict(analytic=a,reference_transients=ref,audio=[],adopted=False,hardware_qualified=False,
                contract_sha256=sha(M/'correction-contract.json'),factory_sha256=sha(Path(__file__)),
                source_sha256=c['source_sha256'],native_sha256=c['native_sha256'])
    output=OUT/'correction-screen.json'
    output.write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'correction-reference.log').write_text('\n'.join(sp.logs))
    cases=[dict(id=f'{ch}-{v}',channel=ch,amp=amp,pre_V=v) for ch,amp in [('clean',.009),('dirty',.02)] for v in [313,300]]
    cases += [dict(cases[1],id='clean-300-fine',refine=2)]
    for case in cases:
        start=time.monotonic();name=case['id'];json_path=OUT/f'correction-{name}.json'
        for suffix in ['json','csv','cir','log']:(OUT/f'correction-{name}.{suffix}').unlink(missing_ok=True)
        try:
            p=subprocess.run([sys.executable,str(Path(__file__)),'--audio',json.dumps(case)],capture_output=True,text=True,timeout=120)
            (OUT/f'correction-{name}.log').write_text(p.stdout+p.stderr)
            row=json.loads(json_path.read_text()) if p.returncode==0 else dict(status='failed',case=case,error=(p.stdout+p.stderr)[-1800:])
        except subprocess.TimeoutExpired as e:
            row=dict(status='timeout',case=case,error='120 s wall limit')
            (OUT/f'correction-{name}.log').write_bytes((e.stdout or b'')+(e.stderr or b''))
        row['elapsed_s']=time.monotonic()-start;json_path.write_text(json.dumps(row,indent=2)+'\n')
        result['audio'].append(row);output.write_text(json.dumps(result,indent=2)+'\n')
        print(name,row['status'],row.get('fundamental_W'),flush=True)
    for path,h in {**c['source_sha256'],**c['native_sha256']}.items():assert sha(ROOT/path)==h,path


if __name__=='__main__':
    if '--audio' in sys.argv:
        try:
            case=json.loads(sys.argv[-1]);row=audio(case)
            (OUT/f'correction-{case["id"]}.json').write_text(json.dumps(row,indent=2)+'\n')
        finally:print('\n'.join(sp.logs[-80:]))
    else:main()
