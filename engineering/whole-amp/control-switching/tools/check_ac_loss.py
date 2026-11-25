"""Independent nodal/interface and RC replay audit; no native edits."""
import copy
import hashlib
import itertools
import json
import math
import random
import subprocess
from pathlib import Path
from buffered_rail_budget import solve
from ac_loss_detector import BASE, DEST, spice, sha

ROOT=BASE.parents[2]


def integrity(report,n):
    assert len(report['cases'])==n
    assert len({r['id'] for r in report['cases']})==n
    assert all(report[k] is False for k in ['qualified','native_adopted','purchase_ready'])
    for path,h in report['input_sha256'].items():assert sha(BASE.parent/path)==h,path
    for r in report['cases']:
        assert 'RBIASDET detref sense' in report['decks'][r['id']]
        if 'residual_after_conditional_mute_s' in r:
            tail=report['contract']['relay_five_percent_current_screen_s']+report['contract']['additional_contact_and_logic_allocation_s']
            hold=min(t for t in r['raw_hold_s'].values() if t is not None)
            assert abs(r['residual_after_detection_s']-(hold-max(r['detection_delay_s'])))<1e-10
            assert abs(r['residual_after_conditional_mute_s']-(r['residual_after_detection_s']-tail))<1e-10
    return True


def interfaces(c):
    old=json.loads((BASE/'rail-monitor-precision-contract.json').read_text())
    old_results=json.loads((BASE/'results/rail-monitor-precision-budget.json').read_text())
    for p,h in old_results['inputs'].items():assert sha(BASE/p)==h,p
    r=c['resistors_ohm'];f=c['resistor_total_fraction_allocation'];pu=old['pullup'];v=max(c['reference_V']);ib=max(map(abs,c['input_current_A']))
    extra_ref=v/((r['reference_top']+r['reference_bottom'])*(1-f))+v/(r['sense_bias']*(1-f))+3*ib
    ref_load=old_results['reference_load_upper_A']+extra_ref
    extra_feedback=v/(r['feedback']*(1-f))
    high=old_results['rail_ok_high_min_V']-(extra_feedback+pu['comparator_leak_each_A'])*pu['ohm']*(1+pu['fraction'])
    sink=old_results['comparator_sink_upper_A']+extra_feedback+pu['comparator_leak_each_A']
    # REF5 has no source. Ignore added reference divider shunt loading to overbound backfeed.
    p=old['positive_resistors_ohm'];tol=old['resistor_fraction']
    rp=pu['ohm']*(1+pu['fraction']);rb=old['reference_bleeder_ohm']*(1+old['reference_bleeder_fraction']);rf=p['feedback']*(1-tol)
    vs=old['largest_analog_rail_abs_V']*p['ground']*(1+tol)/(p['rail']*(1-tol)+p['ground']*(1+tol))
    fb=r['feedback']*(1-f);bias=r['sense_bias']*(1-f);rt=r['sense_top']*(1-f);bottom=r['sense_bottom']*(1+f)
    matrix=[[1/rp+1/rf+1/fb,-1/rp,-1/fb],[-1/rp,1/rp+1/rb+1/bias,-1/bias],[-1/fb,-1/bias,1/fb+1/bias+1/rt+1/bottom]]
    currents=[vs/rf+4e-6,2*ib,35/rt+ib]
    off=solve(matrix,currents)
    kcl=max(abs(sum(a*x for a,x in zip(row,off))-b) for row,b in zip(matrix,currents))
    assert ref_load<.01 and high>=min(c['output_high_V']) and sink<.004 and off[0]<.9
    return dict(reference_load_upper_A=ref_load,rail_ok_high_min_V=high,sink_upper_A=sink,passive_ref_off_nodes_V=dict(zip(['RAIL_OK','REF5','SENSE'],off)),off_kcl_error_A=kcl,
                basis='Adds AC detector to previous settled reference budget;35V ENV sensitivity for passive off-state. Semiconductor power-sequence behavior still unqualified.')


def nodal(c):
    rng=random.Random(20261125);maxerr=0;r=c['resistors_ohm'];f=c['resistor_total_fraction_allocation']
    for _ in range(2000):
        q={k:v*rng.uniform(1-f,1+f) for k,v in r.items()};ref=rng.uniform(*c['reference_V']);offset=rng.uniform(*c['offset_V']);ip,im=[rng.uniform(*c['input_current_A']) for _ in range(2)];out=rng.uniform(0,max(c['output_high_V']))
        # Unknowns sense, reference-divider node and envelope; KCL plus trip condition.
        g=sum(1/q[k] for k in ['sense_top','sense_bottom','feedback','sense_bias'])
        solution=solve([[g,0,-1/q['sense_top']],[0,1/q['reference_top']+1/q['reference_bottom'],0],[1,-1,0]],
                       [out/q['feedback']+ref/q['sense_bias']-ip,ref/q['reference_top']-im,offset])
        vm=(ref/q['reference_top']-im)/(1/q['reference_top']+1/q['reference_bottom'])
        formula=q['sense_top']*((vm+offset)*g+ip-out/q['feedback']-ref/q['sense_bias'])
        maxerr=max(maxerr,abs(formula-solution[2]))
    assert maxerr<1e-9
    return {'comparisons':2000,'maximum_voltage_difference_V':maxerr}


