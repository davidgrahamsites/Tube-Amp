"""Secondary envelope detector integrated with retained auxiliary rectifier decks.

Static threshold bounds are separate from transient front-end behavior. No CAD writes.
"""
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE.parent/'tools'))
import spice_runtime as spice
DEST=BASE/'results/ac-loss'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def thresholds(c):
    r=c['resistors_ohm']; f=c['resistor_total_fraction_allocation']; rows=[]
    keys=['sense_top','sense_bottom','feedback','reference_top','reference_bottom','sense_bias']
    for scales in itertools.product([1-f,1+f],repeat=6):
        rr={k:r[k]*s for k,s in zip(keys,scales)}
        for ref,offset,ibp,ibm in itertools.product(c['reference_V'],c['offset_V'],c['input_current_A'],c['input_current_A']):
            vm=(ref/rr['reference_top']-ibm)/(1/rr['reference_top']+1/rr['reference_bottom'])
            g=1/rr['sense_top']+1/rr['sense_bottom']+1/rr['feedback']+1/rr['sense_bias']
            trip=lambda output:rr['sense_top']*((vm+offset)*g+ibp-output/rr['feedback']-ref/rr['sense_bias'])
            rows.append({'enable_V':[trip(o) for o in c['output_low_V']], 'disable_V':[trip(o) for o in c['output_high_V']],
                         'minimum_hysteresis_V':rr['sense_top']/rr['feedback']*(min(c['output_high_V'])-max(c['output_low_V']))})
    return {'corners':len(rows),'enable_V':[min(min(x['enable_V']) for x in rows),max(max(x['enable_V']) for x in rows)],
            'disable_V':[min(min(x['disable_V']) for x in rows),max(max(x['disable_V']) for x in rows)],
            'minimum_hysteresis_V':min(x['minimum_hysteresis_V'] for x in rows)}


def profiles(c):
    f=c['resistor_total_fraction_allocation'];cf=c['capacitor_total_fraction_allocation']
    return [dict(name='nominal',scale=1,feed=1,cap=1,vf=.7,leak=0,fb=5,ref=5,ib=0),
            dict(name='fast_decay_low_envelope',scale=1-f,feed=1+f,cap=1-cf,vf=max(c['diode_forward_drop_screen_V']),leak=max(c['reverse_leakage_each_screen_A']),fb=0,ref=min(c['reference_V']),ib=max(c['input_current_A'])),
            dict(name='slow_decay_high_envelope',scale=1+f,feed=1-f,cap=1+cf,vf=min(c['diode_forward_drop_screen_V']),leak=min(c['reverse_leakage_each_screen_A']),fb=max(c['output_high_V']),ref=max(c['reference_V']),ib=min(c['input_current_A']))]


def make_deck(original,c,p,step):
    r=c['resistors_ohm']; rr={k:v*p['scale'] for k,v in r.items()};rr['feed']=r['feed']*p['feed']
    extra=f'''* Explicit bounded secondary envelope; not a manufacturer diode model
BSA ac1 env I=max(0,v(ac1,env)-{p['vf']})/{rr['feed']}-{p['leak']}*min(1,max(0,v(env,ac1)))
BSB ac2 env I=max(0,v(ac2,env)-{p['vf']})/{rr['feed']}-{p['leak']}*min(1,max(0,v(env,ac2)))
CENV env 0 {c['capacitor_F']*p['cap']}
RBENV env 0 {rr['bleed']}
RSTOP env sense {rr['sense_top']}
RSBOT sense 0 {rr['sense_bottom']}
RFBDET detfb sense {rr['feedback']}
VFBDET detfb 0 {p['fb']}
VREFDET detref 0 {p['ref']}
RBIASDET detref sense {rr['sense_bias']}
IIBDET sense 0 {p['ib']}
RCAPLEAK env 0 {c['capacitor_leakage_resistance_ohm']}
.save v(env) v(sense) v(ac1) v(ac2) @BSA[i] @BSB[i]
'''
    lines=original.splitlines();out=[]
    for line in lines:
        if line.startswith('.tran '):
            fields=line.split();fields[1]=str(step);fields[-1]=str(step);line=' '.join(fields)
        if line=='.end':out.append(extra)
        out.append(line)
    return '\n'.join(out)+'\n'


def crossing(t,v,threshold,start):
    i=next(i for i,x in enumerate(t) if x>=start)
    if v[i]<=threshold:return t[i]
    for j in range(i+1,len(t)):
        if v[j]<=threshold:
            return t[j-1]+(t[j]-t[j-1])*(v[j-1]-threshold)/(v[j-1]-v[j])
    return None


