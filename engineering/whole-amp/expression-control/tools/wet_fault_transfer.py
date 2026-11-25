"""Source-derived passive wet-fault transfer and unadopted shunt feasibility."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE.parent/'effects-loop/tools'))
from fixture import numeric


def parallel(*values):
    return 1/sum(1/x for x in values if x is not None)


def native_parts(c):
    expected={'R616':('100',{'1':'OUT_BUF','2':'OUT_AC'}),'C607':('1u',{'1':'OUT_AC','2':'WET_AC'}),
              'R617':('1M',{'1':'WET_AC','2':'GND'}),'R618':('1M',{'1':'WET_AC','2':'MIX_OUT'}),
              'R612':('100k',{'1':'FX_RETURN','2':'MIX_OUT'}),'R24':('10M',{'1':'MIX_OUT','2':'GND'})}
    source=json.loads((BASE/c['native_circuit']).read_text())['components'];result={}
    for ref,(value,pins) in expected.items():
        rows=[r for r in source if r['reference']==ref]
        assert len(rows)==1 and rows[0]['pins']==pins and rows[0]['value']==value,(ref,rows)
        result[ref]=numeric(value)
    return result


def ac(p,series,off_cap,hz,source,extra,shunt=None):
    omega=2*math.pi*hz
    rd=p['R612']+source
    rm=parallel(rd,p['R24'],extra)
    zseries=series+1/(1j*omega*p['C607'])
    yw=1/p['R617']+1/(p['R618']+rm)+1j*omega*off_cap+(1/shunt if shunt else 0)
    zw=1/yw
    wet=zw/(zseries+zw)*rm/(p['R618']+rm)
    zground=1/(1/p['R617']+1/zseries+1j*omega*off_cap+(1/shunt if shunt else 0))
    zm=1/(1/p['R24']+(1/extra if extra else 0)+1/(p['R618']+zground))
    dry=zm/(rd+zm)
    return wet,dry


def transient(p,series,source,extra,change,duration,closures,end):
    """Exact piecewise exponential integration of the native coupling capacitor."""
    rm=parallel(p['R612']+source,p['R24'],extra)
    mix_div=rm/(p['R618']+rm)
    events=sorted(set([0,duration,end]+[t for t,r in closures if t<end]))
    cap_voltage=0.0;peak=0.0;integral=0.0;intervals=[]
    for t,next_t in zip(events,events[1:]):
        vin=change if t<duration else 0
        shunts=[r for time,r in closures if time<=t]
        rw=parallel(p['R617'],p['R618']+rm,*shunts)
        tau=(series+rw)*p['C607']
        wet=(vin-cap_voltage)*rw/(series+rw)
        mix=wet*mix_div;dt=next_t-t
        integral+=mix*mix*tau/2*(-math.expm1(-2*dt/tau))
        peak=max(peak,abs(mix))
        intervals.append(dict(start_s=t,end_s=next_t,wet_start_V=wet,mix_start_V=mix,series_current_start_A=(vin-cap_voltage)/(series+rw),tau_s=tau,shunts_ohm=shunts))
        cap_voltage=vin+(cap_voltage-vin)*math.exp(-dt/tau)
    return dict(peak_mix_V=peak,mix_squared_integral_V2s=integral,intervals=intervals)


def main():
    cp=BASE/'wet-fault-contract.json';c=json.loads(cp.read_text());p=native_parts(c)
    ac_rows=[]
    for source,extra,hz in itertools.product(c['return_source_ohm'],c['additional_mix_load_ohm'],c['frequencies_Hz']):
        native_w,native_d=ac(p,p['R616'],0,hz,source,extra)
        candidate_w,candidate_d=ac(p,c['candidate_series_ohm'],c['candidate_off_cap_F'],hz,source,extra)
        muted_w,muted_d=ac(p,c['candidate_series_ohm'],0,hz,source,extra,c['shunt_on_screen_ohm'])
        ac_rows.append(dict(source_ohm=source,extra_load_ohm=extra,hz=hz,
                            wet_gain_ratio_dB=20*math.log10(abs(candidate_w/native_w)),
                            candidate_dry_vs_native_dB=20*math.log10(abs(candidate_d/native_d)),
                            candidate_dry_mute_change_dB=20*math.log10(abs(muted_d/candidate_d)),
                            wet_muted_vs_enabled_dB=20*math.log10(abs(muted_w/candidate_w))))
    assert c['assumed_fast_close_s']==[.00005,.0002] and c['assumed_contact_close_s']==[.005,.015], 'Update named scenario variants for changed timing'
    variants=[('native-no-mute',p['R616'],[]),('native-contact5ms',p['R616'],[(.005,.1)]),
              ('native-contact15ms',p['R616'],[(.015,.1)]),
              ('candidate-fast50us',c['candidate_series_ohm'],[(.00005,c['shunt_on_screen_ohm']),(.015,.1)]),
              ('candidate-fast200us',c['candidate_series_ohm'],[(.0002,c['shunt_on_screen_ohm']),(.015,.1)])]
    rows=[]
    for source,extra,change,duration in itertools.product(c['return_source_ohm'],c['additional_mix_load_ohm'],c['fault_change_V'],c['fault_duration_s']):
        for name,series,closures in variants:
            rows.append(dict(variant=name,source_ohm=source,extra_load_ohm=extra,change_V=change,duration_s=duration,
                             **transient(p,series,source,extra,change,duration,closures,c['end_s'])))
    ratios=[]
    for r in rows:
        if r['variant']!='candidate-fast50us':continue
        baseline=next(x for x in rows if x['variant']=='native-contact15ms' and all(x[k]==r[k] for k in ['source_ohm','extra_load_ohm','change_V','duration_s']))
        ratios.append(r['mix_squared_integral_V2s']/baseline['mix_squared_integral_V2s'])
    fault_max=max(c['fault_change_V']);ron=c['shunt_on_screen_ohm']
    linear_screen=[dict(series_ohm=r,shunt_V=fault_max*ron/(r+ron),within_25C_test_voltage=fault_max*ron/(r+ron)<=c['shunt_linear_test_voltage_V']) for r in [p['R616'],22000,c['candidate_series_ohm']]]
    treble_changes=[]
    for source,extra in itertools.product(c['return_source_ohm'],c['additional_mix_load_ohm']):
        a=next(r for r in ac_rows if r['source_ohm']==source and r['extra_load_ohm']==extra and r['hz']==1000)
        z=next(r for r in ac_rows if r['source_ohm']==source and r['extra_load_ohm']==extra and r['hz']==20000)
        treble_changes.append(z['wet_gain_ratio_dB']-a['wet_gain_ratio_dB'])
    summary=dict(candidate_added_20k_vs_1k_gain_change_dB=[min(treble_changes),max(treble_changes)],native_peak_mix_V=max(r['peak_mix_V'] for r in rows if r['variant']=='native-no-mute'),
                 candidate_peak_mix_V=max(r['peak_mix_V'] for r in rows if r['variant']=='candidate-fast50us'),
                 candidate_wet_gain_change_dB=[min(r['wet_gain_ratio_dB'] for r in ac_rows),max(r['wet_gain_ratio_dB'] for r in ac_rows)],
                 max_candidate_dry_vs_native_dB=max(abs(r['candidate_dry_vs_native_dB']) for r in ac_rows),
                 max_dry_mute_change_dB=max(abs(r['candidate_dry_mute_change_dB']) for r in ac_rows),
                 residual_squared_voltage_ratio_range=[min(ratios),max(ratios)])
    checks=[dict(name='candidate dry gain perturbation within0.1dB screen',passed=summary['max_candidate_dry_vs_native_dB']<=c['dry_gain_change_limit_dB']),
            dict(name='candidate mute dry gain change within0.1dB screen',passed=summary['max_dry_mute_change_dB']<=c['dry_gain_change_limit_dB']),
            dict(name='47k limits33V incremental step within100mV at100ohm',passed=linear_screen[-1]['within_25C_test_voltage']),
            dict(name='native100ohm and22k negative controls rejected',passed=not linear_screen[0]['within_25C_test_voltage'] and not linear_screen[1]['within_25C_test_voltage'])]
    report=dict(scope=c['job'],qualified=False,native_parts=p,summary=summary,checks=checks,linear_shunt_feasibility=linear_screen,ac_cases=ac_rows,transient_cases=rows,limitations=c['limitations'],
                provenance={str(f.relative_to(BASE.parent)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [cp,BASE/c['native_circuit'],Path(__file__),BASE.parent/'effects-loop/tools/fixture.py']})
    (BASE/'results/wet-fault-transfer.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(ac_cases=len(ac_rows),transient_cases=len(rows),summary=summary,checks=checks),indent=2))
    if not all(x['passed'] for x in checks):sys.exit(1)


if __name__=='__main__':main()