def replay(report,row):
    text=report['decks'][row['id']];spice.cmd('destroy all');spice.logs.clear();spice.load(text);spice.cmd('run')
    times=spice.vector('time');actual=spice.vector('v(env)');a=spice.vector('v(ac1)');b=spice.vector('v(ac2)')
    c=report['contract'];p=row['profile'];r={k:v*p['scale'] for k,v in c['resistors_ohm'].items()};r['feed']=c['resistors_ohm']['feed']*p['feed'];cap=c['capacitor_F']*p['cap']
    gs=sum(1/r[k] for k in ['sense_top','sense_bottom','feedback','sense_bias'])
    def slope(e,av,bv):
        sense=(e/r['sense_top']+p['fb']/r['feedback']+p['ref']/r['sense_bias']-p['ib'])/gs
        incoming=sum(max(0,v-e-p['vf'])/r['feed']-p['leak']*min(1,max(0,e-v)) for v in [av,bv])
        return (incoming-e/r['bleed']-e/c['capacitor_leakage_resistance_ohm']-(e-sense)/r['sense_top'])/cap
    y=actual[0];maxerror=0;ys=[y]
    for i in range(1,len(times)):
        dt=times[i]-times[i-1];count=max(1,math.ceil(dt/5e-6));h=dt/count
        def sample(f):return a[i-1]+f*(a[i]-a[i-1]),b[i-1]+f*(b[i]-b[i-1])
        for n in range(count):
            a0,b0=sample(n/count);am,bm=sample((n+.5)/count);a1,b1=sample((n+1)/count)
            k1=slope(y,a0,b0);k2=slope(y+h*k1/2,am,bm);k3=slope(y+h*k2/2,am,bm);k4=slope(y+h*k3,a1,b1)
            y+=h*(k1+2*k2+2*k3+k4)/6
        ys.append(y);maxerror=max(maxerror,abs(y-actual[i]))
    assert maxerror<.02,maxerror
    return {'case_id':row['id'],'max_independent_RK4_error_V':maxerror,'samples':len(times),'maximum_substep_s':5e-6,
            'basis':'Independent branch-current RK4 replay driven by the recorded loaded secondary voltages and same initial ENV voltage; not an independent transformer model.'}


def main():
    report=json.loads((DEST/'screen.json').read_text());pulse=json.loads((DEST/'interruptions.json').read_text())
    integrity(report,84);integrity(pulse,48)
    assert sum('cutoff_s' in r['case'] for r in report['cases'])==72
    assert all(r['healthy_margin_to_max_enable_V']>0 for r in report['cases'])
    assert min(r['sense_min_V'] for r in report['cases'])>0
    assert max(r['sense_max_V'] for r in report['cases'])<11.275-2
    assert min(r.get('residual_after_conditional_mute_s',1) for r in report['cases'])>0
    assert max(r['diode_forward_peak_A'] for r in report['cases'])<.01
    assert max(r['diode_reverse_upper_V'] for r in report['cases'])<75
    assert not any(not r['raw_headroom_retained'] and not r['all_threshold_corners_trigger'] for r in pulse['cases'])
    interruption_reserves=[]
    timing=report['contract']
    for r in pulse['cases']:
        if r['raw_headroom_retained']:continue
        loss=r['first_raw_headroom_loss_relative_s']
        for trace in r['threshold_envelope_traces']:
            start,end=trace['fault_intervals_relative_s'][0]
            expected=loss-start-timing['detection_propagation_allocation_s']-timing['relay_five_percent_current_screen_s']-timing['additional_contact_and_logic_allocation_s']
            assert abs(expected-trace['reserve_before_raw_headroom_loss_s'])<1e-10
            assert expected>0 and (end is None or end>loss)
            interruption_reserves.append(expected)
    short=[r for r in pulse['cases'] if any(z['all_faults_get_2ms'] is False for z in r['threshold_envelope_traces'])]
    assert len(short)==5 and all(r['raw_headroom_retained'] for r in short)
    controls=[]
    for name,fn in [('false qualification',lambda d:d.update(qualified=True)),('missing case',lambda d:d['cases'].pop()),('removed bias',lambda d:d['decks'].__setitem__(d['cases'][0]['id'],d['decks'][d['cases'][0]['id']].replace('RBIASDET detref sense','RBAD detref sense'))),('invented reserve',lambda d:next(r for r in d['cases'] if 'raw_hold_s' in r).__setitem__('residual_after_conditional_mute_s',1))]:
        d=copy.deepcopy(report);fn(d)
        try:integrity(d,84)
        except AssertionError:controls.append({'mutation':name,'rejected':True})
        else:raise AssertionError(name)
    native=json.loads((BASE.parent/'aux-supply/results/hold-up/checks.json').read_text())['native_preserved']
    assert len(native)==22
    for x in native:assert sha(ROOT/x['path'])==x['sha256'],x['path']
    selected=[min(report['cases'],key=lambda r:r['healthy_margin_to_max_enable_V']),min((r for r in report['cases'] if 'raw_hold_s' in r),key=lambda r:r['residual_after_conditional_mute_s'])]
    result={'passed':True,'qualified':False,'native_adopted':False,'purchase_ready':False,'nodal':nodal(report['contract']),
            'shared_interface':interfaces(report['contract']),'independent_replay':[replay(report,r) for r in selected],
            'minimum_interruption_mute_reserve_s':min(interruption_reserves),'short_restart_cases':[r['id'] for r in short],'negative_controls':controls,'native_preserved_count':len(native),
            'inputs':{str(p.relative_to(BASE)):sha(p) for p in [Path(__file__),BASE/'tools/ac_loss_detector.py',BASE/'tools/buffered_rail_budget.py',DEST/'screen.json',DEST/'interruptions.json',BASE/'results/rail-monitor-precision-budget.json',BASE/'rail-monitor-precision-contract.json']}}
    (DEST/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
