"""CB-011. Check the DC-connected high-voltage switches with their steering diodes."""
from contextlib import contextmanager
import itertools
import json
from unittest.mock import patch

import guarded_cutoff as guard
import low_line_rail as rail


@contextmanager
def supply_path(drop, corner, ron=1.5):
    """Inject worst-case diode drops during forward conduction in the original regulator deck."""
    base = rail.variant

    def build(raw, ctr, vth, cap, bypass=True, leak_mA=None, **kwargs):
        net = base(raw, ctr, vth, cap, bypass, leak_mA, **dict(kwargs, ron=ron))
        net = rail.one(net, 'RFEED raw7 sw7', 'RFEED xdrop sw7')
        net += guard.guard('raw7', 'xguard', corner)
        net += f'VRECT11 xguard xdrop {drop*(1+int(bypass))}\n'
        return net + '.nodeset v(supply)=310 v(drive7)=2\n'
    with patch.object(rail,'variant',build):
        yield


def main():
    src = json.loads((guard.MODULE/'results/guarded-cutoff.json').read_text())
    # C connection graph 1 stays above 0.70 A at +85 C. Read down for uncertainty.
    # The new relay does not rely on a hot extrapolation of the 25 C one-shot figure.
    ohms = 855.
    rows = []
    for raw, drop, cap in itertools.product((340,440),(.65,2.),(52.8,105.6)):
        with supply_path(drop,guard.HOT_LOW):
            rows.append(rail.sustained('DC-connected relays and guard',dict(rail.CAND,feed=945,limiter_is=2e-12),
                                       raw,16.5,vth=5.5,cap=cap))
        rows[-1]['diode_bound_V_each'] = drop
    loop_rows=[]
    for raw,ctr,cap in itertools.product((340,440),(.4,2.),(42.4175,103.635)):
        with supply_path(2.,guard.HOT_LOW):
            loop_rows.append(rail.loop(rail.CAND,raw,True,ctr,cap))
    phase_min=min(c['margin_deg'] for row in loop_rows for c in row['crossings'])
    assert phase_min>45
    peaks = [r['peak_mA']/1000 for r in src['hard_close_onto_short']]
    source = 'https://mediap.industry.panasonic.eu/assets/imported/industrial.panasonic.com/ac/cdn/e/control/relay/photomos/catalog/semi_eng_hf1a_aqv20.pdf'
    assert 550/ohms < .7 and max(peaks) <= 550/ohms
    assert all(r['settled_min_V']>305 and r['whole_run_max_V']<320 for r in rows)
    result = dict(id='CB-011',switch='Panasonic AQV209G, independently enabled series and bypass switches',
        connection='C, DC only. Tie both outer drain pins 4 and 6 to the positive feed, return through pin 5. '
                   'A series STTH112A at each switch blocks inverse current. Orient it for normal feed current.',
        sources=[source,'https://www.st.com/resource/en/datasheet/stth112.pdf'],
        assumptions='Forward steady loss screens 0.65 and 2 V per diode. Hot/dynamic switch resistance assumed 1.5 ohm each. '
                    '2 V is a design allowance; measure on cold hardware. Reverse recovery and relay internal output capacitance are not in this model.',
        raw_max_V=550,switch_operating_max_V=960,stand_off_V=1200,diode_repetitive_V=1200,
        contact_A_at_25C=1.4,contact_A_conservative_at_85C=.70,unlimited_feed_peak_A=550/ohms,
        hard_close_peak_A=max(peaks),nominal_forward_switch_drop_W_at_48mA=.048**2*1.5,
        peak_is_resistive_branch_only=True,series_capacitive_discharge_requires_measurement=True,
        control='Each AQV209G requires a separate LED driver. At 25 C and 100 V/100 mA, turn off <=0.5 ms. '
                'Provide a latched reset for faults. Maximum frequency at the rated point is 2.5 cycles/s.',
        minimum_rail_V=min(r['settled_min_V'] for r in rows),cases=rows,loop=loop_rows,minimum_phase_margin_deg=phase_min)
    (guard.MODULE/'results/relay-margin.json').write_text(json.dumps(result,indent=1)+'\n')
    print(result['minimum_rail_V'],max(peaks),550/ohms)


if __name__ == '__main__':
    main()
