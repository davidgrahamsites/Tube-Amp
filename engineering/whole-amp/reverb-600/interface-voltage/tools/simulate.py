"""Source-derived passive interface stress screens; not a whole-amp model."""
from pathlib import Path
import hashlib
import json
import math
import re
import sys

M = Path(__file__).resolve().parents[1]
ROOT = M.parents[3]
sys.path.insert(0, str(ROOT / 'engineering/whole-amp/tools'))
import spice_runtime as sp

C = json.loads((M / 'contract.json').read_text())
SOURCE = M.parent / 'circuit.json'
PARTS = {x['reference']: x for x in json.loads(SOURCE.read_text())['components']}
REFS = ['C601', 'R601', 'R602', 'R612', 'R616', 'C607', 'R617', 'R618', 'R24']
EXPECTED = {
    'C601': ['FX_RETURN', 'IN_AC'], 'R601': ['IN_AC', 'SEND_IN'],
    'R602': ['SEND_IN', 'GND'], 'R612': ['FX_RETURN', 'MIX_OUT'],
    'R616': ['OUT_BUF', 'OUT_AC'], 'C607': ['OUT_AC', 'WET_AC'],
    'R617': ['WET_AC', 'GND'], 'R618': ['WET_AC', 'MIX_OUT'],
    'R24': ['MIX_OUT', 'GND'], 'R7': ['B_EARLY', 'CL_P2'],
    'C6': ['CL_P2', 'CLEAN_OUT'], 'R43': ['CLEAN_OUT', 'GND'],
}
NODES = ['FX_RETURN', 'IN_AC', 'SEND_IN', 'MIX_OUT', 'OUT_AC', 'WET_AC']


def num(ref):
    value = PARTS[ref]['value']
    match = re.fullmatch(r'([\d.]+)(M|k|u|n|p)?', value)
    assert match, value
    return float(match[1]) * {None: 1, 'M': 1e6, 'k': 1e3, 'u': 1e-6, 'n': 1e-9, 'p': 1e-12}[match[2]]


def component(ref):
    row = PARTS[ref]
    pins = [row['pins'][str(i)] for i in (1, 2)]
    assert pins == EXPECTED[ref], (ref, pins)
    return ref + ' ' + ' '.join('0' if n == 'GND' else n for n in pins) + ' ' + str(num(ref))


def base():
    return ['Passive reverb interface stress screen; no hardware qualification',
            '.options method=gear reltol=1e-6 abstol=1p vntol=1u'] + [component(r) for r in REFS]


def run(name, lines, command):
    text = '\n'.join(lines + ['.end']) + '\n'
    (M / 'results' / (name + '.cir')).write_text(text)
    sp.load(text)
    sp.cmd(command)
    return {n: sp.vector('v(' + n.lower() + ')') for n in NODES}


def complex_solve(hz, rs, dry, wet):
    """Independent nodal solution of the AC fixture using complex admittances."""
    # Six nodes, Gaussian elimination; independent of the ngspice solution.
    idx = {n: i for i, n in enumerate(NODES)}
    a = [[0j] * 6 for _ in range(6)]
    b = [0j] * 6
    known = {'GND': 0j, 'OUT_BUF': complex(wet), 'DRIVE': complex(dry)}
    def stamp(n1, n2, y):
        for n, other in [(n1, n2), (n2, n1)]:
            if n not in idx:
                continue
            i = idx[n]; a[i][i] += y
            if other in idx:
                a[i][idx[other]] -= y
            else:
                b[i] += y * known[other]
    for ref in REFS:
        p = EXPECTED[ref]
        y = 1 / num(ref) if ref[0] == 'R' else 2j * math.pi * hz * num(ref)
        stamp(*p, y)
    stamp('DRIVE', 'FX_RETURN', 1 / rs)
    for i in range(6):
        k = max(range(i, 6), key=lambda j: abs(a[j][i]))
        a[i], a[k] = a[k], a[i]; b[i], b[k] = b[k], b[i]
        z = a[i][i]; assert abs(z) > 1e-20
        a[i] = [x / z for x in a[i]]; b[i] /= z
        for j in range(6):
            if j == i:
                continue
            z = a[j][i]; a[j] = [x - z * y for x, y in zip(a[j], a[i])]; b[j] -= z * b[i]
    return dict(zip(NODES, b))


