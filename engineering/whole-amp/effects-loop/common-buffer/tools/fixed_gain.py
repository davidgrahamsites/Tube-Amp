"""CB-010. One fixed effects-return network for both 20 kHz gain corners.

Simulation and arithmetic only. Reuses the CB-006, CB-008 and CB-009 factories unchanged.
Every change is a patch that lives only inside fixture(). No archived file is written.
Run with KiCad Python:  fixed_gain.py screen   (fast)   or   fixed_gain.py   (full).

Terms. Isolator: resistor from the PA340 output to the DC block. Fast shunt: the two
normally conducting MOSFETs and their series resistor at the mixer. Named corners:
hot = 500 pF harness, 600 pF shunt, 150 pF optical, 85 C, inductance -10 %;
opposite = 0 pF harness, 80 pF shunt, 30 pF optical, 25 C, inductance +10 %.
"""
import hashlib
import json
import re
import sys
from contextlib import ExitStack, contextmanager
from itertools import product
from pathlib import Path
from unittest.mock import patch

import numpy as np

import guard_audio
import guard_detector
import guard_handover
import guard_injection
import low_line_rail
import pulse_winding
import rail_winding_audio
import sudden_guard
from sudden_guard import MODULE, sp

OLD = dict(name='CB-009', isolation=3300, series=6.8, start=220, mid=330, end=270, feedback=39700)
# Same MSS1210H coils in every candidate. Only resistors and the entry capacitor change.
CANDIDATES = [dict(name="A", isolation=3000, series=4.7, start=220, mid=330, end=270),
              dict(name="A2", isolation=3000, series=4.7, start=330, mid=330, end=270),
              dict(name="A3", isolation=3000, series=4.7, start=270, mid=330, end=270),
              dict(name='B', isolation=2870, series=3.9, start=270, mid=330, end=270),
              dict(name='C', isolation=2700, series=3.3, start=470, mid=330, end=270)]
# CB-008 used 10 ohm nominal and 18 ohm hot for the fast shunt, including its 6.8 ohm resistor.
PATH_NOMINAL, PATH_HOT = 10 - 6.8, 18 - 6.8
HOT = (20000, 500, 600, 150, False, 85, 310, False, .9)
OPPOSITE = (20000, 0, 80, 30, False, 25, 310, False, 1.1)
SHORT = (20000, 500, 220, 30, True, 85, 320)
LIMIT = dict(gain_dB=.5, thd_pct=1, quiet_V=1, handover_V=1, injection_V=.7, coil_V=400,
             case_C=76, air_C=60, reserve_W=.8, case_to_air_K_W=5)
STATE = dict(net=OLD, cap_scale=1, ac_only=False, ac=None)
E192 = [round(10 ** (i / 192), 2) for i in range(192)]  # 0.1 % resistor series


def nearest_e192(value):
    decade = 10 ** np.floor(np.log10(value))
    return float(min(E192 + [10], key=lambda x: abs(x * decade - value)) * decade)


def shunt_ohm(hot):
    return (PATH_HOT if hot else PATH_NOMINAL) + STATE['net']['series']


# ---- patches around the original factories -------------------------------------------
def delay_line(start, end, scale=1, winding_pF=18, shunt_pF=220, mid_pF=None, end_pF=None, start_pF=None):
    n, k = STATE['net'], STATE['cap_scale']
    return pulse_winding.delay_line(start, end, scale, winding_pF, shunt_pF,
                                    mid_pF or n['mid'] * k, end_pF or n['end'] * k, start_pF or n['start'] * k)


_load, _deck, _fault = sp.load, guard_audio.deck, sudden_guard.fault


