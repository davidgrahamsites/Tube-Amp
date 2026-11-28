"""DC, transient and fault fixtures for the independent cutoff guard."""
import hashlib
from math import log

import numpy as np
import low_line_rail
from low_line_cutoff import AQV, closed_form
from supply_trial import sp
from cutoff_guard_model import (
    CAP_NOM,
    CAP_TOL,
    C_MAX,
    C_ONE_OPEN,
    FEED_MIN,
    NORMAL_A,
    PARTS,
    PA_ABS,
    TRIP_HI,
    guard,
)


def iv(c, led=1, vmax=560):
    """Static current against voltage across the guard, output at 0 V."""
    deck = f'CB010 guard iv\nVG in10 0 0\n{guard("in10", "out10", c, f"VLED10 led10 0 {led}")}VOUT out10 0 0\n.end'
    v, i, vt = [], [], []
    for sweep in ('dc vg 0 12 .01', f'dc vg 20 {vmax} 10'):
        sp.load(deck)
        sp.cmd(sweep)
        v += list(sp.vector('v(in10)'))
        i += list(sp.vector('i(vout)'))
        vt += list(np.array(sp.vector('v(t10)'))-np.array(sp.vector('v(s20)')))
        sp.cmd('destroy all')
    return np.array(v), np.array(i), np.array(vt), hashlib.sha256(deck.encode()).hexdigest()


def static(label, c, led=1, vmax=560):
    v, i, vt, digest = iv(c, led, vmax)
    at = lambda x: float(np.interp(x, v, i))
    k = int(np.argmax(i >= NORMAL_A)) if i.max() >= NORMAL_A else None
    drop = None if k is None else float(np.interp(NORMAL_A, i[k-1:k+1], v[k-1:k+1]))
    top = min(550, vmax)
    return dict(case=label, **{x: c[x] for x in ('vp', 'rd1', 'vth2', 'rs', 'tq', 'is_mult', 'isc', 'voc', 'stack', 'fault')},
                led=led, drop_at_22p72mA_V=drop, mA_at_5V=1000*at(5), mA_at_20V=1000*at(20),
                mA_at_100V=1000*at(min(100, vmax)), mA_at_440V=1000*at(min(440, vmax)), mA_at_top=1000*at(top), top_V=top,
                M1_W_at_top=top*at(top), M2_drain_source_max_V=float(max(vt)), deck_sha256=digest)


# ---------------------------------------------------------------- transients
def series(raw, c, led, body, end, step, start=0., cap=C_ONE_OPEN, rail0=310., feed=FEED_MIN, rsw=0., ramp=None):
    source = raw if ramp is None else f'PWL(0 0 {ramp} {raw})'
    deck = (f'CB010 guard transient\nVRAW raw 0 {source}\n{guard("raw", "x10", c, led)}'
            f'RFEED x10 sw {feed+rsw}\n{body}\nCRES rail 0 {cap}u ic={rail0}\n.ic v(rail)={rail0}\n.end')
    sp.load(deck)
    sp.cmd('save v(rail) v(x10) v(sw) v(t10) v(s20) v(g20) v(g10) v(raw)')
    sp.cmd(f'tran {step} {end} {start} {step} uic')
    t = np.array(sp.vector('time'))
    assert t[-1] >= end*(1-1e-6), sp.logs[-6:]
    r = {k: np.array(sp.vector(f'v({k})')) for k in ('rail', 'x10', 'sw', 't10', 's20', 'g20', 'g10', 'raw')}
    sp.cmd('destroy all')
    r.update(t=t, i=(r['x10']-r['sw'])/(feed+rsw), deck_sha256=hashlib.sha256(deck.encode()).hexdigest())
    r['p1'] = (r['raw']-r['t10'])*r['i']
    return r


def integral(y, t):
    return float(np.sum(.5*(y[1:]+y[:-1])*np.diff(t)))


