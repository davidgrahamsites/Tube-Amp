"""Raw auxiliary supply envelope. Does not model regulator control or faults."""
from pathlib import Path
import hashlib
import itertools
import json
import math
import sys

MODULE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE.parent / 'tools'))
import spice_runtime as spice


def average(t, values):
    return sum((b-a)*(x+y)/2 for a,b,x,y in
               zip(t,t[1:],values,values[1:]))/(t[-1]-t[0])


def currents(c, load):
    iq = c['iq_A']
    coil = load['relays_on']*c['relay_voltage_V']/c['relay_min_resistance_ohm']
    out = {'U4':coil+load['logic_5V_A']+iq['U5'],
           'U5':load['logic_5V_A'], 'U6':load['audio_each_rail_A'],
           'U7':load['audio_each_rail_A']}
    return out, out['U4']+iq['U4']+out['U6']+iq['U6'], out['U7']+iq['U7']


def deck(c, case, step):
    w, load = case['winding'], case['load']
    _, pos, neg = currents(c, load)
    amp = w['open_circuit_half_rms_V']*case['line_factor']*math.sqrt(2)
    sim = c['simulation']
    ramp = f"PWL(0 0 {sim['load_ramp_start_s']} 0 {sim['load_ramp_stop_s']}"
    return f"""Auxiliary rectifier envelope; assumed raw loads, NOT regulator model
VA s1 0 SIN(0 {amp:.12g} {case['frequency_hz']})
VB s2 0 SIN(0 {amp:.12g} {case['frequency_hz']} 0 0 180)
RA s1 ac1 {w['series_ohm_per_half']}
RB s2 ac2 {w['series_ohm_per_half']}
D201 ac1 rawp rect
D202 ac2 rawp rect
D203 rawn ac1 rect
D204 rawn ac2 rect
RP rawp cp {c['reservoir_esr_ohm']}
RN rawn cn {c['reservoir_esr_ohm']}
C201 cp 0 {case['reservoir_uF']}u
C208 0 cn {case['reservoir_uF']}u
IP rawp 0 {ramp} {pos:.12g})
IN 0 rawn {ramp} {neg:.12g})
RBP rawp 0 100meg
RBN 0 rawn 100meg
.model rect D(Is=10n N=1.8 Rs=0.05)
.options reltol=1e-7 abstol=1e-11 vntol=1e-8 method=trap
.save v(rawp) v(rawn) v(cp) v(cn) i(VA) i(VB) @D201[id] @D202[id] @D203[id] @D204[id]
.tran {step} {sim['stop_s']} 0 {step}
.end
"""


