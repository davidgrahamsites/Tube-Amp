"""Precision-reference candidate: independent rail/logic/reference endpoint budget.

Read-only design evidence. Never writes native CAD or selects a purchasing part.
"""
import hashlib
import itertools
import json
import random
from pathlib import Path

from rail_monitor_budget import corners, threshold
from buffered_rail_budget import nodal_threshold, solve

BASE = Path(__file__).resolve().parents[1]


def positive(r, reference, offset, bias, feedback):
    return r['rail'] * ((reference + offset) * sum(1 / r[k] for k in r)
                        - feedback / r['feedback'] - bias)


def positive_nodal(r, reference, offset, bias, feedback):
    # Unknowns PSENSE and rail; KCL assembled independently of the closed form.
    return solve([[1, 0], [sum(1 / v for v in r.values()), -1 / r['rail']]],
                 [reference + offset, feedback / r['feedback'] + bias])[1]


def positive_corners(c):
    names = list(c['positive_resistors_ohm'])
    ranges = {'enable': [], 'disable': []}
    hysteresis = []
    for factors in itertools.product([1-c['resistor_fraction'], 1+c['resistor_fraction']], repeat=len(names)):
        r = {k: c['positive_resistors_ohm'][k]*f for k, f in zip(names, factors)}
        for ref, offset, bias in itertools.product(c['reference_V'], c['offset_V'], c['input_current_A']):
            pair = {}
            for state, feedbacks in [('enable', c['gate_off_V']), ('disable', c['gate_on_assumed_V'])]:
                pair[state] = [positive(r, ref, offset, bias, v) for v in feedbacks]
                ranges[state].extend(pair[state])
            hysteresis.append(min(pair['enable'])-max(pair['disable']))
    return {'corners': sum(map(len, ranges.values())),
            'abs_ranges_V': {k: [min(v), max(v)] for k, v in ranges.items()},
            'minimum_same_corner_hysteresis_V': min(hysteresis)}