def running_short(label, c, raw=440., cap=C_ONE_OPEN, t_fault=.008, guard_delay=None, step=5e-6):
    """Pass shorts while running at 310 V. No load afterwards. Fastest fixed feed."""
    rpre = (raw-.6-NORMAL_A*FEED_MIN-310)/NORMAL_A
    body = (f'RPRE sw rail {rpre}\nSPASS sw rail flt 0 swp\n.model swp SW(vt=.5 vh=0 ron=1m roff=1e12)\n'
            f'VF flt 0 PWL(0 0 {t_fault} 0 {t_fault+1e-6} 1)\n'
            f'ILOAD rail 0 PWL(0 {NORMAL_A} {t_fault} {NORMAL_A} {t_fault+1e-6} 0)')
    lim = 1e-3*static('', c)['mA_at_100V']
    end = t_fault+(TRIP_HI-310)*cap*1e-6/lim*1.25+.013
    r = series(raw, c, 'VLED10 led10 0 1', body, end, step, cap=cap)
    t, v, i = r['t'], r['rail'], r['i']
    after = t > t_fault
    cross = float(np.interp(TRIP_HI, v[after], t[after]))
    at = lambda d: float(np.interp(cross+d, t, v))
    plateau = (t > t_fault+.002) & (t < cross)
    row = dict(case=label, raw_V=raw, cap_uF=cap, prefault_rail_V=float(np.interp(t_fault, t, v)),
               fault_to_trip_ms=1000*(cross-t_fault), trip_V=TRIP_HI,
               limit_mA_mean=float(1000*np.mean(i[plateau])), limit_mA_max_after_2ms=float(1000*max(i[plateau])),
               spike_mA=float(1000*max(i[after])), spike_above_130mA_us=1e6*integral((i[after] > .13)*1., t[after]),
               rail_if_nothing_opens=dict(at_2ms_V=at(.002), at_10ms_V=at(.010)),
               below_350V_at_10ms=at(.010) < PA_ABS,
               M1_W_plateau=float(np.mean(r['p1'][plateau])),
               delay_to_350V_ms=1000*(PA_ABS-TRIP_HI)*cap*1e-6/float(np.mean(i[plateau])),
               deck_sha256=r['deck_sha256'])
    if guard_delay is not None:         # second pass: guard LED removed after the trip crossing
        off = cross+guard_delay
        r2 = series(raw, c, f'VLED10 led10 0 PWL(0 1 {off} 1 {off+1e-6} 0)', body, off+.006, step, cap=cap)
        late = r2['t'] > off
        opened = r2['t'][late][np.argmax(r2['i'][late] < 1e-4)]
        row.update(guard_led_off_after_trip_ms=1000*guard_delay, guard_open_after_led_off_us=1e6*float(opened-off),
                   peak_V_guard_opens=float(max(r2['rail'])),
                   leak_after_open_uA=float(1e6*np.mean(r2['i'][r2['t'] > off+.004])),
                   M2_drain_source_after_open_V=float(max((r2['t10']-r2['s20'])[late])))
    return row


def commanded_open(label, c, raw=440.):
    """Normal 22.72 mA through an intact regulator surrogate. LED removed at 8 ms."""
    rpre = (raw-.6-NORMAL_A*FEED_MIN-310)/NORMAL_A
    off = .008
    r = series(raw, c, f'VLED10 led10 0 PWL(0 1 {off} 1 {off+1e-6} 0)',
               f'RPRE sw rail {rpre}\nILOAD rail 0 {NORMAL_A}', off+.004, 1e-6)
    late = r['t'] > off
    opened = r['t'][late][np.argmax(r['i'][late] < 1e-4)]
    on = (r['t'] > .006) & (r['t'] < off)
    return dict(case=label, roff_ohm=c['roff'], current_before_mA=float(1000*np.mean(r['i'][on])),
                guard_drop_before_V=float(np.mean((r['raw']-r['x10'])[on])),
                M2_gate_before_V=float(np.mean((r['g20']-r['s20'])[on])),
                open_after_led_off_us=1e6*float(opened-off), deck_sha256=r['deck_sha256'])