def main():
    sp.cmd('version')
    f = C['fixtures']; ac = []; dc = []; trans = []; error = 0
    for rs in f['return_source_ohm']:
        for hz in f['frequencies_Hz']:
            for pk in f['dry_peak_V']:
                responses = {}
                for which in ['dry', 'wet']:
                    d, w = (pk, 0) if which == 'dry' else (0, f['wet_peak_V'])
                    name = f'ac-{rs}-{hz}-{pk}-{which}'
                    v = run(name, base() + [f'VDRY DRIVE 0 DC 0 AC {d}',
                            f'RSOURCE DRIVE FX_RETURN {rs}', f'VWET OUT_BUF 0 DC 0 AC {w}'],
                            f'ac lin 1 {hz} {hz}')
                    s = {n: complex(v[n][-1]) for n in NODES}
                    pred = complex_solve(hz, rs, d, w)
                    error = max(error, max(abs(s[n] - pred[n]) for n in NODES))
                    responses[which] = {**s, 'C607': s['OUT_AC'] - s['WET_AC'],
                                        'C601': s['FX_RETURN'] - s['IN_AC']}
                    sp.cmd('destroy all')
                # Sum of magnitudes bounds arbitrary dry/wet relative phase.
                ac.append({'source_ohm': rs, 'Hz': hz, 'dry_peak_V': pk,
                           'wet_peak_V': f['wet_peak_V'],
                           'peak_bound_V': {n: abs(responses['dry'][n]) + abs(responses['wet'][n])
                                            for n in responses['dry']}})
    for supply in f['cold_plate_step_V']:
        for wet in f['wet_DC_V']:
            # C6 short, R7 and R43 retained, cold/open plate-current bound.
            lines = base() + [component('R7'), component('R43'),
                    'VSHORT CL_P2 CLEAN_OUT 0', 'VNORMAL CLEAN_OUT FX_RETURN 0',
                    f'VPLATE B_EARLY 0 {supply}', f'VWET OUT_BUF 0 {wet}']
            v = run(f'dc-c6-short-{supply}-{wet}', lines, 'op')
            actual = v['OUT_AC'][-1] - v['WET_AC'][-1]
            # Exact DC reduction: C601/C607/C19 are open; R616 carries no DC.
            load = 1 / (1 / num('R24') + 1 / (num('R618') + num('R617')))
            fxload = 1 / (1 / num('R43') + 1 / (num('R612') + load))
            mix = supply * fxload / (num('R7') + fxload) * load / (num('R612') + load)
            expected = wet - mix * num('R617') / (num('R618') + num('R617'))
            error = max(error, abs(actual - expected))
            dc.append({'supply_V': supply, 'wet_DC_V': wet, 'C607_differential_V': actual,
                       'C607_abs_V': abs(actual), 'C607_63V_exceeded': abs(actual) > 63,
                       'nodes_V': {n: v[n][-1] for n in NODES}})
            sp.cmd('destroy all')
        for rise in f['plate_rise_s']:
            for wet in f['wet_DC_V']:
                # Healthy C6 blocks sustained DC. Include both switch-on and off.
                lines = base() + [component(r) for r in ['R7', 'C6', 'R43']] + [
                    'VNORMAL CLEAN_OUT FX_RETURN 0',
                    f'VPLATE B_EARLY 0 PWL(0 0 .1 0 {0.1+rise} {supply} 3 {supply} {3+rise} 0 8 0)',
                    f'VWET OUT_BUF 0 {wet}']
                v = run(f'tran-cold-plate-{supply}-{rise}-{wet}', lines, 'tran 0.001 8 0 0.001')
                t = sp.vector('time'); assert t[-1] >= 8
                cap = [x-y for x,y in zip(v['OUT_AC'], v['WET_AC'])]
                cap1 = [x-y for x,y in zip(v['FX_RETURN'], v['IN_AC'])]
                trans.append({'supply_V': supply, 'rise_s': rise, 'wet_DC_V': wet,
                              'C607_abs_peak_V': max(map(abs, cap)), 'C601_abs_peak_V': max(map(abs, cap1)),
                              'nodes_abs_peak_V': {n: max(map(abs, v[n])) for n in NODES},
                              'end_time_s': t[-1], 'samples': len(t)})
                sp.cmd('destroy all')
    assert error < 1e-5, error
    out = {'scope': 'Passive native interface screen; normal signal, conditional cold-plate transition and C6-short available-rail bound',
           'ac': ac, 'dc_c6_short': dc, 'cold_plate_transient': trans,
           'independent_max_error_V': error,
           'max_ac_C607_V': max(x['peak_bound_V']['C607'] for x in ac),
           'max_transient_C607_V': max(x['C607_abs_peak_V'] for x in trans),
           'max_DC_fault_C607_V': max(x['C607_abs_V'] for x in dc),
           'fault_rating_screen_passed': all(not x['C607_63V_exceeded'] for x in dc),
           'all_cases_completed': True, 'whole_amp_qualified': False, 'clearance_qualified': False,
           'limitations': C['limits'],
           'deck_sha256': {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (M/'results').glob('*.cir')},
           'input_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in [Path(__file__), SOURCE, M/'contract.json']}}
    (M/'results/stress.json').write_text(json.dumps(out, indent=2, allow_nan=False)+'\n')
    (M/'results/spice.log').write_text('\n'.join(sp.logs)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['ac','dc_c6_short','cold_plate_transient','input_sha256','limitations','deck_sha256']}, indent=2))


if __name__ == '__main__':
    main()
