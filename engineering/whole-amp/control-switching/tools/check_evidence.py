"""Check retained simulation provenance, completion and explicit failing controls."""
import hashlib
import json
from pathlib import Path

M = Path(__file__).resolve().parents[1]
OUT = M / 'results'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    bounds, reset, driver, rail = [json.loads((OUT / (name + '.json')).read_text())
                                   for name in ['bounds', 'reset-screen', 'driver-screen', 'rail-impedance-screen']]
    assert all(r['contract_sha256'] == sha(M/'contract.json') for r in [bounds, reset, driver])
    assert reset['model_sha256'] == sha(M/'models/TPS389001_TRANS.LIB')
    assert rail['driver_result_sha256'] == sha(OUT/'driver-screen.json')
    assert len(driver['cases']) == 26 and len(driver['refinements']) == 3
    assert len(reset['cases']) == 8 and len(reset['refinements']) == 2
    assert len(rail['cases']) == 8 and len(rail['refinements']) == 2
    hashes = set()
    for result in [reset, driver, rail]:
        hashes.update(hashlib.sha256(deck.encode()).hexdigest() for deck in result['decks'].values())
        assert not result['fabrication_ready']
    all_rows = reset['cases'] + driver['cases'] + rail['cases'] + [rail['missing_decoupling_sensitivity']]
    all_rows += [r['result'] for r in reset['refinements']]
    for result in [driver, rail]:
        assert all(r['within_one_percent'] for r in result['refinements'])
        all_rows += [r[key] for r in result['refinements'] for key in ['result', 'finer_result']]
    assert len(all_rows) == 55
    assert all(r['deck_sha256'] in hashes for r in all_rows)
    assert all(r['completed_time_s'] >= .1 - 1e-9 for r in all_rows)
    local = [r for r in driver['cases'] if r['case']['suppression'] == 'remote_and_local']
    assert all(not r['flags'] for r in local + rail['cases'])
    assert max(r['max_vds_V'] for r in local + rail['cases']) < 24
    assert any('VDS_exceeds_30V_rating' in r['flags'] for r in driver['cases'])
    assert 'VDS_exceeds_30V_rating' in rail['missing_decoupling_sensitivity']['flags']
    assert all(r['steady_kcl_error_A'] < 1e-6 for r in driver['cases'] + rail['cases'])
    flags = {f for r in reset['cases'] for f in r['flags']}
    assert 'manufacturer_model_does_not_repeat_CT_delay_after_manual_reset' in flags
    assert 'fast_rail_drop_crosses_4p5V_before_reset_assertion' in flags
    assert not reset['guaranteed_timing_qualified'] and not bounds['reset_edge_qualification_complete']
    (OUT/'evidence-checks.json').write_text(json.dumps(dict(
        evidence_consistent=True, completed_runs=55, electrical_qualification_complete=False,
        provenance_hashes_checked=True, refinement_limits_checked=True,
        failing_controls_retained=['remote-only clamp', 'missing local decoupling'],
        reset_open_flags=sorted(flags), fabrication_ready=False,
        inputs_sha256={name:sha(OUT/(name+'.json')) for name in ['bounds','reset-screen','driver-screen','rail-impedance-screen']}
    ), indent=2)+'\n')
    print('55 completed runs: provenance/refinement checks pass; reset qualification remains open.')


if __name__ == '__main__': main()
