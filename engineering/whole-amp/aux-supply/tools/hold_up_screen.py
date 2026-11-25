"""Raw supply/relay-warning feasibility with explicit regulator and load seams.

Reuses the existing rectifier adapter only. No regulator dynamics or native writes.
"""
import itertools
import json
import math
from pathlib import Path

from calculate_loads import load, sha
from check_preload import load_bounds
from screen_envelope import average, deck, spice

BASE = Path(__file__).resolve().parents[1]
DEST = BASE/'results/hold-up'


def regulator_bounds(c):
    result = {}
    f = c['set_resistor_total_fraction']
    for ref, part in c['regulators'].items():
        values = [v*(1+r2/r1)+iadj*r2 for v, iadj, r1, r2 in itertools.product(
            c['regulator_reference_magnitude_V'], c['adjust_current_magnitude_A'],
            [part['R1_ohm']*(1-f),part['R1_ohm']*(1+f)],
            [part['R2_ohm']*(1-f),part['R2_ohm']*(1+f)])]
        result[ref] = {'output_abs_V': [min(values),max(values)],
                       'divider_current_A': [min(c['regulator_reference_magnitude_V'])/(part['R1_ohm']*(1+f)),
                                             max(c['regulator_reference_magnitude_V'])/(part['R1_ohm']*(1-f))]}
    return result


def load_case(c, base, budget, preload, bounds, profile):
    logic = profile['logic_5V_A']+preload['maximum_current_A']
    coil = profile['relays_on']*budget['relay']['one_coil_A']
    out = {'U4': coil+logic+base['iq_A']['U5']+bounds['U4']['divider_current_A'][1]+c['additional_positive_raw_current_A'],
           'U5': logic, 'U6': profile['audio_each_rail_A']+bounds['U6']['divider_current_A'][1],
           'U7': profile['audio_each_rail_A']+bounds['U7']['divider_current_A'][1]+c['additional_negative_raw_current_A']}
    adj = max(c['adjust_current_magnitude_A'])
    return out, out['U4']+out['U6']+2*adj, out['U7']+adj