def run(c,tb,base,p,step=20e-6):
    text=make_deck(base['deck'],c,p,step)
    spice.cmd('destroy all');spice.logs.clear();spice.load(text);spice.cmd('run')
    t=spice.vector('time');end=float(next(l for l in text.splitlines() if l.startswith('.tran ')).split()[2]);assert abs(t[-1]-end)<1e-8,spice.logs[-20:]
    vectors={n:spice.vector(n) for n in ['v(env)','v(sense)','v(rawp)','v(rawn)','v(ac1)','v(ac2)','@bsa[i]','@bsb[i]']}
    assert all(math.isfinite(v) for a in vectors.values() for v in a)
    idx=[i for i,x in enumerate(t) if .4<=x<=.6];env=vectors['v(env)']
    row={'id':base['case']['id']+'-'+p['name'],'case':base['case'],'profile':p,'step_s':step,
         'steady_envelope_min_V':min(env[i] for i in idx),'steady_envelope_max_V':max(env[i] for i in idx),
         'healthy_margin_to_max_enable_V':min(env[i] for i in idx)-max(tb['enable_V']),
         'sense_min_V':min(vectors['v(sense)']),'sense_max_V':max(vectors['v(sense)']),
         'diode_forward_peak_A':max(max(vectors['@bsa[i]']),max(vectors['@bsb[i]'])),
         'diode_reverse_upper_V':max(max(env[i]-vectors[n][i] for i in range(len(t))) for n in ['v(ac1)','v(ac2)'])}
    cutoff=base['case'].get('cutoff_s')
    if cutoff is not None:
        detect=[crossing(t,env,th,cutoff) for th in tb['disable_V']]
        assert all(x is not None for x in detect)
        raw_times={side:crossing(t,[sign*x for x in vectors[node]],base['rails'][side]['required_raw_floor_V'],cutoff)
                   for side,node,sign in [('positive','v(rawp)',1),('negative','v(rawn)',-1)]}
        earliest=min(x for x in raw_times.values() if x is not None)
        delay=c['detection_propagation_allocation_s'];tail=c['relay_five_percent_current_screen_s']+c['additional_contact_and_logic_allocation_s']
        row.update(detection_delay_s=[min(detect)-cutoff+delay,max(detect)-cutoff+delay],
                   raw_hold_s={s:None if x is None else x-cutoff for s,x in raw_times.items()},
                   residual_after_detection_s=earliest-max(detect)-delay,
                   residual_after_conditional_mute_s=earliest-max(detect)-delay-tail,
                   steady_healthy=row['healthy_margin_to_max_enable_V']>0)
    return row,text,'\n'.join(spice.logs)


def main():
    c=json.loads((BASE/'ac-loss-contract.json').read_text());tb=thresholds(c)
    upstream_path=BASE/c['supply_evidence'];upstream=json.loads(upstream_path.read_text())
    rows=[];decks={};logs=[]
    for base_row,p in itertools.product(upstream['cases'],profiles(c)):
        source=dict(base_row,deck=upstream['decks'][base_row['case']['id']])
        row,text,log=run(c,tb,source,p);rows.append(row);decks[row['id']]=text;logs.append(row['id']+'\n'+log)
        if len(rows)%12==0:print('Completed',len(rows),flush=True)
    selected=[min((r for r in rows if 'cutoff_s' in r['case']),key=lambda r:r['residual_after_conditional_mute_s']),min(rows,key=lambda r:r['healthy_margin_to_max_enable_V'])]
    refinements=[]
    for r in selected:
        b=next(x for x in upstream['cases'] if x['case']['id']==r['case']['id']);source=dict(b,deck=upstream['decks'][b['case']['id']])
        fine,text,log=run(c,tb,source,r['profile'],10e-6)
        dv=abs(fine['steady_envelope_min_V']-r['steady_envelope_min_V']);assert dv<.02,dv
        dt=None
        if 'detection_delay_s' in r:
            dt=max(abs(x-y) for x,y in zip(r['detection_delay_s'],fine['detection_delay_s']));assert dt<1e-4,dt
        refinements.append(dict(coarse_id=r['id'],voltage_delta_V=dv,detection_delta_s=dt,fine=fine));decks[r['id']+'-fine']=text;logs.append(log)
    result={'qualified':False,'native_adopted':False,'purchase_ready':False,'contract':c,'thresholds':tb,'cases':rows,'refinements':refinements,'decks':decks,
            'simulator':upstream['simulator'],'input_sha256':{str(p.resolve().relative_to(BASE.parent)):sha(p) for p in [BASE/'ac-loss-contract.json',upstream_path,Path(__file__)]}}
    DEST.mkdir(exist_ok=True);(DEST/'screen.json').write_text(json.dumps(result,indent=2)+'\n');(DEST/'simulator.log').write_text('\n\n'.join(logs)+'\n')
    print('thresholds',tb)
    print('cases',len(rows),'minimum healthy margin',min(r['healthy_margin_to_max_enable_V'] for r in rows))
    shutdown=[r for r in rows if 'cutoff_s' in r['case']]
    print('max detection delay',max(max(r['detection_delay_s']) for r in shutdown),'min post-mute reserve',min(r['residual_after_conditional_mute_s'] for r in shutdown))


if __name__=='__main__':main()
