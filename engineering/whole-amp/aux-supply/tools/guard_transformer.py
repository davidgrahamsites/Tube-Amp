"""CB-008 guarded-mute load on actual Triad toroids and an inquiry winding sweep.

Typical-regulation resistive surrogate through the existing raw-supply model.
Writes ../results/guard-transformer.json only. No native CAD or contract writes.
Run with the KiCad bundled Python from this folder.
"""
import copy
import itertools
import json
import math
import sys
from pathlib import Path

from calculate_loads import MODULE, load, sha
from check_preload import load_bounds
from screen_envelope import average, evaluate, spice

# Facts read from the manufacturer PDFs on 28 November 2026 (publish date 12 October 2021).
TRANSFORMERS = [
    dict(mpn='VPT30-1670', VA=50, half_secondary_loaded_V=15, series_current_A=1.67,
         regulation_typ_fraction=.12, efficiency_typ_fraction=.86, temperature_rise_typ_C=40,
         body_diameter_max_mm=83, body_height_max_mm=36, mounting_added_height_mm=3, mass_kg=.6,
         datasheet='https://catalog.triadmagnetics.com/Asset/VPT30-1670.pdf'),
    dict(mpn='VPT30-3330', VA=100, half_secondary_loaded_V=15, series_current_A=3.33,
         regulation_typ_fraction=.09, efficiency_typ_fraction=.89, temperature_rise_typ_C=45,
         body_diameter_max_mm=88, body_height_max_mm=51, mounting_added_height_mm=3, mass_kg=1.0,
         datasheet='https://catalog.triadmagnetics.com/Asset/VPT30-3330.pdf'),
]
# Inquiry sweep. Not part numbers: the two Triad size classes with another loaded voltage.
SWEEP_HALF_V = [15.5, 16, 16.5, 17]
SWEEP_PRIMARY = ['stock_115_230', 'dedicated_120_220']
# Added current in A: (12 V rail, 5 V rail, each 15 V rail).
OPTICAL = (.016, .058, .015)          # prior CB-007 optical-mute budget
GUARD = (.130, .030, 0.)              # new CB-008 guarded mute
BUDGETS = {'baseline': (0., 0., 0.), 'optical': OPTICAL,
           'optical_guard': tuple(a+b for a, b in zip(OPTICAL, GUARD))}
CAP_FRACTIONS = [.8, 1.2]             # electrolytic tolerance screen, both directions
REGULATION_FACTORS = [.75, 1.25]      # assumption: datasheet states typical only
SINK_ATTENTION_C_PER_W = 3.           # assumption: below this a shared sink needs its own design
TI_LM340_FACTS = dict(
    datasheet='https://www.ti.com/lit/ds/symlink/lm340.pdf', revision='SNOSBT0L, revised September 2016',
    absolute_max_input_V=35, u4_12V_output_V=[11.4, 12.6], u4_12V_input_V=[14.5, 27],
    lm7815_15V_output_V=[14.25, 15.75], lm7815_15V_input_V=[17.5, 30], output_power_condition_W=15,
    dropout_typ_V_at_1A_25C=2, iq_over_temperature_A=.0085, iq_line_change_A=.001, iq_load_change_A=.0005,
    to220_theta_jc_note_C_per_W=4, to220_theta_ja_note_C_per_W=54)
SELECTORS = {'lowest_positive': lambda r: r['positive_V']['min'], 'lowest_negative': lambda r: r['negative_V']['min'],
             'highest_positive': lambda r: -r['positive_V']['max'], 'highest_winding': lambda r: -r['half_winding_rms_A'],
             'highest_heat': lambda r: -r['total_regulator_W']}


def surrogate(part, factor=1.):
    reg = part['regulation_typ_fraction']*factor
    v = part['half_secondary_loaded_V']
    return dict(name=f"{part['mpn']}-resistive-surrogate-reg{reg:.4f}",
                open_circuit_half_rms_V=v*(1+reg), series_ohm_per_half=v*reg/part['series_current_A'])


