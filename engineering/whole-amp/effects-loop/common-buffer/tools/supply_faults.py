"""CB-007. Piecewise RC fault simulations and thermal/sequence budgets, SI units."""
import json
from itertools import product
from math import exp, log
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]


def trip_corners():
    # 100 ppm/K reference plus initial error, loading and drift allocation.
    values = []
    for ref, top, bottom, offset, bias in product(
        [.991, 1.009], [.996, 1.004], [.996, 1.004], [-.004, .004], [-62.5e-9, 62.5e-9]):
        rt, rb = 328000 * top, 2490 * bottom
        values.append((2.5*ref+offset)*(1+rt/rb)+bias*rt)
    return min(values), max(values)


def pass_short(name, cap, delay, initial=310, precharge=False, armed=True, raw=440, dt=2e-6):
    # No downstream load gives the fastest rise. An upstream raw step and a
    # hard D-S short also bound loss of regulator feedback with the pass on.
    v, peak, t = initial, initial, 0.
    deadline = None
    max_current = 0.
    energy = 0.
    threshold = trip_corners()[1]
    bypass = not precharge
    while t < 4.:
        if not armed and t>=.8:
            break
        if raw-v < 140:
            bypass = True
        # Force the minimum series resistance in the running fast-rise test.
        r = .95 * (1820 + (0 if bypass else 8200))
        current = (raw-v)/r
        max_current=max(current, max_current)
        new_v = raw-(raw-v)*exp(-dt/(r*cap))
        if v < threshold <= new_v and deadline is None:
            deadline=t+r*cap*log((raw-v)/(raw-threshold))+delay
        if armed and deadline is not None and deadline <= t+dt:
            new_v=raw-(raw-v)*exp(-(deadline-t)/(r*cap))
            energy += cap*(new_v-v)*(raw-.5*(v+new_v))
            t=deadline
            peak=max(peak,new_v)
            break
        energy+=cap*(new_v-v)*(raw-.5*(v+new_v))
        t+=dt
        v=new_v
        peak=max(peak,v)
    return dict(case=name, raw_V=raw, cap_uF=cap*1e6, delay_ms=delay*1000, initial_V=initial,
                peak_V=peak, worst_feed_mA=max_current*1000, total_feed_J=energy,
                disconnected=armed and deadline is not None, final_time_ms=t*1000,
                below_absolute_max=peak<350)


def mute_race(name, lead_ms, welded=False):
    # Low-frequency bound: 160 V source step via 3.3k and series 1.1uF,
    # 500pF harness in parallel with 100k mixer surrogate. Use backward Euler
    # at 0.1us. Charge on the series capacitor cannot change at the source step.
    release=.003
    dt=1e-7
    cap, harness, rs, load=1.1e-6,500e-12,3300,100000
    qv=y=peak=0.
    for i in range(80001):
        t=i*dt
        source=160. if t>=lead_ms*.001 else 0.
        if t<release or welded:
            conductance=1/(rs+dt/cap)
            y=(harness/dt*y + conductance*(source-qv))/(harness/dt+1/load+conductance)
            qv+=dt/cap*conductance*(source-qv-y)
        else:
            y/=1+dt/(harness*load)
        peak=max(peak,abs(y))
    return dict(case=name,lead_ms=lead_ms,opening_ms=release*1000,welded=welded,
                mixer_peak_V=peak)


def thermal():
    budget=json.loads((MODULE/'results/apex-fault-budget.json').read_text())
    p=budget['hot_port_short']['trial_budget_W']
    full=budget['hot_full_sine']['trial_budget_W']
    rows=[]
    for name, r_sink, r_joint in [('catalog-only',2.6,1),('installed-target',4,1),
                                 ('blocked-fins',7,1),('loose-interface',4,4)]:
        rows.append(dict(case=name,sink_K_W=r_sink,joint_K_W=r_joint,
                         full_case_C=70+full*(r_sink+r_joint),
                         short_case_C=70+p*(r_sink+r_joint)))
    rows.append(dict(case='external-wall target',air_C=60,sink_K_W=4,joint_K_W=1,
                     full_case_C=60+5*full,short_case_C=60+5*p))
    return rows


