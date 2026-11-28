"""Re-screen selected 50 VA transformer with the proposed U4/U6/U7 changes."""
import itertools
import json

from guard_transformer import MODULE, TRANSFORMERS, make_case, measure


def main():
    prior=json.loads((MODULE/'results/guard-transformer.json').read_text())
    c=json.loads((MODULE/'envelope-contract.json').read_text())
    c['relay_min_resistance_ohm']=prior['baseline']['relay']['cold_screen_resistance_ohm']
    assert c['relay_voltage_V']==prior['baseline']['relay']['voltage_bound_V']
    # Worst full-load ground current at U6, plus 0.25 mA for setting network.
    # Use light-current estimates separately for high-line/light-load voltage.
    c['thermal_output_bound_V'].update(U4=11.4,U6=14.6,U7=14.25)
    dims=itertools.product(prior['modes'],(.9,1.,1.1),(.8,1.2),prior['baseline']['profiles'],
                           (.75,1,1.25),('optical_guard','baseline'))
    rows=[]
    for mode,line,cap,profile,reg,budget in dims:
        c['iq_A'].update(U4=.010 if budget=='optical_guard' else .001,
                         U6=.02525 if budget=='optical_guard' else .00025,
                         U7=.006 if budget=='optical_guard' else .001)
        case=make_case(c,TRANSFORMERS[0],mode,line,4700*cap,profile,budget,reg)
        r=measure(c,case,c['simulation']['max_step_s'])
        # +15 V worst high setpoint + 510 mV maximum full-load dropout + allowance.
        # U4 limits top of positive range. Evaluate U7 on its negative data-sheet range.
        r.update(budget=budget,regulation_factor=reg,mains_V=line*mode['selector_V'],
                 capacitance_uF=cap*4700,load=profile['name'],line_Hz=mode['frequency_hz'])
        r['voltage_pass']=(r['positive_V']['min']>=16 and r['positive_V']['max']<=27 and
                           r['negative_V']['min']>=17.5 and r['negative_V']['max']<=30)
        assert r['completed_time_s']>=.599999 and r['kcl_max_error_A']<1e-5
        rows.append(r)
    peak=lambda dev:max(r['regulator_W'][dev] for r in rows)
    report=dict(mpn='VPT30-1670',reservoir_uF=4700,case_count=len(rows),
                failed=sum(not r['voltage_pass'] for r in rows),
                positive_range_V=[min(r['positive_V']['min'] for r in rows),max(r['positive_V']['max'] for r in rows)],
                negative_magnitude_range_V=[min(r['negative_V']['min'] for r in rows),max(r['negative_V']['max'] for r in rows)],
                max_rms_A=max(r['half_winding_rms_A'] for r in rows),max_total_W=max(r['total_regulator_W'] for r in rows),
                max_heat_W={dev:peak(dev) for dev in ['U4','U5','U6','U7']},
                U6_local_theta_ja_max_at_60C_K_per_W=40/peak('U6'),cases=rows)
    (MODULE/'results/guard-regulators.json').write_text(json.dumps(report,indent=1)+'\n')
    print({k:v for k,v in report.items() if k!='cases'})


if __name__=='__main__':
    main()
