"""CB-009. Low-line 310 V rail trial.

Reuse the CB-007 pass-regulator text factory and the CB-008 sustained and audio
load fixtures. Change only declared values: fixed feed, current-sense resistor,
gate pull-up, reservoir count and the CB-008 window-divider bleed. Recheck the
CB-007 independent 2 ms cutoff, start, rail-short and heat arithmetic with the
changed values. Prototype trial. No native CAD is read or written.
"""
import hashlib
import json
import sys
from math import exp, log
from pathlib import Path

import numpy as np

import low_line_cutoff
from low_line_cutoff import AQV, pass_short, prearm
import guard_audio
import supply_faults
import supply_loop
import supply_trial
from supply_trial import MODULE, sp

BASE = supply_trial.regulator          # CB-007 factory, text unchanged
OUT = MODULE / 'results/low-line-rail.json'
TRIP_LO, TRIP_HI = supply_faults.trip_corners()   # CB-007 hard-trip corners
CAP_NOM, CAP_TOL = 22.0, .20           # Nichicon UPT2W220MHD, uF
LEAK_PER_CAP_mA = .604                 # CB-007 allowance at 310 V
GUARD_DIVIDER = 4*76800 + 2490         # CB-008 290 V pin-window divider
VBE_ONSET_HOT, VBE_HARD_COLD = .50, .85  # limiter spread; .85 is the CB-007 bound
PRECHARGE = 8200

# Series/bypass switch limits carried from the CB-007 Panasonic AQV256HA review.
CB007 = dict(feed=1820, sense=33, pullup=100000, caps=2, guard=False, ron=30, led=1500, limiter_is=1e-14)
CAND = dict(feed=900, sense=15, pullup=100000, caps=4, guard=True, ron=30, led=1500, limiter_is=1e-14)


