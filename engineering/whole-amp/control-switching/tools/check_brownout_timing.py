"""Evidence audit: retain engineering failures; check hashes, timing and discharge independently."""
import bisect,copy,itertools,json,math,random
from pathlib import Path
from ac_loss_detector import BASE,sha,spice
from buffered_rail_budget import solve
DEST=BASE/'results/brownout-timing'


def integrity(report,n):
    assert len(report['cases'])==n and len({r['id'] for r in report['cases']})==n
    assert all(report[k] is False for k in ['qualified','native_adopted','purchase_ready'])
    for p,h in report['input_sha256'].items():assert sha(BASE.parent/p)==h,p
    for row in report['cases']:
        assert row['id'] in report['decks']
        assert row['ac_reserve_before_raw_floor_s'] == row['ac_reserve_before_raw_floor_s']
    return True


def interpolate(t,v,time):
    i=bisect.bisect_left(t,time);assert 0<i<len(t)
    return v[i-1]+(v[i]-v[i-1])*(time-t[i-1])/(t[i]-t[i-1])


def discharge(report,row):
    spice.cmd('destroy all');spice.logs.clear();spice.load(report['decks'][row['id']]);spice.cmd('run')
    t=spice.vector('time');raw=spice.vector('v(rawp)')
    expected_end=row['case']['cutoff_s']+row['ramp_s']+.5
    assert abs(t[-1]-expected_end)<1e-8
    t0=row['case']['cutoff_s']+row['ramp_s']+.002;t1=t0+.01
    y0=interpolate(t,raw,t0);y1=interpolate(t,raw,t1)
    original=json.loads((BASE.parent/'aux-supply/results/hold-up/comparison.json').read_text())
    source=next(r for r in original['cases'] if r['case']['id']==row['case']['id'])
    current=source['raw_load_A']['positive'];a=1e-8;b=current;esr=.15;cap=source['case']['reservoir_uF']*1e-6
    w=row.get('raw_warning')
    if w:
        r=w['resistors_ohm'];g=sum(1/v for v in r.values());a+=(1-1/(r['rail']*g))/r['rail']
        b+=w['cap_leakage_A']-(row['profile']['fb']/r['feedback']-row['profile']['ib'])/(r['rail']*g)
        esr=w['esr_ohm'];cap=w['positive_cap_F']
    expected=y0*math.exp(-a*(t1-t0)/(cap*(1+a*esr)))-b/a*(-math.expm1(-a*(t1-t0)/(cap*(1+a*esr))))
    error=abs(expected-y1);assert error<.002,error
    return {'id':row['id'],'independent_closed_form_discharge_error_V':error,'interval_s':[t0,t1],
            'basis':'Positive raw capacitor after secondary reaches zero; exact linear resistor/loading discharge equation. Same retained source model, not regulator/contact validation.'}


def main():
    base=json.loads((DEST/'screen.json').read_text());trial=json.loads((DEST/'raw-warning.json').read_text());ac=json.loads((BASE/'ac-loss-contract.json').read_text())
    integrity(base,32);integrity(trial,32)
    latency=ac['detection_propagation_allocation_s']+ac['relay_five_percent_current_screen_s']+ac['additional_contact_and_logic_allocation_s']
    for r in [*base['cases'],*trial['cases']]:
        expected=min(r['raw_floor_relative_s'].values())-max(r['ac_detection_relative_s'])-latency
        assert abs(expected-r['ac_reserve_before_raw_floor_s'])<1e-10
        for tr in r.get('raw_warning_traces',[]):
            at=tr['qualified_pulse_start_relative_s']
            if at is not None:assert abs(min(r['raw_floor_relative_s'].values())-at-latency-tr['conditional_raw_mute_reserve_s'])<1e-10
    assert base['summary']['ac_raw_reserve_failures']==20 and base['summary']['surrogate_combined_failures']==14
    failed_enable=[r['id'] for r in trial['cases'] if r['healthy_enable_margin_V']<0]
    assert len(failed_enable)==8 and trial['summary']['late_cases']==0
    static=json.loads((BASE/'rail-monitor-precision-contract.json').read_text());c=trial['candidate'];rng=random.Random(20261125);worst=0
    for _ in range(2000):
        r={k:v*rng.uniform(1-c['resistor_fraction'],1+c['resistor_fraction']) for k,v in c['positive_resistors_ohm'].items()}
        ref=rng.uniform(*static['reference_V']);off=rng.uniform(*static['offset_V']);bias=rng.uniform(*static['input_current_A']);fb=rng.uniform(0,5.25)
        g=sum(1/v for v in r.values());closed=r['rail']*((ref+off)*g-fb/r['feedback']-bias)
        independent=solve([[1,0],[g,-1/r['rail']]],[ref+off,fb/r['feedback']+bias])[1]
        worst=max(worst,abs(closed-independent))
    assert worst<1e-9
    provenance=json.loads((BASE.parent/'aux-supply/results/hold-up/checks.json').read_text())['native_preserved']
    for row in provenance:assert sha(BASE.parents[2]/row['path'])==row['sha256']
    rejects=[]
    for label,change in [('false qualification',lambda d:d.update(qualified=True)),('removed case',lambda d:d['cases'].pop()),('altered source hash',lambda d:d['input_sha256'].__setitem__(next(iter(d['input_sha256'])),'0'*64))]:
        test=copy.deepcopy(trial);change(test)
        try:integrity(test,32)
        except AssertionError:rejects.append(label)
        else:raise AssertionError(label)
    sources=json.loads((DEST/'source-observations.json').read_text());pdf=sources['manufacturer_pdf'];assert sha(BASE/pdf['path'])==pdf['sha256']
    assert math.isclose(trial['candidate']['profiles'][1]['cap_fraction'],(1-sources['specifications']['initial_tolerance_fraction'])*(1-sources['specifications']['post_load_cap_change_fraction']),abs_tol=1e-12)
    report={'evidence_checks_passed':True,'engineering_accepted':False,'qualified':False,'native_adopted':False,'purchase_ready':False,
            'nodal_comparisons':2000,'maximum_nodal_error_V':worst,'failed_healthy_enable_cases':failed_enable,'negative_controls_rejected':rejects,
            'discharge_checks':[discharge(base,min(base['cases'],key=lambda r:r['surrogate_combined_mute_reserve_s'])),discharge(trial,min(trial['cases'],key=lambda r:r['healthy_enable_margin_V']))],
            'native_preserved_count':len(provenance),'inputs':{str(p.relative_to(BASE)):sha(p) for p in [Path(__file__),DEST/'screen.json',DEST/'raw-warning.json',DEST/'source-observations.json',BASE/'ac-loss-contract.json',BASE/'tools/buffered_rail_budget.py']}}
    (DEST/'checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
