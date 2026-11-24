"""Check retained loaded-winding evidence without certifying physical hardware."""
import hashlib
import json
from pathlib import Path
import subprocess

from fixture import ROOT, fingerprint
from sweep_loaded_feedback import hashes


def main():
    out = ROOT/'results'
    sweep = json.loads((out/'loaded-feedback-summary.json').read_text())
    burst = json.loads((out/'loaded-burst-summary.json').read_text())
    checks = dict(sweep_sources=sweep['source_hashes'] == fingerprint(),
                  sweep_factories=sweep['factory_hashes'] == hashes(),
                  sweep_measurement_checks=all(sweep['checks'].values()),
                  burst_sources=burst['source_hashes'] == fingerprint(),
                  burst_checks=all(burst['checks'].values()))
    for key, value in burst['factory_hashes'].items():
        path = Path(__file__).with_name('check_loaded_transient.py') if key == 'transient_check' else ROOT.parent.parent.parent/key
        checks['burst_factory:' + key] = hashlib.sha256(path.read_bytes()).hexdigest() == value
    for filename in ['loaded-probe-checks.json', 'loaded-winding-checks.json']:
        result = json.loads((out/filename).read_text())
        checks[filename] = result['passed']
        for name, sha in result['factory_hashes'].items():
            checks[filename + ':' + name] = hashlib.sha256((ROOT/'tools'/name).read_bytes()).hexdigest() == sha
    for row in sweep['cases']:
        for kind, sha in row['deck_hashes'].items():
            checks[row['name'] + ':' + kind] = hashlib.sha256((out/f'{row["name"]}-{kind}.cir').read_bytes()).hexdigest() == sha
    for row in burst['cases']:
        checks[row['name']] = hashlib.sha256((out/f'{row["name"]}.cir').read_bytes()).hexdigest() == row['deck_sha256']
    by = {r['name']: r for r in sweep['cases']}
    checks['nominal_screen_passes'] = by['loaded-base-lm40-lk20-cp250']['passes_screen']
    checks['high_leakage_screen_rejects'] = not by['loaded-pi47-fb0-lk80-pres0']['passes_screen']
    checks['negative_control_rejects'] = by['loaded-pi47-fb220-lk80-pres0']['analysis']['min_gain_margin_dB'] < 0
    checks['damping_trials_reject'] = all(not r['passes_screen'] for r in sweep['cases'] if '-damp' in r['name'])
    # A read-only electrical pass must leave native blocks and boards unchanged.
    repo = ROOT.parent.parent.parent
    baseline = '9d69db3e95cbfefd434dcb999c5108d6af8a1f48'
    native = [ROOT.parent/'reverb-600/circuit.json']
    native += list((ROOT.parent/'reverb-600/cad').glob('*.kicad_sch'))
    native += list((ROOT.parent/'pcb-measured-r/boards').glob('*.kicad_pcb'))
    for path in native:
        relative = str(path.relative_to(repo))
        previous = subprocess.check_output(['git', 'show', baseline+':'+relative], cwd=repo)
        checks['native_preserved:' + relative] = path.read_bytes() == previous
    result = dict(scope='Evidence integrity and expected positive/negative controls; not physical approval',
                  baseline_commit=baseline, checks=checks, passed=all(checks.values()),
                  native_compensation_adopted=False, fabrication_ready=False)
    (out/'loaded-feedback-audit.json').write_text(json.dumps(result, indent=2)+'\n')
    assert result['passed'], [k for k,v in checks.items() if not v]
    print(len(checks), 'loaded-feedback evidence checks PASS')


if __name__ == '__main__':
    main()