def evaluate(c, case, step):
    text = deck(c,case,step)
    spice.cmd('destroy all')
    spice.logs.clear()
    spice.load(text)
    spice.cmd('run')
    t_all = spice.vector('time')
    assert abs(t_all[-1]-c['simulation']['stop_s']) < 1e-9, spice.logs[-20:]
    # Common 0.2s observation interval contains integer50Hz and60Hz cycles.
    start = next(i for i,t in enumerate(t_all) if t >= c['simulation']['measure_start_s'])
    t=t_all[start:]
    vectors={n:spice.vector(n)[start:] for n in
             ['v(rawp)','v(rawn)','v(cp)','v(cn)','i(va)','i(vb)',
              '@d201[id]','@d202[id]','@d203[id]','@d204[id]']}
    assert all(math.isfinite(v) for vs in vectors.values() for v in vs)
    p=vectors['v(rawp)']; n=[-v for v in vectors['v(rawn)']]
    pm,nm=average(t,p),average(t,n)
    out,ip,ineg=currents(c,case['load'])
    iq=c['iq_A']
    power={r:(vin-c['thermal_output_bound_V'][r])*out[r]+vin*iq[r]
           for r,vin in [('U4',pm),('U5',c['thermal_U5_input_bound_V']),('U6',pm),('U7',nm)]}
    total=sum(power.values())
    th=c['thermal']
    therm=[]
    for ambient in th['ambient_C']:
        # Shared sink rise is TOTAL dissipation times sink-to-ambient.
        allowable=min((th['junction_design_limit_C']-ambient-
                       w*(th['theta_junction_case_C_per_W']+th['theta_case_sink_assumed_C_per_W']))/total
                      for w in power.values())
        therm.append({'ambient_C':ambient,'shared_sink_theta_sa_max_C_per_W':allowable,
                      'bare_package_reference_junction_C':{r:ambient+w*th['theta_junction_ambient_reference_C_per_W'] for r,w in power.items()}})
    s=c['raw_screen_V']
    flags=[]
    if min(p)<s['positive_min']: flags.append('positive_below_documented_range')
    if max(p)>s['positive_max']: flags.append('positive_above_documented_range')
    if min(n)<s['negative_min_magnitude']: flags.append('negative_below_documented_range')
    if max(n)>s['negative_max_magnitude']: flags.append('negative_above_documented_range')
    if max(max(p),max(n))>=s['absolute_max_magnitude']: flags.append('absolute_input_limit_exceeded')
    if out['U5']<0.005: flags.append('U5_below_minimum_regulation_load')
    irms={k:math.sqrt(average(t,[v*v for v in vectors[k]])) for k in ['i(va)','i(vb)']}
    if max(irms.values())>0.25: flags.append('half_winding_exceeds_provisional_0p25A')
    # Instantaneous KCL checks independently validate all four diode orientations.
    p_err=[vectors['@d201[id]'][i]+vectors['@d202[id]'][i]-ip-p[i]/1e8-
           (p[i]-vectors['v(cp)'][i])/c['reservoir_esr_ohm'] for i in range(len(t))]
    n_err=[vectors['@d203[id]'][i]+vectors['@d204[id]'][i]-ineg-n[i]/1e8-
           (vectors['v(cn)'][i]-vectors['v(rawn)'][i])/c['reservoir_esr_ohm'] for i in range(len(t))]
    kcl=max(max(map(abs,p_err)),max(map(abs,n_err)))
    assert kcl<1e-5, kcl
    assert min(p)>0 and min(n)>0
    result={'case':case,'step_s':step,'raw_positive_V':{'min':min(p),'mean':pm,'max':max(p)},
            'raw_negative_magnitude_V':{'min':min(n),'mean':nm,'max':max(n)},
            'half_winding_rms_A':irms,'raw_load_A':{'positive':ip,'negative':ineg},
            'conditional_regulator_dissipation_W':power,'conditional_total_W':total,
            'thermal':therm,'screen_flags':flags,'kcl_max_error_A':kcl,
            'points':len(t_all),'completed_time_s':t_all[-1],
            'deck_sha256':hashlib.sha256(text.encode()).hexdigest()}
    return result,text


