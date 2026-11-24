"""Loaded-winding AC sensitivity, with bilateral return-wire measurement.

Keeps experiments outside native CAD. Measurement checks are separate from
engineering screens, which cannot qualify an unselected physical transformer.
"""
import hashlib
import json
from pathlib import Path

import numpy as np

from feedback_model import DEFAULTS, build as ideal_tap
from feedback_sweep import analyze
from fixture import ROOT, fingerprint
from loaded_feedback_model import build, split_probe
from loop_probe import injections, return_ratio, run_ac, admittance_probe, append_elements, sp

OUT = ROOT / 'results'
FACTORIES = ['sweep_loaded_feedback.py', 'loaded_feedback_model.py', 'loop_probe.py',
             'feedback_model.py', 'feedback_sweep.py', 'transformer_model.py', 'fixture.py']


def hashes():
    files = [ROOT / 'tools' / p for p in FACTORIES] + [ROOT.parent / 'tools/spice_runtime.py']
    return {str(p.relative_to(ROOT.parent.parent.parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def cases():
    for lm in (10, 40, 160):
        for leak in (.005, .02, .08):
            for cap in (50e-12, 250e-12, 1000e-12):
                yield f'base-lm{lm}-lk{round(leak*1000)}-cp{round(cap*1e12)}', dict(magnetizing_H=lm, leakage_H=leak, primary_cap_F=cap)
    for leak in (.02, .08):
        for presence in (0, .5, 1):
            for pi, fb in ((47, 0), (100, 0), (100, 22), (100, 47), (150, 22), (47, 220)):
                yield f'pi{pi}-fb{fb}-lk{round(leak*1000)}-pres{presence}', dict(leakage_H=leak, presence=presence, pi_cap_F=pi*1e-12, feedback_cap_F=fb*1e-12)
    for load in (4, 16):
        for presence in (0, .5, 1):
            yield f'load{load}-pres{presence}', dict(load_ohm=load, presence=presence, load_cap_F=2e-9)
    for resistance in (8.2, 22, 47):
        for cap in (100e-9, 220e-9, 470e-9):
            for presence in (0, .5):
                yield f'damp{resistance}-{round(cap*1e9)}n-pres{presence}', dict(leakage_H=.08, presence=presence, damping_RC=[resistance, cap])


def main():
    source, factories = fingerprint(), hashes()
    rows, curves = [], {}
    nodes = ['speaker', 'ot_4', 'pi_p1', 'pi_p2', 'pi_k', 'ot_pa', 'ot_pb']
    sp.cmd('version')
    version = list(sp.logs)
    for label, p in cases():
        name = 'loaded-' + label
        text = build(p)
        f, closed, op = run_ac(text, nodes)
        previous_text = ideal_tap(p)
        if p.get('damping_RC'):
            r, c = p['damping_RC']
            previous_text = append_elements(previous_text, [f'RDAMP SPEAKER DAMP_MID {r}', f'CDAMP DAMP_MID 0 {c}'])
        _, previous, _ = run_ac(previous_text, nodes)
        # Zero every external AC stimulus; feedback stimulus inserted separately.
        zero = text.replace('AC 1', 'AC 0')
        split = split_probe(zero)
        measurements, dc_errors, decks = {}, [], dict(closed=text)
        for kind, deck in injections(split).items():
            _, v, bias = run_ac(deck, nodes + ['tx_tap'], ['vprobe'])
            measurements[kind] = v
            dc_errors.append(max(abs(bias[n] - op[n]) for n in nodes))
            decks[kind] = deck
        T = return_ratio(measurements['voltage'], measurements['current'], 'ot_4')
        a = analyze(f, T, closed['speaker'])
        y_error = None
        if label in ('base-lm40-lk20-cp250', 'pi47-fb220-lk80-pres0'):
            Y = admittance_probe(split, op['ot_4'])
            y_error = float(np.max(abs(Y - T) / np.maximum(abs(T), 1e-7)))
        delta = 20 * np.log10(abs(closed['speaker']) / abs(previous['speaker']))
        # These are explicit engineering screening targets, not user tonal specs.
        gm, angle = a['min_gain_margin_dB'], a['min_unity_angle_deg']
        screen = dict(gain_margin_at_least_10dB=gm is None or gm >= 10,
                      all_unity_angles_at_least_45deg=angle is None or angle >= 45,
                      HF_peaking_at_most_3dB=a['HF_peak_relative_1k_dB'] <= 3)
        row = dict(name=name, parameters=dict(DEFAULTS, **p), analysis=a,
                   operating_point=op, probe_DC_error_V=max(dc_errors),
                   independent_Y_relative_error=y_error,
                   ideal_tap_change_dB={str(hz): float(delta[np.argmin(abs(f-hz))]) for hz in (1000, 5000, 10000, 20000)},
                   engineering_screen=screen, passes_screen=all(screen.values()),
                   deck_hashes={k: hashlib.sha256(d.encode()).hexdigest() for k, d in decks.items()})
        rows.append(row)
        for kind, deck in decks.items():
            (OUT / f'{name}-{kind}.cir').write_text(deck)
        if label in ('base-lm40-lk20-cp250', 'pi47-fb0-lk80-pres0', 'pi100-fb22-lk80-pres0', 'pi47-fb220-lk80-pres0'):
            curves[label] = dict(frequency_Hz=f.tolist(), loop_real=T.real.tolist(), loop_imag=T.imag.tolist(), gain=abs(closed['speaker']).tolist())
        print(label, 'GM', gm, 'angle', angle, 'peak', a['HF_peak_relative_1k_dB'], flush=True)
    checks = dict(source_preserved=source == fingerprint(), factories_preserved=factories == hashes(),
                  DC_preserved=all(r['probe_DC_error_V'] < 1e-5 for r in rows),
                  independent_Y_agrees=all(r['independent_Y_relative_error'] < 1e-4 for r in rows if r['independent_Y_relative_error'] is not None),
                  finite=all(np.isfinite(r['analysis']['sensitivity_peak']) for r in rows))
    result = dict(scope='Generic loaded-winding global-loop sensitivity, not physical qualification',
                  source_hashes=source, factory_hashes=factories, simulator_version_log=version,
                  cases=rows, checks=checks, passed=all(checks.values()), native_compensation_changed=False,
                  physical_qualified=False, fabrication_ready=False)
    (OUT / 'loaded-feedback-summary.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    (OUT / 'loaded-feedback-curves.json').write_text(json.dumps(curves, separators=(',', ':'), allow_nan=False) + '\n')
    (OUT / 'loaded-feedback-sweep.log').write_text('\n'.join(sp.logs) + '\n')
    assert result['passed'], checks
    print(len(rows), 'loaded-winding cases; measurement checks PASS')


if __name__ == '__main__':
    main()
