"""Audit saved target evidence, deck reproducibility and timestep sensitivity.
This checks numerical evidence only, never the physical output-power rating.
"""
import hashlib
import json
import math
from fixture import ROOT, deck, fingerprint
from power_target import summarize

out = ROOT / 'results'
sweep = json.loads((out / 'power-target-summary.json').read_text())
target = json.loads((out / 'power-target-25w-check.json').read_text())
checks = {'source_hashes_current': sweep['source_hashes'] == target['source_hashes'] == fingerprint(),
          'ten_sweep_cases_and_two_target_checks': len(sweep['cases']) == 10 and len(target['cases']) == 2}
rows = []
for entry in sweep['cases'] + target['cases']:
    name = entry['name']
    row = json.loads((out / (name + '.json')).read_text())
    checks[name + '_completed'] = row['status'] == 'completed' and row['end_s'] >= .5
    checks[name + '_summary_matches_retained_result'] = entry == {'name': name, **summarize(row)}
    config = {k: v for k, v in row['config'].items() if k not in {'steps', 'max_step'}}
    checks[name + '_deck_reproducible'] = (out / (name + '.cir')).read_text() == deck(**config)[0]
    checks[name + '_settled'] = all(row['settling_relative_fundamental'][n] < .001
                                  for n in ['FX_SEND', 'PI_G1', 'SPEAKER'])
    checks[name + '_finite'] = all(math.isfinite(v) for s in row['signals'].values()
                                for v in s.values() if v is not None)
    rows.append(row)

comparisons = []
for node in ['FX_SEND', 'PI_G1', 'SPEAKER']:
    a, b = [r['signals'][node] for r in rows[-2:]]
    comparisons.append(dict(node=node,
        amplitude_change_percent=100 * abs(b['fundamental_Vpk'] / a['fundamental_Vpk'] - 1),
        THD_change_percentage_points=abs(b['THD_2_to_10_percent'] - a['THD_2_to_10_percent'])))
checks['target_refined_amplitudes_within_0_1_percent'] = max(r['amplitude_change_percent'] for r in comparisons) < .1
checks['target_refined_THD_within_0_02_percentage_points'] = max(r['THD_change_percentage_points'] for r in comparisons) < .02
checks['target_factory_hashes_current'] = all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h
                                           for p, h in target['factory_hashes'].items())
checks['no_hardware_release'] = sweep['fabrication_ready'] is False and target['fabrication_ready'] is False
evidence = [out / (e['name'] + ext) for e in sweep['cases'] + target['cases'] for ext in ['.cir', '.json', '.log']]
report = dict(passed=all(checks.values()), checks=checks, refinement=comparisons,
              source_hashes=fingerprint(), evidence_hashes={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in evidence},
              physical_model_qualified=False, fabrication_ready=False)
(out / 'power-target-audit.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
print(json.dumps({'passed': report['passed'], 'checks': len(checks), 'refinement': comparisons}, indent=2))
assert report['passed'], [k for k, v in checks.items() if not v]