def welded_start(label, c, raw, cap=C_MAX, end=1.8, step=2e-5):
    """Cold start. Bypass welded and pass shorted. Raw rises in 0.5 ms. Guard LED lit at 2 ms.
    Nothing trips."""
    r = series(raw, c, 'VLED10 led10 0 PWL(0 0 .002 0 .002001 1)', 'RSHORT sw rail 1m', end, step,
               cap=cap, rail0=0., ramp=.0005)
    t, v, i = r['t'], r['rail'], r['i']
    when = lambda x: float(np.interp(x, v, t)) if v[-1] >= x else None
    cross = when(TRIP_HI)
    slope = float(np.interp(cross, t, i))/(cap*1e-6) if cross else None
    return dict(case=label, raw_V=raw, cap_uF=cap, peak_series_switch_mA=float(1000*max(i)),
                peak_before_led_mA=float(1000*max(i[t < .002])), charge_current_mA=float(1000*np.mean(i[(t > .01) & (t < .05)])),
                within_AQV_400mA_single_shot=bool(max(i) <= AQV['peak_100ms_single_A']),
                within_AQV_85C_continuous=bool(max(i) <= AQV['continuous_85C_A']),
                reaches_60V_s=when(60), reaches_trip_s=cross,
                rail_at_trip_plus=None if not cross else dict(V_2ms=TRIP_HI+slope*.002, V_10ms=TRIP_HI+slope*.010),
                M1_peak_W=float(max(r['p1'])), M1_J_to_trip=integral(r['p1'][t <= (cross or end)], t[t <= (cross or end)]),
                feed_J=integral(i*i*FEED_MIN, t), switch_J_at_30ohm=integral(i*i*30, t),
                deck_sha256=r['deck_sha256'])


def hard_step(label, c, raw, cap=C_MAX):
    """Guard lit and settled, then the downstream path closes onto a discharged, shorted branch."""
    ts = .003
    body = (f'SCL sw rail cl 0 swc\n.model swc SW(vt=.5 vh=0 ron=1m roff=1e12)\n'
            f'VCL cl 0 PWL(0 0 {ts} 0 {ts+1e-7} 1)\nRIDLE sw 0 100meg')
    r = series(raw, c, 'VLED10 led10 0 1', body, ts+.0006, 2e-8, start=ts-2e-5, cap=cap, rail0=0.)
    t, i = r['t'], r['i']
    k = t >= ts
    above = lambda x: 1e6*integral((i[k] > x)*1., t[k])
    settle = t > ts+.0004
    return dict(case=label, raw_V=raw, unlimited_mA=1000*raw/FEED_MIN, peak_mA=float(1000*max(i)),
                above_400mA_us=above(.4), above_130mA_us=above(.13), i2t_A2s=integral(i[k]**2, t[k]),
                AQV_single_shot_i2t_A2s=AQV['peak_100ms_single_A']**2*.1,
                settled_mA=float(1000*np.mean(i[settle])), M1_peak_W=float(max(r['p1'])),
                M2_drain_source_peak_V=float(max(r['t10']-r['s20'])), M2_gate_peak_V=float(max(r['g20']-r['s20'])),
                M1_gate_source_min_V=float(min(r['g10']-r['t10'])), M1_gate_transient_rating_V=-30,
                deck_sha256=r['deck_sha256'])


# ---------------------------------------------------------------- CB-009 regulator with the guard
def with_guard(c):
    base = low_line_rail.variant

    def variant(*a, **k):
        net = low_line_rail.one(base(*a, **k), 'RFEED raw7 sw7', 'RFEED x10 sw7')
        # Released starting guesses, as in the CB-007 guided case. They do not force the solution.
        return net+guard('raw7', 'x10', c)+'.nodeset v(supply)=310 v(drive7)=2\n'
    return base, variant


def regulated(label, c, cfg, *a, **k):
    base, low_line_rail.variant = with_guard(c)
    try:
        row = low_line_rail.sustained(label, cfg, *a, **k)
    finally:
        low_line_rail.variant = base
    return row


def loop(c, *case):
    base, low_line_rail.variant = with_guard(c)
    try:
        return low_line_rail.loop(low_line_rail.CAND, *case)
    finally:
        low_line_rail.variant = base


def startup(limit_A, raw, stuck=False):
    """CB-009 startup envelope with the guard as the lower of the two limits."""
    old = low_line_rail.VBE_ONSET_HOT
    own = old/(low_line_rail.CAND['sense']*1.01)
    low_line_rail.VBE_ONSET_HOT = min(own, limit_A)*low_line_rail.CAND['sense']*1.01
    try:
        row = low_line_rail.startup(low_line_rail.CAND, raw, stuck)
    finally:
        low_line_rail.VBE_ONSET_HOT = old
    row.update(charging_limit_mA=1000*min(own, limit_A))
    return row


