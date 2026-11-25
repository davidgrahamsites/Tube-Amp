#!/usr/bin/env python3
"""Source-derived preamp cable-loading screen. No native CAD writes.

Capacitances describe a hypothetical harness, not the UL1330 candidate.
The reused fixture includes the native passive mix and generic tube stages;
report FX_SEND only, not speaker response or output-loop stability.
"""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

MODULE = Path(__file__).resolve().parents[1]
WHOLE = MODULE.parent
sys.path.insert(0, str(WHOLE / 'effects-loop/tools'))
from fixture import deck, fingerprint, PARTS
sys.path.insert(0, str(WHOLE / 'tools'))
import spice_runtime as sp

POTS = {x['reference']: x for x in PARTS if x['reference'] in {f'RV{i}' for i in range(1,9)}}
OUT = MODULE / 'results'
LIMIT_DB = 1.0  # Engineering comparison budget, not a user-approved specification.


def build(config, ground_pf, mutual_pf, pots=None):
    assert ground_pf >= 0 and mutual_pf >= 0
    text, _ = deck(mode='native', stimulus='dry', amp=0,
                   guard_pentode_power=True, **config)
    extra = []
    for ref in sorted(pots if pots is not None else POTS):
        pins = {pin: ('0' if net == 'GND' else net) for pin,net in POTS[ref]['pins'].items()}
        # Each physical lead contributes: repeated nets must not deduplicate
        # their lead-to-shield/chassis capacitance.
        if ground_pf:
            for pin, net in pins.items():
                if net != '0':
                    extra.append(f'CHG_{ref}_{pin} {net} 0 {ground_pf}p')
        if mutual_pf:
            for a,b in [('1','2'),('1','3'),('2','3')]:
                if pins[a] != pins[b]:
                    extra.append(f'CHM_{ref}_{a}{b} {pins[a]} {pins[b]} {mutual_pf}p')
    assert text.count('\n.end\n') == 1
    return text.replace('\n.end\n', '\n'+'\n'.join(extra)+'\n.end\n'), extra


def run(config, ground_pf, mutual_pf, pots=None, points=201):
    text, extra = build(config, ground_pf, mutual_pf, pots)
    sp.load(text)
    sp.cmd('op')
    op = float(sp.vector('v(fx_send)')[-1])
    # Linear grid includes exactly 1, 5, 10 and 20 kHz.
    sp.cmd(f'ac lin {points} 0 20000')
    freq = np.real(sp.vector('frequency'))
    signal = np.asarray(sp.vector('v(fx_send)'))
    sp.cmd('destroy all')
    assert len(freq) == points and np.all(np.isfinite(signal)) and np.isfinite(op)
    assert np.allclose(freq, np.linspace(0,20000,points))
    return signal, op, hashlib.sha256(text.encode()).hexdigest(), len(extra), text


def compare(signal, reference):
    assert np.all(np.abs(reference[1:]) > 1e-15)
    frequency = np.linspace(0,20000,len(signal))[1:]
    delta = 20*np.log10(np.maximum(np.abs(signal[1:]),1e-30)/np.abs(reference[1:]))
    samples = {str(hz): float(delta[int(np.argmin(abs(frequency-hz)))]) for hz in [1000,5000,10000,20000]}
    band = delta[frequency >= 100]
    return {
        'delta_db': samples,
        'shape_delta_relative_1k_db': {hz: db-samples['1000'] for hz,db in samples.items()},
        'worst_abs_delta_100_to_20000_db': float(np.max(np.abs(band))),
        'within_1db_over_100_to_20000': bool(np.max(np.abs(band)) <= LIMIT_DB),
        'within_1db_at_10k_and_20k': all(abs(samples[str(hz)]) <= LIMIT_DB for hz in [10000,20000])
    }


