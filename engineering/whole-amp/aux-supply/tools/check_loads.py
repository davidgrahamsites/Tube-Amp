"""Independent audit of current load/model receipts, with corruption controls."""
import copy
import hashlib
import itertools
import json
import math
from calculate_loads import MODULE, calculate, load, sha


def close(a, b):
    assert math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-12), (a, b)


def check(d, expected_budget):
    assert d['budget'] == expected_budget, 'Stale or altered load budget'
    for path, digest in d['input_sha256'].items():
        assert sha(MODULE/path) == digest, path
    c = d['effective_contract']
    base = json.loads((MODULE/'envelope-contract.json').read_text())
    replacement = copy.deepcopy(base)
    replacement['relay_min_resistance_ohm'] = expected_budget['relay']['cold_screen_resistance_ohm']
    replacement['relay_voltage_V'] = expected_budget['relay']['voltage_bound_V']
    assert c == replacement, 'Unreviewed model changes'
    expected = set(itertools.product(c['line_factors'],c['frequency_hz'],
                                    [w['name'] for w in c['winding_scenarios']],c['reservoir_uF'],
                                    [p['name'] for p in c['loads']]))
    seen = set()
    assert len(d['cases']) == d['case_count'] == len(expected)
    for row in d['cases']:
        case = row['case']; profile = case['load']
        seen.add((case['line_factor'],case['frequency_hz'],case['winding']['name'],case['reservoir_uF'],profile['name']))
        assert case['winding'] in c['winding_scenarios']
        original = next(p for p in c['loads'] if p['name'] == profile['name'])
        assert profile['relays_on'] == original['relays_on']
        close(profile['audio_each_rail_A'],original['audio_each_rail_A']+expected_budget['reverb_rail_loads']['each_rail_maximum_A'])
        logic = original['logic_5V_A']+d['preload']['maximum_current_A']
        close(profile['logic_5V_A'],logic)
        coil = expected_budget['relay']['one_coil_A']*profile['relays_on']
        pos = coil+logic+c['iq_A']['U5']+c['iq_A']['U4']+profile['audio_each_rail_A']+c['iq_A']['U6']
        neg = profile['audio_each_rail_A']+c['iq_A']['U7']
        close(row['raw_load_A']['positive'],pos); close(row['raw_load_A']['negative'],neg)
        close(row['completed_time_s'],c['simulation']['stop_s'])
        assert row['kcl_max_error_A'] < 1e-5
        assert 'U5_below_minimum_regulation_load' not in row['screen_flags']
        text = d['decks'][case['id']]
        assert hashlib.sha256(text.encode()).hexdigest() == row['deck_sha256']
        assert 'D203 rawn ac1 rect' in text and 'D204 rawn ac2 rect' in text
        for node in ['raw_positive_V','raw_negative_magnitude_V']:
            v = row[node]; assert 0 < v['min'] <= v['mean'] <= v['max']
        paths = row['path_currents']
        assert set(paths) == {'i(va)','i(vb)','@d201[id]','@d202[id]','@d203[id]','@d204[id]','C201_branch','C208_branch'}
        for name, values in paths.items():
            assert all(math.isfinite(v) for v in values.values())
            assert abs(values['steady_mean_A']) <= values['steady_rms_A'] <= values['steady_peak_abs_A'] <= values['whole_run_peak_abs_A']
        for name in ['i(va)','i(vb)']:
            close(paths[name]['steady_rms_A'],row['half_winding_rms_A'][name])
        # Independent time-average KCL joins pulse-current evidence to raw loads.
        # The 100Mohm bleed remains part of the model and is included here.
        # Simulator residuals are not exact arithmetic: allow 1uA mean error,
        # tighter than the existing 10uA instantaneous KCL acceptance.
        assert abs(paths['@d201[id]']['steady_mean_A']+paths['@d202[id]']['steady_mean_A']-
                   pos-row['raw_positive_V']['mean']/1e8-paths['C201_branch']['steady_mean_A']) < 1e-6
        assert abs(paths['@d203[id]']['steady_mean_A']+paths['@d204[id]']['steady_mean_A']-
                   neg-row['raw_negative_magnitude_V']['mean']/1e8-paths['C208_branch']['steady_mean_A']) < 1e-6
        powers = row['conditional_regulator_dissipation_W']
        close(row['conditional_total_W'],sum(powers.values()))
        for thermal in row['thermal']:
            hottest = thermal['ambient_C']+sum(powers.values())*thermal['shared_sink_theta_sa_max_C_per_W']+max(powers.values())*(c['thermal']['theta_junction_case_C_per_W']+c['thermal']['theta_case_sink_assumed_C_per_W'])
            close(hottest,c['thermal']['junction_design_limit_C'])
    assert seen == expected
    assert len(d['refinements']) >= 4
    by_id = {row['case']['id']:row for row in d['cases']}
    for refinement in d['refinements']:
        coarse = by_id[refinement['coarse_id']]; fine = refinement['fine']
        assert fine['case'] == coarse['case']
        close(fine['step_s'],coarse['step_s']/2)
        assert fine['kcl_max_error_A'] < 1e-5
        close(fine['completed_time_s'],c['simulation']['stop_s'])
        assert fine['screen_flags'] == coarse['screen_flags']
        dv = max(abs(fine[k][n]-coarse[k][n]) for k in ['raw_positive_V','raw_negative_magnitude_V'] for n in ['min','mean','max'])
        di = max(abs(fine['half_winding_rms_A'][k]/coarse['half_winding_rms_A'][k]-1) for k in ['i(va)','i(vb)'])
        close(dv,refinement['voltage_delta_V']); close(di,refinement['rms_relative_delta'])
        assert dv < .01 and di < .005
        path_delta = max(abs(fine['path_currents'][path][metric]/coarse['path_currents'][path][metric]-1)
                         for path in fine['path_currents'] for metric in ['steady_rms_A','steady_peak_abs_A','whole_run_peak_abs_A'])
        close(path_delta,refinement['path_relative_delta'])
        assert path_delta < .01
        assert sha_text(d['decks'][refinement['coarse_id']+'-fine']) == fine['deck_sha256']
    assert not d['purchase_ready'] and not d['native_changes']