def thermal_trip(sensor_tau, sensor_error, detached=False, air=70):
    # Two thermal masses. Capacities and coupling are fault-study assumptions.
    # The sensor is mounted at the package. Detached case senses the sink only.
    case=sink=sensor=float(air)
    p=2.844
    trip=None
    peak=case
    dt=.001
    for i in range(300000):
        t=i*dt
        if sensor+sensor_error>=79 and trip is None:
            trip=t
        heat=p if trip is None else p*exp(-(t-trip)/.20)
        flow=(case-sink)/4
        case+=dt*(heat-flow)/1
        sink+=dt*(flow-(sink-air)/7)/8
        sensor+=dt*((sink if detached else case)-sensor)/sensor_tau
        peak=max(peak,case)
    return dict(ambient_C=air,sensor_tau_s=sensor_tau,sensor_error_C=sensor_error,
                detached_to_sink=detached,trip_s=trip,peak_case_C=peak)


def rail_short():
    # Worst DC when the protected output capacitor itself shorts. Healthy pass
    # current limiter; common gate current can also flow through the clamp.
    limit=.85/(33*.95)
    rows=[]
    for name,r,time in [('cold start',.95*(1820+8200),1.0),
                        ('running bypass initially closed',.95*1820,.002)]:
        # Upper bound over current incl gate bypass: maximize MOS power at Vraw/2R.
        i=min(limit,440/(2*r))
        power=(440-i*r)*i
        rows.append(dict(case=name,pass_peak_bound_W=power,duration_s=time,
                         pass_energy_bound_J=power*time, feed_current_ceiling_A=min(440/r,limit+.0044),
                         resistor_bank_peak_W=min(440/r,limit+.0044)**2*r))
    return rows


if __name__=='__main__':
    lo,hi=trip_corners()
    scenarios=[('both caps at minimum',35.2e-6,.002),
               ('one reservoir open',17.6e-6,.002),
               ('late disconnect',17.6e-6,.010),
               ('reservoir lost; local bypass only',.1e-6,.002),
               ('cutoff welded and pass short',35.2e-6,.002,310,False,False),
               ('pass short before arm',52.8e-6,.002,0,True),
               ('pass short; precharge bypass welded before arm',52.8e-6,.002,0,False),
               ('550V raw diagnostic outside input allocation',17.6e-6,.002,310,False,True,550)]
    faults=[pass_short(*c) for c in scenarios]
    residual=pass_short('half step',17.6e-6,.002,dt=1e-6)
    exact=440-(440-hi)*exp(-.002/(.95*1820*17.6e-6))
    assert abs(faults[1]['peak_V']-exact)<1e-6 and abs(residual['peak_V']-exact)<1e-6
    assert [r['below_absolute_max'] for r in faults[:5]]==[True,True,False,False,False]
    # Startup is tested with the bypass physically open and the pass limiting.
    # Conservative idle-current budget includes both capacitor leakage allowances.
    startup=[]
    for raw,bypass_stuck in product([340,390,400,405,410,415,420,430,440],[False,True]):
        t=v=0.
        latched=False
        crossover=None
        dt=.0001
        while t<4:
            if not bypass_stuck and raw-v<140 and not latched:
                crossover=t
                latched=True
            r=1820+(30 if latched else 8200)+30
            # Low-end current limit; 5.5V pass overhead incl gate and sense.
            src=min(.014,max(0,(raw-v-5.5)/r))
            idle=.0025 + v*(1/360000+1/330490+1/308490+1/940000)+.001208
            v=min(310,max(0,v+dt*(src-idle)/52.8e-6))
            t+=dt
        startup.append(dict(raw_V=raw,bypass_forced_open=bypass_stuck,final_V=v,
                            bypass_closed_s=crossover,window_reached=v>=300))
    out=dict(ov_trip_V=[lo,hi],faults=faults,one_open_closed_form_V=exact,
             one_open_max_delay_to_350_ms=1000*.95*1820*17.6e-6*log((440-hi)/(440-350)),
             startup_envelope=startup,mute_race=[mute_race('simultaneous loss',0),
             mute_race('5ms advance warning',5),mute_race('welded NO',5,True)],
             thermal=thermal(), thermal_trip=[thermal_trip(1,-3),thermal_trip(8,-3),thermal_trip(8,-3,True),
                 thermal_trip(1,-3,air=60),thermal_trip(8,-3,air=60),thermal_trip(8,-3,True,air=60)],
             protected_rail_short=rail_short(), maximum_stored_J=.5*52.8e-6*350**2,
             bleed_only_to_60_s=360000*1.05*52.8e-6*log(350/60))
    (MODULE/'results/supply-faults.json').write_text(json.dumps(out,indent=2)+'\n')