def make_case(c, part, mode, line, cap_uF, profile, budget, factor=1.):
    extra12, extra5, extra15 = BUDGETS[budget]
    item = copy.deepcopy(profile)
    # The upstream model carries direct U4 load as coil units; same current, same KCL and heat.
    item['relays_on'] += extra12*c['relay_min_resistance_ohm']/c['relay_voltage_V']
    item['logic_5V_A'] += extra5
    item['audio_each_rail_A'] += extra15
    rating = mode['selector_V'] if part.get('primary') == 'dedicated_120_220' else mode['primary_rating_V']
    return dict(line_factor=mode['selector_V']*line/rating, frequency_hz=mode['frequency_hz'],
                winding=surrogate(part, factor), reservoir_uF=cap_uF, load=item)


def measure(c, case, step):
    row, _ = evaluate(c, case, step)
    t = spice.vector('time')
    a = next(i for i, x in enumerate(t) if x >= c['simulation']['measure_start_s'])
    middle = (c['simulation']['measure_start_s']+c['simulation']['stop_s'])/2
    b = next(i for i, x in enumerate(t) if x >= middle)
    drift = 0.
    for name in ['v(rawp)', 'v(rawn)']:
        v = spice.vector(name)
        drift = max(drift, abs(average(t[a:b+1], v[a:b+1])-average(t[b:], v[b:])))
    peak = max(abs(x) for name in ['i(va)', 'i(vb)'] for x in spice.vector(name))
    th = {str(x['ambient_C']): x['shared_sink_theta_sa_max_C_per_W'] for x in row['thermal']}
    return dict(positive_V=row['raw_positive_V'], negative_V=row['raw_negative_magnitude_V'],
                half_winding_rms_A=max(row['half_winding_rms_A'].values()),
                raw_load_A=row['raw_load_A'], regulator_W=row['conditional_regulator_dissipation_W'],
                total_regulator_W=row['conditional_total_W'], shared_sink_theta_sa_max_C_per_W=th,
                steady_drift_V=drift, zero_phase_start_peak_winding_A=peak,
                kcl_max_error_A=row['kcl_max_error_A'], completed_time_s=row['completed_time_s'],
                step_s=step, deck_sha256=row['deck_sha256'])


def flags(m, env, rating):
    out = []
    if m['positive_V']['min'] < env['positive_min']: out.append('positive_below_range')
    if m['positive_V']['max'] > env['positive_max']: out.append('positive_above_range')
    if m['negative_V']['min'] < env['negative_min_magnitude']: out.append('negative_below_range')
    if m['negative_V']['max'] > env['negative_max_magnitude']: out.append('negative_above_range')
    if max(m['positive_V']['max'], m['negative_V']['max']) >= env['absolute_max_magnitude']: out.append('absolute_input_limit')
    if m['half_winding_rms_A'] > rating: out.append('winding_above_rating')
    if min(m['shared_sink_theta_sa_max_C_per_W'].values()) <= 0: out.append('no_sink_can_hold_junction_target')
    return out


def margins(env, low_p, low_n, high_p, high_n):
    return dict(positive_low_V=low_p-env['positive_min'], negative_low_V=low_n-env['negative_min_magnitude'],
                positive_high_V=env['positive_max']-high_p, negative_high_V=env['negative_max_magnitude']-high_n)


