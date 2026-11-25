"""Audit stationary DC evidence; never promote it to power-on qualification."""
import copy
import hashlib
import json
import math
from pathlib import Path
import ota_screen as ota


def acceptable(row):
    """Independent bounds on retained metrics, including emitter current balance."""
    metrics = [*row['final'].values(), *row['late_peak_to_peak_V'].values(),
               *row['late_capacitor_max_abs_A'].values(), row['late_emitter_kcl_max_abs_A']]
    rail = row['case'].get('rail', 15)
    return (row['status'] == 'settled' and all(math.isfinite(x) for x in metrics)
            and abs(row['end_s'] - row['case'].get('stop', 2)) < 1e-8
            and all(abs(row['final'][n]) < rail for n in ['out', 'bo'])
            and max(row['late_peak_to_peak_V'].values()) < 1e-5
            and max(row['late_capacitor_max_abs_A'].values()) < 1e-9
            and row['late_emitter_kcl_max_abs_A'] < 1e-9)


def main():
    checks = []
    def check(name, passed):
        checks.append(dict(name=name, passed=bool(passed)))
    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()
    source = ota.OUT/'settled-bias.json'
    data = json.loads(source.read_text())
    rows = {r['name']: r for r in data['cases']}
    check('24 distinct cases', len(rows) == len(data['cases']) == 24)
    for path, digest in data['provenance'].items():
        check('input '+path, sha(ota.ROOT/path) == digest)
    for name, row in rows.items():
        for kind in ['deck', 'log']:
            check(name+' '+kind+' hash', sha(ota.OUT/row[kind]) == row[kind+'_sha256'])
        check(name+' stationary DC and KCL', acceptable(row))
    # Distinct time grids, integration durations, initialization steps and weak shunts.
    for label in ['half-step', 'longer', 'warm-half', 'warm-double']:
        for target in [0, 5]:
            ref = rows['15-'+str(target)]['final']
            trial = rows[label+'-'+str(target)]['final']
            check(label+' '+str(target)+' agreement 10uV',
                  max(abs(trial[n]-ref[n]) for n in ref) < 1e-5)
    for rail in [12, 15, 16.5]:
        for target in [0, 2.5, 4.9, 5]:
            check('matrix coverage '+str((rail, target)), str(rail)+'-'+str(target) in rows)
    # Known false-success modes must fail this audit even with status left "settled".
    for name, field, value in [('unfinished', 'end_s', .002),
                               ('KCL imbalance', 'late_emitter_kcl_max_abs_A', 1e-6)]:
        bad = copy.deepcopy(rows['15-5']); bad[field] = value
        check('reject '+name, not acceptable(bad))
    for field, key, value in [('final', 'bo', 99), ('final', 'out', float('nan')),
                              ('late_peak_to_peak_V', 'bo', .01),
                              ('late_capacitor_max_abs_A', 'cin', 1e-6)]:
        bad = copy.deepcopy(rows['15-5']); bad[field][key] = value
        check('reject '+field+' '+key+' '+str(value), not acceptable(bad))
    # Changing rshunt changes conductance, not only integration settings. Retain
    # the original 10uV screen and expose the dry-end ABC sensitivity separately.
    shunt = {}
    for target in [0, 5]:
        ref = rows['15-'+str(target)]['final']
        trial = rows['weak-shunt-'+str(target)]['final']
        delta = {n:trial[n]-ref[n] for n in ref}
        shunt[str(target)] = dict(delta_V=delta, all_nodes_under_10uV=max(map(abs,delta.values())) < 1e-5)
    result = dict(evidence_checks_passed=all(r['passed'] for r in checks), checks=checks,
                  weak_shunt_sensitivity=shunt,
                  steady_dc_cases_settled=sum(acceptable(r) for r in rows.values()),
                  circuit_qualified=False, cold_start_qualified=False,
                  provenance={str(source.relative_to(ota.ROOT)):sha(source),
                              str(Path(__file__).relative_to(ota.ROOT)):sha(Path(__file__))})
    (ota.OUT/'settled-bias-audit.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['checks','provenance']}))
    print('checks:', len(checks))
    assert result['evidence_checks_passed'], [r for r in checks if not r['passed']]


if __name__ == '__main__':
    main()
