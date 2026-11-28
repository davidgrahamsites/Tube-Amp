"""Apply CB-007 candidate loads to all 72 existing auxiliary rectifier cases."""
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
AUX=HERE.parents[1]/'aux-supply'
sys.path.insert(0,str(AUX/'tools'))
from screen_envelope import evaluate


def main(optical=False):
    prior=json.loads((AUX/'results/loads/raw-screen.json').read_text())
    c=prior['effective_contract']
    # 150 ohm at 25 C, -10% tolerance budget, -25 C; other circuits reserved.
    coil_A=12.6/(150*.9*(1-.00393*50))
    extra12=.016 if optical else coil_A+.016
    extra5=.058 if optical else .028
    rows=[]
    for old in prior['cases']:
        case=old['case']
        actual_count=case['load']['relays_on']
        # The upstream model represents U4 direct loads as coil current units.
        # This equivalent adds the exact same current ahead of its U4 heat/KCL.
        case['load']['relays_on']+=extra12*c['relay_min_resistance_ohm']/c['relay_voltage_V']
        case['load']['audio_each_rail_A']+=.015
        case['load']['logic_5V_A']+=extra5
        row,_=evaluate(c,case,c['simulation']['max_step_s'])
        rows.append(dict(id=case['id'],baseline_coils=actual_count,
                         rms_A=max(row['half_winding_rms_A'].values()),
                         regulator_heat_W=row['conditional_total_W'], flags=row['screen_flags'],
                         reached_s=row['completed_time_s'],kcl_A=row['kcl_max_error_A'],
                         deck_sha256=row['deck_sha256']))
    out=dict(mute='optical' if optical else 'mechanical',cold_coil_A=0 if optical else coil_A,extra_12V_A=extra12,extra_5V_A=extra5,
             extra_each_15V_A=.015,flagged=sum(bool(r['flags']) for r in rows),
             winding_over_screen=sum(r['rms_A']>.25 for r in rows),
             max_half_winding_rms_A=max(r['rms_A'] for r in rows),
             max_conditional_heat_W=max(r['regulator_heat_W'] for r in rows), cases=rows)
    (HERE/'results'/('supply-aux-optical.json' if optical else 'supply-aux.json')).write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':
    main()
    main(optical=True)
