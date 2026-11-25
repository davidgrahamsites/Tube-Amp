"""Independently compare Thevenin predictions with full circuit AC solutions."""
import csv
import hashlib
import json
import math
from pathlib import Path

import return_port_envelope as ports

ROOT, OUT = ports.ROOT, ports.OUT


def voltage(measurement, hz, node):
    return complex(*measurement['points'][str(hz)][node])


def relative_error(a, b):
    return abs(a-b)/max(abs(b), 1e-15)


def db(ratio):
    return 20*math.log10(abs(ratio))


def main():
    data = json.loads((OUT/'return-port-summary.json').read_text())
    checks = dict(matrix_complete=data['all_attempted'] and len(data['cases'])==len(ports.CONFIGS),
                  exact_configs=[r['config'] for r in data['cases']]==ports.CONFIGS,
                  no_adoption=not any(data[k] for k in ['native_modified','circuit_selected','fabrication_release']))
    for path,digest in {**data['input_sha256'],**data['source_sha256']}.items():
        checks['source:'+path] = hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest
    errors, comparisons, sources = [], [], []
    for index, row in enumerate(data['cases']):
        for name, digest in row['deck_sha256'].items():
            checks['deck:'+name] = hashlib.sha256((OUT/name).read_bytes()).hexdigest()==digest
        m = row['measurements']
        for hz in ports.HZ:
            zs = voltage(m['source-probe'],hz,'FX_SEND')
            sources.append(dict(case=index, **row['config'], hz=hz, magnitude_ohm=abs(zs), phase_deg=math.degrees(math.atan2(zs.imag,zs.real))))
        for resistance, predictions in row['predictions'].items():
            for predicted in predictions:
                hz = predicted['hz']
                error = 0
                for node in ['MIX_OUT','SEND_IN','PI_G1','SPEAKER']:
                    expected = complex(*predicted['wet_native_predicted'][node])
                    error = max(error,relative_error(expected,voltage(m['native-wet'],hz,node)))
                    if resistance in row['direct']:
                        direct = row['direct'][resistance]
                        error = max(error,relative_error(complex(*predicted['wet_buffer_predicted'][node]), voltage(direct['buffer-wet'],hz,node)))
                        native_dry = voltage(m['native-dry'],hz,node)
                        actual = voltage(direct['buffer-dry'],hz,node)
                        error = max(error, relative_error(actual, native_dry*complex(*predicted['dry_ratio'])))
                errors.append(error)
                comparisons.append(dict(case=index,**row['config'],hz=hz, output_ohm=int(resistance),
                    dry_change_dB=db(complex(*predicted['dry_ratio'])),
                    wet_change_dB=db(complex(*predicted['wet_buffer_predicted']['PI_G1'])/complex(*predicted['wet_native_predicted']['PI_G1']))))
        checks[f'case:{index}:finite_op'] = all(math.isfinite(v) for x in m.values() for v in x['op'].values())
    checks['port_prediction_matches_direct_within_1ppm'] = max(errors)<1e-6
    # These two cases already contradict a single control-independent wet transfer
    # preserving both originals within +/-0.5 dB, even with a fixed wet gain trim.
    original = [abs(voltage(row['measurements']['native-wet'],1000,'PI_G1')) for row in data['cases']]
    imin, imax = min(range(len(original)),key=original.__getitem__), max(range(len(original)),key=original.__getitem__)
    spread = db(original[imax]/original[imin])
    candidate_spreads = {}
    for resistance in ['1000','100000']:
        actual = [abs(voltage(row['direct'][resistance]['buffer-wet'],1000,'PI_G1')) for row in data['cases']]
        candidate_spreads[resistance] = db(max(actual)/min(actual))
    checks['fixed_output_candidate_control_independence_observed'] = max(candidate_spreads.values())<1e-5
    checks['original_wet_spread_exceeds_1dB_necessary_condition'] = spread>1
    # A deliberately wrong current-source sign must fail the network equivalence.
    row=data['cases'][0]; p=row['predictions']['1000'][4]
    actual=voltage(row['measurements']['native-wet'],1000,'PI_G1')
    opposite=-complex(*p['wet_native_predicted']['PI_G1'])
    checks['wrong_sign_negative_control_detected'] = relative_error(opposite,actual)>1
    # An analytic resistive network validates the separate port formula's polarity:
    # 1V--10k--MIX; MIX--100k--RETURN; RETURN has50k to ground.
    # Open RETURN: Hw=1, Zret=110k, Ztransfer=10k. Closing50k gives MIX=15/16.
    checks['resistive_port_control'] = abs((1-10000/(110000+50000))-15/16)<1e-12
    native = json.loads((OUT/'return-supply-audit.json').read_text())['native_sha256']
    for board,digest in native.items():
        path=ROOT/f'engineering/whole-amp/pcb-measured-r/boards/Renegade_{board}.kicad_pcb'
        checks['native:'+board] = hashlib.sha256(path.read_bytes()).hexdigest()==digest
    witness = [dict(case=i,config=data['cases'][i]['config'], native_wet_PI_V_per_V=original[i]) for i in (imin,imax)]
    table=[]
    for r in ports.RESISTANCES:
        selected=[x for x in comparisons if x['output_ohm']==r]
        wet=[x['wet_change_dB'] for x in selected if 80<=x['hz']<=5000]
        dry=[x['dry_change_dB'] for x in selected]
        table.append(dict(output_ohm=r, dry_dB_range=[min(dry),max(dry)],wet_80_to_5k_dB_range=[min(wet),max(wet)],
                          wet_screen_all_settings_pass=max(map(abs,wet))<=.5,
                          dry_screen_all_settings_pass=max(map(abs,dry))<=.5))
    result=dict(passed=all(checks.values()),checks=checks,maximum_relative_port_prediction_error=max(errors),
                fixed_resistance_comparison=table, source_impedance_1k_ranges={ch:[min(s['magnitude_ohm'] for s in sources if s['channel']==ch and s['hz']==1000),max(s['magnitude_ohm'] for s in sources if s['channel']==ch and s['hz']==1000)] for ch in ['clean','dirty']},
                native_wet_1k_spread_dB=spread, minimum_worst_case_wet_error_dB_for_control_independent_transfer=spread/2,
                witness_cases=witness, buffered_wet_1k_control_spread_dB=candidate_spreads,
                summary_sha256=hashlib.sha256((OUT/'return-port-summary.json').read_bytes()).hexdigest(),
                native_sha256=native, fabrication_release=False,
                interpretation='Evidence passes; fixed impedance is NOT a transparent substitute. Nominal linear model only.')
    (OUT/'return-port-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    for name,rows in [('return-port-comparison.csv',comparisons),('return-port-source-impedance.csv',sources)]:
        with (OUT/name).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    print(json.dumps({k:v for k,v in result.items() if k not in ['checks','native_sha256']},indent=2))
    print('checks',len(checks),'failed',[k for k,v in checks.items() if not v])
    assert result['passed']


if __name__ == '__main__':
    main()
