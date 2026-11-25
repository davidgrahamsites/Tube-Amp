"""Current cold-coil + R215 screen; preserve historical room-temperature results."""
import copy
import itertools
import json
import math
from pathlib import Path
from calculate_loads import MODULE, load, sha
from check_preload import load_bounds
from screen_envelope import average, evaluate, spice


def path_currents(c):
    """Read the just-completed transient before another case destroys the plot."""
    times = spice.vector('time')
    start = next(i for i,t in enumerate(times) if t >= c['simulation']['measure_start_s'])
    paths = {name: spice.vector(name) for name in
             ['i(va)','i(vb)','@d201[id]','@d202[id]','@d203[id]','@d204[id]']}
    rawp, cp, rawn, cn = [spice.vector(name) for name in ['v(rawp)','v(cp)','v(rawn)','v(cn)']]
    paths['C201_branch'] = [(a-b)/c['reservoir_esr_ohm'] for a,b in zip(rawp,cp)]
    paths['C208_branch'] = [(a-b)/c['reservoir_esr_ohm'] for a,b in zip(cn,rawn)]
    return {name:dict(steady_rms_A=math.sqrt(average(times[start:],[v*v for v in values[start:]])),
                      steady_mean_A=average(times[start:],values[start:]),
                      steady_peak_abs_A=max(abs(v) for v in values[start:]),
                      whole_run_peak_abs_A=max(abs(v) for v in values))
            for name, values in paths.items()}


def main():
    c = json.loads((MODULE/'envelope-contract.json').read_text())
    budget = load()
    preload = load_bounds(json.loads((MODULE/'preload-contract.json').read_text()))
    c['relay_min_resistance_ohm'] = budget['relay']['cold_screen_resistance_ohm']
    c['relay_voltage_V'] = budget['relay']['voltage_bound_V']
    source = json.loads((MODULE.parent/'reverb-600/circuit.json').read_text())
    relay_count = len(json.loads((MODULE/'load-contract.json').read_text())['relay_references'])
    parts = {(p['reference'],p['unit']): p for p in source['components']}
    for ref, pins in {
        'U4': {'1':'CTRL_RAW','2':'GND','3':'+12V'},
        'U5': {'1':'+12V','2':'GND','3':'+5V'},
        'U6': {'1':'CTRL_RAW','2':'GND','3':'+15V'},
        'U7': {'1':'GND','2':'NEG_RAW','3':'-15V'},
        'D201': {'1':'CTRL_RAW','2':'CTRL_AC1'},
        'D202': {'1':'CTRL_RAW','2':'CTRL_AC2'},
        'D203': {'1':'CTRL_AC1','2':'NEG_RAW'},
        'D204': {'1':'CTRL_AC2','2':'NEG_RAW'},
        'C201': {'1':'CTRL_RAW','2':'GND'},
        'C208': {'1':'GND','2':'NEG_RAW'},
        'R215': {'1':'+5V','2':'GND'}
    }.items():
        assert parts[ref,1]['pins'] == pins, (ref,'model topology changed')
    assert parts['R215',1]['value'] == '820'
    assert all(parts[r,1]['value'] == '1000u' for r in ['C201','C208'])
    rows, decks, logs = [], {}, []
    combinations = itertools.product(c['line_factors'], c['frequency_hz'], c['winding_scenarios'], c['reservoir_uF'], c['loads'])
    for index, (line,hz,winding,cap,original_load) in enumerate(combinations):
        profile = copy.deepcopy(original_load)
        profile['logic_5V_A'] += preload['maximum_current_A']
        assert profile['relays_on'] <= relay_count
        case = dict(id=f'cold{index:03d}',line_factor=line,frequency_hz=hz,winding=winding,reservoir_uF=cap,load=profile)
        row, deck = evaluate(c,case,c['simulation']['max_step_s'])
        row['path_currents'] = path_currents(c)
        rows.append(row); decks[case['id']] = deck
        logs.append(case['id']+'\n'+'\n'.join(spice.logs))
    selectors = [lambda r:r['raw_positive_V']['min'],lambda r:r['raw_negative_magnitude_V']['min'],
                 lambda r:-r['conditional_total_W'],lambda r:-max(r['half_winding_rms_A'].values()),
                 lambda r:-r['raw_negative_magnitude_V']['max']]
    selected = sorted({min(range(len(rows)),key=lambda i:f(rows[i])) for f in selectors})
    refinements = []
    for i in selected:
        coarse = rows[i]
        fine, deck = evaluate(c,coarse['case'],c['simulation']['max_step_s']/2)
        fine['path_currents'] = path_currents(c)
        delta_v = max(abs(fine[k][limit]-coarse[k][limit]) for k in ['raw_positive_V','raw_negative_magnitude_V'] for limit in ['min','mean','max'])
        delta_i = max(abs(fine['half_winding_rms_A'][k]/coarse['half_winding_rms_A'][k]-1) for k in ['i(va)','i(vb)'])
        path_delta = max(abs(fine['path_currents'][path][metric]/coarse['path_currents'][path][metric]-1)
                         for path in fine['path_currents'] for metric in ['steady_rms_A','steady_peak_abs_A','whole_run_peak_abs_A'])
        assert delta_v < .01 and delta_i < .005 and path_delta < .01 and fine['screen_flags'] == coarse['screen_flags']
        refinements.append(dict(coarse_id=coarse['case']['id'],voltage_delta_V=delta_v,rms_relative_delta=delta_i,path_relative_delta=path_delta,fine=fine))
        decks[coarse['case']['id']+'-fine'] = deck
        logs.append(coarse['case']['id']+'-fine\n'+'\n'.join(spice.logs))
    report = dict(case_count=len(rows),budget=budget,preload=preload,cases=rows,refinements=refinements,decks=decks,
                  effective_contract=c,input_sha256={p:sha(MODULE/p) for p in ['envelope-contract.json','preload-contract.json','load-contract.json']},
                  simulator_library_sha256=sha(Path(spice.lib._name)),
                  limitations=c['limitations']+['Cold-coil electrical load combined with hot-regulator ambient is a conservative independent-corner screen, not a simultaneous equilibrium.',
                  'Path currents describe this assumed secondary model only; whole-run peaks use zero-phase sine startup, not worst switch-on phase, transformer saturation or fault current.'],
                  native_changes=False,purchase_ready=False)
    dest=MODULE/'results/loads'
    (dest/'budget.json').write_text(json.dumps(budget,indent=2)+'\n')
    (dest/'raw-screen.json').write_text(json.dumps(report,indent=2)+'\n')
    (dest/'simulator.log').write_text('\n\n'.join(logs)+'\n')
    print(json.dumps(dict(cases=len(rows),refinements=len(refinements),flagged=sum(bool(r['screen_flags']) for r in rows),max_winding_A=max(max(r['half_winding_rms_A'].values()) for r in rows),max_heat_W=max(r['conditional_total_W'] for r in rows))))


if __name__ == '__main__':
    main()