def main():
    c=json.loads((MODULE/'envelope-contract.json').read_text())
    circuit=MODULE.parent/'reverb-600/circuit.json'
    source=json.loads(circuit.read_text())
    components={x['reference']:x for x in source['components']}
    assert 'R215' not in components, 'Historical unloaded model: use screen_adopted_preload.py for the repaired circuit'
    expected={'U4':{'1':'CTRL_RAW','2':'GND','3':'+12V'},
              'U5':{'1':'+12V','2':'GND','3':'+5V'},
              'U6':{'1':'CTRL_RAW','2':'GND','3':'+15V'},
              'U7':{'1':'GND','2':'NEG_RAW','3':'-15V'},
              'D201':{'1':'CTRL_RAW','2':'CTRL_AC1'},
              'D202':{'1':'CTRL_RAW','2':'CTRL_AC2'},
              'D203':{'1':'CTRL_AC1','2':'NEG_RAW'},
              'D204':{'1':'CTRL_AC2','2':'NEG_RAW'},
              'C201':{'1':'CTRL_RAW','2':'GND'},
              'C208':{'1':'GND','2':'NEG_RAW'}}
    for ref,pins in expected.items(): assert components[ref]['pins']==pins,(ref,'topology changed')
    for ref in ['C201','C208']: assert components[ref]['value']=='1000u'
    dest=MODULE/'results/envelope';dest.mkdir(exist_ok=True)
    (dest/'CONTEXT.md').write_text('# Auxiliary raw-supply envelope evidence\nOwner: supply qualification. Inputs: ../../envelope-contract.json and current circuit topology.\nProcess: ../../tools/screen_envelope.py overwrites this one current result set; deck text and metrics retained together, no CAD copies.\nOutputs: screen.json and simulator.log. All regulator/thermal values are conditional estimates.\nHuman check: replace transformer/load/temperature assumptions with exact evidence and compare raw-waveform and heatsink measurements before release.\n')
    rows=[];decks={};run_logs=[]
    for index,(line,hz,w,cap,load) in enumerate(itertools.product(c['line_factors'],c['frequency_hz'],c['winding_scenarios'],c['reservoir_uF'],c['loads'])):
        case={'id':f'aux{index:03d}','line_factor':line,'frequency_hz':hz,'winding':w,'reservoir_uF':cap,'load':load}
        row,text=evaluate(c,case,c['simulation']['max_step_s']);rows.append(row);decks[case['id']]=text
        run_logs.append(case['id']+'\n'+'\n'.join(spice.logs))
    # Refine distinct limiting cases, not a random subset.
    selected={min(range(len(rows)),key=lambda i:rows[i]['raw_positive_V']['min']),
              min(range(len(rows)),key=lambda i:rows[i]['raw_negative_magnitude_V']['min']),
              max(range(len(rows)),key=lambda i:rows[i]['conditional_total_W']),
              max(range(len(rows)),key=lambda i:max(rows[i]['half_winding_rms_A'].values())),
              max(range(len(rows)),key=lambda i:rows[i]['raw_negative_magnitude_V']['max'])}
    refinements=[]
    for i in sorted(selected):
        fine,text=evaluate(c,rows[i]['case'],c['simulation']['max_step_s']/2)
        diffs={k:abs(fine[k]['min']-rows[i][k]['min']) for k in ['raw_positive_V','raw_negative_magnitude_V']}
        diffs['total_power_W']=abs(fine['conditional_total_W']-rows[i]['conditional_total_W'])
        assert max(diffs.values())<0.01,diffs
        rms_delta=max(abs(fine['half_winding_rms_A'][k]/rows[i]['half_winding_rms_A'][k]-1) for k in ['i(va)','i(vb)'])
        assert rms_delta<0.005,rms_delta
        diffs['winding_rms_relative']=rms_delta
        assert fine['screen_flags']==rows[i]['screen_flags']
        refinements.append({'coarse_id':rows[i]['case']['id'],'differences':diffs,'fine':fine})
        decks[rows[i]['case']['id']+'_refined']=text
        run_logs.append(rows[i]['case']['id']+'_refined\n'+'\n'.join(spice.logs))
    report={'contract_sha256':hashlib.sha256((MODULE/'envelope-contract.json').read_bytes()).hexdigest(),
            'circuit_sha256':hashlib.sha256(circuit.read_bytes()).hexdigest(),
            'simulator':'KiCad bundled libngspice.0.dylib via existing spice_runtime.py',
            'library_sha256':hashlib.sha256(Path(spice.lib._name).read_bytes()).hexdigest(),
            'case_count':len(rows),'cases':rows,'refinements':refinements,'decks':decks,
            'limitations':c['limitations'],'native_changes':False}
    (dest/'screen.json').write_text(json.dumps(report,indent=2)+'\n')
    (dest/'simulator.log').write_text('\n\n'.join(run_logs)+'\n')
    print(json.dumps({'cases':len(rows),'refinements':len(refinements),'flagged':sum(bool(r['screen_flags']) for r in rows),
                      'max_total_W':max(r['conditional_total_W'] for r in rows),
                      'max_winding_A':max(max(r['half_winding_rms_A'].values()) for r in rows),
                      'min_positive_V':min(r['raw_positive_V']['min'] for r in rows)}))


if __name__=='__main__':main()
