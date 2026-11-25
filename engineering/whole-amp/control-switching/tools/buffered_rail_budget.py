"""Settled candidate thresholds and independent nodal cross-check; never edits CAD."""
import hashlib
import json
import random
from pathlib import Path

from rail_monitor_budget import corners, threshold

BASE = Path(__file__).resolve().parents[1]
CONTRACT = BASE / 'rail-monitor-buffered-contract.json'


def solve(matrix, rhs):
    """Small pivoted linear solver, independent of the closed-form threshold code."""
    a = [list(row) + [value] for row, value in zip(matrix, rhs)]
    for col in range(len(a)):
        pivot = max(range(col, len(a)), key=lambda i: abs(a[i][col]))
        a[col], a[pivot] = a[pivot], a[col]
        divisor = a[col][col]
        if abs(divisor) < 1e-15:
            raise ValueError('singular circuit')
        a[col] = [v / divisor for v in a[col]]
        for row in range(len(a)):
            if row != col:
                factor = a[row][col]
                a[row] = [v - factor*w for v, w in zip(a[row], a[col])]
    return [row[-1] for row in a]


def nodal_threshold(kind, r, v5, offset, ip, im, feedback, leak):
    g = {key: 1/value for key, value in r.items()}
    if kind == 'positive':
        # Unknowns PREF, PSENSE, positive rail. KCL plus comparator trip equality.
        return solve([
            [g['ref_top'] + g['ref_bottom'], 0, 0],
            [-1, 1, 0],
            [0, g['rail'] + g['ground'] + g['feedback'], -g['rail']],
        ], [v5*g['ref_top'] + im, offset, feedback*g['feedback'] + ip])[-1]
    # Unknowns NREF, NSENSE, CLAMP, negative rail.
    return solve([
        [g['ref_top'] + g['ref_bottom'] + g['feedback'], 0, 0, 0],
        [-1, 1, 0, 0],
        [0, g['sense_to_ground'] + g['clamp_to_sense'], -g['clamp_to_sense'], 0],
        [0, -g['clamp_to_sense'], g['ref_to_clamp'] + g['rail_to_clamp'] + g['clamp_to_sense'], -g['rail_to_clamp']],
    ], [v5*g['ref_top'] + feedback*g['feedback'] + ip, offset, im, v5*g['ref_to_clamp'] - leak])[-1]


def main():
    c = json.loads(CONTRACT.read_text())
    results = {kind: corners(kind, c) for kind in ['positive', 'negative']}
    checks = []

    def check(name, passed):
        checks.append(dict(name=name, passed=bool(passed)))

    for kind, result in results.items():
        check(kind + ' enable below allocated maximum', result['abs_ranges_V']['enable'][1] < c['screen']['latest_enable_abs_V'])
        check(kind + ' disable above allocated minimum', result['abs_ranges_V']['disable'][0] > c['screen']['earliest_disable_abs_V'])
        check(kind + ' hysteresis above allocation', result['minimum_same_corner_hysteresis_V'] > c['screen']['minimum_hysteresis_V'])

    # Compare algebra against independently assembled KCL matrices, at endpoints and interiors.
    rng = random.Random(393)
    errors = []
    for kind in results:
        for _ in range(1000):
            r = {key: value*rng.uniform(1-c['resistor_fraction'], 1+c['resistor_fraction']) for key, value in c[kind+'_resistors_ohm'].items()}
            args = [kind, r, rng.uniform(*c['reference_V']), rng.uniform(*c['offset_V']), rng.uniform(*c['input_current_A']), rng.uniform(*c['input_current_A']), rng.uniform(0, 5.25), rng.uniform(*c['clamp_leakage_A']) if kind == 'negative' else 0]
            errors.append(abs(threshold(*args) - nodal_threshold(*args)))
        for label in ['lowest_case', 'highest_case']:
            w = results[kind][label]
            args = [kind, w['resistors_ohm'], w['v5'], w['offset_V'], w['ip_A'], w['im_A'], w['gate_V'], w['clamp_leak_A']]
            errors.append(abs(w['rail_threshold_V'] - nodal_threshold(*args)))
    check('independent nodal comparison within1nV', max(errors) < 1e-9)

    tol = c['resistor_fraction']
    p, n = c['positive_resistors_ohm'], c['negative_resistors_ohm']
    pu = c['pullup']
    # Valid for the settled, powered sense nodes >=0, not startup/back-powering.
    feedback_load = max(c['reference_V'])*(1/(p['feedback']*(1-tol)) + 1/(n['feedback']*(1-tol)))
    leakage = 2*pu['comparator_leak_each_A'] + pu['hc14_input_leak_A']
    high_min = min(c['reference_V']) - (feedback_load+leakage)*pu['ohm']*(1+pu['fraction'])
    # Max healthy sense <=5.25V gives a conservative feedback-current sink allowance.
    sink_max = max(c['reference_V'])/(pu['ohm']*(1-pu['fraction'])) + feedback_load + pu['hc14_input_leak_A']
    check('feedback high lower bound supported by pullup budget', high_min >= min(c['gate_on_assumed_V']))
    check('comparator sink below4mA test condition', sink_max <= pu['maximum_sink_A'])
    ratio = n['sense_to_ground']*(1+tol)/(n['sense_to_ground']*(1+tol)+n['clamp_to_sense']*(1-tol))
    clamp_abs = c['allocated_negative_clamp_max_V']*ratio + max(abs(i) for i in c['input_current_A'])*n['sense_to_ground']*(1+tol)
    check('conditional clamp magnitude below0.3V', clamp_abs < .3)

    t = c['tolerance_profile']
    delta = max(abs(v-t['reference_temperature_C']) for v in t['film_temperature_C'])

    def allowance(r):
        return t['initial_fraction'] + delta*t['tcr_per_K'] + t['endurance_fraction'] + t['endurance_absolute_ohm']/r + t['solder_fraction'] + t['solder_absolute_ohm']/r

    allowances = {}
    for kind in results:
        for name, value in c[kind+'_resistors_ohm'].items():
            series = t['ref_bottom_series_ohm'] if (kind, name) == ('negative', 'ref_bottom') else [value]
            allowances[kind+'.'+name] = sum(r*allowance(r) for r in series)/sum(series)
    check('conditional resistor error allocation covers declared profile', max(allowances.values()) <= tol)
    report = dict(scope='Candidate settled threshold screen only; no CAD or transient qualification.', results=results, checks=checks, passed=sum(x['passed'] for x in checks), total=len(checks), qualified=False, nodal_comparisons=len(errors), nodal_max_error_V=max(errors), rail_ok_high_min_V=high_min, comparator_sink_upper_A=sink_max, clamp_input_abs_allocation_V=clamp_abs, clamp_current_upper_A=c['largest_analog_rail_abs_V']/(n['rail_to_clamp']*(1-tol)), resistor_error_fractions=allowances, limitations=c['limitations'], inputs={str(path.relative_to(BASE)):hashlib.sha256(path.read_bytes()).hexdigest() for path in [CONTRACT, Path(__file__), BASE/'tools/rail_monitor_budget.py']})
    (BASE/'results/rail-monitor-buffered-budget.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ['passed','total','qualified','nodal_max_error_V','rail_ok_high_min_V','comparator_sink_upper_A','clamp_input_abs_allocation_V']}, indent=2))
    for kind, result in results.items():
        print(kind, result['abs_ranges_V'], result['minimum_same_corner_hysteresis_V'])


if __name__ == '__main__':
    main()