# ---------------------------------------------------------------- arithmetic
def rise(limit_A, cap_uF, delay_s):
    return TRIP_HI+limit_A*delay_s/(cap_uF*1e-6)


def cap_table(limit_A):
    rows = []
    for name, cap in [('four fitted +20%', C_MAX), ('four fitted -20%', 70.4), ('one open', C_ONE_OPEN),
                      ('two open', 35.2), ('three open', 17.6), ('all reservoirs lost, 0.1 uF local', .1)]:
        rows.append(dict(reservoir=name, cap_uF=cap, peak_V=dict(guard_0p5ms=rise(limit_A, cap, .0005),
                         cutoff_2ms=rise(limit_A, cap, .002), late_10ms=rise(limit_A, cap, .010)),
                         delay_to_350V_ms=1000*(PA_ABS-TRIP_HI)*cap*1e-6/limit_A,
                         below_350V=dict(guard_0p5ms=rise(limit_A, cap, .0005) < PA_ABS,
                                         cutoff_2ms=rise(limit_A, cap, .002) < PA_ABS,
                                         late_10ms=rise(limit_A, cap, .010) < PA_ABS)))
    return rows


def passive_alternative():
    """Split resistor and larger reservoir, no guard. One capacitor open, rest -20 %."""
    rows = []
    for feed in (900, 1200, 1500):
        for fitted in (4, 6, 8, 12):
            c = (fitted-1)*CAP_NOM*(1-CAP_TOL)*1e-6
            r = feed*.95
            extra = (feed-900)*1.05*NORMAL_A
            rows.append(dict(feed_ohm=feed, caps_fitted=fitted, cap_one_open_uF=c*1e6,
                             peak_10ms_440V=closed_form(440, r, c, .010), peak_10ms_550V=closed_form(550, r, c, .010),
                             weld_surge_mA_440V=1000*440/r, weld_surge_mA_550V=1000*550/r,
                             extra_trough_needed_V=extra, leakage_mA=fitted*low_line_rail.LEAK_PER_CAP_mA,
                             stored_J_350V_max=.5*fitted*CAP_NOM*1.2e-6*350**2,
                             passes=bool(closed_form(550, r, c, .010) < PA_ABS and 550/r <= .4 and extra < .5)))
    return rows


def heat(lim_lo, lim_hi):
    """M1 heat. Arithmetic bounds, SI units. Feed and sense at minimum."""
    series_r = FEED_MIN+15*.99
    soa_W = 75.
    rows = []
    for name, raw, rail, i, seconds in [
            ('normal 22.72 mA', 445, None, NORMAL_A, None),
            ('guard limiting, rail held at 295 V window edge, raw 445 V mean', 445, 295, lim_hi, None),
            ('same at the low guard limit', 445, 295, lim_lo, None),
            ('rail short, bypass closed, 2 ms trip, 440 V', 440, 0, lim_hi, .002),
            ('rail short, 10 ms late trip, 550 V', 550, 0, lim_hi, .010),
            ('cold-start rail short to the 1 s timeout, bypass welded, 550 V', 550, 0, lim_hi, 1.),
            ('same, trip never comes', 550, 0, lim_hi, None)]:
        v = None if rail is None else raw-rail-i*series_r
        p = i*i*(6*2.3+.18+13.7) if rail is None else v*i
        rows.append(dict(case=name, raw_V=raw, current_mA=1000*i, M1_V=v, M1_W=p, duration_s=seconds,
                         M1_J=p*seconds if seconds else None, fraction_of_SOA_power=p/soa_W,
                         junction_rise_over_case_K=p*PARTS['M1']['RthJC_K_W']))
    cont = rows[1]['M1_W']
    sink = [dict(air_C=a, case_limit_C=100, power_W=cont, max_case_to_air_K_W=(100-a)/cont,
                 junction_C=100+cont*1.0) for a in (60, 70)]
    return dict(cases=rows, sink_requirement=sink,
                note='In the window-edge case the CB-009 pass device is in dropout. Heat moves from the pass '
                     'device to M1. The CB-009 overload bound for the pass device was 5.0 W.')
