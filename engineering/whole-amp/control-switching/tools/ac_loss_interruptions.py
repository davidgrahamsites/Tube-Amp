"""Finite secondary outages: reuse AC detector front end, retain untriggered cases."""
import itertools
import json
import math
from pathlib import Path
from ac_loss_detector import BASE, DEST, sha, make_deck, spice, profiles, crossing


def intervals(t,v,low,high,start):
    healthy=True;opened=None;out=[]
    for i in range(1,len(t)):
        if t[i]<start:continue
        if healthy and v[i]<=low:
            opened=t[i-1]+(t[i]-t[i-1])*(v[i-1]-low)/(v[i-1]-v[i]) if v[i-1]>low else t[i]
            healthy=False
        elif not healthy and v[i]>=high:
            closed=t[i-1]+(t[i]-t[i-1])*(high-v[i-1])/(v[i]-v[i-1]) if v[i-1]<high else t[i]
            out.append([opened,closed]);opened=None;healthy=True
    if opened is not None:out.append([opened,None])
    return out


def run(c,ic,thresholds,upstream,b,p,duration,step=20e-6):
    x=b['case'];cut=x['cutoff_s'];restore=cut+duration;transition=1e-6
    lines=upstream['decks'][x['id']].splitlines();amp=x['winding']['open_circuit_half_rms_V']*x['line_factor']*math.sqrt(2)
    off=f'max(0,min(1,({cut+transition}-time)/{transition}))'
    on=f'max(0,min(1,(time-{restore})/{transition}))'
    for i,line in enumerate(lines):
        if line.startswith(('BXs1 ','BXs2 ')):
            sign=1 if line.startswith('BXs1 ') else -1;node='s1' if sign==1 else 's2'
            lines[i]=f'BX{node} bx{node} 0 V={sign*amp}*sin(2*pi*{x["frequency_hz"]}*time)*({off}+{on})'
        elif line.startswith('.tran '):lines[i]=f'.tran {step} {restore+ic["post_restore_window_s"]} 0 {step}'
    text=make_deck('\n'.join(lines)+'\n',c,p,step)
    spice.cmd('destroy all');spice.logs.clear();spice.load(text);spice.cmd('run')
    t=spice.vector('time');assert abs(t[-1]-restore-ic['post_restore_window_s'])<1e-8,spice.logs[-20:]
    env=spice.vector('v(env)');raw={'positive':spice.vector('v(rawp)'),'negative':[-v for v in spice.vector('v(rawn)')]}
    assert all(math.isfinite(v) for a in [env,*raw.values()] for v in a)
    traces=[]
    for low,high in itertools.product(thresholds['disable_V'],thresholds['enable_V']):
        if high<=low:continue
        spans=intervals(t,env,low,high,cut-.01)
        traces.append({'disable_V':low,'enable_V':high,'fault_intervals_relative_s':[[a-cut,None if z is None else z-cut] for a,z in spans],
                       'all_faults_get_2ms':all(z is not None and z-a>=ic['full_restart_discharge_screen_s'] for a,z in spans) if spans else None})
    mins={s:min(v[i] for i,tt in enumerate(t) if tt>=cut) for s,v in raw.items()}
    raw_crossings={side:crossing(t,values,b['rails'][side]['required_raw_floor_V'],cut) for side,values in raw.items()}
    first_loss=min((z for z in raw_crossings.values() if z is not None),default=None)
    for trace in traces:
        spans=trace['fault_intervals_relative_s']
        assertion=cut+spans[0][0] if spans else None
        trace['reserve_before_raw_headroom_loss_s']=None if first_loss is None or assertion is None else first_loss-assertion-c['detection_propagation_allocation_s']-c['relay_five_percent_current_screen_s']-c['additional_contact_and_logic_allocation_s']
    row={'id':x['id']+'-'+p['name']+'-'+str(duration),'case':x,'profile':p,'duration_s':duration,'step_s':step,
         'raw_min_V':mins,'first_raw_headroom_loss_relative_s':None if first_loss is None else first_loss-cut,'raw_headroom_retained':all(mins[s]>=b['rails'][s]['required_raw_floor_V'] for s in raw),
         'envelope_min_during_event_V':min(env[i] for i,tt in enumerate(t) if tt>=cut),
         'threshold_envelope_traces':traces,'no_threshold_corner_triggers':all(not z['fault_intervals_relative_s'] for z in traces),
         'all_threshold_corners_trigger':all(bool(z['fault_intervals_relative_s']) for z in traces)}
    return row,text,'\n'.join(spice.logs)


def main():
    c=json.loads((BASE/'ac-loss-contract.json').read_text());ic=json.loads((BASE/'ac-loss-interruption-contract.json').read_text())
    main_path=DEST/'screen.json';main=json.loads(main_path.read_text());tb=main['thresholds']
    upstream_path=BASE/c['supply_evidence'];upstream=json.loads(upstream_path.read_text())
    bases=[b for b in upstream['cases'] if b['case'].get('phase_deg') in ic['phases_deg'] and b['case']['winding_voltage_factor']==ic['winding_factor']]
    pp=[p for p in profiles(c) if p['name'] in ic['profile_names']];rows=[];decks={};logs=[]
    for b,p,d in itertools.product(bases,pp,ic['durations_s']):
        row,text,log=run(c,ic,tb,upstream,b,p,d);rows.append(row);decks[row['id']]=text;logs.append(row['id']+'\n'+log)
        if len(rows)%12==0:print('Interruptions completed',len(rows),flush=True)
    # Refine both a missed short event and a long interruption that loses headroom.
    refinements=[]
    for r in [rows[1],next(x for x in rows if not x['raw_headroom_retained'])]:
        b=next(b for b in bases if b['case']['id']==r['case']['id'])
        fine,text,log=run(c,ic,tb,upstream,b,r['profile'],r['duration_s'],10e-6)
        dv=max(abs(fine['raw_min_V'][s]-r['raw_min_V'][s]) for s in ['positive','negative']);assert dv<.02,dv
        assert fine['raw_headroom_retained']==r['raw_headroom_retained']
        refinements.append({'coarse_id':r['id'],'raw_voltage_delta_V':dv,'fine':fine});decks[r['id']+'-fine']=text;logs.append(log)
    report={'qualified':False,'native_adopted':False,'purchase_ready':False,'contract':ic,'thresholds':tb,'cases':rows,'refinements':refinements,'decks':decks,
            'input_sha256':{str(p.resolve().relative_to(BASE.parent)):sha(p) for p in [BASE/'ac-loss-contract.json',BASE/'ac-loss-interruption-contract.json',main_path,upstream_path,Path(__file__),BASE/'tools/ac_loss_detector.py']}}
    (DEST/'interruptions.json').write_text(json.dumps(report,indent=2)+'\n');(DEST/'interruptions-simulator.log').write_text('\n\n'.join(logs)+'\n')
    print('Interruption cases',len(rows),'lost headroom',sum(not r['raw_headroom_retained'] for r in rows))
    print('Blind and lost headroom',sum(not r['raw_headroom_retained'] and not r['all_threshold_corners_trigger'] for r in rows))
    print('Short asserted hold retained',sum(any(z['all_faults_get_2ms'] is False for z in r['threshold_envelope_traces']) for r in rows))


if __name__=='__main__':main()
