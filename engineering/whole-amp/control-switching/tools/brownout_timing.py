"""Finite-slope secondary collapse; retain failed warning/contact windows."""
import itertools
import json
import math
from pathlib import Path
from ac_loss_detector import BASE, sha, make_deck, spice, profiles, crossing

DEST=BASE/'results/brownout-timing'


def run(contract, detector, thresholds, precision, upstream, base, profile, duration, step, warning=None):
    case=base['case']; start=case['cutoff_s']; end=start+duration+contract['post_ramp_window_s']
    amplitude=case['winding']['open_circuit_half_rms_V']*case['line_factor']*math.sqrt(2)
    lines=upstream['decks'][case['id']].splitlines()
    for i,line in enumerate(lines):
        if line.startswith(('BXs1 ','BXs2 ')):
            sign=1 if line.startswith('BXs1 ') else -1
            node='s1' if sign==1 else 's2'
            lines[i]=f'BX{node} bx{node} 0 V={sign*amplitude}*sin(2*pi*{case["frequency_hz"]}*time)*max(0,min(1,({start+duration}-time)/{duration}))'
        elif line.startswith('.tran '):lines[i]=f'.tran {step} {end} 0 {step}'
    if warning is not None:
        for i,line in enumerate(lines):
            if line.startswith('C201 '):lines[i]=f"C201 cp 0 {warning['positive_cap_F']}"
            elif line.startswith('RP '):lines[i]=f"RP rawp cp {warning['esr_ohm']}"
        r=warning['resistors_ohm']
        extra=f"RRAW rawp raw_sense {r['rail']}\nRRAWG raw_sense 0 {r['ground']}\nRRAWFB detfb raw_sense {r['feedback']}\nIRAWBIAS raw_sense 0 {profile['ib']}"
        extra+=f"\nIRAWCAP rawp 0 PWL(0 0 .05 0 .06 {warning['cap_leakage_A']})"
        lines.insert(lines.index('.end'),extra)
    deck=make_deck('\n'.join(lines)+'\n',detector,profile,step)
    spice.cmd('destroy all');spice.logs.clear();spice.load(deck);spice.cmd('run')
    t=spice.vector('time');assert abs(t[-1]-end)<1e-8
    env=spice.vector('v(env)')
    raw={'positive':spice.vector('v(rawp)'),'negative':[-v for v in spice.vector('v(rawn)')]}
    assert all(math.isfinite(v) for a in [env,*raw.values()] for v in a)
    floor={s:crossing(t,raw[s],base['rails'][s]['required_raw_floor_V'],start) for s in raw}
    first=min(x for x in floor.values() if x is not None)
    latency=detector['detection_propagation_allocation_s']+detector['relay_five_percent_current_screen_s']+detector['additional_contact_and_logic_allocation_s']
    ac=[crossing(t,env,z,start) for z in thresholds['disable_V']]
    assert all(z is not None for z in ac)
    # Memoryless regulator surrogate: threshold+3V raw crossing; useful for diagnosis only.
    rail_detect={s:[crossing(t,raw[s],z+contract['regulator_drop_surrogate_V'],start) for z in precision['results'][s]['abs_ranges_V']['disable']] for s in raw}
    rail_floor={side:crossing(t,raw[side],precision['results'][side]['abs_ranges_V']['disable'][0]-precision['minimum_disable_headroom_margin_V'][side]+contract['regulator_drop_surrogate_V'],start) for side in raw}
    audio_first=min(rail_floor.values())
    last_rail=min(max(times) for times in rail_detect.values())
    trial={str(v):first-crossing(t,raw['positive'],v,start)-latency for v in contract['raw_warning_trial_V']}
    row={'id':case['id']+'-'+profile['name']+'-ramp'+str(duration),'case':case,'profile':profile,'ramp_s':duration,'step_s':step,
         'raw_floor_relative_s':{s:z-start for s,z in floor.items()},
         'ac_detection_relative_s':[z-start for z in ac],
         'ac_reserve_before_raw_floor_s':first-max(ac)-latency,
         'surrogate_audio_floor_relative_s':audio_first-start,
         'surrogate_rail_detection_relative_s':last_rail-start,
         'surrogate_combined_mute_reserve_s':audio_first-min(last_rail,max(ac))-latency,
         'ideal_positive_raw_warning_reserve_s':trial,
         'healthy_positive_raw_min_V':min(raw['positive'][i] for i,tt in enumerate(t) if .4<=tt<=.59)}
    if warning is not None:
        from ac_loss_interruptions import intervals
        spans=[]
        for low,high in itertools.product(warning['thresholds']['disable'],warning['thresholds']['enable']):
            if high<=low:continue
            events=intervals(t,raw['positive'],low,high,start-.01)
            eligible=[(a,z) for a,z in events if (end if z is None else z)-a>=.002 and (z is None or z+.05>=first)]
            at=eligible[0][0] if eligible else None
            spans.append({'disable_V':low,'enable_V':high,'intervals_relative_s':[[a-start,None if z is None else z-start] for a,z in events],
                          'qualified_pulse_start_relative_s':None if at is None else at-start,
                          'conditional_raw_mute_reserve_s':None if at is None else first-at-latency})
        row['raw_warning']=warning
        row['raw_warning_traces']=spans
        row['healthy_enable_margin_V']=row['healthy_positive_raw_min_V']-max(warning['thresholds']['enable'])
    return row,deck,'\n'.join(spice.logs)