def load(text):
    n = STATE['net']
    if 'CENTRY8' not in text:  # detector deck has no windings; drop the stale probe list
        pulse_winding.STATE['probe'] = None
    if 'RISO src ' in text:
        text, count = re.subn(r'^(RISO src (?:cap8|coupling)) 3135(?:\.0)?$',
                              lambda m: f'{m.group(1)} {n["isolation"] * .95}', text, flags=re.M)
        assert count == 1
    text = text.replace('.model fast sw(ron=18 ', f'.model fast sw(ron={shunt_ohm(True)} ')
    text = text.replace('RSH retour 0 6.8', f'RSH retour 0 {n["series"]}')
    _load(text)


def deck(f, target, pf, rail, isolation, *rest):
    assert isolation == 3300
    return _deck(f, target, pf, rail, STATE['net']['isolation'], *rest)


def linked_fault(label, **kw):
    """guard_detector passes the CB-008 hot shunt value. Substitute the candidate value."""
    assert kw.pop('shunt_ohm') == 18
    return _fault(label, shunt_ohm=shunt_ohm(True), **kw)


class AcOnly(Exception):
    pass


def cmd(text):
    if text.startswith('ac '):
        pulse_winding.cmd(text)
        STATE['ac'] = [np.asarray(sp.vector(n)) for n in ('frequency', 'v(fx_return)', 'v(preout)')]
        return
    if STATE['ac_only'] and text.startswith('tran '):
        raise AcOnly
    pulse_winding.cmd(text)


def low_line(raw, ctr, threshold, original_cap, bypass, original_leak):
    cfg = low_line_rail.CAND
    cap = (cfg['caps'] - 1) * low_line_rail.CAP_NOM * (1 - low_line_rail.CAP_TOL)
    return low_line_rail.variant(raw, ctr, threshold, cap, bypass, None, **cfg)


@contextmanager
def fixture():
    with ExitStack() as stack:
        stack.enter_context(pulse_winding.instrument())
        for module in (sudden_guard, guard_handover, guard_audio, guard_injection):
            stack.enter_context(patch.object(module, 'delay_line', delay_line))
        stack.enter_context(patch.object(sp, 'cmd', cmd))
        stack.enter_context(patch.object(sp, 'load', load))
        stack.enter_context(patch.object(guard_audio, 'deck', deck))
        stack.enter_context(patch.object(guard_audio, 'regulator', low_line))
        stack.enter_context(patch.object(guard_detector, 'fault', linked_fault))
        pulse_winding.STATE.update(spec=rail_winding_audio.SPEC, corner={})
        yield


# ---- analytic screen of the passive network ------------------------------------------
def line(freq, net, harness, shunt, optical, lscale, cscale, hot, feedback_T=0):
    """Complex mixer/PA-output ratio. Mixer load 2.84 uS and 15 pF from the full-deck AC probe."""
    w = 2j * np.pi * np.asarray(freq, float)
    coils = rail_winding_audio.SPEC['coils']
    copper = 1.236 if hot else 1
    y = 2.84e-6 + w * (net['end'] * cscale + shunt + harness + 15) * 1e-12 + 1 / (4.7 + 1 / (w * optical * 1e-12))
    ratio = 1
    for coil, cap in ((coils[1], net['mid']), (coils[0], net['start'])):
        z = 1 / (1 / (coil['dcr'] * copper + w * coil['L'] * lscale) + w * coil['cw_pF'] * 1e-12)
        ratio = ratio / (1 + z * y)
        y = w * cap * cscale * 1e-12 + 1 / (z + 1 / y)
    zin = 30 + 1 / y
    yport = 2e-6 + 1 / (1e4 + 1 / (w * optical * 1e-12)) + 1 / zin
    port = 1 / (1 + (net['isolation'] + 1 / (w * 1.1e-6)) * yport)
    h = port * (1 / y) / zin * ratio
    if feedback_T:  # resistive feedback from the mixer to the first stage, normalized at 1 kHz
        hn = h / h[0]
        h = h[0] * hn * (1 + feedback_T) / (1 + feedback_T * hn)
    return h, port


STACK = [(h, s, o, ls, cs, hot) for h in (0, 500) for s in (80, 220, 600) for o in (30, 150)
         for ls in (.9, 1, 1.1) for cs in (.95, 1.05) for hot in (0, 1)]
