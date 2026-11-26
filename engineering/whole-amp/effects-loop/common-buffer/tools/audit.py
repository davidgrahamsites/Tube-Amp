"""Independent waveform metrics and evidence binding for the ceiling decision."""
from pathlib import Path
import copy
import hashlib
import json
import sys
import numpy as np

M=Path(__file__).resolve().parents[1]
ROOT=M.parents[3]


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def metrics(csv, freq):
    data=np.genfromtxt(csv,delimiter=',',names=True)
    t=data['time_s']; y=data['SPEAKER']
    # Least-squares harmonic fit, independent of the producer's FFT indices.
    basis=np.column_stack([np.ones(len(t)),*[v for k in range(1,11)
             for v in [np.sin(2*np.pi*k*freq*t),np.cos(2*np.pi*k*freq*t)]]])
    coefficients=np.linalg.lstsq(basis,y,rcond=None)[0]
    harmonics=np.hypot(coefficients[1::2],coefficients[2::2])
    return data,dict(power_W=float(harmonics[0]**2/16),
                     THD_percent=float(100*np.linalg.norm(harmonics[1:])/harmonics[0]))


def binding(contract,summary):
    assert summary['contract_sha256']==sha(M/'contract.json')
    assert summary['factory_sha256']==sha(M/'tools/run.py')
    assert not summary['adopted'] and not summary['hardware_qualified']
    assert summary['source_sha256']==contract['source_sha256']
    for p,h in contract['source_sha256'].items():assert sha(ROOT/p)==h,p
    assert {r['case']['id'] for r in summary['cases']}=={c['id'] for c in contract['cases']}
    assert len(summary['cases'])==len(contract['cases'])


def main():
    c=json.loads((M/'contract.json').read_text());s=json.loads((M/'results/summary.json').read_text())
    binding(c,s);completed={};failures=[];residual=0
    for row in s['cases']:
        case=row['case']; name=case['id']
        if row['status']!='completed':failures.append(name);continue
        assert row['deck_sha256']==sha(M/'results'/f'{name}.cir')
        assert row['waveform_sha256']==sha(M/'results'/f'{name}.csv')
        assert row['end_s']>=.5
        data,m=metrics(M/'results'/f'{name}.csv',case['freq'])
        err=max(abs(m['power_W']-row['fundamental_load_W']),
                abs(m['THD_percent']-row['signals']['SPEAKER']['THD_2_to_10_percent']))
        residual=max(residual,err);assert err<1e-5,(name,err)
        if case['ceiling_V'] is not None:
            assert max(abs(data['BUF_OUT']))<=case['ceiling_V']+1e-6
        completed[name]=(row,data,m)
    comparisons=[]
    for case in c['cases']:
        if case['ceiling_V'] is None:continue
        ref=case['scenario']+'-unlimited';name=case['id']
        if ref not in completed or name not in completed:continue
        a,ad,am=completed[ref];b,bd,bm=completed[name]
        assert np.allclose(ad['time_s'],bd['time_s'],rtol=0,atol=1e-10)
        gain=10*np.log10(bm['power_W']/am['power_W'])
        thd=bm['THD_percent']-am['THD_percent']
        nrmse=np.sqrt(np.mean((ad['SPEAKER']-bd['SPEAKER'])**2)/np.mean(ad['SPEAKER']**2))
        limits=c['comparison_limits']
        comparisons.append(dict(id=name,reference_W=am['power_W'],candidate_W=bm['power_W'],
             fundamental_delta_dB=float(gain),THD_delta_percentage_points=thd,
             waveform_NRMSE=float(nrmse),clipped_fraction=b['clipped_fraction'],
             settled=max(a['settling_relative']['SPEAKER'],b['settling_relative']['SPEAKER'])<.01,
             sampled_comparison_pass=bool(abs(gain)<=limits['fundamental_delta_dB'] and
               abs(thd)<=limits['THD_delta_percentage_points'] and nrmse<=limits['waveform_NRMSE'])))
    negatives=[]
    for label in ['missing case','wrong source','false adoption']:
        bad=copy.deepcopy(s)
        if label=='missing case':bad['cases'].pop()
        elif label=='wrong source':bad['source_sha256']={}
        else:bad['adopted']=True
        try:binding(c,bad)
        except AssertionError:negatives.append(label)
        else:raise AssertionError(label)
    refinement=[]
    r=json.loads((M/'results/refinement.json').read_text())
    assert r['contract_sha256']==sha(M/'contract.json')
    assert r['factory_sha256']==sha(M/'tools/run.py')
    assert r['source_sha256']==c['source_sha256']
    for fine in r['cases']:
        assert fine['status']=='completed'
        name=fine['case']['id'];base=name.removesuffix('-fine')
        assert fine['case']['refinement']==2 and fine['step_s']==completed[base][0]['step_s']/2
        assert fine['deck_sha256']==sha(M/'results'/f'{name}.cir')
        assert fine['deck_sha256']==completed[base][0]['deck_sha256']
        assert fine['waveform_sha256']==sha(M/'results'/f'{name}.csv')
        _,fm=metrics(M/'results'/f'{name}.csv',fine['case']['freq'])
        bm=completed[base][2]
        delta=abs(fm['power_W']-bm['power_W'])/fm['power_W']
        thd=abs(fm['THD_percent']-bm['THD_percent'])
        assert delta<.001 and thd<.01
        refinement.append(dict(id=name,relative_power_change=delta,THD_delta_percentage_points=thd))
    target=json.loads((M/'results/target.json').read_text())
    assert target['contract_sha256']==sha(M/'contract.json')
    assert target['factory_sha256']==sha(M/'tools/target.py')
    assert target['worker_sha256']==sha(M/'tools/run.py')
    assert target['source_sha256']==c['source_sha256']
    target_results=[]
    for row in target['cases']:
        assert row['status']=='completed',row
        name=row['case']['id']
        assert sha(M/'results'/f'{name}.cir')==row['deck_sha256']
        assert sha(M/'results'/f'{name}.csv')==row['waveform_sha256']
        _,tm=metrics(M/'results'/f'{name}.csv',row['case']['freq'])
        assert abs(tm['power_W']-row['fundamental_load_W'])<1e-5
        target_results.append(dict(id=name,**tm,FX_SEND_peak_V=max(abs(row['signals']['FX_SEND']['min_V']),
                   abs(row['signals']['FX_SEND']['max_V'])),settling_relative=row['settling_relative']['SPEAKER']))
    retry=json.loads((M/'results/retry.json').read_text())
    assert retry['retry_factory_sha256']==sha(M/'tools/retry.py')
    assert retry['worker_sha256']==sha(M/'tools/run.py')
    for row in retry['cases']:
        assert row['prior_result']['status']=='timeout'
        assert sha(M/'results'/(row['id']+'.cir'))==row['unchanged_deck_sha256']
        result=next(r for r in s['cases'] if r['case']['id']==row['id'])
        assert result['status']==row['final_status']
    out=dict(evidence_check_passed=True,negative_controls=negatives,failed_cases=failures,
             independent_metric_max_error=residual,comparisons=comparisons,
             refinement=refinement,target_probe=target_results,
             retried_cases=len(retry['cases']),
             hardware_qualified=False,adopted=False,
             input_sha256={p:sha(M/p) for p in ['contract.json','tools/run.py','tools/audit.py',
               'tools/retry.py','tools/target.py','results/summary.json','results/refinement.json',
               'results/target.json','results/retry.json']})
    (M/'results/audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