def main():
    contract = BASE/'rail-monitor-precision-contract.json'
    c = json.loads(contract.read_text())
    results = {'positive': positive_corners(c), 'negative': corners('negative', c)}
    checks = []
    def check(name, passed):
        checks.append({'name': name, 'passed': bool(passed)})
    for kind, result in results.items():
        screen = c['screen'][kind]
        check(kind+' enables within regulator healthy minimum', result['abs_ranges_V']['enable'][1] < screen['enable_max_V'])
        check(kind+' disables above allocated audio floor', result['abs_ranges_V']['disable'][0] > screen['disable_min_V'])
        check(kind+' hysteresis exceeds new noise allocation', result['minimum_same_corner_hysteresis_V'] > c['screen']['minimum_hysteresis_allocation_V'])

    rng = random.Random(5050393)
    errors = []
    for kind in results:
        for _ in range(1000):
            r = {k: v*rng.uniform(1-c['resistor_fraction'], 1+c['resistor_fraction']) for k, v in c[kind+'_resistors_ohm'].items()}
            ref = rng.uniform(*c['reference_V'])
            offset = rng.uniform(*c['offset_V'])
            ip, im = [rng.uniform(*c['input_current_A']) for _ in range(2)]
            feedback = rng.uniform(0, c['logic_supply_V'][1])
            if kind == 'positive':
                errors.append(abs(positive(r, ref, offset, ip, feedback)-positive_nodal(r, ref, offset, ip, feedback)))
            else:
                args = [kind, r, ref, offset, ip, im, feedback, rng.uniform(*c['clamp_leakage_A'])]
                errors.append(abs(threshold(*args)-nodal_threshold(*args)))
    check('independent nodal comparison below1nV', max(errors) < 1e-9)
    p, n, pu = c['positive_resistors_ohm'], c['negative_resistors_ohm'], c['pullup']
    tol = c['resistor_fraction']
    # Settled sense nodes >=0. Pullup deliberately follows REF5, not logic +5V.
    feedback_load = c['reference_V'][1]*sum(1/(r['feedback']*(1-tol)) for r in [p, n])
    leakage = 2*pu['comparator_leak_each_A']+pu['hc14_input_leak_A']
    high = c['reference_V'][0]-(feedback_load+leakage)*pu['ohm']*(1+pu['fraction'])
    sink = c['reference_V'][1]/(pu['ohm']*(1-pu['fraction']))+feedback_load+pu['hc14_input_leak_A']
    check('reference pullup supports feedback high bound', high >= c['gate_on_assumed_V'][0])
    check('sink below4mA test current', sink <= pu['maximum_sink_A'])
    b = c['reference_budget']
    static_error = b['initial_fraction']+1e-6*(b['box_drift_ppm_per_K']*b['full_specified_span_K']+b['line_ppm_per_V']*b['full_input_span_V']+b['load_ppm_per_mA']*b['allocated_load_mA'])
    check('declared static reference terms fit allocation', static_error <= b['total_fraction_allocation'])
    # At settled CLAMP>=0, this upper bound deliberately overstates normal load.
    # Include collector-low pullup load and bleeder, rather than only healthy state.
    bleeder_min = c['reference_bleeder_ohm']*(1-c['reference_bleeder_fraction'])
    reference_load = c['reference_V'][1]*(1/(n['ref_to_clamp']*(1-tol))+1/(n['ref_top']*(1-tol))+1/(pu['ohm']*(1-pu['fraction']))+1/bleeder_min)+2*max(map(abs,c['input_current_A']))
    check('reference settled load within10mA allocation', reference_load <= b['allocated_load_mA']*.001)
    check('series rail resistor matches explicit parts', sum(c['negative_rail_series_ohm']) == n['rail_to_clamp'])
    t = c['tolerance_profile']
    def allowance(r):
        return t['initial_fraction']+max(abs(v-t['reference_temperature_C']) for v in t['film_temperature_C'])*t['tcr_per_K']+t['endurance_fraction']+t['endurance_absolute_ohm']/r+t['solder_fraction']+t['solder_absolute_ohm']/r
    resistor_errors = {}
    for kind in results:
        for name, value in c[kind+'_resistors_ohm'].items():
            series = [value]
            if (kind, name) == ('negative', 'ref_bottom'): series = t['ref_bottom_series_ohm']
            if (kind, name) == ('negative', 'rail_to_clamp'): series = c['negative_rail_series_ohm']
            resistor_errors[kind+'.'+name] = sum(v*allowance(v) for v in series)/sum(series)
    check('effective resistor allowance covers declared series profiles', max(resistor_errors.values()) <= tol)
    # Screening only: isolated measured inventory, no regulator feed/backfeed model.
    headroom = json.loads((BASE/'results/audio-headroom-budget.json').read_text())
    for path, digest in headroom['provenance'].items():
        assert hashlib.sha256((BASE.parent/path).read_bytes()).hexdigest() == digest, path
    margins = {kind: r['abs_ranges_V']['disable'][0]-c['screen'][kind]['disable_min_V'] for kind, r in results.items()}
    for kind in margins:
        assert c['screen'][kind]['disable_min_V'] == headroom['sides'][kind]['allocated_valid_rail_floor_V']
    # REF5 supplies no current, negative rail contributes none to an upper bound.
    # Open negative paths and ignore positive divider loading for conservative backfeed.
    off_bleeder = c['reference_bleeder_ohm']*(1+c['reference_bleeder_fraction'])
    off_pullup = pu['ohm']*(1+pu['fraction'])
    off_feedback = p['feedback']*(1-tol)
    sense_max = c['largest_analog_rail_abs_V']*p['ground']*(1+tol)/(p['rail']*(1-tol)+p['ground']*(1+tol))
    off_rail_ok = sense_max*(off_pullup+off_bleeder)/(off_feedback+off_pullup+off_bleeder)+leakage*(off_pullup+off_bleeder)
    # HC14 0.9V negative-going threshold at4.5V is a conservative design screen,
    # not an interpolated guarantee at every supply/temp; full digital interface pending.
    check('passive reference-off backfeed below0.9V allocation', off_rail_ok < .9)
    isolated_hold = {kind: {str(load): headroom['sides'][kind]['screen_low_capacitance_F']*margin/load for load in [.03,.05,.1]} for kind, margin in margins.items()}
    report = dict(scope='Conditional static precision candidate; reference-valid sequencing and timing unresolved.',
                  results=results, checks=checks, passed=sum(x['passed'] for x in checks), total=len(checks), qualified=False,
                  nodal_comparisons=len(errors), nodal_max_error_V=max(errors), reference_static_error_fraction=static_error,
                  reference_load_upper_A=reference_load, rail_ok_high_min_V=high, comparator_sink_upper_A=sink,
                  resistor_error_fractions=resistor_errors, minimum_disable_headroom_margin_V=margins,
                  passive_reference_off_rail_ok_upper_V=off_rail_ok,
                  conditional_isolated_hold_s_by_rail_and_load_A=isolated_hold, limitations=c['limitations'])
    inputs = [contract, Path(__file__), BASE/'tools/rail_monitor_budget.py', BASE/'tools/buffered_rail_budget.py', BASE/'results/audio-headroom-budget.json', BASE/'evidence/TI-REF50-O.pdf', BASE/'evidence/TI-LM393-AH.pdf', BASE/'evidence/TI-SN74HC14-L.pdf']
    report['inputs'] = {str(p.relative_to(BASE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    (BASE/'results/rail-monitor-precision-budget.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: report[k] for k in ['passed','total','qualified','results','minimum_disable_headroom_margin_V']}, indent=2))
    if not all(x['passed'] for x in checks): raise SystemExit(1)


if __name__ == '__main__':
    main()
