"""Piecewise-linear RC bounds and base-drive checks for an unadopted rail inhibit.

Uses explicit allocations, not a transistor/comparator/relay vendor simulation.
Generated outputs never modify native CAD.
"""
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
CONTRACT = BASE / 'rail-delay-contract.json'
sys.path.insert(0, str(BASE.parent/'tools'))
from native_sexpr import parse, children


def native_binding(c):
    """Read-only source/schematic/board guard for the unadopted gate resistor."""
    binding = c['native_binding']
    paths = {k: BASE/binding[k] for k in ['circuit', 'schematic', 'board']}
    source = [x for x in json.loads(paths['circuit'].read_text())['components'] if x['reference']==binding['reference']]
    assert len(source)==1 and source[0]['pins']==binding['expected_pin_nets']
    values = {'circuit':source[0]['value']}
    for kind, element in [('schematic', 'symbol'), ('board', 'footprint')]:
        matches=[]
        for node in children(parse(paths[kind].read_text()), element):
            props={p[1].strip('"'):p[2].strip('"') for p in children(node,'property')}
            if props.get('Reference')==binding['reference']:
                matches.append(props['Value'])
        assert len(matches)==1, (kind, matches)
        values[kind]=matches[0]
    assert all(x==binding['expected_current_value'] for x in values.values()), values
    return dict(reference=binding['reference'],native_values=values,candidate_value=binding['candidate_value'],native_change_pending=True,
                file_hashes={binding[k]:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in paths.items()})


def equilibrium(v5, charge, discharge, leakage, saturation, fault):
    conductance = 1 / charge + (1 / discharge if fault else 0)
    return (v5 / charge + (saturation / discharge if fault else 0) - leakage) / conductance, 1 / conductance


def advance(initial, final, resistance, cap, duration):
    return final + (initial - final) * math.exp(-duration / (resistance * cap))


def crossing(initial, final, resistance, cap, target):
    if target == initial:
        return 0.0
    if not min(initial, final) < target < max(initial, final):
        return None
    return -resistance * cap * math.log((target-final)/(initial-final))


def integrate_crossing(case, fault, duration, steps=4096):
    """Independent RK4 charge integration from branch currents; linear event interpolation.

    Does not call equilibrium/advance/crossing. The analytic result only selects
    a sufficiently long integration window, not the numerical crossing time.
    """
    v = case['healthy_delay_V'] if fault else case['fault_delay_V']
    target = case['fall_V'] if fault else case['rise_V']
    dt = duration / steps

    def slope(voltage):
        current = (case['v5']-voltage)/case['charge_ohm']-case['leakage_A']
        if fault:
            current -= (voltage-case['saturation_V'])/case['discharge_ohm']
        return current / case['cap_F']

    for i in range(steps):
        k1 = slope(v)
        k2 = slope(v+dt*k1/2)
        k3 = slope(v+dt*k2/2)
        k4 = slope(v+dt*k3)
        after = v+dt*(k1+2*k2+2*k3+k4)/6
        if min(v, after) <= target <= max(v, after):
            return dt*(i+(target-v)/(after-v))
        v = after
    return None