BAND = np.array([1000., 5000, 10000, 14000, 17000, 20000])


def analytic(net, feedback_T=0):
    def rel(corner):
        h = line(BAND, net, *corner, feedback_T=feedback_T)[0]
        return 20 * np.log10(abs(h / h[0]))
    named = [rel((500, 600, 150, .9, 1, 1))[-1], rel((0, 80, 30, 1.1, 1, 0))[-1]]
    stack = np.array([rel(c) for c in STACK])[:, 1:]
    return dict(named_20k_rel_1k_dB=named, named_half_spread_dB=abs(named[1] - named[0]) / 2,
                stack_144_band_rel_1k_dB=[stack.min(), stack.max()], stack_half_spread_dB=(stack.max() - stack.min()) / 2)


def rejected_alternatives():
    """Two feedback ideas, screened on the unchanged CB-009 passive network."""
    sweep = np.logspace(3, 6.3, 3000)
    mixer = []
    for T in (.3, .5, 1.):
        margin, peak = np.inf, 0
        for corner in STACK:
            hn = line(sweep, OLD, *corner)[0]
            hn = hn / hn[0]
            phase = np.unwrap(np.angle(hn))
            for k in range(-3, 1):  # every crossing of -180 degrees modulo 360
                for i in np.flatnonzero(np.diff(np.sign(phase - (2 * k + 1) * np.pi))):
                    margin = min(margin, 1 / (T * abs(hn[i])))
            peak = max(peak, max(20 * np.log10(abs(hn * (1 + T) / (1 + T * hn)))))
        mixer.append(dict(mixer_feedback_fraction_T=T, **analytic(OLD, T), min_gain_margin_ratio=margin,
                          worst_closed_loop_peak_dB=peak))
    # Feedback fraction k taken after the isolator gives an effective isolator of R(1-k).
    # The PA output must then rise by 1/|1-k+k*port/output| at the hot corner.
    h, port = line([20000.], OLD, 500, 600, 150, .9, 1, 1)
    post = []
    for target in (3000, 2700):
        k = 1 - target / OLD['isolation']
        post.append(dict(effective_isolation_ohm=target, fraction_k=k,
                         PA_peak_V_for_135V_mixer=135 / abs(h[0]) / abs(1 - k + k * port[0]),
                         PA_peak_V_same_resistance_passive=135 / abs(line([20000.], dict(OLD, isolation=target), 500, 600, 150, .9, 1, 1)[0][0])))
    return dict(mixer_feedback=mixer, post_isolator_feedback=post, half_rail_V=155)


# ---- ngspice runs ----------------------------------------------------------------------
def audio(args, raw=None, cap_scale=1, feedback=None, ac_only=False):
    defaults = [False, 25, 310, False, 1]
    f, harness, shunt, optical, short, temp, rail, nonlinear, lscale = list(args) + defaults[len(args) - 4:]
    STATE.update(cap_scale=cap_scale, ac_only=ac_only)
    pulse_winding.STATE.update(corner={'r_scale': 1 + .00393 * (temp - 25)})
    feedback = feedback or STATE['net']['feedback']
    try:
        row = guard_audio.audio(f, harness, shunt, optical, short, temp, rail, nonlinear, lscale, raw, feedback)
        row['windings'] = pulse_winding.STATE['seen']
    except AcOnly:
        pulse_winding._cmd('destroy all')
        row = dict(frequency_Hz=f, harness_pF=harness, fast_shunt_pF=shunt, open_optical_pF=optical, temp_C=temp,
                   inductance_scale=lscale, feedback_ohm=feedback)
    finally:
        STATE.update(cap_scale=1, ac_only=False)
        pulse_winding.STATE.update(corner={})
    freq, port, pre = STATE['ac']
    freq = np.real(freq)
    gain = 20 * np.log10(abs(port) / 100)
    band = (freq >= 20) & (freq <= 20001)
    top = int(np.argmax(gain))
    row.update(local_cap_scale=cap_scale, small_signal=dict(
        gain_dB={str(p): float(np.interp(np.log(p), np.log(freq), gain)) for p in (20, 1000, 10000, 20000)},
        band_min_max_dB=[min(gain[band]), max(gain[band])], peak_dB=gain[top], peak_Hz=freq[top],
        PA_output_peak_dB=max(20 * np.log10(abs(pre) / 100))))
    return row


