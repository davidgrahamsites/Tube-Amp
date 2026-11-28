"""Check the CB-010/011 evidence and preserve a distinction between passes and open cases."""
import hashlib
import json
from pathlib import Path

BUFFER=Path(__file__).resolve().parents[1]
WHOLE=BUFFER.parents[1]


def read(folder, name):
    return json.loads((folder/name).read_text())


def main():
    data=BUFFER/'results'
    gain=read(data,'assembled-return.json')
    guard=read(data,'guarded-cutoff.json')
    cap=read(data,'local-reservoir.json')
    relay=read(data,'relay-margin.json')
    heat=read(WHOLE/'aux-supply/results','raw-relay-cooling.json')
    fit=read(WHOLE/'mechanical/review','fischer-template-checks.json')
    file=WHOLE/'mechanical/review/fischer-recess-fit-template.pdf'
    audio=gain['audio']
    tests={
        'all_96_declared_fixed_capacitance_AC_cases_in_band':len(gain['band_samples'])==96 and
            all(max(map(abs,r['band_dB']))<.5 for r in gain['band_samples']),
        'all_sampled_full_level_audio_in_band':all(abs(r['result']['gain_dB'])<.5 and r['result']['thd_pct']<1 for r in audio),
        'coupled_power_path_holds_305V':all(r['result']['rail_min_V']>=305 for r in audio),
        'two_seeds_reproduce_hot_short':abs(read(data,'hot-short-bias.json')['rows'][0]['result']['chip_W']-2.022)<.001,
        'guarded_10ms_fault':all(r['guard_present_V']<350 for r in cap['guard_cutoff']),
        'independent_2ms_open_guard_removed':all(r['guard_bypassed_V']<350 for r in cap['guard_cutoff'] if r['total_delay_ms']==2),
        'new_relay_carries_worst_resistive_close':relay['hard_close_peak_A']<=550/855<relay['contact_A_conservative_at_85C'],
        'new_relay_holds_working_voltage':relay['switch_operating_max_V']>550,
        'loop_has_positive_margin':relay['minimum_phase_margin_deg']>45,
        'all_auxiliary_cases_with_guard_and_relay_loads':len(heat['rows'])==216 and
            not heat['raw_failures'] and max(heat['peak_Tj_C'].values())<100,
        'actual_size_document':fit['digital_pass'] and hashlib.sha256(file.read_bytes()).hexdigest()==fit['PDF_sha256'],
        'negative_controls_retained':max(r['guard_bypassed_V'] for r in cap['guard_cutoff'])>350 and
            guard['checks']['hard_close_spike_peak_mA']>400 and
            not read(data,'shunt-bias-trade.json')['bias_passes_all_leakages']}
    nonlinear_pass=all(max(map(abs,r['result']['small_signal']['band_min_max_dB']))<.5 for r in audio if r['result']['nonlinear'])
    result=dict(checks=tests,nonlinear_small_signal_gain_meets_target=nonlinear_pass,
                cabinet_mockup_verified=fit['printed_and_cabinet_fit_verified'],installed_thermal_verified=False,
                integrated_hardware_verified=False,layout_release=False)
    assert all(tests.values()),tests
    (data/'gain-cutoff-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result)


if __name__=='__main__':
    main()
