"""Audit added load, retained case coverage, timing arithmetic and deck identities."""
from pathlib import Path
import copy, hashlib, json, math

M = Path(__file__).resolve().parents[1]
ROOT = M.parents[3]
D = M / 'results'
W = M.parent.parent


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def close(a, b):
    assert math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-12), (a, b)


def check(d):
    old = json.loads((W/'control-switching/results/fast-clamp/brownout.json').read_text())
    for path, digest in d['input_sha256'].items():
        assert sha(ROOT/path) == digest, path
    extra = 18 / (10000 * .98)
    close(d['summary']['extra_each_rail_A'], extra)
    detector = old['detector']
    latency = sum(detector[k] for k in ['detection_propagation_allocation_s',
                  'relay_five_percent_current_screen_s', 'additional_contact_and_logic_allocation_s'])
    assert len(d['cases']) == len(old['cases']) == 32
    assert [r['id'] for r in d['cases']] == [r['id'] for r in old['cases']]
    reserves = []
    for i, row in enumerate(d['cases'] + [d['refinement']]):
        reference = next(r for r in old['cases'] if r['id'] == row['id'])
        for key in ['case', 'profile', 'ramp_s', 'raw_warning']:
            assert row[key] == reference[key], key
        close(row['step_s'], reference['step_s'] / (2 if i == 32 else 1))
        floor = min(row['raw_floor_relative_s'].values())
        values = []
        for t in row['raw_warning_traces']:
            at = t['qualified_pulse_start_relative_s']
            assert at is not None, 'Missing qualifying fault pulse'
            close(t['conditional_raw_mute_reserve_s'], floor-at-latency)
            assert any(abs(a-at) < 1e-12 and (z is None or z-a >= .002)
                       for a, z in t['intervals_relative_s'])
            values.append(t['conditional_raw_mute_reserve_s'])
        reserves.append(min(values))
        close(row['healthy_enable_margin_V'], row['healthy_positive_raw_min_V']-
              max(row['raw_warning']['thresholds']['enable']))
        key = f'brownout-{i:02d}.cir' if i < 32 else 'brownout-refined.cir'
        assert sha(D/key) == d['deck_sha256'][key]
        lines = (D/key).read_text().splitlines()
        for branch, nodes in [('IR619', 'rawp 0'), ('IR620', '0 rawn')]:
            hits = [line for line in lines if line.startswith(branch+' ')]
            assert hits == [f'{branch} {nodes} PWL(0 0 .05 0 .06 {extra:.15g})']
    close(min(reserves[:32]), d['summary']['minimum_conditional_raw_reserve_s'])
    close(min(r['healthy_enable_margin_V'] for r in d['cases']),
          d['summary']['minimum_healthy_enable_margin_V'])
    close(abs(reserves[-1]-min(reserves[:32])), d['summary']['refinement_reserve_difference_s'])
    assert d['summary']['reserve_failures'] == sum(x < 0 for x in reserves[:32]) == 0
    assert d['summary']['healthy_enable_failures'] == sum(r['healthy_enable_margin_V'] < 0 for r in d['cases']) == 0
    assert not d['summary']['whole_system_qualified'] and not d['summary']['protection_candidate_native_adopted']


def main():
    d = json.loads((D/'supply-regression.json').read_text())
    check(d)
    rejected = []
    mutations = {
        'load_omitted': lambda x: x['summary'].__setitem__('extra_each_rail_A', 0),
        'missing_case': lambda x: x['cases'].pop(),
        'inflated_timing_margin': lambda x: x['cases'][0]['raw_warning_traces'][0].__setitem__('conditional_raw_mute_reserve_s', 1),
        'stale_source': lambda x: x['input_sha256'].__setitem__('engineering/whole-amp/reverb-600/circuit.json', 'wrong'),
    }
    for name, mutate in mutations.items():
        bad = copy.deepcopy(d)
        mutate(bad)
        try:
            check(bad)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError('Negative control escaped: '+name)
    receipt = dict(passed=True, case_count=32, refinement_count=1,
                   negative_controls_rejected=rejected,
                   report_sha256=sha(D/'supply-regression.json'), checker_sha256=sha(Path(__file__)),
                   helper_hashes_at_review={str(p.relative_to(ROOT)): sha(p) for p in
                     [W/'control-switching/tools/ac_loss_interruptions.py', W/'tools/spice_runtime.py']},
                   full_power_system_qualified=False)
    (D/'supply-checks.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
