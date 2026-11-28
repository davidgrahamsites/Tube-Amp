"""CB-009. Isolated pass-short and precharge fault fixtures."""
from math import exp, log

import numpy as np
import supply_faults
from supply_trial import sp

TRIP_LO, TRIP_HI = supply_faults.trip_corners()
CAP_NOM, CAP_TOL = 22.0, .20
PRECHARGE = 8200
AQV = dict(abs_V=600, recommended_V=480, continuous_25C_A=.130, continuous_70C_A=.085,
           continuous_85C_A=.070, peak_100ms_single_A=.400, ron_max_25C=30, ron_hot_assumed=45)


def closed_form(raw, r, c, delay, start=TRIP_HI):
    return raw-(raw-start)*exp(-delay/(r*c))


def cutoff_spice(raw, r, c, delay, initial=310.):
    """Shorted pass. Two passes: find the threshold crossing, then open after the delay."""
    def run(t_open, end):
        deck = f'''CB009 shorted pass cutoff
VRAW raw 0 {raw}
RF raw a {r}
S1 a rail ctl 0 sw9
.model sw9 SW(vt=.5 vh=0 ron=1m roff=10g)
VCTL ctl 0 PWL(0 1 {t_open} 1 {t_open+1e-6} 0)
C1 rail 0 {c} ic={initial}
.ic v(rail)={initial}
.end'''
        sp.load(deck)
        sp.cmd(f'tran 2u {end} 0 2u uic')
        t, v = np.array(sp.vector('time')), np.array(sp.vector('v(rail)'))
        sp.cmd('destroy all')
        return t, v
    tau = r*c
    guess = tau*log((raw-initial)/(raw-TRIP_HI))
    t, v = run(1., guess*1.2)
    cross = float(np.interp(TRIP_HI, v, t))
    t, v = run(cross+delay, cross+delay+.004)
    return dict(threshold_cross_ms=1000*cross, peak_V=float(max(v)))


def pass_short(label, feed, caps_fitted, delay=.002, raw=440, cap_factor=1-CAP_TOL, spice=True,
               feed_tol=.05):
    """Fastest rise: minimum fixed resistance, zero switch resistance and no load."""
    r, c = feed*(1-feed_tol), caps_fitted*CAP_NOM*cap_factor*1e-6
    tau = r*c
    peak = closed_form(raw, r, c, delay)
    i_start, i_break = (raw-310)/r, (raw-peak)/r
    t_rise = tau*log((raw-310)/(raw-TRIP_HI))
    # Energy in each 30 ohm maximum switch while carrying the fault. I(t) is exponential.
    i2t = (i_start**2)*tau/2*(1-exp(-2*(t_rise+delay)/tau))
    row = dict(case=label, feed_nominal_ohm=feed, feed_min_ohm=r, raw_V=raw, caps_fitted=caps_fitted,
               cap_uF=c*1e6, delay_ms=delay*1000, trip_V=TRIP_HI, peak_V=peak,
               margin_to_350_V=350-peak, below_PA340_350V=peak < 350,
               max_delay_to_350_ms=1000*tau*log((raw-TRIP_HI)/(raw-350)) if raw > 350 else None,
               min_cap_for_350_uF=1e6*delay/(r*log((raw-TRIP_HI)/(raw-350))),
               onset_to_trip_ms=1000*t_rise, switch_start_mA=1000*i_start, switch_break_mA=1000*i_break,
               open_switch_first_V=raw-peak, open_switch_final_V=raw,
               switch_joule_at_30ohm=i2t*AQV['ron_max_25C'],
               within_peak_single_shot=i_start <= AQV['peak_100ms_single_A'],
               above_25C_continuous=i_start > AQV['continuous_25C_A'],
               above_70C_continuous=i_start > AQV['continuous_70C_A'],
               within_recommended_switch_V=raw <= AQV['recommended_V'],
               within_absolute_switch_V=raw <= AQV['abs_V'])
    if spice:
        s = cutoff_spice(raw, r, c, delay)
        row.update(ngspice_peak_V=s['peak_V'], ngspice_cross_ms=s['threshold_cross_ms'],
                   ngspice_minus_closed_form_V=s['peak_V']-peak)
    return row


def prearm(label, feed, caps_fitted, bypass_welded, raw=440, delay=.002, dt=5e-6):
    """Pass already shorted at arm, reservoirs at +20%. Follows the CB-007 stepping model."""
    c = caps_fitted*CAP_NOM*(1+CAP_TOL)*1e-6
    v = t = energy_fixed = energy_pre = i2t = 0.
    peak_i = peak_bypass_i = 0.
    bypass, deadline = bypass_welded, None
    while t < 8:
        if raw-v < 140 and not bypass:
            bypass = True
            peak_bypass_i = (raw-v)/(.95*feed)
        r_fixed = .95*feed
        r = r_fixed+(0 if bypass else .95*PRECHARGE)
        i = (raw-v)/r
        peak_i = max(peak_i, i)
        if deadline is None and v >= TRIP_HI:
            deadline = t+delay
        if deadline is not None and t >= deadline:
            break
        v += dt*i/c
        energy_fixed += i*i*r_fixed*dt
        energy_pre += i*i*(r-r_fixed)*dt
        i2t += i*i*dt
        t += dt
    return dict(case=label, feed_nominal_ohm=feed, raw_V=raw, cap_uF=c*1e6, bypass_welded=bypass_welded,
                peak_V=v, opened_ms=1000*t, peak_series_switch_mA=1000*peak_i,
                bypass_switch_closing_mA=1000*peak_bypass_i,
                fixed_feed_J=energy_fixed, precharge_string_J=energy_pre,
                series_switch_J_at_30ohm=i2t*AQV['ron_max_25C'],
                within_peak_single_shot=peak_i <= AQV['peak_100ms_single_A'],
                below_PA340_350V=v < 350)
