"""Join the new cutoff-control current to the auxiliary winding and U4 thermal model."""
import json
import sys
from unittest.mock import patch

import guard_transformer
import u4_margin as thermal

M=thermal.MODULE


def main(two_relay_leds=False, raw_leds=False):
    source=json.loads((M/'results/guard-transformer.json').read_text())
    c=json.loads((M/'envelope-contract.json').read_text())
    c['relay_min_resistance_ohm']=source['baseline']['relay']['cold_screen_resistance_ohm']
    c['thermal_output_bound_V'].update(U4=11.4,U6=14.5,U7=14.25)
    direct,logic,audio=guard_transformer.BUDGETS['optical_guard']
    # Reserve 20 mA at +5 V for the isolated cutoff driver (17.8 mA upper estimate).
    # Charge 1.3 mA on U4 for the 10 kohm output preload, including disconnected rails.
    bounds={'optical_guard':(direct+.0013+(.025 if two_relay_leds else 0),logic+.020,audio),'baseline':(.001,0.,0.)}
    with patch.dict(guard_transformer.BUDGETS,bounds):
        rows=thermal.matrix(source,c,'LT3086-12','LM340T-5',{})
    jc=dict(thermal.JC,U4=3.)
    results=[]
    for r in rows:
        # The raw rectifier sees identical current in both trials. A raw-fed
        # constant-current LED path bypasses U4 and its series resistor.
        raw_led_A=.025 if raw_leds and r['budget']=='optical_guard' else 0.
        r['direct_12V_A']-=raw_led_A
        watts=thermal.heat(r,c,'cascade',6.8*.95,0.)[0]
        _,res,edges=thermal.heat(r,c,'cascade',6.8,0.)
        result=dict(raw_driver_input_W=raw_led_A*r['positive_V']['max'],supply_hash=r['deck_sha256'],load=r['load'],line_V=r['line_V'],
                    hot_budget=r['budget']=='optical_guard',U4_input_V=edges['U4'],
                    winding_rms_A=r['winding_rms_A'],resistor_W=res['R_U4'],
                    raw_pass=r['voltage_ok'],heat_W=watts,
                    temperatures={name:thermal.junctions(watts,jc,*f) for name,f in thermal.FAULTS.items()})
        results.append(result)
    peaks={name:max(max(r['temperatures'][name].values()) for r in results) for name in thermal.FAULTS}
    receipt=dict(cases=len(rows),raw_LED_mA=25. if raw_leds else 0.,reserve_12V_relay_mA=25. if two_relay_leds and not raw_leds else 0.,reserve_5V_mA=20.,U4_bleed_upper_mA=1.3,
                 U4='LT3086IT7#PBF with 6.8 ohm +/-5% raw-input resistor',U5='L7805CV, retained cascade',
                 U5_basis='CB009 ST 5 K/W junction-case and 9.5 mA ground-current envelope; U4 supplies 11.4 to 12.6 V.',
                 peak_Tj_C=peaks,U4_min_input_V=min(r['U4_input_V'][0] for r in results),
                 max_resistor_W=max(r['resistor_W'] for r in results),
                 winding_peak_A=max(r['winding_rms_A'] for r in results),
                 raw_failures=sum(not r['raw_pass'] for r in results),
                 raw_model='Imposed linear regulator loads; raw ripple includes all previous guard budgets. Cold and hot installed thermal resistance require measurement.',
                 rows=results)
    assert receipt['U4_min_input_V']>13 and not receipt['raw_failures']
    filename='relay-load-cooling.json' if two_relay_leds else 'cutoff-load-cooling.json'
    if raw_leds:
        assert max(peaks.values()) < 100 and receipt['winding_peak_A'] < 1.67
        filename='raw-relay-cooling.json'
    (M/'results'/filename).write_text(json.dumps(receipt,indent=1)+'\n')
    print({k:v for k,v in receipt.items() if k!='rows'})


if __name__=='__main__':
    main(bool({'--relay-leds','--raw-leds'} & set(sys.argv)), '--raw-leds' in sys.argv)
