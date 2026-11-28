"""CB-010. Screen extra U4 junction margin on the CB-009 dedicated sink.

Reuses the CB-009 rectifier matrix (216 cases per electrical arrangement), sink and
contact allocations. Writes ../results/u4-margin.json only. No native CAD or contract
writes. Run with the KiCad bundled Python from this folder.
"""
import itertools
import json
from pathlib import Path

from guard_transformer import MODULE, TRANSFORMERS, make_case, measure, sha
from regulator_cooling import CONTACT, JC, LEAK, PRELOAD, SINK
from screen_envelope import currents

LIMIT_C = 100.
TARGET_GAIN_C = 10.
E12 = [1., 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
R_VALUES = [m*d for d in (1, 10, 100) for m in E12]
R_TOL = .05                 # Vishay AC series, J tolerance
R_MARGIN_V = .5             # kept above each regulator input floor at the worst trough
R_LOAD_LIMIT = .3           # own derating: fraction of the 70 C rating
RESISTOR = dict(series='Vishay AC05', P40_W=5., P70_W=4.7, tolerance_fraction=R_TOL,
                part_number_format='AC05000 0 0 <3 digits><multiplier> J AC 00; 9 = x0.1, 0 = x1')

# Regulator facts used here. Each "source" names the document that was read.
PARTS = {
    'LM340T-12': dict(
        mpn='LM340T-12/NOPB', role='U4', jc_K_W=JC['U4'], tab='GND',
        input_floor_V=15., input_ceiling_V=27., ground_heavy_A=.010, ground_light_A=.001,
        source='TI SNOSBT0L section 6.7: output 11.4-12.6 V for 14.5-27 V input; line regulation over temperature from 15 V; '
               'dropout 2 V typical at 1 A, 25 C. Note 3 of 6.1: TO-220 junction-to-case 4 C/W. '
               'Table 6.4 lists 1.7 C/W junction-to-case (bottom). CB-009 used 5 K/W; kept.'),
    'LM340T-5': dict(
        mpn='LM340T-5.0/NOPB', role='U5', jc_K_W=JC['U5'], tab='GND',
        input_floor_V=8., input_ceiling_V=20., ground_heavy_A=.0095, ground_light_A=.0095,
        source='TI SNOSBT0L section 6.6: output 4.75-5.25 V for 7.5-20 V input; line regulation over temperature 8-20 V; '
               'absolute maximum 35 V. Ground current carried from the envelope contract.'),
    'LT3086-12': dict(
        mpn='LT3086IT7#PBF', role='U4', jc_K_W=JC['U6'], tab='GND', set_resistor_ohm=232e3,
        input_floor_V=13., input_ceiling_V=27., ground_heavy_A=.025, ground_light_A=.001,
        source='Carried from CB-009 and CB-008 records for U6: 3 K/W T7 junction-to-case, 0.4 V + 50 uA x R(SET), '
               '510 mV full-load dropout bound, 25 mA full-load ground current bound. '
               'Floor = 12 V x 1.03 + 0.51 V, rounded up. Not re-read in CB-010.'),
    'LT3086-5': dict(
        mpn='LT3086IT7#PBF', role='U5', jc_K_W=JC['U6'], tab='GND', set_resistor_ohm=93.1e3,
        input_floor_V=6., input_ceiling_V=27., ground_heavy_A=.0105, ground_light_A=.001,
        source='As LT3086-12. 0.4 V + 50 uA x 93.1 kOhm = 5.055 V. Floor = 5.055 V x 1.03 + 0.51 V, rounded up. '
               'Ground current bound is the CB-009 value for U6 at a similar load.'),
}
# name: (U4 part, U5 part, U5 feed, series resistor ahead of U4)
OPTIONS = {
    'A0_CB009_reference': ('LM340T-12', 'LM340T-5', 'cascade', False),
    'A1_U4_LT3086': ('LT3086-12', 'LM340T-5', 'cascade', False),
    'A2_U4_LM340_series_R': ('LM340T-12', 'LM340T-5', 'cascade', True),
    'A3_U4_LT3086_series_R': ('LT3086-12', 'LM340T-5', 'cascade', True),
    'B1_U5_LM340_raw_R': ('LM340T-12', 'LM340T-5', 'raw', False),
    'B2_U5_LT3086_raw_R': ('LM340T-12', 'LT3086-5', 'raw', False),
    'B3_U4_U5_LT3086_raw_R': ('LT3086-12', 'LT3086-5', 'raw', False),
}
FAULTS = dict(normal_60C=(60., SINK, CONTACT), air_70C=(70., SINK, CONTACT),
              restricted_sink_3K_W=(60., 3., CONTACT), poor_contact_3K_W=(60., SINK, 3.))


def matrix(prior, c, u4, u5, cache):
    """CB-009 matrix for one U4/U5 pair. Returns rows with raw rails and branch currents."""
    rows = []
    for mode, line, cap, profile, regulation, budget in itertools.product(
            prior['modes'], (.9, 1., 1.1), (.8, 1.2), prior['baseline']['profiles'],
            (.75, 1, 1.25), ('optical_guard', 'baseline')):
        heavy = budget == 'optical_guard'
        leakage = LEAK if heavy else 0
        preload = PRELOAD if heavy else .001
        g4 = PARTS[u4]['ground_heavy_A' if heavy else 'ground_light_A']
        g5 = PARTS[u5]['ground_heavy_A' if heavy else 'ground_light_A']
        c['iq_A'].update(U4=g4+leakage, U5=g5, U6=(.0105 if heavy else .00025)+preload,
                         U7=(.006 if heavy else .001)+leakage)
        case = make_case(c, TRANSFORMERS[0], mode, line, 4700*cap, profile, budget, regulation)
        key = json.dumps([c['iq_A'], case], sort_keys=True)
        if key not in cache:
            cache[key] = measure(c, case, c['simulation']['max_step_s'])
        r = cache[key]
        assert r['completed_time_s'] >= .599999 and r['kcl_max_error_A'] < 1e-5
        out, _, _ = currents(c, case['load'])
        pos, neg = r['positive_V'], r['negative_V']
        fixed = dict(U6=r['regulator_W']['U6']-preload*c['thermal_output_bound_V']['U6'],
                     U7=r['regulator_W']['U7']-leakage*neg['mean'])
        rows.append(dict(line_V=line*mode['selector_V'], frequency_Hz=mode['frequency_hz'], load=profile['name'],
                         budget=budget, regulation_factor=regulation, reservoir_uF=4700*cap,
                         positive_V=pos, negative_magnitude_V=neg, winding_rms_A=r['half_winding_rms_A'],
                         deck_sha256=r['deck_sha256'], fixed_W=fixed, ground_A=dict(U4=g4, U5=g5),
                         logic_A=out['U5'], direct_12V_A=out['U4']-out['U5']-g5,
                         voltage_ok=pos['min'] >= 16 and pos['max'] <= 27 and neg['min'] >= 17.5 and neg['max'] <= 30))
    return rows


def branch_A(row, feed):
    """Currents entering U4 and U5, including their ground currents."""
    i5 = row['logic_A']+row['ground_A']['U5']
    i4 = row['direct_12V_A']+row['ground_A']['U4']+(i5 if feed == 'cascade' else 0)
    return i4, i5


def pick_resistor(rows, feed, which, floor):
    """Largest E12 value that keeps the input trough above floor + margin at +5% resistance."""
    ok = [R for R in R_VALUES if all(
        row['positive_V']['min']-branch_A(row, feed)[which]*R*(1+R_TOL) >= floor+R_MARGIN_V for row in rows)]
    return max(ok) if ok else None


def heat(row, c, feed, r4, r5):
    """Mean heat in each regulator and resistor, plus regulator input extremes."""
    vp = row['positive_V']
    i4, i5 = branch_A(row, feed)
    out = c['thermal_output_bound_V']
    v4 = vp['mean']-i4*r4
    v5 = c['thermal_U5_input_bound_V'] if feed == 'cascade' else vp['mean']-i5*r5
    w = dict(U4=(v4-out['U4'])*(i4-row['ground_A']['U4'])+v4*row['ground_A']['U4'],
             U5=(v5-out['U5'])*row['logic_A']+v5*row['ground_A']['U5'], **row['fixed_W'])
    res = dict(R_U4=i4*i4*r4*(1+R_TOL), R_U5=i5*i5*r5*(1+R_TOL))
    edge = dict(U4=[vp['min']-i4*r4*(1+R_TOL), vp['max']-i4*r4*(1-R_TOL)])
    if feed == 'raw':
        edge['U5'] = [vp['min']-i5*r5*(1+R_TOL), vp['max']-i5*r5*(1-R_TOL)]
    return w, res, edge


def junctions(w, jc, ambient, sink, contact):
    total = sum(w.values())
    return {k: ambient+sink*total+(jc[k]+contact)*p for k, p in w.items()}


def main():
    prior = json.loads((MODULE/'results/guard-transformer.json').read_text())
    cb009 = json.loads((MODULE/'results/regulator-cooling.json').read_text())
    c = json.loads((MODULE/'envelope-contract.json').read_text())
    c['relay_min_resistance_ohm'] = prior['baseline']['relay']['cold_screen_resistance_ohm']
    c['thermal_output_bound_V'].update(U4=11.4, U6=14.5, U7=14.25)
    cache, sets, report = {}, {}, {}
    for name, (u4, u5, feed, series) in OPTIONS.items():
        if (u4, u5) not in sets:
            sets[u4, u5] = matrix(prior, c, u4, u5, cache)
        rows = sets[u4, u5]
        jc = dict(JC, U4=PARTS[u4]['jc_K_W'], U5=PARTS[u5]['jc_K_W'])
        r4 = pick_resistor(rows, feed, 0, PARTS[u4]['input_floor_V']) if series else 0.
        r5 = pick_resistor(rows, feed, 1, PARTS[u5]['input_floor_V']) if feed == 'raw' else 0.
        if r4 is None or r5 is None:
            report[name] = dict(U4=u4, U5=u5, U5_feed=feed, rejected='No E12 resistor keeps the input floor with margin.')
            continue
        done = [(row,)+heat(row, c, feed, r4, r5) for row in rows]
        peak = {tag: {k: max(junctions(w, jc, *f)[k] for _, w, _, _ in done) for k in jc} for tag, f in FAULTS.items()}
        # A shorted resistor returns its heat to the regulator.
        short = [heat(row, c, feed, 0., 0.)[0] for row in rows]
        hot = max(done, key=lambda d: junctions(d[1], jc, *FAULTS['normal_60C'])['U4'])
        edges = {k: [min(e[k][0] for *_, e in done), max(e[k][1] for *_, e in done)] for k in done[0][3]}
        limits = {k: [PARTS[p]['input_floor_V'], PARTS[p]['input_ceiling_V']] for k, p in (('U4', u4), ('U5', u5)) if k in edges}
        input_ok = all(limits[k][0] <= edges[k][0] and edges[k][1] <= limits[k][1] for k in edges)
        res_peak = {k: max(res[k] for _, _, res, _ in done) for k in ('R_U4', 'R_U5')}
        gain = cb009['max_Tj_C']['U4']-peak['normal_60C']['U4']
        item = dict(
            U4=PARTS[u4]['mpn'], U5=PARTS[u5]['mpn'], U5_feed=feed, R_U4_ohm=r4, R_U5_ohm=r5,
            case_count=len(rows), raw_voltage_failures=sum(not row['voltage_ok'] for row in rows),
            winding_rms_peak_A=max(row['winding_rms_A'] for row in rows),
            pos_range_V=[min(row['positive_V']['min'] for row in rows), max(row['positive_V']['max'] for row in rows)],
            regulator_input_range_V=edges, regulator_input_limits_V=limits, regulator_inputs_inside_documented_range=input_ok,
            max_heat_W={k: max(w[k] for _, w, _, _ in done) for k in jc},
            max_sink_W=max(sum(w.values()) for _, w, _, _ in done),
            max_resistor_W=res_peak, resistor_fraction_of_P70=max(res_peak.values())/RESISTOR['P70_W'],
            max_aux_heat_in_cabinet_W=max(sum(w.values())+sum(res.values()) for _, w, res, _ in done),
            peak_Tj_C=peak, hottest_device_60C=max(peak['normal_60C'], key=peak['normal_60C'].get),
            resistor_shorted_peak_Tj_60C={k: max(junctions(w, jc, *FAULTS['normal_60C'])[k] for w in short) for k in jc},
            U4_gain_over_CB009_C=gain, U4_margin_60C=LIMIT_C-peak['normal_60C']['U4'],
            U4_allowed_sink_K_W=min((LIMIT_C-60-(jc['U4']+CONTACT)*w['U4'])/sum(w.values()) for _, w, _, _ in done),
            governing_case=dict({k: v for k, v in hot[0].items() if k not in ('fixed_W', 'deck_sha256')},
                                heat_W=hot[1], resistor_W=hot[2], regulator_input_V=hot[3]),
            passes=dict(gain_10C_at_60C=gain >= TARGET_GAIN_C, all_below_100C_at_70C=max(peak['air_70C'].values()) <= LIMIT_C,
                        all_below_100C_with_3K_W_sink=max(peak['restricted_sink_3K_W'].values()) <= LIMIT_C,
                        all_below_100C_with_3K_W_contact=max(peak['poor_contact_3K_W'].values()) <= LIMIT_C,
                        documented_input_ranges=input_ok,
                        resistor_within_own_derating=max(res_peak.values()) <= R_LOAD_LIMIT*RESISTOR['P70_W']))
        item['accepted_for_trial'] = all(item['passes'].values()) and not item['raw_voltage_failures']
        report[name] = item
    ref = report['A0_CB009_reference']
    old = {(r['line_V'], r['frequency_Hz'], r['load'], r['budget'], r['regulation_factor'], r['reservoir_uF']): r for r in cb009['cases']}
    checks = dict(
        cb009_decks_reproduced=all(row['deck_sha256'] == old[row['line_V'], row['frequency_Hz'], row['load'], row['budget'],
                                                             row['regulation_factor'], row['reservoir_uF']]['deck_sha256']
                                   for row in sets['LM340T-12', 'LM340T-5']),
        cb009_junctions_reproduced=all(abs(ref['peak_Tj_C']['normal_60C'][k]-cb009['max_Tj_C'][k]) < 1e-6 for k in JC),
        cb009_faults_reproduced=all(abs(max(ref['peak_Tj_C'][a].values())-cb009['faults_peak_Tj_C'][b]) < 1e-6 for a, b in
                                    (('air_70C', 'air_at_70C'), ('restricted_sink_3K_W',)*2, ('poor_contact_3K_W',)*2)),
        raw_feed_leaves_rectifier_load_unchanged=report['B1_U5_LM340_raw_R'].get('pos_range_V') == ref['pos_range_V'],
        distinct_rectifier_runs=len(cache))
    assert all(checks.values()), checks
    accepted = [k for k, v in report.items() if v.get('accepted_for_trial')]
    result = dict(
        task='CB-010 additional U4 junction margin on the CB-009 auxiliary sink', native_adopted=False, purchase_ready=False,
        cb009_U4_Tj_60C=cb009['max_Tj_C']['U4'], target=dict(gain_C=TARGET_GAIN_C, junction_limit_C=LIMIT_C),
        accepted_for_trial=accepted,
        preferred_trial=max(accepted, key=lambda k: report[k]['U4_margin_60C']) if accepted else None,
        preferred_rule='Accepted option with the largest U4 margin at 60 C. A trial choice only.',
        resistor_part_numbers={'6.8': 'AC05000006808JAC00', '68': 'AC05000006809JAC00',
                               'basis': 'Built from the Vishay part-number key. Not checked against a distributor listing.'},
        limitations=[
            'LT3086 data sheet was not re-read. Confirm dropout, ground current, input range and current limit at a 21 V input-output difference before use.',
            'No mains-loss hold-up run. A series resistor ahead of U4 lowers 12 V hold-up. A raw-fed U5 lowers 5 V hold-up. Rerun the hold-up screen first.',
            'No startup, short-circuit, stability or noise model. An open resistor removes its rail.',
            'Resistor heat stays in the closed cabinet. Total auxiliary heat is not reduced. Resistor surface temperature and spacing are not checked.',
            'Sink 1.6 K/W and contact 1.0 K/W are CB-009 allocations, not measurements. Sink space in the power compartment remains open.',
            'Typical-regulation transformer surrogate and imposed DC loads, as CB-009.'],
        options=report, parts=PARTS, resistor=RESISTOR,
        resistor_rule=dict(values='E12', tolerance_fraction=R_TOL, margin_above_floor_V=R_MARGIN_V, load_limit_fraction_of_P70=R_LOAD_LIMIT,
                           basis='Largest value that holds floor + margin at the lowest raw trough with +5% resistance. No credit for an input capacitor after the resistor.'),
        thermal=dict(sink_K_W=SINK, tab_pad_K_W=CONTACT, faults={k: dict(air_C=a, sink_K_W=s, contact_K_W=p) for k, (a, s, p) in FAULTS.items()},
                     model='Steady state. All four regulators share the Fischer SK 92 75 SA allocation. Resistors heat the cabinet air, not the sink.'),
        checks=checks,
        sources=dict(
            TI_LM340=dict(url='https://www.ti.com/lit/ds/symlink/lm340.pdf', revision='SNOSBT0L, revised September 2016',
                          sha256_when_read='49391342cf3b05f89ae94607257ef03f678ae9f1a3bdd388252adb8b00da043d', read_on='2026-11-28',
                          used='Sections 6.1 note 3, 6.4, 6.6, 6.7; Figure 22 series input resistor; orderable list has no 12 V TO-3 part.'),
            Vishay_AC=dict(url='https://www.vishay.com/docs/28730/ac_ac-at_ac-ni.pdf', revision='Document 28730, 05-Dec-2024',
                           sha256_when_read='ebd3c714bb6b8c267c4cee006f5c72f105ee79c47d43ca680eb7e65929051f51', read_on='2026-11-28',
                           used='Rated dissipation P40 and P70, tolerance, part-number format.'),
            LT3086=dict(url='https://www.analog.com/media/en/technical-documentation/data-sheets/lt3086.pdf',
                        status='Download timed out on 28 November 2026. Values are carried from the CB-008 and CB-009 records.'),
            CB009='results/regulator-cooling.json and ../effects-loop/common-buffer/winding-rail-fit.html'),
        input_sha256={p: sha(MODULE/p) for p in ['envelope-contract.json', 'results/guard-transformer.json', 'results/regulator-cooling.json',
                                                 'tools/regulator_cooling.py', 'tools/guard_transformer.py']},
        factory_sha256=sha(Path(__file__)))
    (MODULE/'results/u4-margin.json').write_text(json.dumps(result, indent=1)+'\n')
    for k, v in report.items():
        print(k, {a: v.get(a) for a in ('R_U4_ohm', 'R_U5_ohm', 'U4_gain_over_CB009_C', 'regulator_input_range_V', 'max_resistor_W', 'accepted_for_trial')},
              v.get('peak_Tj_C'), v.get('passes'))
    print(checks, accepted)


if __name__ == '__main__':
    main()
