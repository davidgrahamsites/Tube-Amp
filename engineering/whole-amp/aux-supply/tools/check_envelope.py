"""Read-only audit of raw-supply screening evidence, not circuit acceptance."""
from pathlib import Path
import copy
import hashlib
import json
import math

M=Path(__file__).resolve().parents[1]


def check(c,d):
    assert len(d['cases'])==72
    assert len({r['case']['id'] for r in d['cases']})==72
    assert len(d['refinements'])>=4
    for row in d['cases']:
        assert row['completed_time_s']>=c['simulation']['stop_s']-1e-9
        assert row['kcl_max_error_A']<1e-5
        assert abs(sum(row['conditional_regulator_dissipation_W'].values())-row['conditional_total_W'])<1e-12
        for name in ['raw_positive_V','raw_negative_magnitude_V']:
            values=row[name]
            assert 0<values['min']<=values['mean']<=values['max']
        deck=d['decks'][row['case']['id']]
        assert hashlib.sha256(deck.encode()).hexdigest()==row['deck_sha256']
        assert 'D203 rawn ac1 rect' in deck and 'D204 rawn ac2 rect' in deck
        pmax=max(row['conditional_regulator_dissipation_W'].values())
        total=row['conditional_total_W'];th=c['thermal']
        for thermal in row['thermal']:
            predicted=thermal['ambient_C']+thermal['shared_sink_theta_sa_max_C_per_W']*total+pmax*(th['theta_junction_case_C_per_W']+th['theta_case_sink_assumed_C_per_W'])
            assert abs(predicted-th['junction_design_limit_C'])<1e-9
    for r in d['refinements']:
        assert r['differences']['winding_rms_relative']<0.005
        assert r['fine']['kcl_max_error_A']<1e-5


def main():
    cp=M/'envelope-contract.json';rp=M/'results/envelope/screen.json'
    c=json.loads(cp.read_text());d=json.loads(rp.read_text())
    assert hashlib.sha256(cp.read_bytes()).hexdigest()==d['contract_sha256']
    assert hashlib.sha256((M.parent/'reverb-600/circuit.json').read_bytes()).hexdigest()==d['circuit_sha256']
    check(c,d)
    mutations={
        'missing_case':lambda x:x['cases'].pop(),
        'wrong_negative_diode':lambda x:x['decks'].__setitem__('aux000',x['decks']['aux000'].replace('D203 rawn ac1 rect','D203 ac1 rawn rect')),
        'shared_sink_uses_single_device_heat':lambda x:x['cases'][0]['thermal'][0].__setitem__('shared_sink_theta_sa_max_C_per_W',99),
        'unfinished_run':lambda x:x['cases'][0].__setitem__('completed_time_s',0.2)}
    rejected=[]
    for name,mutate in mutations.items():
        altered=copy.deepcopy(d);mutate(altered)
        try:check(c,altered)
        except AssertionError:rejected.append(name)
        else:raise AssertionError('negative control escaped: '+name)
    # Candidate bleeder calculation is independent of SPICE and remains unadopted.
    proposal={'resistance_ohm':820,'tolerance_fraction':0.01,'rated_power_proposed_W':0.25,
              'minimum_current_A':4.75/(820*1.01),'maximum_current_A':5.25/(820*0.99),
              'maximum_dissipation_W':5.25**2/(820*0.99),
              'status':'engineering proposal only; no selected China-stock part or native integration',
              'caveat':'Initial resistor tolerance only; temperature coefficient/ageing/derating and regulator-startup/reset corners remain to qualify.'}
    assert proposal['minimum_current_A']>0.005
    assert 4.75/(1000*1.01)<0.005,'1k negative control unexpectedly sufficient'
    result={'status':'evidence checks pass; supply remains unqualified','cases_checked':72,
            'refinement_cases':len(d['refinements']),'negative_controls_rejected':rejected,
            'bleeder_proposal':proposal,'screen_sha256':hashlib.sha256(rp.read_bytes()).hexdigest()}
    (rp.parent/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