def sha_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


def main():
    path = MODULE/'results/loads/raw-screen.json'
    d = json.loads(path.read_text()); budget = load()
    check(d,budget)
    # Independent concrete checks catch a wrong unit/package count and the old
    # room-temperature relay load, rather than comparing only two shared formulas.
    close(budget['heater']['tube_nominal_total_A'],4.2)
    close(budget['heater']['balance_pair_nominal_A'],.0315)
    close(budget['heater']['nominal_plus_pilot_allowance_A'],4.3815)
    close(budget['relay']['cold_screen_resistance_ohm'],701.01504)
    close(budget['relay']['groups_A']['COIL_CH'],2*budget['relay']['groups_A']['COIL_REV'])
    mutations = {
        'room_temperature_resistance_reintroduced': lambda x:x['effective_contract'].__setitem__('relay_min_resistance_ohm',864),
        'reverb_load_omitted': lambda x:x['cases'][0]['case']['load'].__setitem__('audio_each_rail_A',x['cases'][0]['case']['load']['audio_each_rail_A']-budget['reverb_rail_loads']['each_rail_maximum_A']),
        'preload_omitted': lambda x:x['cases'][0]['case']['load'].__setitem__('logic_5V_A',.002),
        'missing_case': lambda x:x['cases'].pop(),
        'incomplete_run': lambda x:x['cases'][0].__setitem__('completed_time_s',.2),
        'corrupted_deck': lambda x:x['decks'].__setitem__('cold000','wrong'),
        'rectifier_pulse_replaced_with_load_average': lambda x:x['cases'][0]['path_currents']['@d201[id]'].__setitem__('steady_rms_A',0),
        'invalid_shared_sink': lambda x:x['cases'][0]['thermal'][0].__setitem__('shared_sink_theta_sa_max_C_per_W',99)}
    rejected = []
    for name, mutate in mutations.items():
        bad = copy.deepcopy(d); mutate(bad)
        try: check(bad,budget)
        except AssertionError: rejected.append(name)
        else: raise AssertionError('Negative control escaped: '+name)
    c = json.loads((MODULE/'load-contract.json').read_text())
    ctrl = json.loads((MODULE/c['control_contract']).read_text())
    circuit = json.loads((MODULE/c['source_circuit']).read_text())
    bad = copy.deepcopy(c); bad['heater_packages']['ECC83S']['references'].append('V1')
    try: calculate(bad,ctrl,circuit)
    except AssertionError: rejected.append('double_counted_valve_package')
    else: raise AssertionError('Double-counted valve escaped')
    # VAL-069 raises only the working allocation by 20 mA. Preserve the
    # independent comparison to the historical room-temperature + R215 matrix.
    audio_path=MODULE.parent/'pcb-measured-r/current-budget/results/budget.json'
    audio=json.loads(audio_path.read_text())
    audio_checks=json.loads((audio_path.parent/'checks.json').read_text())
    assert audio_checks['passed'] and audio_checks['budget_sha256']==sha(audio_path)
    assert audio['input_sha256']['engineering/whole-amp/reverb-600/circuit.json']==sha(MODULE.parent/'reverb-600/circuit.json')
    allocation={x['name']:x['audio_each_rail_A'] for x in d['effective_contract']['loads']}
    for name,peak in [('working_reserve',10),('expansion_stress',18)]:
        required=max(x['each_rail_conditional_A'] for x in audio['cases'] if x['output_peak_V']==peak)-budget['reverb_rail_loads']['each_rail_maximum_A']
        assert allocation[name]>=required, (name,allocation[name],required)
    old = json.loads((MODULE/'results/preload/raw-screen.json').read_text())
    for new, previous in zip(d['cases'],old['cases']):
        oldcase = copy.deepcopy(previous['case']); newcase = copy.deepcopy(new['case'])
        oldcase.pop('id'); newcase.pop('id')
        profile_delta={'idle':0.,'working_reserve':.020,'expansion_stress':0.}[newcase['load']['name']]
        extra=budget['reverb_rail_loads']['each_rail_maximum_A']+profile_delta
        close(newcase['load']['audio_each_rail_A'],oldcase['load']['audio_each_rail_A']+extra)
        newcase['load']['audio_each_rail_A']=oldcase['load']['audio_each_rail_A']
        assert oldcase == newcase
        delta = new['raw_load_A']['positive']-previous['raw_load_A']['positive']
        close(delta,new['case']['load']['relays_on']*(budget['relay']['one_coil_A']-budget['relay']['room_temperature_one_coil_A'])+extra)
        close(new['raw_load_A']['negative'],previous['raw_load_A']['negative']+extra)
        if new['case']['load']['relays_on']:
            assert max(new['half_winding_rms_A'].values()) > max(previous['half_winding_rms_A'].values())
            assert new['raw_positive_V']['mean'] < previous['raw_positive_V']['mean']
    receipt = dict(status='Evidence checks pass; supply and copper remain unqualified',
                   cases=len(d['cases']),refinements=len(d['refinements']),negative_controls_rejected=rejected,
                   screen_sha256=sha(path),comparison_sha256=sha(MODULE/'results/preload/raw-screen.json'),
                   reverb_output_budget_sha256=sha(audio_path),
                   factory_sha256={name:sha(MODULE/'tools'/name) for name in ['calculate_loads.py','screen_cold_loads.py','check_loads.py','screen_envelope.py','check_preload.py']})
    (path.parent/'checks.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