def main():
    option = json.loads((MODULE/'transformer-candidates.json').read_text())
    c = json.loads((MODULE/'envelope-contract.json').read_text())
    budget = load()
    preload = load_bounds(json.loads((MODULE/'preload-contract.json').read_text()))
    # Baseline cold-coil and preload binding, identical to screen_cold_loads.py.
    c['relay_min_resistance_ohm'] = budget['relay']['cold_screen_resistance_ohm']
    c['relay_voltage_V'] = budget['relay']['voltage_bound_V']
    profiles = []
    for original in c['loads']:
        p = copy.deepcopy(original)
        p['logic_5V_A'] += preload['maximum_current_A']
        p['audio_each_rail_A'] += budget['reverb_rail_loads']['each_rail_maximum_A']
        profiles.append(p)
    known = {p['mpn']: p for p in option['candidates']}
    for key, value in known['VPT30-1670'].items():
        assert TRANSFORMERS[0][key] == value, (key, 'existing candidate record disagrees with datasheet reading')
    ti = option['replacement_U4']
    assert ti['regulated_input_V'] == TI_LM340_FACTS['u4_12V_input_V'] and ti['output_V'] == TI_LM340_FACTS['u4_12V_output_V']
    assert abs(ti['iq_screen_A']-sum(TI_LM340_FACTS[k] for k in ['iq_over_temperature_A', 'iq_line_change_A', 'iq_load_change_A'])) < 1e-12
    native = dict(c['raw_screen_V'])
    replacement = dict(native, positive_min=max(native['positive_min'], ti['regulated_input_V'][0]),
                       positive_max=ti['regulated_input_V'][1])
    envelopes = {'native_ST_regulators': native, 'TI_LM340T_12_as_U4': replacement}
    step = c['simulation']['max_step_s']
    modes, lines, caps = option['modes'], option['line_fractions'], option['reservoir_nominal_uF']
    nominal_out = c['regulator_output_nominal_V']
    checks = {}

    # Regression anchor: an archived candidate case must reproduce through this interpreter.
    prior = json.loads((MODULE/'results/transformer-candidates/screen.json').read_text())
    anchor = next(r for r in prior['cases'] if r['mpn'] == 'VPT30-1670')
    again, _ = evaluate(prior['effective_model'], anchor['case'], anchor['step_s'])
    checks['archived_case_reproduced'] = (again['deck_sha256'] == anchor['deck_sha256'] and
        abs(again['raw_positive_V']['min']-anchor['raw_positive_V']['min']) < 1e-6 and
        abs(max(again['half_winding_rms_A'].values())-max(anchor['half_winding_rms_A'].values())) < 1e-6)
    checks['archived_surrogate_matches'] = all(
        abs(anchor['case']['winding'][k]-surrogate(TRANSFORMERS[0])[k]) < 1e-12
        for k in ['open_circuit_half_rms_V', 'series_ohm_per_half'])

    rows, summary, refinements, sensitivity = [], [], [], []

    def full_matrix(part):
        """Every mode, mains, capacitor tolerance, profile and budget for one option."""
        matrix = itertools.product(modes, lines, caps, CAP_FRACTIONS, range(len(profiles)), BUDGETS)
        for mode, line, cap, fraction, pi, name in matrix:
            case = make_case(c, part, mode, line, cap*fraction, profiles[pi], name)
            m = measure(c, case, step)
            m.update(id=f'guard{len(rows):03d}', mpn=part['mpn'], hypothetical=bool(part.get('hypothetical')),
                     selector_V=mode['selector_V'], mains_V=mode['selector_V']*line,
                     line_factor=case['line_factor'], frequency_hz=mode['frequency_hz'], nominal_cap_uF=cap,
                     cap_fraction=fraction, profile=profiles[pi]['name'], budget=name, model_load=case['load'],
                     winding_loading_fraction=m['half_winding_rms_A']/part['series_current_A'],
                     headroom_over_nominal_output_V={
                         'U4_12V': m['positive_V']['min']-nominal_out['U4'], 'U6_15V': m['positive_V']['min']-nominal_out['U6'],
                         'U7_15V': m['negative_V']['min']-nominal_out['U7']},
                     flags={k: flags(m, env, part['series_current_A']) for k, env in envelopes.items()},
                     replacement_U4_added_W=(ti['iq_screen_A']-c['iq_A']['U4'])*m['positive_V']['mean'],
                     sink_attention=min(m['shared_sink_theta_sa_max_C_per_W'].values()) < SINK_ATTENTION_C_PER_W)
            m['_case'] = case
            rows.append(m)
            if len(rows) % 54 == 0: print('matrix case', len(rows), part['mpn'], file=sys.stderr, flush=True)
        for cap in caps:
            rs = [r for r in rows if r['mpn'] == part['mpn'] and r['nominal_cap_uF'] == cap]
            limiting = {name: min(rs, key=f) for name, f in SELECTORS.items()}
            for name, r in limiting.items():
                fine = measure(c, r['_case'], step/2)
                dv = max(abs(fine[k][n]-r[k][n]) for k in ['positive_V', 'negative_V'] for n in ['min', 'mean', 'max'])
                di = abs(fine['half_winding_rms_A']/r['half_winding_rms_A']-1)
                dw = abs(fine['total_regulator_W']-r['total_regulator_W'])
                assert dv < .01 and di < .005 and dw < .01, (r['id'], dv, di, dw)
                refinements.append(dict(coarse_id=r['id'], role=name, voltage_delta_V=dv, rms_relative_delta=di, heat_delta_W=dw))
            spread = {}
            for factor in REGULATION_FACTORS:
                ms = {}
                for name, r in limiting.items():
                    case = copy.deepcopy(r['_case']); case['winding'] = surrogate(part, factor)
                    ms[name] = measure(c, case, step)
                spread[str(factor)] = dict(
                    regulation_fraction=part['regulation_typ_fraction']*factor,
                    lowest_positive_V=ms['lowest_positive']['positive_V']['min'],
                    lowest_negative_V=ms['lowest_negative']['negative_V']['min'],
                    highest_positive_V=ms['highest_positive']['positive_V']['max'],
                    highest_winding_A=ms['highest_winding']['half_winding_rms_A'],
                    highest_heat_W=ms['highest_heat']['total_regulator_W'])
            sensitivity.append(dict(mpn=part['mpn'], nominal_cap_uF=cap, cases=spread,
                                    basis='Limiting typical-regulation cases rerun; assumed spread, not a manufacturer tolerance.'))
            low_p = limiting['lowest_positive']['positive_V']['min']; low_n = limiting['lowest_negative']['negative_V']['min']
            high_p = limiting['highest_positive']['positive_V']['max']; high_n = max(r['negative_V']['max'] for r in rs)
            hot = limiting['highest_heat']
            s = dict(mpn=part['mpn'], hypothetical=bool(part.get('hypothetical')), VA=part['VA'], nominal_cap_uF=cap, cases=len(rs),
                     limiting_ids={name: r['id'] for name, r in limiting.items()},
                     lowest_positive_V=low_p, lowest_negative_V=low_n, highest_positive_V=high_p, highest_negative_V=high_n,
                     highest_winding_rms_A=limiting['highest_winding']['half_winding_rms_A'],
                     winding_rating_A=part['series_current_A'],
                     winding_loading_fraction=limiting['highest_winding']['half_winding_rms_A']/part['series_current_A'],
                     highest_total_regulator_W=hot['total_regulator_W'], regulator_W_at_highest_heat=hot['regulator_W'],
                     shared_sink_theta_sa_max_C_per_W_at_highest_heat=hot['shared_sink_theta_sa_max_C_per_W'],
                     sink_attention_cases=sum(r['sink_attention'] for r in rs),
                     lowest_headroom_over_nominal_output_V={k: min(r['headroom_over_nominal_output_V'][k] for r in rs)
                                                            for k in ['U4_12V', 'U6_15V', 'U7_15V']},
                     cases_below_typical_2V_dropout_headroom=sum(
                         min(r['headroom_over_nominal_output_V'].values()) < TI_LM340_FACTS['dropout_typ_V_at_1A_25C'] for r in rs),
                     worst_phase_surge_bound_A=max(r['line_factor'] for r in rs)*surrogate(part)['open_circuit_half_rms_V']*math.sqrt(2) /
                         (surrogate(part)['series_ohm_per_half']+c['reservoir_esr_ohm']+.05),
                     highest_zero_phase_start_peak_A=max(r['zero_phase_start_peak_winding_A'] for r in rs),
                     by_budget={b: dict(lowest_positive_V=min(r['positive_V']['min'] for r in rs if r['budget'] == b),
                                        lowest_negative_V=min(r['negative_V']['min'] for r in rs if r['budget'] == b),
                                        highest_positive_V=max(r['positive_V']['max'] for r in rs if r['budget'] == b),
                                        highest_winding_rms_A=max(r['half_winding_rms_A'] for r in rs if r['budget'] == b),
                                        highest_total_regulator_W=max(r['total_regulator_W'] for r in rs if r['budget'] == b))
                                for b in BUDGETS},
                     envelopes={})
            for name, env in envelopes.items():
                bad = [r for r in rs if r['flags'][name]]
                typical = margins(env, low_p, low_n, high_p, high_n)
                worst = {k: min([typical[k]]+[margins(env, v['lowest_positive_V'], v['lowest_negative_V'], v['highest_positive_V'], high_n)[k]
                                              for v in spread.values()]) for k in typical}
                s['envelopes'][name] = dict(
                    flagged_cases=len(bad),
                    flag_counts={f: sum(f in r['flags'][name] for r in rs) for f in sorted({f for r in bad for f in r['flags'][name]})},
                    flagged_by_mains_V={str(v): sum(r['mains_V'] == v for r in bad) for v in sorted({r['mains_V'] for r in bad})},
                    typical_margin_V=typical, clears_typical=not bad, margin_with_assumed_regulation_spread_V=worst,
                    clears_assumed_regulation_spread=not bad and min(worst.values()) >= 0)
            summary.append(s)

    for part in TRANSFORMERS: full_matrix(part)
    real_rows = len(rows)

    # Independent arithmetic bounds on every real-part row.
    checks['line_factor_range'] = (abs(min(r['line_factor'] for r in rows)-198/230) < 1e-12 and
                                   abs(max(r['line_factor'] for r in rows)-132/115) < 1e-12)

    # Inquiry sweep on the corners that limited the real parts; the pick is then run through the full matrix.
    def corner_screen(part, cap, factor=1.):
        got = dict(low_p=1e9, low_n=1e9, high_p=0., high_n=0., rms=0., heat=0., sink=1e9, runs=0)
        for mode in modes:
            jobs = [(lines[0], CAP_FRACTIONS[0], 2, 'optical_guard')]
            jobs += [(lines[-1], f, 0, 'baseline') for f in CAP_FRACTIONS]
            jobs += [(lines[-1], f, 2, 'optical_guard') for f in CAP_FRACTIONS]
            for line, fraction, pi, name in jobs:
                m = measure(c, make_case(c, part, mode, line, cap*fraction, profiles[pi], name, factor), step)
                got.update(low_p=min(got['low_p'], m['positive_V']['min']), low_n=min(got['low_n'], m['negative_V']['min']),
                           high_p=max(got['high_p'], m['positive_V']['max']), high_n=max(got['high_n'], m['negative_V']['max']),
                           rms=max(got['rms'], m['half_winding_rms_A']), heat=max(got['heat'], m['total_regulator_W']),
                           sink=min(got['sink'], min(m['shared_sink_theta_sa_max_C_per_W'].values())), runs=got['runs']+1)
        return got

    assert profiles[2]['name'] == 'expansion_stress' and profiles[0]['name'] == 'idle'
    sweep = []
    grid = list(itertools.product(TRANSFORMERS, SWEEP_HALF_V, SWEEP_PRIMARY, caps))
    for n, (base, volts, primary, cap) in enumerate(grid):
        part = dict(mpn=f"INQUIRY-{base['VA']}VA-2x{volts:g}V-{primary}", hypothetical=True, VA=base['VA'], primary=primary,
                    half_secondary_loaded_V=volts, series_current_A=base['VA']/(2*volts),
                    regulation_typ_fraction=base['regulation_typ_fraction'], regulation_class_from=base['mpn'])
        typ = corner_screen(part, cap)
        item = dict(part=part, nominal_cap_uF=cap, typical=typ, envelopes={})
        for name, env in envelopes.items():
            typical = margins(env, typ['low_p'], typ['low_n'], typ['high_p'], typ['high_n'])
            item['envelopes'][name] = dict(typical_margin_V=typical, clears_typical_corners=min(typical.values()) >= 0 and
                                           typ['rms'] <= part['series_current_A'] and typ['sink'] > 0)
        if any(v['clears_typical_corners'] for v in item['envelopes'].values()):
            spreads = [corner_screen(part, cap, f) for f in REGULATION_FACTORS]
            for name, env in envelopes.items():
                worst = {k: min([item['envelopes'][name]['typical_margin_V'][k]] +
                                [margins(env, s['low_p'], s['low_n'], s['high_p'], s['high_n'])[k] for s in spreads])
                         for k in item['envelopes'][name]['typical_margin_V']}
                item['envelopes'][name].update(margin_with_assumed_regulation_spread_V=worst,
                    clears_assumed_regulation_spread_corners=item['envelopes'][name]['clears_typical_corners'] and min(worst.values()) >= 0)
        sweep.append(item)
        if n % 8 == 0: print('sweep option', n, 'of', len(grid), file=sys.stderr, flush=True)

    def sweep_pick(name):
        ok = [x for x in sweep if x['envelopes'][name].get('clears_assumed_regulation_spread_corners')]
        if not ok: return None
        # Prefer a stock primary arrangement, then lowest VA, then smallest reservoir, then widest worst margin.
        return min(ok, key=lambda x: (x['part']['primary'] != 'stock_115_230', x['part']['VA'], x['nominal_cap_uF'],
                                      -min(x['envelopes'][name]['margin_with_assumed_regulation_spread_V'].values())))
    picks = {name: sweep_pick(name) for name in envelopes}
    confirmed = []
    for name, x in picks.items():
        if x and x['part']['mpn'] not in confirmed:
            full_matrix(x['part']); confirmed.append(x['part']['mpn'])

    checks['winding_rms_at_least_mean_abs_current'] = all(
        r['half_winding_rms_A'] >= (r['raw_load_A']['positive']+r['raw_load_A']['negative'])/2 for r in rows)
    checks['raw_below_open_circuit_peak'] = all(
        max(r['positive_V']['max'], r['negative_V']['max']) <
        r['_case']['winding']['open_circuit_half_rms_V']*r['line_factor']*math.sqrt(2) for r in rows)
    checks['steady_state_reached'] = max(r['steady_drift_V'] for r in rows) < .005
    checks['all_runs_completed'] = all(abs(r['completed_time_s']-c['simulation']['stop_s']) < 1e-9 for r in rows)
    by = {}
    for r in rows:
        by.setdefault((r['mpn'], r['line_factor'], r['frequency_hz'], r['nominal_cap_uF'], r['cap_fraction'], r['profile']), {})[r['budget']] = r
    checks['more_load_never_raises_raw_minimum_or_lowers_current'] = all(
        g['baseline']['positive_V']['min'] >= g['optical']['positive_V']['min'] >= g['optical_guard']['positive_V']['min'] and
        g['baseline']['half_winding_rms_A'] <= g['optical']['half_winding_rms_A'] <= g['optical_guard']['half_winding_rms_A']
        for g in by.values())
    full = BUDGETS['optical_guard']
    checks['guard_budget_current_accounting'] = all(
        abs(g['optical_guard']['raw_load_A']['positive']-g['baseline']['raw_load_A']['positive']-sum(full)) < 1e-12 and
        abs(g['optical_guard']['raw_load_A']['negative']-g['baseline']['raw_load_A']['negative']-full[2]) < 1e-12
        for g in by.values())
    checks['matrix_complete'] = all(len(g) == len(BUDGETS) for g in by.values()) and len(rows) == (len(TRANSFORMERS)+len(confirmed))*216

    def real_pick(name, field):
        ok = [s for s in summary if not s['hypothetical'] and s['envelopes'][name][field]]
        best = min(ok, key=lambda s: (s['VA'], s['nominal_cap_uF'])) if ok else None
        return dict(mpn=best['mpn'], nominal_cap_uF=best['nominal_cap_uF']) if best else None
    selection = {}
    for name in envelopes:
        x = picks[name]
        spec = None
        if x:
            s = next(s for s in summary if s['mpn'] == x['part']['mpn'] and s['nominal_cap_uF'] == x['nominal_cap_uF'])
            spec = dict(option=x['part'], nominal_cap_uF=x['nominal_cap_uF'],
                        full_matrix_clears_typical=s['envelopes'][name]['clears_typical'],
                        full_matrix_clears_assumed_regulation_spread=s['envelopes'][name]['clears_assumed_regulation_spread'],
                        full_matrix_margin_with_assumed_regulation_spread_V=s['envelopes'][name]['margin_with_assumed_regulation_spread_V'],
                        highest_total_regulator_W=s['highest_total_regulator_W'],
                        shared_sink_theta_sa_max_C_per_W_at_highest_heat=s['shared_sink_theta_sa_max_C_per_W_at_highest_heat'],
                        winding_loading_fraction=s['winding_loading_fraction'])
        selection[name] = dict(actual_part_clearing_typical=real_pick(name, 'clears_typical'),
                               actual_part_clearing_assumed_regulation_spread=real_pick(name, 'clears_assumed_regulation_spread'),
                               inquiry_specification=spec)
    selection['rule'] = ('Actual parts: lowest VA, then smallest reservoir, with zero flagged cases over the full matrix. '
                         'Inquiry specification: corner-screened sweep, stock primary preferred, then lowest VA, smallest reservoir and widest margin; '
                         'the pick is confirmed on the full matrix. A screen result for supplier inquiry and bench proof. No purchase or native adoption.')
    assert all(checks.values()), checks
    for r in rows: del r['_case']
    result = dict(
        task='CB-008 guarded-mute auxiliary transformer screen', native_adopted=False, purchase_ready=False,
        transformers=TRANSFORMERS, budgets_added_A={k: dict(rail_12V=v[0], rail_5V=v[1], each_15V_rail=v[2]) for k, v in BUDGETS.items()},
        baseline=dict(relay=budget['relay'], preload_maximum_A=preload['maximum_current_A'],
                      reverb_rail_load_each_A=budget['reverb_rail_loads']['each_rail_maximum_A'], profiles=profiles),
        modes=modes, line_fractions=lines, reservoir_nominal_uF=caps,
        cap_fractions=CAP_FRACTIONS, regulation_factors_assumed=REGULATION_FACTORS,
        envelopes_V=envelopes, thermal_model=c['thermal'], sink_attention_C_per_W_assumed=SINK_ATTENTION_C_PER_W,
        regulator_facts=dict(TI_LM340=TI_LM340_FACTS, ST_L78_L79='Native limits are carried from envelope-contract.json; the ST files could not be fetched on 28 November 2026 and were not re-read.',
                             ST_sources=[x['url'] for x in c['sources'][:2]]),
        case_count=len(rows), actual_part_case_count=real_rows, summary=summary, selection=selection,
        inquiry_sweep=dict(half_secondary_loaded_V=SWEEP_HALF_V, primary=SWEEP_PRIMARY,
                           corners='Per mode: 0.9 mains with expansion_stress, full budget and minus-tolerance reservoir; 1.1 mains idle baseline and 1.1 mains expansion_stress full budget at both reservoir tolerances.',
                           basis='Triad 50 VA and 100 VA typical regulation reused at another loaded voltage. dedicated_120_220 means primaries wound for 120 V and 220 V so the ratio error of a 115/230 V part is absent. Not existing part numbers.',
                           options=sweep),
        regulation_sensitivity=sensitivity, refinements=refinements, checks=checks, cases=rows,
        input_sha256={p: sha(MODULE/p) for p in ['transformer-candidates.json', 'envelope-contract.json', 'preload-contract.json',
                                                 'load-contract.json', 'results/transformer-candidates/screen.json']},
        factory_sha256=sha(Path(__file__)), simulator_library_sha256=sha(Path(spice.lib._name)),
        limitations=[
            'Transformer model is a resistive equivalent from typical regulation at 25 C. No measured winding resistance, secondary voltage tolerance, leakage, core flux or temperature rise.',
            'Operating a 115/230 V primary at 132 V or 242 V is an engineering screen, not a manufacturer approval.',
            'Regulators are imposed loads. No dropout, startup, protection or stability model. Heat uses the contract minimum-output corners and an assumed 6 C/W junction-to-sink path.',
            'Guarded-mute and optical currents are the stated budgets applied continuously to every profile; the baseline budget bounds the unloaded raw maximum.',
            'Reservoir ESR is the contract 0.15 ohm for both sizes. Ripple-current rating, lifetime and fit are not checked.',
            'Worst-phase surge is a closed-form bound against the surrogate resistance only; the rectifier surge rating was not verified here.',
            'Inquiry options are hypothetical windings. Their regulation, size and availability are unknown until a supplier answers.',
            'No chassis fit, fuse, heatsink, supplier stock or delivery evidence.'])
    (MODULE/'results/guard-transformer.json').write_text(json.dumps(result, indent=1)+'\n')
    print(json.dumps(dict(cases=len(rows), checks=checks, selection=selection), indent=1))


if __name__ == '__main__':
    main()