def faults(full):
    hot, nom = shunt_ohm(True), shunt_ohm(False)
    n = STATE['net']
    low = dict(end_pF=n['end'] * .95, mid_pF=n['mid'] * .95, start_pF=n['start'] * .95)
    corner = dict(rise_us=.05, wire_pF=0, scale=.9, winding_pF=30)
    quiet = [dict(label='nominal', shunt_ohm=nom), dict(label='negative', sign=-1, shunt_ohm=nom),
             dict(label='hot shunt', shunt_ohm=hot),
             dict(label='short harness fast edge', shunt_pF=80, shunt_ohm=nom, **corner),
             dict(label='combined quiet corner', shunt_pF=50, shunt_ohm=hot, fine=True, **corner, **low)]
    playing = [dict(label='playing', sign=s, live_phase=p, shunt_ohm=nom) for s in (-1, 1) for p in (0, 90, 180, 270)]
    with_coils = pulse_winding.with_coils
    fast = [with_coils(sudden_guard.fault(**c)) for c in quiet + (playing if full else [])]
    cases = [{}, dict(sign=-1), dict(stuck=True), dict(open_guard=True)] if full else [{}]
    hand = [with_coils(guard_handover.run(**c)) for c in cases]
    if full:  # unequal winding capacitance, opposite inductance errors, hot copper
        for ca, cb, la in product((.65, 1.5), (.65, 1.5), (.9, 1.1)):
            pulse_winding.STATE.update(corner=dict(c_scales=[ca, cb], l_mismatch=[la, 2 - la], r_scale=1.236))
            hand.append(dict(with_coils(guard_handover.run()), sensitivity=dict(pulse_winding.STATE['corner'])))
        pulse_winding.STATE.update(corner={})
    scales = (1, 2, 4) if full else (1, 4)
    injection = [guard_injection.run(step, m, 6.2, cscale=k) for step in (-160, 0, 160) for m in (.5, 2) for k in scales]
    summary = dict(fast_path_ohm=dict(nominal=nom, hot=hot),
                   static_divider_V=160 * hot / (n['isolation'] * .95 + 30 + 10.5 + hot),
                   quiet_mixer_V=max(r['peak_mixer_V'] for r in fast if r['phase_deg'] is None),
                   handover_V=max(r['peak_V'] for r in hand if not r['fast_open']),
                   injection_V=max(r['peak_V'] for r in injection),
                   peak_by_coil_V=[max(r['windings'][i]['peak_V'] for r in fast + hand) for i in (0, 1)],
                   peak_by_coil_A=[max(r['windings'][i]['peak_A'] for r in fast + hand) for i in (0, 1)],
                   optical_contact_peak_V=max(r['optical_contact_peak_V'] for r in hand))
    if full:
        summary.update(playing_after_switch_V=max(r['post_switch_peak_V'] for r in fast if r['phase_deg'] is not None),
                       playing_peak_shunt_A=max(r['peak_shunt_A'] for r in fast if r['phase_deg'] is not None),
                       open_fast_shunt_V=max(r['peak_V'] for r in hand if r['fast_open']))
    return dict(summary=summary, fast=fast, handover=hand, injection=injection)


