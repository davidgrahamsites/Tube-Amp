"""Independent interval/receipt audit; no SPICE rerun or native mutation."""
from pathlib import Path
import hashlib
import itertools
import json
import math

M = Path(__file__).resolve().parents[1]
ROOT = M.parents[2]


def main():
    c = json.loads((M / 'interface-contract.json').read_text())
    r = json.loads((M / 'results/interface-screen.json').read_text())
    tube = json.loads((ROOT / c['tube_limit_source']).read_text())['references']
    assert r['contract_sha256'] == hashlib.sha256((M / 'interface-contract.json').read_bytes()).hexdigest()
    assert r['factory_sha256'] == hashlib.sha256((M / 'tools/interface_screen.py').read_bytes()).hexdigest()
    for p, h in r['input_sha256'].items():
        assert hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h, p
    keys = ('early_supply_V', 'channel', 'input_peak_V', 'gain_fraction')
    expected = set(itertools.product(c['early_supply_V'], c['channels'], c['input_peak_V'], c['gain_fractions']))
    base = [x for x in r['cases'] if x['kind'] == 'base']
    assert {tuple(x[k] for k in keys) for x in base} == expected
    assert len(base) == len(expected) == 36
    assert r['completed_cases'] == len(r['cases']) == 38
    assert not r['native_changes'] and not r['qualified']
    peak = r['heater_endpoint_peak_bound_V']
    assert c['heater_rms_max_V'] / math.sqrt(2) <= peak < c['heater_rms_max_V'] * math.sqrt(2)
    limits = {t['type']: t for t in tube}
    checked = 0
    failed = 0
    for row in r['cases']:
        assert row['stop_s'] > row['measure_start_s'] > 0 and row['points'] > 100
        assert all(math.isfinite(v) for node in row['nodes'].values() for v in node.values())
        for group, refs in [('all_six', list(c['cathode_nodes'])), ('preamps', ['V1', 'V2', 'V3', 'V4']), ('power', ['V5', 'V6'])]:
            intervals = []
            for ref in refs:
                lim = limits['JJ EL34' if ref in ['V5', 'V6'] else 'JJ ECC83S']['heater_cathode_limit_V']
                for n in c['cathode_nodes'][ref]:
                    a, b = row['nodes'][n]['minimum_V'], row['nodes'][n]['maximum_V']
                    assert a <= b
                    # Every corner |cathode - (reference + heater endpoint)| <= limit
                    # gives an allowed interval for the DC reference.
                    intervals.extend((v - h - lim, v - h + lim) for v in (a, b) for h in (-peak, peak))
            lo, hi = max(a for a, _ in intervals), min(b for _, b in intervals)
            got = row['windows'][group]
            assert math.isclose(lo, got['minimum_reference_V'], abs_tol=1e-10)
            assert math.isclose(hi, got['maximum_reference_V'], abs_tol=1e-10)
            assert got['nonempty'] == (lo <= hi)
            checked += 1
        failed += not row['windows']['all_six']['nonempty']
    assert failed == r['shared_reference_infeasible_cases']
    # A 1 V test injection independently recovers the resistance from total current.
    top, bottom = c['reference_divider_ohm']
    resistance = 1 / (1 / top + 1 / bottom) + c['midpoint_resistor_ohm'] / 2
    assert math.isclose(resistance, r['stiff_rail_nominal_reference_resistance_ohm'])
    assert resistance > limits['JJ EL34']['heater_cathode_resistance_limit_ohm']
    assert all(x['both_shared_windows_fail'] and x['cathode_peak_delta_V'] < .001 for x in r['refinement_comparisons'])
    receipt = {'checked_windows': checked, 'completed_cases': len(r['cases']),
               'infeasible_shared_windows': failed, 'native_hashes_preserved': len(c['native_sha256']),
               'evidence_checks_pass': True, 'engineering_qualified': False,
               'result_sha256': hashlib.sha256((M / 'results/interface-screen.json').read_bytes()).hexdigest(),
               'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (M / 'results/interface-checks.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
