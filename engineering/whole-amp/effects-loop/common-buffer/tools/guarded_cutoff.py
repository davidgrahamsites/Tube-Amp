"""Run the CB-010 independent guard qualification and write its result."""
import json
import sys
import hashlib
from pathlib import Path

import numpy as np
import low_line_rail
import supply_faults
import cutoff_guard_faults
import cutoff_guard_model
from low_line_cutoff import AQV, closed_form
from cutoff_guard_model import (
    COLD_HIGH,
    C_ONE_OPEN,
    FEED_MIN,
    HOT_LOW,
    MODULE,
    NOM,
    NORMAL_A,
    OUT,
    PARTS,
    PA_ABS,
    REJECTED,
    STOCK,
    TRIP_HI,
    TRIP_LO,
    corner,
    guard
)
from cutoff_guard_faults import (
    cap_table,
    commanded_open,
    hard_step,
    heat,
    loop,
    passive_alternative,
    regulated,
    rise,
    running_short,
    startup,
    static,
    welded_start
)


if __name__ == '__main__':
    out = dict(id='CB-010', status='prototype trial; simulation, arithmetic and data-sheet limits only',
               trip_corners_V=[TRIP_LO, TRIP_HI], normal_branch_mA=1000*NORMAL_A,
               circuit=cutoff_guard_model.__doc__.split('\n\n')[1].strip().splitlines(), parts=PARTS, rejected=REJECTED,
               stock=STOCK, model_nominal=NOM, corners=dict(hot_low=HOT_LOW, cold_high=COLD_HIGH),
               declared_assumptions=[
                   'VOM1271 hot minimum: 4 uA and 6.0 V. Cold maximum: 40 uA and 9.5 V. The sheet gives 6 uA and '
                   '7.8 V minimum at 10 mA, 25 C only.',
                   'VOM1271 turn-off is a 150 k switch fitted to the 65 us typical at 200 pF. 470 k is the slow case.',
                   'M1 and M2 are level-1 surrogates with series drift resistance and fixed capacitances.',
                   'M1 drift resistance x2.3 hot. Q1 0 to 85 C. RS 1 %.',
                   'Raw B+ is a stiff source. Wiring inductance is absent.'])

    # 1. Static limit and drop. Choose RS.
    choose = []
    for rs in (12.4, 13.0, 13.7, 14.3, 15.0):
        lo = static('hot low', dict(HOT_LOW, rs=rs*1.01))
        hi = static('cold high', dict(COLD_HIGH, rs=rs*.99))
        choose.append(dict(rs_ohm=rs, limit_mA=[lo['mA_at_100V'], static('nominal', corner(rs=rs))['mA_at_100V'],
                                               hi['mA_at_100V']],
                           drop_V=[static('nominal', corner(rs=rs))['drop_at_22p72mA_V'], lo['drop_at_22p72mA_V']],
                           margin_over_normal=lo['mA_at_100V']/1000/NORMAL_A,
                           late_10ms_V=rise(hi['mA_at_100V']/1000, C_ONE_OPEN, .010)))
    out['sense_resistor_choice'] = choose
    static_rows = [static('nominal', NOM), static('hot low', HOT_LOW), static('cold high', COLD_HIGH)]
    for tq in (0, 25, 55, 85):
        for isc in (4e-6, 15e-6, 40e-6):
            static_rows.append(static('temperature and driver current', corner(tq=tq, isc=isc)))
    static_rows += [static('M1 threshold', corner(vp=vp, kp1=kp)) for vp in (-2.5, -4.5) for kp in (.48, 1.33)]
    static_rows += [static('optional two-device stack, nominal', corner(stack=True)),
                    static('optional two-device stack, hot low', dict(HOT_LOW, stack=True))]
    out['static'] = static_rows
    lim_lo, lim_hi = HOT_LOW and static_rows[1]['mA_at_100V']/1000, static_rows[2]['mA_at_top']/1000
    lim_hi = max(lim_hi, static_rows[2]['mA_at_100V']/1000)
    out['limit_range_mA'] = [1000*lim_lo, 1000*lim_hi]
    out['drop_at_normal_V'] = dict(nominal=static_rows[0]['drop_at_22p72mA_V'], hot_low=static_rows[1]['drop_at_22p72mA_V'],
                                   cold_high=static_rows[2]['drop_at_22p72mA_V'],
                                   as_equivalent_feed_ohm=static_rows[1]['drop_at_22p72mA_V']/NORMAL_A)

    # 2. LED off and one-fault cases of the guard itself.
    out['off_state'] = [static('LED off', NOM, led=0), static('LED off, hot low', HOT_LOW, led=0)]
    out['off_state_note'] = ('Level-1 model has no drain leakage. Data sheet: 5 uA at 25 C, 50 uA at 125 C at 1000 V. '
                             'DZ carries it; M2 then holds 10 V and M1 gate-source is -10 V of the 20 V rating.')
    faults = []
    for f, text in [('q_open', 'Q1 open'), ('m2_short', 'M2 drain-source short'), ('dz_short', 'DZ short'),
                    ('rs_one_open', 'one RS resistor open'), ('m1_gate_source_short', 'M1 gate-source short')]:
        for c in (corner(fault=f), dict(COLD_HIGH, fault=f)):
            faults.append(dict(static(text, c), led_off_mA_at_top=static(text, c, led=0)['mA_at_top']))
    for f, text in [('rs_short', 'RS short'), ('m1_short', 'M1 drain-source short')]:
        faults.append(static(text, corner(fault=f), vmax=60))
        faults.append(static(text+', LED off', corner(fault=f), led=0, vmax=60))
    faults.append(static('stack: upper 1000 V device shorted', corner(stack=True, fault='m1_short')))
    faults.append(static('stack: upper shorted, LED off', corner(stack=True, fault='m1_short'), led=0))
    out['guard_one_fault'] = faults
    out['guard_one_fault_reading'] = dict(
        fails_safe=['LED, driver or VOM1271 dead: open', 'Q1 collector-emitter short: open',
                    'both RS open: under 4 mA through RB', 'one RS open: limit falls to 20 to 24 mA, the safe direction'],
        degrades_to_self_bias='Q1 open, M2 short or DZ short leave M1 self-biased on RS: 212 to 288 mA, below the 400 mA '
                              'switch pulse rating. The 10 ms case is then lost. M2 or DZ short also loses the guard disconnect.',
        removes_guard=['M1 drain-source or gate-source short. M2 and DZ then meet raw B+ and must be assumed shorted.',
                       'RS short (film resistors normally fail open)', 'LED driver stuck on removes only the disconnect'],
        with_guard_removed='CB-009 applies unchanged: AQV256HA 2 ms cutoff holds 342.45 V; 10 ms and weld cases fail.',
        latent_fault_test='At each start hold the guard LED off for 100 ms after the series switch closes. '
                          'Any rail rise above 60 V means a shorted guard. Refuse to arm.')

    # 3. Pass short while running.
    run = [running_short('nominal', NOM, guard_delay=.0005),
           running_short('cold high limit', COLD_HIGH, guard_delay=.0005),
           running_short('hot low limit', HOT_LOW, guard_delay=.0005),
           running_short('cold high, 450 V crest', COLD_HIGH, raw=450),
           running_short('cold high, 550 V cold', COLD_HIGH, raw=550, guard_delay=.0005),
           running_short('cold high, slow 470 k turn-off', dict(COLD_HIGH, roff=470e3), guard_delay=.0005),
           running_short('cold high, two open 35.2 uF', COLD_HIGH, cap=35.2, guard_delay=.0005),
           running_short('cold high, three open 17.6 uF', COLD_HIGH, cap=17.6, guard_delay=.0005, step=2e-6),
           running_short('cold high, M1 gate-drain 100 pF', dict(COLD_HIGH, cgd1=100e-12, cgd2=200e-12)),
           running_short('cold high, two-device stack', dict(COLD_HIGH, stack=True))]
    out['pass_short_running'] = run
    out['commanded_open_at_normal_load'] = [
        commanded_open('nominal', NOM), commanded_open('cold high', COLD_HIGH),
        commanded_open('hot low', HOT_LOW), commanded_open('cold high, slow 470 k turn-off', dict(COLD_HIGH, roff=470e3)),
        commanded_open('cold high, 1.5 M turn-off, ten times the typical', dict(COLD_HIGH, roff=1.5e6))]
    out['cb009_reference'] = dict(peak_2ms_V=closed_form(440, FEED_MIN, C_ONE_OPEN*1e-6, .002),
                                  peak_10ms_V=closed_form(440, FEED_MIN, C_ONE_OPEN*1e-6, .010),
                                  weld_surge_mA=[1000*440/FEED_MIN, 1000*550/FEED_MIN])
    out['reservoir_table_at_high_limit'] = cap_table(lim_hi)

    # 4. Bypass welded and pass shorted.
    weld = [welded_start('cold high', COLD_HIGH, 440), welded_start('cold high', COLD_HIGH, 550),
            welded_start('hot low', HOT_LOW, 440), welded_start('nominal', NOM, 550),
            welded_start('cold high, one open', COLD_HIGH, 550, cap=C_ONE_OPEN, end=1.)]
    out['welded_bypass_shorted_pass_start'] = weld
    step = [hard_step('nominal', NOM, 440), hard_step('cold high', COLD_HIGH, 550),
            hard_step('hot low', HOT_LOW, 550),
            hard_step('cold high, larger Miller capacitances', dict(COLD_HIGH, cgd1=100e-12, cgd2=200e-12), 550),
            hard_step('cold high, two-device stack', dict(COLD_HIGH, stack=True), 550)]
    out['hard_close_onto_short'] = step
    out['sequence_rule'] = 'Close the series AQV256HA first. Light the guard LED last. The driver then ramps the current.'

    # 5. CB-009 regulator with the guard in circuit.
    hot9 = dict(low_line_rail.CAND, feed=945, ron=AQV['ron_hot_assumed'], limiter_is=2e-12)
    ref = low_line_rail.sustained('CB-009 hot corner, no guard', hot9, 340, 16.5, vth=5.5)
    assert abs(ref['settled_min_V']-309.33) < .05, ref
    reg = [ref,
           regulated('nominal guard', NOM, hot9, 340, 16.5, vth=5.5),
           regulated('hot low guard', HOT_LOW, hot9, 340, 16.5, vth=5.5),
           regulated('cold high guard', COLD_HIGH, hot9, 340, 16.5, vth=5.5),
           regulated('hot low guard, 336 V trough', HOT_LOW, hot9, 336, 16.5, vth=5.5),
           low_line_rail.sustained('no guard, 336 V trough', hot9, 336, 16.5, vth=5.5),
           regulated('hot low guard, 18 mA load', HOT_LOW, hot9, 340, 18, vth=5.5),
           regulated('hot low guard, 20 mA load', HOT_LOW, hot9, 340, 20, vth=5.5),
           regulated('hot low guard, 22 mA load', HOT_LOW, hot9, 340, 22, vth=5.5),
           regulated('high line, idle then full', NOM, low_line_rail.CAND, 440, 16.5),
           regulated('high line, light load', COLD_HIGH, low_line_rail.CAND, 440, 2.),
           regulated('550 V cold, bypass open', NOM, low_line_rail.CAND, 540, 16.5, bypass=False)]
    out['regulated_rail'] = reg
    out['loop'] = [dict(guard=n, **loop(c, *case)) for n, c, case in
                   [('hot low', HOT_LOW, (340, True, .4, 52.8)), ('cold high', COLD_HIGH, (440, True, 2, 105.6))]]

    # 6. Start, heat, headroom, alternatives.
    out['startup'] = [startup(lim_lo, raw, stuck) for raw in (340, 390, 440) for stuck in (False, True)]
    out['heat'] = heat(lim_lo, lim_hi)
    need = COLD_HIGH['vth2']+(2*lim_hi/COLD_HIGH['kp2'])**.5
    out['gate_drive_headroom'] = dict(
        M2_gate_needed_at_limit_V=need, driver_VOC_min_25C_V=7.8, driver_VOC_hot_assumed_V=6.0,
        margin_V=6.0-need, M2_gate_rating_V=20, driver_VOC_max_assumed_V=9.5,
        driver_ISC_min_uA=6, gate_leak_budget_uA=.1+9.5/10,
        M1_needs_no_drive=True, isolation_working_V=dict(raw_cold=550, VIORM_Vpeak=707, fraction=550/707),
        M1_voltage_fraction_at_550V=.55, extra_plus5V_load_mA=[10.3, 17.8],
        note='Recheck the CB-009 +5 V regulator heat with the added LED current.')
    out['self_bias_only'] = dict(
        note='IXTP3N100D2 with only a source resistor. Limit is about |VGS(off)|/R. VGS(off) spans 2.5 to 4.5 V.',
        rows=[dict(source_ohm=r, limit_mA=[1000*2.5/r, 1000*4.5/r], drop_at_normal_V=NORMAL_A*(r+6),
                   late_10ms_V=rise(4.5/r, C_ONE_OPEN, .010)) for r in (56, 75, 100, 120)],
        verdict='No value gives more than 22.72 mA at the low end and under 63 mA at the high end with a small drop.')
    out['max_limit_for_350V_at_10ms_mA'] = 1000*(PA_ABS-TRIP_HI)*C_ONE_OPEN*1e-6/.010
    out['passive_alternative'] = passive_alternative()

    out['checks'] = dict(
        cb009_anchor_reproduced=True,
        limit_above_normal_all_corners=lim_lo > NORMAL_A*1.15,
        limit_range_mA=out['limit_range_mA'],
        drop_at_normal_under_0p7V=static_rows[1]['drop_at_22p72mA_V'] < .7,
        pass_short_10ms_late_below_350V=all(r['below_350V_at_10ms'] for r in run[:6]),
        pass_short_10ms_late_peak_V=max(r['rail_if_nothing_opens']['at_10ms_V'] for r in run[:6]),
        guard_opens_within_2ms=all(r['guard_open_after_led_off_us'] < 1500 for r in run if 'guard_open_after_led_off_us' in r),
        weld_and_short_surge_below_400mA=all(r['within_AQV_400mA_single_shot'] for r in weld),
        weld_and_short_surge_peak_mA=max(r['peak_series_switch_mA'] for r in weld),
        hard_close_spike_peak_mA=max(r['peak_mA'] for r in step),
        hard_close_spike_above_400mA_us=max(r['above_400mA_us'] for r in step),
        low_line_hot_corner_holds_305V=reg[2]['holds_305V'], low_line_hot_corner_min_V=reg[2]['settled_min_V'],
        low_line_loss_against_cb009_mV=1000*(ref['settled_min_V']-reg[2]['settled_min_V']),
        regulated_runs_never_above_320V=all(r['whole_run_max_V'] < 320 for r in reg),
        hot_low_guard_load_margin='18 mA holds 309.3 V; 20 mA sags; 22 mA fails. CB-009 alone held 22 mA at 306.4 V.',
        loop_margin_min_deg=min(c['margin_deg'] for r in out['loop'] for c in r['crossings']),
        start_meets_cb007_timeouts=all(r['meets_CB007_timeouts'] for r in out['startup'] if not r['bypass_forced_open']),
        M1_inside_SOA_point=max(r['fraction_of_SOA_power'] for r in out['heat']['cases']) < 1,
        open_items=['All reservoirs lost with a shorted pass still exceeds 350 V.',
                    'M1 short is a latent single fault. Use the start proof test or the two-device stack.',
                    'VOM1271 switching and hot output are typical or assumed. Measure them.',
                    'M1 needs a 5.6 K/W insulated path or the pass sink.',
                    'Bench: capture guard current, M2 gate and rail in a forced pass short.'])
    out['source_sha256'] = {Path(m.__file__).name: hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()
                            for m in (sys.modules['__main__'], cutoff_guard_model, cutoff_guard_faults, low_line_rail, supply_faults,
                                      sys.modules['low_line_cutoff'], sys.modules['supply_trial'])}
    OUT.write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(out['checks'], indent=1))