def slew_matrix():
    """CB-008 rail-loss and output-edge matrix with early pin detectors, relinked to this network."""
    rows = [guard_detector.measure(rail, edge, pin, sign, droop=True)
            for rail, pin, sign, edge in product(('hv', 'pos', 'neg', 'five', 'twelve', 'all'), (.5, 4, 40), (-1, 1),
                                                 (.05, .14, .4, 1, 2, 3, 4, 5, 6, 8, 12, 20, 40))]
    worst = max(rows, key=lambda r: r['mixer_peak_V'])
    return dict(cases=len(rows), max_mixer_V=worst['mixer_peak_V'],
                worst={k: worst[k] for k in ('lost_pin', 'output_sign', 'edge_us', 'pin_fall_us', 'closed_us')})


def short_heat(row):
    watts = row['chip_W']
    return dict(modeled_chip_W=watts, budget_W=watts + LIMIT['reserve_W'],
                case_C=LIMIT['air_C'] + (watts + LIMIT['reserve_W']) * LIMIT['case_to_air_K_W'])


def screen(net):
    """Fast checks for one candidate. Selects its single feedback resistor from the AC corners."""
    STATE['net'] = net
    ac = [audio(c, feedback=39700, ac_only=True)['small_signal']['gain_dB']['20000'] for c in (HOT, OPPOSITE)]
    # Large-signal 20 kHz gain read about 0.035 dB below small-signal in CB-008/009.
    stage = (1 + 39700 / 10000) * 10 ** ((.035 - sum(ac) / 2) / 20)
    net['feedback'] = nearest_e192(10000 * (stage - 1))
    shift = 20 * np.log10((1 + net['feedback'] / 10000) / (1 + 39700 / 10000))
    fault = faults(False)['summary']
    heat = short_heat(audio(SHORT))
    ok = dict(named_corners=max(abs(g + shift) for g in ac) < LIMIT['gain_dB'], quiet=fault['quiet_mixer_V'] < LIMIT['quiet_V'],
              handover=fault['handover_V'] < LIMIT['handover_V'], injection=fault['injection_V'] < LIMIT['injection_V'],
              coils=max(fault['peak_by_coil_V']) < LIMIT['coil_V'], short_heat=heat['case_C'] < LIMIT['case_C'])
    return dict(network=dict(net), analytic=analytic(net), ac_20k_hot_opposite_at_39k7_dB=ac,
                ac_20k_hot_opposite_dB=[g + shift for g in ac], ac_half_spread_dB=abs(ac[1] - ac[0]) / 2,
                fault_screen=fault, hot_short=heat, old_limits_met=ok)


def verify(net):
    STATE['net'] = net
    heavy, light = (500, 600, 150), (0, 80, 30)
    cases = [('hot named corner', HOT, {}), ('opposite named corner', OPPOSITE, {}),
             ('nominal 20 kHz', (20000, 500, 220, 30), {}), ('nominal 1 kHz', (1000, 500, 220, 30), {}),
             ('nominal 20 Hz', (20, 500, 220, 30), {}),
             ('heavy load, 25 C, inductance +10 %', (20000, *heavy, False, 25, 310, False, 1.1), {}),
             ('light load, 85 C, inductance -10 %', (20000, *light, False, 85, 310, False, .9), {}),
             ('hot corner, local capacitors +5 %', HOT, dict(cap_scale=1.05)),
             ('opposite corner, local capacitors -5 %', OPPOSITE, dict(cap_scale=.95)),
             ('heavy load, 25 C, inductance +10 %, capacitors -5 %', (20000, *heavy, False, 25, 310, False, 1.1), dict(cap_scale=.95)),
             ('charge-dependent shunt 1300 pF, 25 C', (20000, 500, 1300, 150, False, 25, 310, True), {}),
             ('charge-dependent shunt 2600 pF, 85 C', (20000, 500, 2600, 150, False, 85, 310, True), {}),
             ('charge-dependent shunt 1300 pF, short harness', (20000, 0, 1300, 30, False, 25, 310, True, 1.1), {}),
             ('hot mixer short, 320 V', SHORT, {}),
             ('hot named corner, 340 V raw, CB-009 rail', HOT, dict(raw=340)),
             ('opposite named corner, 340 V raw, CB-009 rail', OPPOSITE, dict(raw=340))]
    rows = []
    for label, args, extra in cases:
        row = dict(case=label, **audio(args, **extra))
        rows.append(row)
        print(label, round(row['gain_dB'], 3), round(row['thd_pct'], 3), flush=True)
    return rows


