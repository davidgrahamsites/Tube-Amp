"""Bounded HREF divider/fault ratings; independent ngspice startup comparison."""
from pathlib import Path
import hashlib, itertools, json, math, sys

M = Path(__file__).resolve().parents[1]
ROOT = M.parents[2]
sys.path.insert(0, str(ROOT / 'engineering/whole-amp/tools'))
from spice_runtime import load, cmd, vector, logs


def allowed(part, temperature):
    return part['rated_W_at70C'] * max(0, min(1, (part['zero_power_C']-temperature)/(part['zero_power_C']-70)))


def main():
    c = json.loads((M/'contract.json').read_text())
    for path, digest in c['native_sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, path
    for path, digest in c['evidence_sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, path
    source = json.loads((ROOT/c['source']).read_text())
    for ref, expected in c['source_parts'].items():
        p = next(p for p in source['components'] if p['reference'] == ref)
        assert all(p[k] == v for k, v in expected.items()), ref
    coverage = json.loads((M.parent/'coverage.json').read_text())
    for ref, mpn in c['selected_reference'].items():
        assert next(g for g in coverage if ref in g['refs'])['selected_mpn'] == mpn, ref
    # Endpoint ranges include initial tolerance and a separately declared drift allocation.
    factors = [(1+s*c['initial_tolerance'])*(1+d*c['additional_resistance_drift_allocation'])
               for s, d in itertools.product([-1, 1], repeat=2)]
    bottom_part = c['implementations'][0]  # R507 is also the selected FMP200 family.
    rows = []
    for part in c['implementations']:
        for values, supply, temp, fault in itertools.product(
            itertools.product(factors, repeat=len(part['resistors_ohm'])+1),
            c['supply_V'], c['ambient_C'], c['faults']):
            upper = [r*f for r, f in zip(part['resistors_ohm'], values)]
            lower = 39000*values[-1]
            if fault == 'normal':
                current = supply/(sum(upper)+lower)
                href = current*lower
                upper_v = [current*r for r in upper]
            elif fault == 'C505_short':
                current = supply/sum(upper)
                href = 0
                upper_v = [current*r for r in upper]
            elif fault == 'R507_open':
                current = 0
                href = supply
                upper_v = [0 for r in upper]
            else:  # whole feed bypassed; not an individual two-series-part failure
                current = supply/lower
                href = supply
                upper_v = [0 for r in upper]
            upper_w = [v*v/r for v, r in zip(upper_v, upper)]
            lower_w = 0 if fault == 'R507_open' else href*href/lower
            a = allowed(part, temp)
            b = allowed(bottom_part, temp)
            rows.append(dict(implementation=part['id'], fault=fault, supply_V=supply,
                ambient_C=temp, upper_ohm=upper, lower_ohm=lower,
                source_current_A=current, href_V=href, upper_V=upper_v, upper_W=upper_w,
                lower_W=lower_w, upper_allowed_W=a, lower_allowed_W=b,
                upper_continuous_rating_pass=all(v <= part['maximum_working_V'] and w <= a
                                               for v, w in zip(upper_v, upper_w)),
                lower_rating_pass=lower_w <= b and (fault == 'R507_open' or href <= 500),
                capacitor_voltage_pass=href <= c['C505_rating_V']))
    # Startup: zero initial capacitor voltage and instantaneous 550 V source are deliberately
    # more abrupt than ordinary energization. No pulse-overload exemption is credited.
    startup = []
    supply = max(c['supply_V'])
    try:
        for rf, bf, cf in itertools.product([min(factors), max(factors)],
                                           [min(factors), max(factors)], [.8, 1.2]):
            rt, rb, cap = 220000*rf, 39000*bf, c['C505_F']*cf
            tau = cap/(1/rt+1/rb)
            final = supply*rb/(rt+rb)
            deck = f'''HREF RC startup, isolated passive model
Vrail rail 0 {supply}
Rtop rail href {rt}
Rbottom href 0 {rb}
Cfilter href 0 {cap} ic=0
.options reltol=1e-6 abstol=1e-12
.end
'''
            load(deck)
            cmd('tran 2m 20 0 2m uic')
            t, v = vector('time'), vector('v(href)')
            assert t[-1] >= 20-1e-9
            error = max(abs(y-final*(1-math.exp(-x/tau))) for x, y in zip(t, v))
            assert error < .002, error
            startup.append(dict(upper_ohm=rt, lower_ohm=rb, capacitor_F=cap,
                tau_s=tau, settled_href_V=final, analytical_error_max_V=error,
                initial_upper_V=supply, initial_upper_W=supply*supply/rt,
                settling_to_1percent_s=-tau*math.log(.01)))
            cmd('destroy all')
    finally:
        (M/'results/simulator.log').write_text('\n'.join(logs)+'\n')
    summaries=[]
    for part, fault, temp in itertools.product(c['implementations'], c['faults'], c['ambient_C']):
        subset=[r for r in rows if r['implementation']==part['id'] and r['fault']==fault and r['ambient_C']==temp]
        summaries.append(dict(implementation=part['id'], fault=fault, ambient_C=temp,
            upper_V_max=max(max(r['upper_V']) for r in subset),
            upper_W_max=max(max(r['upper_W']) for r in subset),
            lower_W_max=max(r['lower_W'] for r in subset),
            href_V_max=max(r['href_V'] for r in subset),
            upper_continuous_rating_pass=all(r['upper_continuous_rating_pass'] for r in subset),
            lower_rating_pass=all(r['lower_rating_pass'] for r in subset),
            capacitor_voltage_pass=all(r['capacitor_voltage_pass'] for r in subset)))
    # Independent KCL and supply-power balance checks for every enumerated DC corner.
    for row in rows:
        total_loss = sum(row['upper_W'])+row['lower_W']
        assert math.isclose(total_loss, row['supply_V']*row['source_current_A'], abs_tol=1e-12)
        if row['fault']=='normal':
            assert math.isclose(sum(row['upper_V'])+row['href_V'], row['supply_V'], abs_tol=1e-10)
    # Prevent accidentally treating a higher watt rating as a solution to the voltage limit.
    assert max(c['supply_V']) > c['implementations'][0]['maximum_working_V']
    assert not next(s for s in summaries if s['implementation']=='current' and s['fault']=='C505_short' and s['ambient_C']==100)['upper_continuous_rating_pass']
    assert next(s for s in summaries if s['implementation']=='PR03_candidate' and s['fault']=='C505_short' and s['ambient_C']==100)['upper_continuous_rating_pass']
    for path, digest in c['native_sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, path
    result=dict(calculation_checks_passed=True, dc_cases=len(rows), startup_cases=len(startup),
        summaries=summaries, startup=startup, cases=rows,
        preserved_native_files=len(c['native_sha256']),
        circuit_qualified=False, native_changes=False, fabrication_ready=False,
        source_sha256=c['evidence_sha256'],
        contract_sha256=hashlib.sha256((M/'contract.json').read_bytes()).hexdigest(),
        factory_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (M/'results/screen.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['calculation_checks_passed','dc_cases','startup_cases','circuit_qualified']},indent=2))
    print(json.dumps([s for s in summaries if s['ambient_C']==100],indent=2))


if __name__ == '__main__':
    main()
