"""Check the published CB-006 cases against the decks and release limits."""
import hashlib
import json
from pathlib import Path
import subprocess

from apex_return import M, ROOT, TI, deck


def digest(content):
    return hashlib.sha256(content).hexdigest()


def main():
    results = M / 'results'
    cases = json.loads((results/'apex-return.json').read_text())
    checks = {}
    for name, case in cases.items():
        args = case['parameters']
        text = deck(args['hz'], args['peak'], args['pf'], args['rail'], args['iso'],
                    args['cc'], args['short'], args['temp'], args['old_send'],
                    args['part'], args['trimmed'], args['guarded'])
        checks[name + '_deck'] = digest(text.encode()) == case['deck_sha256']
        checks[name + '_end'] = case['status'] == 'completed' and abs(case['end_s']-case['reached_s']) < 1e-9
    checks['nominal_and_refinement'] = all(abs(cases[k]['gain_error_dB']) < .5 and
        cases[k]['thd_percent'] < 1 and cases[k]['send_peak_V'] < 10 for k in
        ['guard-20k','guard-fine','guard-zero','guard-hot','guard-clean','guard-bass'])
    probes = json.loads((results/'apex-protection.json').read_text())
    checks['sag_failure_preserved'] = probes['runs'][1]['thd_percent'] > 1
    checks['loop_crossings'] = all(len(p['crossings']) == 1 and p['crossings'][0]['deg'] > 45
                                   for p in probes['margins'])
    budget = json.loads((results/'apex-fault-budget.json').read_text())
    checks['hot_short_energy'] = abs(budget['hot_port_short']['modeled_W']-probes['runs'][-1]['chip_W']) < 1e-8
    checks['isolator_short_rms'] = 2.8 < probes['runs'][-1]['resistor_W'] < 3.2
    paths = list((M.parent.parent/'pcb-measured-r/boards').glob('*.kicad_pcb'))
    paths += list((M.parent.parent/'reverb-600/cad').glob('*.kicad_sch'))
    baseline = '008cdb81a803b99ef074cca1314f06c8b056552d'
    checks['native_parity'] = len(paths) == 22 and all(subprocess.check_output(
        ['git','show',baseline+':'+str(p.relative_to(ROOT))],cwd=ROOT)==p.read_bytes() for p in paths)
    assert all(checks.values()),checks
    sources=[TI,M.parent.parent/'reverb-600/circuit.json',*sorted((M/'tools').glob('*apex*.py')),
             M/'tools/integrated_load.py',*sorted(results.glob('apex-*.json'))]
    hashes={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in sources if p.name!='apex-audit.json'}
    (results/'apex-audit.json').write_text(json.dumps(dict(baseline=baseline,checks=checks,
        sources_sha256=hashes,hardware_qualified=False),indent=2)+'\n')
    print(f'{len(cases)} full case receipts, {len(checks)} checks, {len(paths)} native files preserved.')


if __name__=='__main__':
    main()