def main(full):
    files = [Path(__file__)] + [Path(m.__file__) for m in (guard_audio, guard_detector, guard_handover, guard_injection,
                                                             low_line_rail, pulse_winding, rail_winding_audio, sudden_guard)]
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    report = dict(id='CB-010', date='2026-11-28', evidence='ngspice and arithmetic only', sources=before, limits_used=LIMIT,
                  windings=rail_winding_audio.SPEC, rejected_alternatives=rejected_alternatives())
    with fixture():
        report['baseline'] = screen(dict(OLD))
        report['candidates'] = [screen(dict(c)) for c in CANDIDATES]
        for row in [report['baseline']] + report['candidates']:
            print(row['network'], [round(x, 3) for x in row['ac_20k_hot_opposite_dB']],
                  round(row['analytic']['stack_half_spread_dB'], 3), round(row['fault_screen']['quiet_mixer_V'], 3),
                  round(row['fault_screen']['injection_V'], 3), round(row['hot_short']['case_C'], 2), row['old_limits_met'], flush=True)
        passing = [c for c in report['candidates'] if all(c['old_limits_met'].values())]
        report['selected'] = min(passing, key=lambda c: c['ac_half_spread_dB'])['network'] if passing else None
        if full and passing:
            net = report['selected']
            rows = verify(net)
            fault = faults(True)
            slew = slew_matrix()
            named = rows[:2]
            normal = [r for r in rows if not r['short']]
            s = fault['summary']
            report.update(audio=rows, faults=fault, rail_loss_matrix=slew)
            report["checks"] = {k: bool(v) for k, v in dict(
                named_20k_full_load_within_0p5_dB=all(abs(r['gain_dB']) < LIMIT['gain_dB'] for r in named),
                named_band_20Hz_20kHz_within_0p5_dB=all(max(map(abs, r['small_signal']['band_min_max_dB'])) < LIMIT['gain_dB'] for r in named),
                low_line_rail_named_within_0p5_dB=all(abs(r['gain_dB']) < LIMIT['gain_dB'] for r in rows if r['raw_input_V']),
                every_full_load_case_within_0p5_dB=all(abs(r['gain_dB']) < LIMIT['gain_dB'] for r in normal),
                every_small_signal_band_within_0p5_dB=all(max(map(abs, r['small_signal']['band_min_max_dB'])) < LIMIT['gain_dB'] for r in normal),
                thd_below_1_pct=all(r['thd_pct'] < LIMIT['thd_pct'] for r in normal),
                quiet_below_1_V=s['quiet_mixer_V'] < LIMIT['quiet_V'], playing_after_switch_below_1_V=s['playing_after_switch_V'] < 1,
                handover_below_1_V=s['handover_V'] < LIMIT['handover_V'], injection_below_0p7_V=s['injection_V'] < LIMIT['injection_V'],
                windings_below_400_V=max(s['peak_by_coil_V']) < LIMIT['coil_V'],
                rail_loss_matrix_below_1_V=slew['max_mixer_V'] < 1,
                PA_rail_mean_below_16p5_mA=max(r["mean_PA_rail_mA"] for r in normal) < 16.5,
                hot_short_case_below_76_C=short_heat(next(r for r in rows if r['short']))['case_C'] < LIMIT['case_C']).items()}
            print(report['checks'], s, slew, flush=True)
    assert before == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    if full:
        (MODULE / 'results/fixed-gain.json').write_text(json.dumps(report, indent=1, default=float) + '\n')
    return report


if __name__ == '__main__':
    main(sys.argv[1:] != ['screen'])