def one(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def variant(raw, ctr, vth, cap, bypass=True, leak_mA=None, *, feed, sense, pullup, caps,
            guard, ron, led, limiter_is):
    """CB-007 regulator with declared value changes. cap is the fitted total in uF."""
    leak = LEAK_PER_CAP_mA*caps if leak_mA is None else leak_mA
    net = BASE(raw, ctr, vth, cap, bypass, leak)
    net = one(net, f'RFEED raw7 sw7 {1820 + (30 if bypass else 8200)}',
              f'RFEED raw7 sw7 {feed + (ron if bypass else PRECHARGE)}')
    net = one(net, 'RSW sw7 d7 30', f'RSW sw7 d7 {ron}')
    net = one(net, 'RGATE d7 g7 100k', f'RGATE d7 g7 {pullup}')
    net = one(net, 'RSENSE src7 supply 33', f'RSENSE src7 supply {sense}')
    net = one(net, 'NPN(bf=80 is=1e-14)', f'NPN(bf=80 is={limiter_is})')
    net = one(net, '(v(drive7)-1.15)/1500)', f'(v(drive7)-1.15)/{led})')
    if guard:
        net += f'RGUARD9 supply 0 {GUARD_DIVIDER}\n'
    return net


def bleed_mA(cfg, v=310.):
    r = [360000, 330490, 308490] + ([GUARD_DIVIDER] if cfg['guard'] else [])
    return 1000*v*sum(1/x for x in r) + LEAK_PER_CAP_mA*cfg['caps']*v/310


def sustained(label, cfg, trough, load_mA, ctr=.4, vth=5, cap=None, bypass=True, idle_mA=2.,
              leak_mA=None, end=1.5, ripple=5.):
    """CB-008 guard_sustained fixture: 100 Hz raw ripple, idle then continuous load."""
    cap = CAP_NOM*(1-CAP_TOL)*(cfg['caps']-1) if cap is None else cap   # one open, rest low
    net = variant(trough, ctr, vth, cap, bypass, leak_mA, **cfg)
    net = one(net, f'VRAW raw7 0 {trough}', f'VRAW raw7 0 SIN({trough+ripple} {ripple} 100)')
    deck = (f'CB009 {label}\n'+net +
            f'ILOAD supply 0 PULSE({idle_mA/1000} {load_mA/1000} .1 .0001 .0001 9 10)\n.end')
    sp.load(deck)
    sp.cmd('save v(supply) v(d7) v(src7) v(g7) v(drive7) i(vraw)')
    sp.cmd(f'tran .00005 {end} 0 .00005')
    t = np.array(sp.vector('time'))
    assert t[-1] >= end-1e-8, sp.logs[-6:]
    rail, drain, src, gate, drive = (np.array(sp.vector(f'v({n})')) for n in
                                     ['supply', 'd7', 'src7', 'g7', 'drive7'])
    current = -np.array(sp.vector('i(vraw)'))
    w = t > end-.1                      # ten ripple cycles
    pull = (drain-gate)/cfg['pullup']
    sp.cmd('destroy all')
    return dict(case=label, raw_trough_V=trough, raw_crest_V=trough+2*ripple, load_mA=load_mA,
                bleed_and_leak_mA_at_310V=bleed_mA(cfg) if leak_mA is None else None,
                feed_ohm=cfg['feed'], sense_ohm=cfg['sense'], pullup_ohm=cfg['pullup'],
                switch_ohm_each=cfg['ron'], limiter_is=cfg['limiter_is'], fitted_cap_uF=cap,
                CTR=ctr, threshold_V=vth, bypass=bypass,
                settled_min_V=float(min(rail[w])), settled_max_V=float(max(rail[w])),
                whole_run_min_V=float(min(rail)), whole_run_max_V=float(max(rail)),
                ripple_mVpp=float(1000*(max(rail[w])-min(rail[w]))),
                branch_mA=float(1000*np.mean(current[w])),
                drain_minus_rail_min_V=float(min((drain-rail)[w])),
                pullup_drop_min_V=float(min((drain-gate)[w])),
                led_drive_max_mA=float(1000*max(0, max(drive[w])-1.15)/cfg['led']),
                pass_W=float(np.mean(((drain-src)*(current-pull))[w])),
                pullup_W=float(np.mean((pull**2*cfg['pullup'])[w])),
                fixed_feed_W=float(np.mean(current[w]**2)*cfg['feed']),
                precharge_W=0. if bypass else float(np.mean(current[w]**2)*PRECHARGE),
                each_switch_W=float(np.mean(current[w]**2)*cfg['ron']),
                holds_305V=bool(min(rail[w]) >= 305), inside_295_320_window=bool(
                    min(rail[w]) > 295 and max(rail) < 320),
                deck_sha256=hashlib.sha256(deck.encode()).hexdigest())


def loop(cfg, raw, bypass, ctr, cap):
    old = supply_loop.regulator
    supply_loop.regulator = lambda r, c, v, cp, b, lk: variant(r, c, v, cp, b, None, **cfg)
    try:
        return supply_loop.probe(raw, bypass, ctr, cap)
    finally:
        supply_loop.regulator = old


def audio(cfg, raw, cap):
    """CB-008 guard_audio fixture (Apex PA340, TI OPA134, mixer, spring send, guard)."""
    old = guard_audio.regulator
    guard_audio.regulator = lambda r, c, v, cp, b, lk: variant(r, c, v, cap, b, None, **cfg)
    try:
        row = guard_audio.audio(20000, 500, 600, 150, False, 25, 310, False, 1, raw)
    finally:
        guard_audio.regulator = old
    row.update(fitted_cap_uF=cap, feed_ohm=cfg['feed'], sense_ohm=cfg['sense'])
    return row


# ---------------------------------------------------------------- cutoff
def startup(cfg, raw, stuck=False, cap_factor=1+CAP_TOL):
    """CB-007 startup envelope with the changed feed, limit, reservoir and bleed."""
    c = cfg['caps']*CAP_NOM*cap_factor*1e-6
    limit = VBE_ONSET_HOT/(cfg['sense']*1.01)        # weakest limiter
    t = v = 0.
    closed = at60 = at300 = None
    dt = .0001
    while t < 8:
        if not stuck and closed is None and raw-v < 140:
            closed = t
        r = cfg['feed']*1.05+2*AQV['ron_hot_assumed']+(0 if closed is not None else PRECHARGE*1.05)
        src = min(limit, max(0, (raw-v-5.5)/r))
        idle = .0025+bleed_mA(cfg, v)/1000+v/940000
        v = min(310, max(0, v+dt*(src-idle)/c))
        t += dt
        at60 = t if at60 is None and v >= 60 else at60
        at300 = t if at300 is None and v >= 300 else at300
    return dict(raw_V=raw, bypass_forced_open=stuck, cap_uF=c*1e6, final_V=v, reached_60V_s=at60,
                bypass_closed_s=closed, reached_300V_s=at300,
                meets_CB007_timeouts=bool(at60 and at60 < 1 and at300 and at300 < 4))


def heat(cfg, raw_mean_hi=435., raw_cold=550.):
    """Arithmetic bounds. Currents in A. Feed at minimum for pass heat, maximum for feed heat."""
    rmin = cfg['feed']*.95
    lim_lo = VBE_ONSET_HOT/(cfg['sense']*1.01)
    lim_hi = VBE_HARD_COLD/(cfg['sense']*.95)
    normal = (16.5+bleed_mA(cfg))/1000
    rows = []
    for name, raw, i, seconds in [
            ('normal 16.5 mA plus bleed, 430-440 V raw', raw_mean_hi, normal, None),
            ('same, 440-450 V sensitivity', raw_mean_hi+10, normal, None),
            ('overload held at cold limiter ceiling, rail still in window', raw_mean_hi+10, lim_hi, None),
            ('running rail short, bypass closed, until 2 ms trip', 440, lim_hi, .002)]:
        vds = raw-i*rmin-(0 if seconds else 310)
        rows.append(dict(case=name, current_mA=1000*i, pass_V=vds, pass_W=vds*i, duration_s=seconds,
                         pass_J=vds*i*seconds if seconds else None,
                         fixed_feed_W=i*i*cfg['feed']*1.05, each_switch_W_at_45ohm=i*i*AQV['ron_hot_assumed']))
    rpre = .95*(cfg['feed']+PRECHARGE)
    i = min(lim_hi, 440/(2*rpre))
    rows.append(dict(case='cold-start rail short through precharge, 1 s timeout', current_mA=1000*i,
                     pass_V=440-i*rpre, pass_W=(440-i*rpre)*i, duration_s=1., pass_J=(440-i*rpre)*i,
                     precharge_W=(440/rpre)**2*.95*PRECHARGE, fixed_feed_W=(440/rpre)**2*rmin))
    # 550 V cold raw: raw minus rail is 240 V, so the bypass opens and the load runs through 8.2k.
    i = min(normal, (raw_cold-310-5.5)/rpre)
    rows.append(dict(case='550 V cold raw, bypass open, full load through precharge', current_mA=1000*i,
                     pass_V=raw_cold-i*rpre-310, pass_W=(raw_cold-i*rpre-310)*i, duration_s=None,
                     precharge_W=i*i*PRECHARGE*1.05, fixed_feed_W=i*i*cfg['feed']*1.05,
                     note='Continuous precharge-string heat. Trip or rate the string.'))
    worst_cont = max(r['pass_W'] for r in rows if r['duration_s'] is None)
    sink = [dict(air_C=a, case_limit_C=c, power_W=p, max_case_to_air_K_W=(c-a)/p)
            for a in (60, 70) for c, p in ((75, rows[1]['pass_W']), (100, worst_cont))]
    return dict(limiter_range_mA=[1000*lim_lo, 1000*lim_hi], normal_branch_mA=1000*normal,
                limiter_margin_over_normal=lim_lo/normal, cases=rows, pass_sink_requirement=sink,
                pullup_W_at_440V=(440-normal*rmin-316)**2/cfg['pullup'],
                pullup_W_at_550V_bypass_welded=(550-normal*rmin-316)**2/cfg['pullup'])


def required_trough(cfg, load_mA=16.5, vgs=5.5, hot=True):
    i = (load_mA+bleed_mA(cfg))/1000
    r = cfg['feed']*1.05+2*(AQV['ron_hot_assumed'] if hot else cfg['ron'])+cfg['sense']*1.01
    limiter_ok = i*cfg['sense']*1.01 < VBE_ONSET_HOT-.1
    return dict(feed_ohm=cfg['feed'], sense_ohm=cfg['sense'], branch_mA=1000*i, series_drop_V=i*r,
                gate_overhead_V=vgs, setpoint_V=309.73, required_raw_trough_V=309.73+i*r+vgs,
                sense_drop_V=i*cfg['sense']*1.01, limiter_clear=bool(limiter_ok))


if __name__ == '__main__':
    out = dict(id='CB-009', status='prototype trial; simulation and arithmetic only',
               trip_corners_V=[TRIP_LO, TRIP_HI], cb007=CB007, candidate=CAND, switch_limits_used=AQV)

    # 1. Regression anchors: reproduce the CB-008 sags and the CB-007 one-open cutoff.
    anchors = [sustained(f'cb008 anchor {m} mA', CB007, 340, m, cap=17.6, leak_mA=1.208) for m in (14, 16.5)]
    assert abs(anchors[0]['settled_min_V']-297.94) < .05 and abs(anchors[1]['settled_min_V']-255.30) < .05, anchors
    old = supply_faults.pass_short('one reservoir open', 17.6e-6, .002)['peak_V']
    mine = pass_short('cb007 anchor', 1820, 1, spice=True)
    assert abs(old-mine['peak_V']) < 1e-6 and abs(mine['ngspice_minus_closed_form_V']) < .05, (old, mine)
    out['anchors'] = dict(cb008_sustained=anchors, cb007_one_open_peak_V=old, reproduced=mine)

    # 2. Which change does what. Same CB-008 fixture, one reservoir of two, full bleed.
    grid = []
    for feed, sense, pullup in [(1820, 33, 100000), (1820, 18, 100000), (900, 33, 100000),
                                (900, 22, 100000), (900, 18, 100000), (900, 15, 100000),
                                (910, 15, 100000), (940, 15, 100000), (680, 15, 100000)]:
        cfg = dict(CB007, feed=feed, sense=sense, pullup=pullup, guard=True)
        for load in (14, 16.5):
            grid.append(sustained('cause grid', cfg, 340, load, cap=17.6))
    out['cause_grid_340V'] = grid

    # 3. Candidate corners at the 340 V trough and below.
    hot = dict(CAND, feed=945, ron=AQV['ron_hot_assumed'], limiter_is=2e-12)
    corners = [sustained('nominal parts', CAND, 340, 16.5),
               sustained('feed +5%, hot switches, hot limiter, Vth 5.5', hot, 340, 16.5, vth=5.5),
               sustained('same, strong opto', hot, 340, 16.5, ctr=2, vth=5.5),
               sustained('same, all four reservoirs +20%', hot, 340, 16.5, vth=5.5, cap=105.6),
               sustained('same, 22 ohm sense', dict(hot, sense=22), 340, 16.5, vth=5.5),
               sustained('same, 18 ohm sense', dict(hot, sense=18), 340, 16.5, vth=5.5)]
    corners += [sustained('load margin', hot, 340, m, vth=5.5) for m in (18, 20, 22, 25, 30)]
    corners += [sustained('raw margin', hot, raw, 16.5, vth=5.5) for raw in (325, 330, 335)]
    out['candidate_low_line'] = corners

    trade = []
    for pull in (47400, 68100, 100000):
        for sense in (22, 18, 15):
            h = dict(hot, pullup=pull, sense=sense)
            trade += [sustained('trade: lower raw', h, raw, 16.5, vth=5.5) for raw in (333, 336, 340)]
            trade += [sustained('trade: more load', h, 340, m, vth=5.5) for m in (20, 22)]
    trade += [sustained('trade: 680 ohm feed (714 max)', dict(hot, feed=714), raw, 16.5, vth=5.5)
              for raw in (325, 330, 335)]
    out['pullup_sense_feed_trade'] = trade

    # 4. High-line authority, heat and the 550 V cold diagnostic.
    high = [sustained('idle then full, weak opto', CAND, 430, 16.5),
            sustained('idle then full, weak opto, 450 V crest', CAND, 440, 16.5),
            sustained('light load, weak opto', CAND, 440, 2.),
            sustained('light load, weak opto, 47.4k pull-up', dict(CAND, pullup=47400), 440, 2.),
            sustained('light load, strong opto, low Vth', CAND, 440, 2., ctr=2, vth=3),
            sustained('550 V cold, bypass open', CAND, 540, 16.5, bypass=False),
            sustained('550 V cold, bypass open, light load', CAND, 540, 2., bypass=False),
            sustained('550 V cold, bypass welded, light load', CAND, 540, 2.),
            sustained('550 V cold, bypass open, light, 47.4k pull-up', dict(CAND, pullup=47400), 540, 2., bypass=False),
            sustained('550 V cold, bypass welded, light, 47.4k pull-up', dict(CAND, pullup=47400), 540, 2.),
            sustained('550 V cold, bypass welded, light, 68.1k pull-up', dict(CAND, pullup=68100), 540, 2.),
            sustained('550 V cold, bypass welded, light, 47.4k pull-up and 1k LED resistor', dict(CAND, pullup=47400, led=1000), 540, 2.)]
    out['candidate_high_line'] = high

    # 5. Compensation with the changed plant.
    out['loop'] = [loop(CAND, *c) for c in [(340, True, .4, 52.8), (340, True, 2, 105.6), (390, True, 1, 88),
                                             (440, False, 2, 105.6), (440, True, 2, 105.6), (440, True, .4, 52.8)]]
    out['loop_led_1k'] = [loop(dict(CAND, led=1000), *c) for c in [(340, True, .4, 52.8), (440, True, 2, 105.6)]]

    # 6. Independent cutoff with a shorted pass.
    cut = []
    for feed, fitted in [(1820, 2), (900, 2), (900, 3), (900, 4), (910, 4), (940, 4), (680, 4), (680, 5)]:
        cut.append(pass_short(f'{fitted} fitted, one open', feed, fitted-1))
    cut += [pass_short('4 fitted, none open', 900, 4),
            pass_short('4 fitted, one open, 450 V crest', 900, 3, raw=450),
            pass_short('4 fitted, one open, further 15% cold loss', 900, 3, cap_factor=.8*.85),
            pass_short('4 fitted, one open, 10 ms trip', 900, 3, delay=.010),
            pass_short('4 fitted, two open', 900, 2),
            pass_short('3 fitted, one open, 550 V cold', 900, 2, raw=550),
            pass_short('4 fitted, one open, 550 V cold', 900, 3, raw=550),
            pass_short('reservoir lost, 0.1 uF local only', 900, .1/17.6, spice=False),
            pass_short('faster 0.5 ms disconnect, 4 fitted one open, 550 V', 900, 3, delay=.0005, raw=550),
            pass_short('faster 0.5 ms disconnect, 2 fitted one open, 440 V', 900, 1, delay=.0005)]
    out['pass_short_cutoff'] = cut
    out['pass_short_before_arm'] = [prearm('healthy precharge', 900, 4, False),
                                    prearm('precharge bypass welded', 900, 4, True),
                                    prearm('CB-007 values, bypass welded', 1820, 2, True),
                                    prearm('healthy precharge, 550 V', 900, 4, False, raw=550),
                                    prearm('bypass welded, 550 V', 900, 4, True, raw=550)]
    out['dual_fault_pass_and_cutoff_short_V'] = 440.

    # 7. Start, heat, stored energy and discharge.
    out['startup'] = [startup(CAND, raw, stuck) for raw in (340, 390, 440) for stuck in (False, True)]
    out['heat'] = heat(CAND)
    out['heat_cb007_values'] = heat(dict(CB007, guard=True))
    cmax = CAND['caps']*CAP_NOM*(1+CAP_TOL)*1e-6
    out['stored_J_at_350V'] = .5*cmax*350**2
    out['bleeder_only_350_to_60_s'] = 360000*1.05*cmax*log(350/60)
    out['required_trough'] = [required_trough(c) for c in (dict(CB007, guard=True), dict(CAND, feed=945), CAND)]

    # 8. Full CB-008 audio load on the candidate. Slow; skip with --no-audio.
    if '--no-audio' not in sys.argv:
        out['audio'] = [audio(hot, 340, 52.8), audio(CAND, 440, 105.6)]

    low, hi = corners[1], high
    out['checks'] = dict(
        anchors_reproduced=True,
        low_line_16p5mA_worst_parts_holds_305V=low['holds_305V'],
        low_line_ripple_mVpp=low['ripple_mVpp'],
        high_line_settled_and_transition_in_window=all(r['whole_run_max_V'] < 320 and r['whole_run_min_V'] > 295
                                for r in hi if r['raw_crest_V'] <= 450 and 'pull-up' not in r['case']),
        loop_margin_min_deg=min(c['margin_deg'] for r in out['loop'] for c in r['crossings']),
        cutoff_440V_one_open_below_350V=cut[3]['below_PA340_350V'],
        cutoff_spice_agrees=max(abs(r['ngspice_minus_closed_form_V']) for r in cut if 'ngspice_peak_V' in r) < .05,
        start_meets_cb007_timeouts=all(r['meets_CB007_timeouts'] for r in out['startup'] if not r['bypass_forced_open']))
    out['source_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                            [Path(__file__), Path(supply_trial.__file__), Path(supply_faults.__file__),
                             Path(supply_loop.__file__), Path(guard_audio.__file__), Path(low_line_cutoff.__file__)]}
    OUT.write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(out['checks'], indent=1))