def hashes():
    paths = [Path(__file__), WHOLE/'effects-loop/tools/fixture.py', WHOLE/'tools/spice_runtime.py']
    paths += sorted((WHOLE/'pcb-measured-r/boards').glob('*.kicad_pcb'))
    return {str(p.relative_to(WHOLE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def main():
    inputs = {**fingerprint(), **hashes()}
    sp.cmd('version')
    version = list(sp.logs)
    controls = {}
    config = dict(channel='clean', volume=.5, tone=.5, gain=.5)
    zero, zero_extra = build(config,0,0)
    assert not zero_extra and 'CHG_' not in zero and 'CHM_' not in zero
    _, dup = build(config,100,0,['RV2'])
    assert len(dup)==3 and sum('CL_BASS_TOP 0' in x for x in dup)==2
    _, pair = build(config,0,100,['RV2'])
    assert len(pair)==2 and all('CL_BASS_TOP CL_BASS_BOTTOM' in x for x in pair)
    controls['repeated_net_leads_preserved'] = True
    controls['same_net_mutual_caps_omitted'] = True
    # Independent elementary RC control checks solver units and comparison sign.
    sp.load('Harness RC control\nV1 in 0 AC 1\nR1 in out 100k\nC1 out 0 100p\n.end\n')
    sp.cmd('ac lin 1 20000 20000')
    actual = complex(sp.vector('v(out)')[0])
    sp.cmd('destroy all')
    expected = 1/(1+1j*2*np.pi*20000*100e3*100e-12)
    assert abs(actual-expected)<1e-9
    controls['independent_rc_complex_error'] = float(abs(actual-expected))
    baseline, op, _, _, _ = run(config,0,0)
    check, check_op, _, _, _ = run(config,0,0)
    assert np.max(abs(check-baseline))<1e-10 and abs(check_op-op)<1e-8
    controls['zero_load_repeat_max_error'] = float(np.max(abs(check-baseline)))
    rows=[]; baselines=[]; count=0
    for channel in ['clean','dirty']:
        for volume in [.1,.5,1.0]:
            for tone in [0,.5,1.0]:
                for gain in ([.5] if channel=='clean' else [.1,.5,1.0]):
                    cfg=dict(channel=channel,volume=volume,tone=tone,gain=gain)
                    ref,dc,sha,_,text=run(cfg,0,0)
                    baselines.append(dict(config=cfg,deck_sha256=sha,fx_send_dc_v=dc))
                    for ground_pf,mutual_pf in [(1,0),(3,0),(5,0),(10,0),(30,0),(100,0),(300,0),
                                                (1,.5),(3,1.5),(5,2.5),(10,5),(30,15),(100,50),(300,150)]:
                        y,dc2,sha,n,text=run(cfg,ground_pf,mutual_pf)
                        assert abs(dc2-dc)<1e-6, 'Pure cable capacitors changed DC'
                        rows.append(dict(config=cfg,ground_pf_per_lead=ground_pf,
                            mutual_pf_per_pair=mutual_pf,deck_sha256=sha,added_capacitors=n,
                            dc_delta_v=dc2-dc,**compare(y,ref)))
                        if cfg==config and (ground_pf,mutual_pf)==(100,50):
                            (OUT/'cable-loading-example.cir').write_text(text)
                    count+=1
                    print('Completed cable setting',count,cfg,flush=True)
    attribution=[]
    for channel,pots in [('clean',['RV1','RV2','RV3']),('dirty',['RV4','RV5','RV6','RV7','RV8'])]:
        cfg=dict(channel=channel,volume=.5,tone=.5,gain=.5)
        ref,_,_,_,_=run(cfg,0,0)
        for pot in pots:
            y,_,sha,_,_=run(cfg,100,50,[pot])
            attribution.append(dict(pot=pot,config=cfg,ground_pf_per_lead=100,
                mutual_pf_per_pair=50,deck_sha256=sha,**compare(y,ref)))
    refinements=[]
    for row in [max(rows,key=lambda x:x['worst_abs_delta_100_to_20000_db']),
                max(rows,key=lambda x:x['delta_db']['20000'])]:
        cfg=row['config']
        ref,_,_,_,_=run(cfg,0,0,points=2001)
        y,_,sha,_,_=run(cfg,row['ground_pf_per_lead'],row['mutual_pf_per_pair'],points=2001)
        refined=compare(y,ref)
        difference=abs(refined['worst_abs_delta_100_to_20000_db']-row['worst_abs_delta_100_to_20000_db'])
        assert difference<.1, 'Frequency-grid refinement materially changed extremum'
        refinements.append(dict(config=cfg,ground_pf_per_lead=row['ground_pf_per_lead'],
            mutual_pf_per_pair=row['mutual_pf_per_pair'],points=2001,deck_sha256=sha,
            maximum_difference_db=difference,**refined))
    aggregate=[]
    for cg,cm in sorted({(r['ground_pf_per_lead'],r['mutual_pf_per_pair']) for r in rows}):
        rs=[r for r in rows if (r['ground_pf_per_lead'],r['mutual_pf_per_pair'])==(cg,cm)]
        aggregate.append(dict(ground_pf_per_lead=cg,mutual_pf_per_pair=cm,
            settings=len(rs),within_1db_over_band=sum(r['within_1db_over_100_to_20000'] for r in rs),
            worst_abs_delta_db=max(r['worst_abs_delta_100_to_20000_db'] for r in rs)))
    assert inputs=={**fingerprint(),**hashes()}, 'Inputs changed during simulation'
    assert len(baselines)==36 and len(rows)==504 and len(attribution)==8
    summary = {
        'scope':'RV1–RV8 cable-loading comparison at FX_SEND; not physical cable selection or whole-amplifier acceptance',
        'source_and_factory_hashes': inputs, 'simulator_version':version,
        'comparison_budget_db':LIMIT_DB, 'budget_authority':'Engineering screening proposal only',
        'controls':controls, 'baseline_count':len(baselines), 'loaded_count':len(rows),
        'exceeding_budget_count':sum(not x['within_1db_at_10k_and_20k'] for x in rows),
        'baselines':baselines, 'loaded_cases':rows, 'one_pot_attribution':attribution,
        'frequency_grid_refinements':refinements,'aggregate':aggregate,
        'worst_case':max(rows,key=lambda x:x['worst_abs_delta_100_to_20000_db']),
        'native_cad_preserved':True, 'physical_cable_length_limit_m':None,
        'limits':['Hypothetical per-lead shunt and per-pair mutual capacitance; no measured cable matrix',
          'Pot settings are resistance fractions, not knob rotation; correlated tone controls do not cover every independent setting',
          'Generic tube models, stiff supply, 20k input source and 470p input cable inherited from fixture',
          'RV9 presence, RV602 wet harness, crosstalk between separate harnesses, pickup/EMI and large-signal faults not qualified',
          'Source fixture ideal output transformer is unsuitable for output-stage/stability certification'],
        'checks_passed':True, 'harness_qualified':False, 'fabrication_ready':False
    }
    (OUT/'cable-loading.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    (OUT/'cable-loading.log').write_text('\n'.join(line.rstrip() for item in sp.logs for line in item.splitlines())+'\n')
    print(json.dumps({k:summary[k] for k in ['baseline_count','loaded_count','exceeding_budget_count','worst_case','harness_qualified']},indent=2))


if __name__=='__main__':
    main()
