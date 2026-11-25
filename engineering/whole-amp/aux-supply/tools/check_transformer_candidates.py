"""Audit candidate comparison; zero model flags cannot authorize selection."""
import copy
import hashlib
import itertools
import json
import math
from calculate_loads import MODULE, load, sha


def check(d):
    for path,digest in d['input_sha256'].items():assert sha(MODULE/path)==digest,path
    assert d['budget']==load()
    assert d['factory_sha256']==sha(MODULE/'tools/screen_transformer_candidates.py')
    c=d['contract']; assert c==json.loads((MODULE/'transformer-candidates.json').read_text())
    expected=set(itertools.product([p['mpn'] for p in c['candidates']],[m['selector_V'] for m in c['modes']],c['line_fractions'],c['reservoir_nominal_uF'],[p['name'] for p in d['effective_model']['loads']]))
    actual=set()
    for r in d['cases']:
        case=r['case'];part=next(p for p in c['candidates'] if p['mpn']==r['mpn']);mode=next(m for m in c['modes'] if m['selector_V']==r['selector_V'])
        fraction=next(f for f in c['line_fractions'] if math.isclose(r['mains_V'],mode['selector_V']*f))
        actual.add((r['mpn'],r['selector_V'],fraction,r['nominal_cap_uF'],case['load']['name']))
        assert math.isclose(case['line_factor'],r['mains_V']/mode['primary_rating_V'],rel_tol=1e-12)
        assert case['frequency_hz']==mode['frequency_hz']
        assert case['reservoir_uF']==r['nominal_cap_uF']*c['reservoir_min_fraction']
        w=case['winding'];v=part['half_secondary_loaded_V'];reg=part['regulation_typ_fraction']
        assert math.isclose(w['open_circuit_half_rms_V'],v*(1+reg))
        assert math.isclose(w['series_ohm_per_half'],v*reg/part['series_current_A'])
        assert math.isclose(r['completed_time_s'],d['effective_model']['simulation']['stop_s'],abs_tol=1e-9) and r['kcl_max_error_A']<1e-5
        assert hashlib.sha256(d['decks'][case['id']].encode()).hexdigest()==r['deck_sha256']
        assert 'half_winding_exceeds_provisional_0p25A' not in r['screen_flags']
        assert ('half_winding_above_candidate_rating' in r['screen_flags'])==(max(r['half_winding_rms_A'].values())>part['series_current_A'])
        limits=d['effective_model']['raw_screen_V']
        for flag,truth in [('positive_below_documented_range',r['raw_positive_V']['min']<limits['positive_min']),('positive_above_documented_range',r['raw_positive_V']['max']>limits['positive_max']),('negative_below_documented_range',r['raw_negative_magnitude_V']['min']<limits['negative_min_magnitude']),('negative_above_documented_range',r['raw_negative_magnitude_V']['max']>limits['negative_max_magnitude'])]:
            assert (flag in r['screen_flags'])==truth
        assert r['existing_ST_U4_above_documented_range']==(r['raw_positive_V']['max']>25)
    assert len(d['cases'])==len(expected) and actual==expected
    for summary in d['summary']:
        rs=[r for r in d['cases'] if (r['mpn'],r['nominal_cap_uF'])==(summary['mpn'],summary['cap_uF'])]
        assert summary['cases']==len(rs) and summary['flagged']==sum(bool(r['screen_flags']) for r in rs)
    assert len(d['refinements'])>=8
    byid={r['case']['id']:r for r in d['cases']}
    for r in d['refinements']:
        coarse=byid[r['coarse_id']];fine=r['fine']; assert fine['case']==coarse['case']
        assert fine['step_s']==coarse['step_s']/2 and fine['kcl_max_error_A']<1e-5
        dv=max(abs(fine[k][n]-coarse[k][n]) for k in ['raw_positive_V','raw_negative_magnitude_V'] for n in ['min','mean','max'])
        di=max(abs(fine['half_winding_rms_A'][k]/coarse['half_winding_rms_A'][k]-1) for k in coarse['half_winding_rms_A'])
        assert math.isclose(dv,r['voltage_delta_V']) and math.isclose(di,r['rms_relative_delta']) and dv<.01 and di<.005
    assert not d['native_adopted'] and not d['purchase_ready']


def main():
    path=MODULE/'results/transformer-candidates/screen.json';d=json.loads(path.read_text());check(d)
    mutations={
        'nominal_line_factor_reused':lambda x:x['cases'][0]['case'].__setitem__('line_factor',.9),
        'old_0p25A_limit_reused':lambda x:x['cases'][0]['screen_flags'].append('half_winding_exceeds_provisional_0p25A'),
        'missing_case':lambda x:x['cases'].pop(),
        'zero_flags_claimed_as_selection':lambda x:x.__setitem__('native_adopted',True)}
    rejected=[]
    for name,mutate in mutations.items():
        bad=copy.deepcopy(d);mutate(bad)
        try:check(bad)
        except AssertionError:rejected.append(name)
        else:raise AssertionError(name)
    result=dict(status='Comparison internally consistent; no candidate qualified',cases=len(d['cases']),refinements=len(d['refinements']),negative_controls_rejected=rejected,screen_sha256=sha(path),checker_sha256=sha(__import__('pathlib').Path(__file__)))
    (path.parent/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':main()
