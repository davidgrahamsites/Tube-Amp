"""Raw warning candidate using the brownout factory; preserves the failed baseline."""
import itertools,json
from pathlib import Path
from brownout_timing import BASE, DEST, run, sha, profiles
from precision_rail_budget import positive_corners

def main():
    paths=[BASE/'raw-warning-contract.json',BASE/'brownout-timing-contract.json',BASE/'ac-loss-contract.json',BASE/'results/ac-loss/screen.json',BASE/'results/rail-monitor-precision-budget.json',BASE.parent/'aux-supply/results/hold-up/comparison.json',BASE/'rail-monitor-precision-contract.json']
    candidate,contract,detector,ac,precision,upstream,static=[json.loads(p.read_text()) for p in paths]
    static['positive_resistors_ohm']=candidate['positive_resistors_ohm'];static['resistor_fraction']=candidate['resistor_fraction'];threshold=positive_corners(static)
    bases=[r for r in upstream['cases'] if r['case'].get('phase_deg') in contract['phases_deg'] and r['case']['winding_voltage_factor']==contract['winding_factor']]
    # Slow/high envelope profile is late for the AC detector; raw warning is checked separately at all endpoint thresholds.
    profile=next(p for p in profiles(detector) if p['name']=='slow_decay_high_envelope')
    rows=[];decks={};logs=[]
    for base,duration,cp in itertools.product(bases,contract['ramp_durations_s'],candidate['profiles']):
        warning={'profile':cp['name'],'positive_cap_F':candidate['positive_cap_nominal_F']*cp['cap_fraction'],'esr_ohm':cp['esr_ohm'],'cap_leakage_A':candidate['cap_leakage_screen_A'],
                 'resistors_ohm':candidate['positive_resistors_ohm'],'thresholds':threshold['abs_ranges_V']}
        row,deck,log=run(contract,detector,ac['thresholds'],precision,upstream,base,profile,duration,contract['step_s'],warning)
        row['id']+='-'+cp['name'];rows.append(row);decks[row['id']]=deck;logs.append(row['id']+'\n'+log)
        if len(rows)%8==0:print('Raw warning cases',len(rows),flush=True)
    fine=[]
    worst=min(rows,key=lambda r:min(z['conditional_raw_mute_reserve_s'] if z['conditional_raw_mute_reserve_s'] is not None else -100 for z in r['raw_warning_traces']))
    base=next(b for b in bases if b['case']['id']==worst['case']['id'])
    result,deck,log=run(contract,detector,ac['thresholds'],precision,upstream,base,profile,worst['ramp_s'],contract['step_s']/2,worst['raw_warning'])
    errors=[abs(a['conditional_raw_mute_reserve_s']-b['conditional_raw_mute_reserve_s']) for a,b in zip(worst['raw_warning_traces'],result['raw_warning_traces']) if a['conditional_raw_mute_reserve_s'] is not None and b['conditional_raw_mute_reserve_s'] is not None]
    assert errors and max(errors)<1e-4
    fine.append({'coarse_id':worst['id'],'maximum_timing_delta_s':max(errors),'fine':result});decks[worst['id']+'-fine']=deck;logs.append(log)
    summary={'cases':len(rows),'minimum_enable_margin_V':min(r['healthy_enable_margin_V'] for r in rows),
             'no_full_fault_pulse_cases':sum(any(z['conditional_raw_mute_reserve_s'] is None for z in r['raw_warning_traces']) for r in rows),
             'late_cases':sum(any(z['conditional_raw_mute_reserve_s'] is not None and z['conditional_raw_mute_reserve_s']<0 for z in r['raw_warning_traces']) for r in rows),
             'minimum_conditional_reserve_s':min(z['conditional_raw_mute_reserve_s'] for r in rows for z in r['raw_warning_traces'] if z['conditional_raw_mute_reserve_s'] is not None)}
    report={'qualified':False,'native_adopted':False,'purchase_ready':False,'candidate':candidate,'thresholds':threshold,'summary':summary,'cases':rows,'refinements':fine,'decks':decks,
            'input_sha256':{str(p.resolve().relative_to(BASE.parent)):sha(p) for p in [*paths,Path(__file__),BASE/'tools/brownout_timing.py',BASE/'tools/ac_loss_detector.py',BASE/'tools/ac_loss_interruptions.py',BASE/'tools/precision_rail_budget.py']}}
    (DEST/'raw-warning.json').write_text(json.dumps(report,indent=2)+'\n');(DEST/'raw-warning-simulator.log').write_text('\n\n'.join(logs)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