def main():
    c = json.loads(CONTRACT.read_text())
    native = native_binding(c)
    tol = c['resistor_fraction']
    endpoints = lambda v: [v*(1-tol), v*(1+tol)]
    cap_values = [c['capacitor_F']*(1+d*c['capacitor_total_fraction_allocation']) for d in [-1,1]]
    cases = []
    pulse_results = {str(t): {'timer_inhibit_asserted':0,'timer_not_asserted':0,'hold_below50ms':0,'minimum_recovery_hold_s':None,'minimum_voltage_V':None,'maximum_voltage_V':None} for t in c['short_fault_duration_s']}
    for v5, charge, discharge, cap, leakage, saturation in itertools.product(c['supply_V'], endpoints(c['charge_resistor_ohm']), endpoints(c['discharge_resistor_ohm']), cap_values, c['net_delay_leakage_A'], c['saturation_allocation_V']):
        healthy, healthy_r = equilibrium(v5,charge,discharge,leakage,saturation,False)
        fault, fault_r = equilibrium(v5,charge,discharge,leakage,saturation,True)
        for rise, fall in itertools.product(c['threshold_rise_V'], c['threshold_fall_V']):
            if fall >= rise:
                continue  # Impossible Schmitt hysteresis pair; independent enclosing extrema remain covered.
            case = dict(v5=v5,charge_ohm=charge,discharge_ohm=discharge,cap_F=cap,leakage_A=leakage,saturation_V=saturation,rise_V=rise,fall_V=fall,healthy_delay_V=healthy,fault_delay_V=fault,release_s=crossing(fault,healthy,healthy_r,cap,rise),discharge_s=crossing(healthy,fault,fault_r,cap,fall))
            cases.append(case)
            for duration in c['short_fault_duration_s']:
                after = advance(healthy,fault,fault_r,cap,duration)
                row = pulse_results[str(duration)]
                asserted = after <= fall
                row['timer_inhibit_asserted' if asserted else 'timer_not_asserted'] += 1
                hold = crossing(after,healthy,healthy_r,cap,rise) if asserted else 0
                if hold is None:
                    raise ValueError('recovery threshold unreachable')
                row['hold_below50ms'] += int(hold < c['screens']['release_min_s'])
                row['minimum_recovery_hold_s'] = hold if row['minimum_recovery_hold_s'] is None else min(hold,row['minimum_recovery_hold_s'])
                row['minimum_voltage_V'] = after if row['minimum_voltage_V'] is None else min(after,row['minimum_voltage_V'])
                row['maximum_voltage_V'] = after if row['maximum_voltage_V'] is None else max(after,row['maximum_voltage_V'])

    complete = all(x['release_s'] is not None and x['discharge_s'] is not None for x in cases)
    releases = [x['release_s'] for x in cases if x['release_s'] is not None]
    discharges = [x['discharge_s'] for x in cases if x['discharge_s'] is not None]
    numeric = []
    for index, case in enumerate(cases):
        for fault, key in [(False, 'release_s'), (True, 'discharge_s')]:
            expected = case[key]
            observed = integrate_crossing(case, fault, expected*1.25) if expected is not None else None
            numeric.append(dict(corner=index, phase=key, analytic_s=expected,
                                numerical_s=observed, relative_error=None if observed is None else abs(observed-expected)/expected))
    numeric_max = max(x['relative_error'] for x in numeric if x['relative_error'] is not None)
    voh, vbe = c['hc14_voh_min_V'], c['base_emitter_max_allocation_V']
    base_dis_min = (voh-vbe)/(c['qdis_base_ohm']*(1+tol))-vbe/(c['base_pulldown_ohm']*(1-tol))
    base_inhibit_min = (voh-vbe)/(c['qinhibit_input_ohm']*(1+tol))-vbe/(c['qinhibit_input_ohm']*(1-tol))-vbe/(c['base_pulldown_ohm']*(1-tol))
    collector_dis_max = max(x['healthy_delay_V'] for x in cases)/(c['discharge_resistor_ohm']*(1-tol))
    collector_inhibit_max = max(c['supply_V'])/(c['gate_series_ohm']*(1-tol))
    hc14_load_at_min_voh = (voh-c['base_emitter_min_allocation_V'])*(1/(c['qdis_base_ohm']*(1-tol))+1/(c['qinhibit_input_ohm']*(1-tol)))
    truth = []
    for fault, ready, rev in itertools.product([False,True],repeat=3):
        truth.append(dict(fault=fault,timer_ready=ready,rev_q=rev,driver_enable=rev and not(fault or not ready)))
    checks = [
        dict(name='independent current integration agrees within1ppm',passed=all(x['relative_error'] is not None and x['relative_error']<1e-6 for x in numeric)),
        dict(name='all allocated corners cross both thresholds',passed=complete),
        dict(name='release at least50ms',passed=complete and min(releases)>=c['screens']['release_min_s']),
        dict(name='release at most1s',passed=complete and max(releases)<=c['screens']['release_max_s']),
        dict(name='timer discharges below falling threshold within2ms',passed=complete and max(discharges)<=c['screens']['timer_discharge_max_s']),
        dict(name='QDIS forced beta within allocation',passed=base_dis_min>0 and collector_dis_max/base_dis_min<=c['screens']['forced_beta_max']),
        dict(name='QINHIBIT one-high-one-low base OR within allocation',passed=base_inhibit_min>0 and collector_inhibit_max/base_inhibit_min<=c['screens']['forced_beta_max']),
        dict(name='U1E load line supports4mA VOH test',passed=hc14_load_at_min_voh<=.004),
        dict(name='both logic lows below allocated turn-on voltage',passed=c['hc14_vol_max_V']<c['base_emitter_min_allocation_V']),
        dict(name='fault and user-OFF retain command priority',passed=all(not x['driver_enable'] for x in truth if x['fault'] or not x['rev_q'])),
    ]
    report = dict(scope='Conditional RC/base-drive analysis, not full-circuit or quiet-audio qualification.',qualified=False,corners=len(cases),checks=checks,passed=sum(x['passed'] for x in checks),total=len(checks),release_range_s=[min(releases),max(releases)],timer_discharge_range_s=[min(discharges),max(discharges)],short_faults=pulse_results,every_short_fault_gets50ms_hold=all(x['hold_below50ms']==0 for x in pulse_results.values()),worst_release_case=max(cases,key=lambda x:x['release_s'] or -1),fastest_release_case=min(cases,key=lambda x:x['release_s'] if x['release_s'] is not None else math.inf),worst_discharge_case=max(cases,key=lambda x:x['discharge_s'] or -1),drive=dict(qdis_base_min_A=base_dis_min,qinhibit_base_min_A=base_inhibit_min,qdis_collector_max_A=collector_dis_max,qinhibit_collector_max_A=collector_inhibit_max,hc14_load_at_min_voh_A=hc14_load_at_min_voh),command_truth=truth,limitations=c['limitations'],inputs={str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [CONTRACT,Path(__file__)]})
    report['independent_integration'] = dict(method='RK4 from branch KCL,4096 steps per crossing window; linear event interpolation', comparisons=len(numeric),maximum_relative_error=numeric_max, worst=max(numeric,key=lambda x:x['relative_error'] or 0))
    report['native_binding'] = native
    native_gate_resistance = float(c['native_binding']['expected_current_value'].removesuffix('k'))*1000
    report['native_resistor_negative_control'] = dict(gate_series_ohm=native_gate_resistance,
        forced_beta=max(c['supply_V'])/(native_gate_resistance*(1-tol))/base_inhibit_min,
        within_allocation=max(c['supply_V'])/(native_gate_resistance*(1-tol))/base_inhibit_min<=c['screens']['forced_beta_max'])
    report['qualification_gates'] = [
        dict(name='every tested short fault restarts at least50ms inhibit', passed=report['every_short_fault_gets50ms_hold'], note='A diagnostic screen, not yet a justified audio requirement; direct driver inhibit remains separate.'),
        dict(name='hot component limits and intermediate-supply threshold envelope verified', passed=None),
        dict(name='full circuit power sequence and actual relay/contact timing qualified', passed=None),
        dict(name='exact Chinese small-quantity parts and Shanghai delivery verified', passed=None),
    ]
    (BASE/'results/rail-delay-budget.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['passed','total','corners','release_range_s','timer_discharge_range_s','every_short_fault_gets50ms_hold','short_faults']},indent=2))


if __name__ == '__main__':
    main()