def run(c, base, budget, preload, bounds, case, step=20e-6):
    out, ip, ine = load_case(c,base,budget,preload,bounds,case['load'])
    text = deck(base,case,step)
    lines = text.splitlines()
    ramp = base['simulation']
    for i,line in enumerate(lines):
        if line.startswith('IP '): lines[i]=f"IP rawp 0 PWL(0 0 {ramp['load_ramp_start_s']} 0 {ramp['load_ramp_stop_s']} {ip:.12g})"
        if line.startswith('IN '): lines[i]=f"IN 0 rawn PWL(0 0 {ramp['load_ramp_start_s']} 0 {ramp['load_ramp_stop_s']} {ine:.12g})"
    cutoff = case.get('cutoff_s')
    if cutoff is not None:
        amp = case['winding']['open_circuit_half_rms_V']*case['line_factor']*math.sqrt(2)
        frequency = case['frequency_hz']; transition=c['secondary_cutoff_transition_s']
        for i,line in enumerate(lines):
            if line.startswith(('VA ', 'VB ')):
                sign=1 if line.startswith('VA ') else -1
                node='s1' if sign==1 else 's2'
                # Keep independent voltage sources for common current probes.
                lines[i]=f"{line[:2]} {node} bx{node} 0\nBX{node} bx{node} 0 V={sign*amp:.12g}*sin(2*pi*{frequency}*time)*max(0,min(1,({cutoff+transition:.12g}-time)/{transition:.12g}))"
            if line.startswith('.tran '): lines[i]=f".tran {step} {cutoff+c['shutdown_post_window_s']} 0 {step}"
    text='\n'.join(lines)+'\n'
    spice.cmd('destroy all');spice.logs.clear();spice.load(text);spice.cmd('run')
    times=spice.vector('time'); expected=cutoff+c['shutdown_post_window_s'] if cutoff is not None else ramp['stop_s']
    assert abs(times[-1]-expected)<1e-8, spice.logs[-20:]
    vectors={k:spice.vector(k) for k in ['v(rawp)','v(rawn)','v(cp)','v(cn)','i(va)','i(vb)','@d201[id]','@d202[id]','@d203[id]','@d204[id]']}
    assert all(math.isfinite(x) for v in vectors.values() for x in v)
    ids=[i for i,t in enumerate(times) if ramp['measure_start_s']<=t<=ramp['stop_s']]
    ts=[times[i] for i in ids]
    rails={'positive':[vectors['v(rawp)'][i] for i in ids],'negative':[-vectors['v(rawn)'][i] for i in ids]}
    floors={'positive':max(bounds['U4']['output_abs_V'][1],bounds['U6']['output_abs_V'][1])+c['required_input_output_headroom_V'],
            'negative':bounds['U7']['output_abs_V'][1]+c['required_input_output_headroom_V']}
    metrics={side:{'min_V':min(v),'max_V':max(v),'mean_V':average(ts,v),'required_raw_floor_V':floors[side]} for side,v in rails.items()}
    rms={k:math.sqrt(average(ts,[vectors[k][i]**2 for i in ids])) for k in ['i(va)','i(vb)']}
    # Exact rectifier KCL after startup. No current disappears at input cutoff.
    errors=[]
    for i,t in enumerate(times):
        if t<ramp['measure_start_s']:continue
        p=vectors['v(rawp)'][i];n=-vectors['v(rawn)'][i]
        errors.extend([abs(vectors['@d201[id]'][i]+vectors['@d202[id]'][i]-ip-p/1e8-(p-vectors['v(cp)'][i])/base['reservoir_esr_ohm']),
                       abs(vectors['@d203[id]'][i]+vectors['@d204[id]'][i]-ine-n/1e8-(vectors['v(cn)'][i]-vectors['v(rawn)'][i])/base['reservoir_esr_ohm'])])
    assert max(errors)<1e-5,max(errors)
    flags=[]
    for side,m in metrics.items():
        if m['min_V']<floors[side]:flags.append(side+' insufficient regulated headroom')
        if m['max_V']>=c['raw_voltage_design_ceiling_V']:flags.append(side+' above raw design ceiling')
    if max(rms.values())>c['transformer']['series_current_A']:flags.append('winding RMS exceeds candidate rating')
    heat={ref:(metrics[side]['mean_V']-bounds[ref]['output_abs_V'][0])*out[ref]+metrics[side]['mean_V']*max(c['adjust_current_magnitude_A']) for ref,side in [('U4','positive'),('U6','positive'),('U7','negative')]}
    heat['U5']=(bounds['U4']['output_abs_V'][1]-4.75)*out['U5']+bounds['U4']['output_abs_V'][1]*base['iq_A']['U5']
    result={'case':case,'step_s':step,'raw_load_A':{'positive':ip,'negative':ine},'rails':metrics,'winding_rms_A':rms,'conditional_regulator_heat_W':heat,'kcl_max_error_A':max(errors),'screen_flags':flags}
    if cutoff is not None:
        hold={}
        for side,key,sign in [('positive','v(rawp)',1),('negative','v(rawn)',-1)]:
            start=next(i for i,t in enumerate(times) if t>=cutoff)
            if sign*vectors[key][start]<floors[side]:hold[side]=0
            else:
                crossing=next((i for i in range(start+1,len(times)) if sign*vectors[key][i]<floors[side]),None)
                if crossing is None:hold[side]=None
                else:
                    i=crossing;v0=sign*vectors[key][i-1];v1=sign*vectors[key][i]
                    tx=times[i-1]+(times[i]-times[i-1])*(v0-floors[side])/(v0-v1)
                    hold[side]=tx-cutoff
        origin=next(i for i,t in enumerate(times) if t>=cutoff+c['secondary_cutoff_transition_s']+step)
        result['post_cutoff_sample']={'elapsed_s':times[origin]-cutoff,'positive_V':vectors['v(rawp)'][origin],'negative_V':-vectors['v(rawn)'][origin]}
        result['hold_to_documented_headroom_loss_s']=hold
        result['hypothetical_total_mute_fits']={str(delay):all(t is None or t>=delay for t in hold.values()) and not flags for delay in c['hypothetical_detection_plus_contact_s']}
    return result,text,'\n'.join(spice.logs)


