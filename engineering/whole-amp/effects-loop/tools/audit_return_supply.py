"""Audit retained RETURN diagnostics without promoting them to hardware acceptance."""
import copy
import hashlib
import json
import math
from pathlib import Path

import return_driver as driver
import return_isolation_check as isolated
import return_supply_diagnostics as diagnostic

ROOT = Path(__file__).resolve().parents[4]
OUT = driver.OUT


def sha(data):
    return hashlib.sha256(data).hexdigest()


def finite_numbers(value):
    if isinstance(value, dict):
        return all(finite_numbers(v) for v in value.values())
    if isinstance(value, list):
        return all(finite_numbers(v) for v in value)
    return not isinstance(value, float) or math.isfinite(value)


def screen(row):
    """Finite nominal-model screen only; thresholds are existing engineering targets."""
    if row.get('status') != 'completed' or not finite_numbers(row):
        return False
    case = row['case']
    return (row['end_s'] >= max(.03, 30/case[0])*(1-1e-8)
            and abs(20*math.log10(1+row['gain_error_percent']/100)) <= .5
            and row['signals']['PORT']['THD_2_to_10_percent'] < .1
            and row['settled_relative_fundamental'] < .001
            and row['maximum_main_supply_span_V'] < 180
            and min(row['minimum_upper_output_margin_V'], row['minimum_lower_output_margin_V']) > 3
            and max(abs(row['op']['BUF']), abs(row['op']['PORT'])) < 1)


def main():
    diag = json.loads((OUT/'return-supply-summary.json').read_text())
    iso = json.loads((OUT/'return-isolated-summary.json').read_text())
    checks = {}
    checks['manufacturer_model_unchanged'] = sha(driver.MODEL.read_bytes()) == driver.SHA == diag['model_sha256'] == iso['model_sha256']
    checks['all_8_diagnostics_and_12_followups_attempted'] = (len(diag['cases']) == 8 and len(iso['cases']) == 12
        and diag['all_attempted'] and iso['all_attempted'])
    checks['diagnostic_matrix_exact'] = [(r['variant'], r['rail_V']) for r in diag['cases']] == [(v, s) for v in diagnostic.VARIANTS for s in (166.6,173.4)]
    checks['causal_measurement_revision_resolves'] = sha(Path(driver.__file__).read_bytes()) == diag['source_sha256']['return_driver.py']
    checks['causal_factory_matches'] = sha(Path(diagnostic.__file__).read_bytes()) == diag['source_sha256']['return_supply_diagnostics.py']
    for path, digest in iso['sources'].items():
        checks['source:'+path] = sha((ROOT/path).read_bytes()) == digest
    for row in diag['cases']:
        key = f"return-supply-{row['variant']}-{row['rail_V']}"
        text = diagnostic.make_deck(row['variant'], row['rail_V'])
        checks[key+':deck'] = sha(text.encode()) == row['deck_sha256'] == sha((OUT/(key+'.cir')).read_bytes())
        checks[key+':receipt'] = json.loads((OUT/(key+'.json')).read_text()) == row
    for i, row in enumerate(iso['cases']):
        key = isolated.key(i)
        case, divisor = isolated.CASES[i]
        checks[key+':case'] = row['case'] == list(case) and row['step_divisor'] == divisor
        checks[key+':deck'] = sha(isolated.deck(case).encode()) == row['deck_sha256'] == sha((OUT/(key+'.cir')).read_bytes())
        checks[key+':receipt'] = json.loads((OUT/(key+'.json')).read_text()) == row
        checks[key+':nominal_screen'] = screen(row)
        checks[key+':timestep'] = row.get('maximum_step_s') == min(2e-6, 1/(case[0]*192))/divisor
        checks[key+':runtime'] = 'ngspice-45.2 shared library' in (OUT/(key+'.log')).read_text()
    checks['original_failures_preserved'] = all(r['status']=='failed' and 'Timestep too small' in r['error'] for r in diag['cases'] if r['variant']=='original')
    checks['10n_timeouts_not_passes'] = all(r['status']=='timeout' for r in diag['cases'] if r['variant']=='bypass-10n')
    refinements, probe_equivalence = [], []
    for fine in iso['cases'][10:]:
        coarse = next(r for r in iso['cases'][:10] if r['case'] == fine['case'])
        refinements.append(dict(rail_V=fine['case'][2],
            amplitude_change_percent=100*abs(fine['signals']['PORT']['fundamental_Vpk']/coarse['signals']['PORT']['fundamental_Vpk']-1),
            THD_change_percentage_points=abs(fine['signals']['PORT']['THD_2_to_10_percent']-coarse['signals']['PORT']['THD_2_to_10_percent'])))
        original = next(r for r in diag['cases'] if r['variant']=='rail-50ohm' and r['rail_V']==fine['case'][2])
        probe_equivalence.append(max(abs(coarse['signals'][n][m]-original['signals'][n][m]) for n in original['signals'] for m in original['signals'][n]))
    checks['half_timestep_amplitude_within_0_1_percent'] = max(r['amplitude_change_percent'] for r in refinements) < .1
    checks['half_timestep_THD_within_0_02_points'] = max(r['THD_change_percentage_points'] for r in refinements) < .02
    checks['extra_probe_default_step_equivalence'] = max(probe_equivalence) < 1e-9
    controls = {}
    for name, field, value in [('timeout','status','timeout'), ('short_window','end_s',.001),
                              ('high_supply','maximum_main_supply_span_V',181),
                              ('clipping','minimum_upper_output_margin_V',-1),
                              ('lost_gain','gain_error_percent',-20),
                              ('unsettled','settled_relative_fundamental',.01)]:
        row = copy.deepcopy(iso['cases'][3]); row[field] = value
        controls[name] = not screen(row)
    checks['negative_controls_rejected'] = all(controls.values())
    hashes = dict(Main='b97844b51aed2b7e99e142902bc5c12d6b35d96a2dd5afd7667dd2e879dc4bc6',
                  Power='3ff2b701ece8ab2c7d7aca8da45cfdc4fc36fce1f9fda4b063c876e52c176788',
                  Control='ca65723ca8be01a4fc8fce46dccd3082610d0d28229695e0bea6b3564ef1e642',
                  Reverb='2c1af294f09cb902c330ef5c52ceaadd44d48af136f5e22d5fe30e3e216f3683')
    for board, digest in hashes.items():
        path = ROOT/f'engineering/whole-amp/pcb-measured-r/boards/Renegade_{board}.kicad_pcb'
        checks['native_unchanged:'+board] = sha(path.read_bytes()) == digest
    checks['no_adoption_or_headroom_release'] = all(not s[k] for s in [diag,iso] for k in ['native_modified','circuit_selected','headroom_qualified'])
    result = dict(passed=all(checks.values()), checks=checks, negative_controls=controls,
                  refinements=refinements, extra_probe_maximum_metric_difference=probe_equivalence,
                  native_sha256=hashes,
                  input_sha256={p.name:sha(p.read_bytes()) for p in [OUT/'return-supply-summary.json', OUT/'return-isolated-summary.json']},
                  scope='Nominal fixture evidence and numerical screen only; no integrated loop, thermal, startup, Shanghai purchasing or fabrication qualification',
                  fabrication_release=False)
    (OUT/'return-supply-audit.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(passed=result['passed'], check_count=len(checks), failed=[k for k,v in checks.items() if not v], refinements=refinements), indent=2))
    assert result['passed'], 'RETURN evidence checks failed'


if __name__ == '__main__':
    main()