def main():
    paths=[BASE/'brownout-timing-contract.json',BASE/'ac-loss-contract.json',BASE/'results/ac-loss/screen.json',BASE/'results/rail-monitor-precision-budget.json',BASE.parent/'aux-supply/results/hold-up/comparison.json']
    contract,detector,ac,precision,upstream=[json.loads(p.read_text()) for p in paths]
    bases=[r for r in upstream['cases'] if r['case'].get('phase_deg') in contract['phases_deg'] and r['case']['winding_voltage_factor']==contract['winding_factor']]
    pp=[p for p in profiles(detector) if p['name'] in contract['profiles']]
    rows=[];decks={};logs=[]
    for base,p,duration in itertools.product(bases,pp,contract['ramp_durations_s']):
        row,deck,log=run(contract,detector,ac['thresholds'],precision,upstream,base,p,duration,contract['step_s'])
        rows.append(row);decks[row['id']]=deck;logs.append(row['id']+'\n'+log)
        if len(rows)%8==0:print('Brownout cases',len(rows),flush=True)
    refined=[]
    for row in [min(rows,key=lambda r:r['ac_reserve_before_raw_floor_s']),min(rows,key=lambda r:r['surrogate_combined_mute_reserve_s'])]:
        base=next(b for b in bases if b['case']['id']==row['case']['id'])
        fine,deck,log=run(contract,detector,ac['thresholds'],precision,upstream,base,row['profile'],row['ramp_s'],contract['step_s']/2)
        differences={k:abs(fine[k]-row[k]) for k in ['ac_reserve_before_raw_floor_s','surrogate_combined_mute_reserve_s']}
        assert max(differences.values())<1e-4,differences
        refined.append({'coarse_id':row['id'],'timing_deltas_s':differences,'fine':fine});decks[row['id']+'-fine']=deck;logs.append(log)
    summary={'cases':len(rows),'ac_raw_reserve_failures':sum(r['ac_reserve_before_raw_floor_s']<0 for r in rows),
             'surrogate_combined_failures':sum(r['surrogate_combined_mute_reserve_s']<0 for r in rows),
             'ideal_raw_trial_failures':{str(v):sum(r['ideal_positive_raw_warning_reserve_s'][str(v)]<0 for r in rows) for v in contract['raw_warning_trial_V']}}
    report={'qualified':False,'native_adopted':False,'purchase_ready':False,'contract':contract,'summary':summary,'cases':rows,'refinements':refined,'decks':decks,
            'input_sha256':{str(p.resolve().relative_to(BASE.parent)):sha(p) for p in [*paths,Path(__file__),BASE/'tools/ac_loss_detector.py']}}
    DEST.mkdir(exist_ok=True);(DEST/'screen.json').write_text(json.dumps(report,indent=2)+'\n');(DEST/'simulator.log').write_text('\n\n'.join(logs)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
