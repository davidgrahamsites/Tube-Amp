"""Reconcile CB-009 receipts and retain the reasons placement remains on hold."""
import hashlib
import json
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
MODULE = TOOLS.parent
AMP = MODULE.parents[1]


def read(path):
    return json.loads(path.read_text())


def main():
    audio = read(MODULE/'results/rail-winding-audio.json')
    supply = read(MODULE/'results/low-line-rail.json')
    cooling = read(AMP/'aux-supply/results/regulator-cooling.json')
    fit = read(AMP/'mechanical/review/rear-cover-sink.json')['direct_cover_on_check']
    for table in (audio['sources'], supply['source_sha256']):
        for filename, digest in table.items():
            assert hashlib.sha256((TOOLS/filename).read_bytes()).hexdigest() == digest
    assert len(cooling['cases']) == 216 and cooling['voltage_failures'] == cooling['thermal_failures'] == 0
    assert 98 < cooling['max_Tj_C']['U4'] < 100 < cooling['faults_peak_Tj_C']['air_at_70C']
    assert supply['checks']['anchors_reproduced'] and supply['checks']['cutoff_spice_agrees']
    assert supply['checks']['low_line_16p5mA_worst_parts_holds_305V']
    assert any(r['case'].endswith('10 ms trip') and r['ngspice_peak_V']>350 for r in supply['pass_short_cutoff'])
    assert any(r['bypass_welded'] and not r['within_peak_single_shot'] for r in supply['pass_short_before_arm'])
    limits = audio['fault_summary']
    assert all(x < 400 for x in limits['peak_by_coil_V'])
    assert limits['quiet_mixer_V'] < 1
    assert any(r['gain_dB'] < -.5 and not r['short'] for r in audio['audio'])
    assert all(r['rail_min_V'] > 305 for r in audio['audio'] if r['raw_input_V']==340)
    assert any(r['short'] and r['raw_V']==440 for r in audio['invalid_cases'])
    assert fit['measured_approx_mm']==155 and fit['measurement_uncertainty_mm'] is None
    assert abs(fit['flat_needed_mm']-162.88)<1e-6 and abs(fit['trial_guard_to_wood_mm']-12.12)<1e-6
    print('CB-009 receipts reconcile. Gain, protection, installed heat and physical fit remain open.')


if __name__ == '__main__':
    main()
