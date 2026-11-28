"""CB-009. Rectified auxiliary currents and four devices on one dedicated sink."""
import itertools
import json
from pathlib import Path

from guard_transformer import MODULE, TRANSFORMERS, make_case, measure, sha

# Conservative junction-to-case paths and allocated tab/pad contact paths in K/W.
JC = dict(U4=5., U5=5., U6=3., U7=5.)
CONTACT = 1.0
SINK = 1.6
LEAK = .001645      # each 4700 uF, 35 V reservoir
PRELOAD = .00117    # conservative bound for the U6 output resistor


def main():
    prior = json.loads((MODULE/'results/guard-transformer.json').read_text())
    previous = json.loads((MODULE/'results/guard-regulators.json').read_text())
    c = json.loads((MODULE/'envelope-contract.json').read_text())
    c['relay_min_resistance_ohm'] = prior['baseline']['relay']['cold_screen_resistance_ohm']
    c['thermal_output_bound_V'].update(U4=11.4, U6=14.5, U7=14.25)
    rows = []
    for mode, line, cap, profile, regulation, budget in itertools.product(
            prior['modes'], (.9, 1., 1.1), (.8, 1.2), prior['baseline']['profiles'],
            (.75, 1, 1.25), ('optical_guard', 'baseline')):
        heavy = budget == 'optical_guard'
        leakage = LEAK if heavy else 0
        # Account for positive-only output preload through U6's input branch.
        # Subtract its delivered output power below. Leakage bypasses the regulators.
        preload = PRELOAD if heavy else .001
        c['iq_A'].update(U4=(.010 if heavy else .001) + leakage,
                         U6=(.0105 if heavy else .00025) + preload,
                         U7=(.006 if heavy else .001) + leakage)
        case = make_case(c, TRANSFORMERS[0], mode, line, 4700*cap, profile, budget, regulation)
        r = measure(c, case, c['simulation']['max_step_s'])
        assert r['completed_time_s'] >= .599999 and r['kcl_max_error_A'] < 1e-5
        pos, neg = r['positive_V'], r['negative_V']
        power = r['regulator_W']
        power['U4'] -= leakage*pos['mean']
        power['U6'] -= preload*c['thermal_output_bound_V']['U6']
        power['U7'] -= leakage*neg['mean']
        total = sum(power.values())
        limit = min((100-60-(JC[k]+CONTACT)*p)/total for k, p in power.items())
        rows.append(dict(line_V=line*mode['selector_V'], frequency_Hz=mode['frequency_hz'],
                         load=profile['name'], budget=budget, regulation_factor=regulation,
                         reservoir_uF=4700*cap, positive_V=pos, negative_magnitude_V=neg,
                         winding_rms_A=r['half_winding_rms_A'], heat_W=power, total_W=total,
                         junction_at_60C={k:60+total*SINK+p*(JC[k]+CONTACT) for k,p in power.items()},
                         allowed_sink_K_W=limit, deck_sha256=r['deck_sha256'],
                         voltage_ok=pos['min']>=16 and pos['max']<=27 and neg['min']>=17.5 and neg['max']<=30))
    worst = min(rows, key=lambda r:r['allowed_sink_K_W'])
    def hottest(ambient, sink, interface):
        return max(ambient+sink*r['total_W']+(JC[k]+interface)*p
                   for r in rows for k,p in r['heat_W'].items())
    report = dict(case_count=len(rows), voltage_failures=sum(not r['voltage_ok'] for r in rows),
                  thermal_failures=sum(max(r['junction_at_60C'].values())>100 for r in rows),
                  winding_rms_peak_A=max(r['winding_rms_A'] for r in rows),
                  pos_range_V=[min(r['positive_V']['min'] for r in rows),max(r['positive_V']['max'] for r in rows)],
                  neg_range_V=[min(r['negative_magnitude_V']['min'] for r in rows),max(r['negative_magnitude_V']['max'] for r in rows)],
                  max_heat_W={k:max(r['heat_W'][k] for r in rows) for k in JC},
                  max_total_W=max(r['total_W'] for r in rows),
                  max_Tj_C={k:max(r['junction_at_60C'][k] for r in rows) for k in JC},
                  sink_max_K_W=worst['allowed_sink_K_W'], governing_case=worst,
                  faults_peak_Tj_C=dict(air_at_70C=hottest(70,SINK,CONTACT),
                                       restricted_sink_3K_W=hottest(60,3.,CONTACT),
                                       poor_contact_3K_W=hottest(60,SINK,3.)),
                  old_U6_at_28K_W_60C=60+28*previous['max_heat_W']['U6'],
                  assumptions=dict(sink_K_W=SINK, tab_pad_K_W=CONTACT, junction_to_case_K_W=JC,
                       ground_current_U6_upper_A=.0105, output_preload_upper_A=PRELOAD,
                       capacitor_leakage_upper_A=LEAK, in_air_C=60, design_Tj_C=100),
                  model='Thermally steady. Imposed DC regulator loads on a typical-regulation transformer model. Light case is a high-input bound. Four regulators alone share the sink.',
                  factory_sha256=sha(Path(__file__)), cases=rows)
    (MODULE/'results/regulator-cooling.json').write_text(json.dumps(report,indent=1)+'\n')
    print({k:v for k,v in report.items() if k not in ('cases','governing_case')})


if __name__ == '__main__':
    main()