def main():
    c=json.loads((BASE/'hold-up-contract.json').read_text());base=json.loads((BASE/'envelope-contract.json').read_text())
    base['reservoir_esr_ohm']=c['reservoir_esr_ohm']
    budget=load();preload=load_bounds(json.loads((BASE/'preload-contract.json').read_text()));bounds=regulator_bounds(c)
    assert all(v['divider_current_A'][0]>=c['minimum_regulator_load_A'] for v in bounds.values())
    assert max(v['output_abs_V'][1] for v in bounds.values())<16.5
    rows=[];decks={};logs=[]
    part=c['transformer']
    def case(index,mode,line,cap,profile,vfactor=1):
        return {'id':f'hold{index:03d}','line_factor':mode['selector_V']*line/mode['primary_rating_V'],'frequency_hz':mode['frequency_hz'],
                'winding':{'name':part['mpn']+' typical-resistive surrogate','open_circuit_half_rms_V':part['half_secondary_loaded_V']*(1+part['regulation_typ_fraction'])*vfactor,'series_ohm_per_half':part['half_secondary_loaded_V']*part['regulation_typ_fraction']/part['series_current_A']},
                'reservoir_uF':cap*c['reservoir_min_fraction'],'nominal_cap_uF':cap,'load':profile,'winding_voltage_factor':vfactor,'selector_V':mode['selector_V'],'line_fraction':line}
    cases=[case(i,*args) for i,args in enumerate(itertools.product(c['modes'],c['line_fractions'],c['reservoir_nominal_uF'],base['loads']))]
    for mode,cap,vfactor in itertools.product(c['modes'],[4700,6800],[.95,1.05]):
        # Explicit sensitivity endpoints: low mains/winding at stress; high at idle.
        low = vfactor<1
        cases.append(case(len(cases),mode,.9 if low else 1.1,cap,base['loads'][-1] if low else base['loads'][0],vfactor))
    for mode,cap,phase,vfactor in itertools.product(c['modes'],c['reservoir_nominal_uF'],c['shutdown_phases_deg'],c['shutdown_winding_voltage_factors']):
        x=case(len(cases),mode,.9,cap,base['loads'][-1],vfactor);x.update(cutoff_s=.6+phase/360/mode['frequency_hz'],phase_deg=phase);cases.append(x)
    for x in cases:
        row,text,log=run(c,base,budget,preload,bounds,x);rows.append(row);decks[x['id']]=text;logs.append(x['id']+'\n'+log)
        if len(rows)%12==0:print('Completed',len(rows),'/',len(cases),flush=True)
    shutdown=[r for r in rows if 'cutoff_s' in r['case']]
    refine_indices={min(range(len(rows)),key=lambda i:rows[i]['rails']['positive']['min_V']),max(range(len(rows)),key=lambda i:sum(rows[i]['conditional_regulator_heat_W'].values()))}
    for cap in [4700,6800]:
        relevant=[i for i,r in enumerate(rows) if 'cutoff_s' in r['case'] and r['case']['nominal_cap_uF']==cap]
        refine_indices.add(min(relevant,key=lambda i:min(v if v is not None else 1e9 for v in rows[i]['hold_to_documented_headroom_loss_s'].values())))
    refinements=[]
    for i in sorted(refine_indices):
        fine,text,log=run(c,base,budget,preload,bounds,rows[i]['case'],10e-6)
        dv=max(abs(fine['rails'][s][k]-rows[i]['rails'][s][k]) for s in ['positive','negative'] for k in ['min_V','max_V'])
        assert dv<.02,dv
        dt=None
        if 'hold_to_documented_headroom_loss_s' in fine:
            pairs=[(fine['hold_to_documented_headroom_loss_s'][s],rows[i]['hold_to_documented_headroom_loss_s'][s]) for s in ['positive','negative']]
            assert all((a is None)==(b is None) for a,b in pairs),pairs
            dt=max([abs(a-b) for a,b in pairs if a is not None]+[0])
            assert dt<.0001,dt
        refinements.append({'coarse_id':rows[i]['case']['id'],'max_voltage_delta_V':dv,'max_hold_delta_s':dt,'fine':fine})
        decks[rows[i]['case']['id']+'-fine']=text;logs.append('fine\n'+log)
    spice.logs.clear();spice.cmd('version')
    runtime=BASE.parent/'tools/spice_runtime.py'
    library=Path('/Applications/KiCad/KiCad.app/Contents/Frameworks/libngspice.0.dylib')
    report={'simulator':{'version_output':list(spice.logs),'library_sha256':sha(library),'runtime_sha256':sha(runtime)},'qualified':False,'native_adopted':False,'purchase_ready':False,'bounds':bounds,'cases':rows,'refinements':refinements,'decks':decks,'contract':c,
            'load_dependency_sha256':budget['input_sha256'],
            'input_sha256':{str(p.relative_to(BASE.parent)):sha(p) for p in [BASE/'hold-up-contract.json',BASE/'envelope-contract.json',BASE/'preload-contract.json',BASE/'load-contract.json',BASE.parent/'reverb-600/circuit.json',Path(__file__),BASE/'tools/screen_envelope.py',BASE/'tools/calculate_loads.py',BASE/'tools/check_preload.py']}}
    DEST.mkdir(exist_ok=True);(DEST/'screen.json').write_text(json.dumps(report,indent=2)+'\n');(DEST/'simulator.log').write_text('\n\n'.join(logs)+'\n')
    print('Cases',len(rows),'refinements',len(refinements),'flagged',sum(bool(r['screen_flags']) for r in rows))
    for cap in c['reservoir_nominal_uF']:
        selected=[r for r in shutdown if r['case']['nominal_cap_uF']==cap]
        print(cap,'minimum hold',min(v for r in selected for v in r['hold_to_documented_headroom_loss_s'].values() if v is not None),'20ms fits',sum(r['hypothetical_total_mute_fits']['0.02'] for r in selected),'/',len(selected))


if __name__=='__main__':main()
