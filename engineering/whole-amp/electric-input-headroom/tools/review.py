"""Review saved nonlinear sweep; never changes the circuit or simulation."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results'
summary = OUT / 'summary.json'
d = json.loads(summary.read_text())
assert len(d['cases']) == 108 and len(d['refinements']) == 8
assert len(d['volume_comparison']) == 2
assert d['contract_sha256'] == hashlib.sha256((ROOT.parent / 'reverb-600/circuit.json').read_bytes()).hexdigest()
assert d['model_sha256'] == hashlib.sha256((ROOT.parent / 'simulation/models/dm12ax7s.inc').read_bytes()).hexdigest()

def plate(row):
    return row['signals'][('CL' if row['channel'] == 'clean' else 'DR') + '_P1']

comparisons = []
for r in d['refinements']:
    c = next(c for c in d['cases'] if all(c[k] == r[k] for k in
             ['channel', 'B_EARLY_V', 'frequency_Hz', 'source_Vpk']))
    comparisons.append(dict(baseline=c['id'], refinement=r['id'],
        first_stage_gain_change_percent=100 * (r['first_stage_gain'] / c['first_stage_gain'] - 1),
        first_stage_THD_change_percentage_points=plate(r)['THD_2_to_10_percent'] - plate(c)['THD_2_to_10_percent']))

brackets = []
for ch in ['clean', 'dirty']:
    for supply in [240, 278, 320]:
        for frequency in [82.4, 1000]:
            rows = sorted([c for c in d['cases'] if c['channel'] == ch and
                           c['B_EARLY_V'] == supply and c['frequency_Hz'] == frequency],
                          key=lambda c: c['source_Vpk'])
            for metric in ['5_percent_THD', '1_dB_gain_compression']:
                hit = next((i for i, c in enumerate(rows) if
                            (plate(c)['THD_2_to_10_percent'] >= 5 if metric.startswith('5')
                             else c['gain_change_dB_from_10mV'] <= -1)), None)
                brackets.append(dict(channel=ch, supply_V=supply, frequency_Hz=frequency,
                    diagnostic=metric, last_below_source_Vpk=rows[hit-1]['source_Vpk'] if hit else
                    (rows[-1]['source_Vpk'] if hit is None else None),
                    first_at_or_above_source_Vpk=rows[hit]['source_Vpk'] if hit is not None else None))

rows = d['cases'] + d['refinements'] + d['volume_comparison']
report = dict(summary_sha256=hashlib.sha256(summary.read_bytes()).hexdigest(), total_cases=len(rows),
    scope='First-stage numerical stability, not real-pickup or whole-amplifier qualification',
    max_refinement_gain_change_percent=max(abs(c['first_stage_gain_change_percent']) for c in comparisons),
    max_refinement_THD_change_percentage_points=max(abs(c['first_stage_THD_change_percentage_points']) for c in comparisons),
    max_adjacent_window_gain_change_percent=100*max(c['first_stage_settling_fundamental_relative_change'] for c in rows),
    max_adjacent_window_THD_change_percentage_points=max(c['first_stage_settling_THD_percentage_point_change'] for c in rows),
    comparisons=comparisons, first_sample_crossings=brackets)
(OUT / 'numerical-review.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
lines = ['# Electric input headroom — 21 November 2026', '',
    'Keep the original electric input. The model shows progressive first-stage distortion with large signals; an added unity-gain buffer would not supply extra tube headroom. No attenuator or circuit change is selected from these assumed sine-wave tests.', '',
    '## Nominal first-stage screen', '',
    'B_EARLY 278 V, B_PRE 313 V, 1 kHz. Source amplitude is before the assumed 20 kΩ pickup resistance and 470 pF cable. Jack amplitude is measured in the fixture. THD includes harmonics 2–10 at the first plate, not the speaker output.', '',
    '| Channel | Source V peak | Jack V peak | First-plate THD % | Gain change dB |',
    '|---|---:|---:|---:|---:|']
for c in d['cases']:
    if c['B_EARLY_V'] == 278 and c['frequency_Hz'] == 1000 and c['source_Vpk'] in [.25, .5, 1, 1.5, 2]:
        lines.append(f"| {c['channel']} | {c['source_Vpk']} | {c['signals']['INPUT']['fundamental_Vpk']:.4f} | {plate(c)['THD_2_to_10_percent']:.3f} | {c['gain_change_dB_from_10mV']:.3f} |")
lines += ['', '## Numerical check', '',
    f"Completed {len(rows)} cases: 108 supply/frequency/amplitude points, eight finer-step/longer-settling comparisons and two clean-volume controls. Baselines settle at least 0.5 seconds; refinements at least 1 second. Maximum first-stage gain change on refinement is {report['max_refinement_gain_change_percent']:.5f}%; maximum THD change is {report['max_refinement_THD_change_percentage_points']:.5f} percentage points. Adjacent last-ten-period windows differ by at most {report['max_adjacent_window_gain_change_percent']:.5f}% gain and {report['max_adjacent_window_THD_change_percentage_points']:.5f} THD percentage points. These observed differences support the coarse amplitude brackets; no precision clipping-voltage specification is implied.", '',
    'At 1 kHz, the first-stage 5% THD diagnostic is crossed between 1 and 1.5 V source peak in both channels at all three supply settings. This threshold was a diagnostic, not an agreed clean-output specification. Whole-preamp results include later-stage distortion, especially the intentional dirty channel. Lowering the post-first-stage volume does not remove distortion already produced by the first triode.', '',
    '## Scope and limits', '',
    'This is the unchanged generic Duncan Munro 1997 12AX7 model, not the exact purchased tube. Supplies 240/278/320 V with the second rail 35 V higher are assumed sensitivity points. Pickup inductance, actual guitar waveform, power stage, output transformer, reverb loading and hardware noise are excluded. Tone/gain controls are 0.5 electrical fraction and volume/master 0.25, not knob markings. Output load is an assumed 1 MΩ. The full-amplifier high-frequency transformer ringing remains unresolved; this isolated fixture does not claim to fix it.', '',
    'The original dirty fixture omitted the tone/output sheet. That failed attempt and the later short-settling results remain archived. See [fixture correction](fixture-correction.md). Current [summary](summary.json), [numerical comparison](numerical-review.json), per-case decks/logs and sampled waveforms are generated evidence. Actual guitar/cable, selected tube spread, signal levels at each stage and assembled noise still need bench checks before a product specification or release.', '']
(OUT / 'review.md').write_text('\n'.join(lines))
print(json.dumps({k:v for k,v in report.items() if k not in ['comparisons', 'first_sample_crossings']}, indent=2))
