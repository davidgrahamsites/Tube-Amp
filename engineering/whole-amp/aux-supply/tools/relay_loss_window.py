"""Lower-bound the valid regulator-input time after abrupt loss of the secondary."""
import json
from unittest.mock import patch

import guard_transformer
import u4_margin as thermal


def main():
    module=thermal.MODULE
    src=json.loads((module/'results/guard-transformer.json').read_text())
    config=json.loads((module/'envelope-contract.json').read_text())
    config['relay_min_resistance_ohm']=src['baseline']['relay']['cold_screen_resistance_ohm']
    config['thermal_output_bound_V'].update(U4=11.4,U6=14.5,U7=14.25)
    direct,logic,audio=guard_transformer.BUDGETS['optical_guard']
    budgets={'optical_guard':(direct+.0013+.025,logic+.020,audio),'baseline':(.001,0.,0.)}
    actual={}
    original=thermal.measure

    def capture(*args):
        r=original(*args)
        actual[r['deck_sha256']]=r['raw_load_A']
        return r

    with patch.dict(guard_transformer.BUDGETS,budgets),patch.object(thermal,'measure',capture):
        rows=thermal.matrix(src,config,'LT3086-12','LM340T-5',{})
    cases=[]
    for row in rows:
        loads=actual[row['deck_sha256']]
        if row['budget']=='optical_guard':
            row['direct_12V_A']-=.025
        i4=thermal.branch_A(row,'cascade')[0]
        # Keep full pre-fault load imposed and assume the secondary contributes zero
        # from the instant of loss. Start at the measured simulated ripple trough.
        pos,neg=row['positive_V']['min'],row['negative_magnitude_V']['min']
        cap=row['reservoir_uF']*1e-6
        floors={'U4':13.+6.8*1.05*i4,'U6':16.,'U7':17.5}
        windows={ref:1000*cap*((neg if ref=='U7' else pos)-minimum)/
                 loads['negative' if ref=='U7' else 'positive'] for ref,minimum in floors.items()}
        cases.append(dict(hash=row['deck_sha256'],window_ms=windows,
                          raw_trough_V=[pos,neg],reservoir_uF=row['reservoir_uF'],raw_load_A=loads))
    result=dict(cases=cases,minimum_ms={k:min(r['window_ms'][k] for r in cases) for k in floors},
                scope='Time to first loss of the allocated input floor from the steady ripple trough. '
                      'No blocking diodes or extra hold capacitors credited. Valid only for loss of secondary drive. '
                      'A hard downstream short needs the independent pin-level mute.')
    assert len(cases)==216 and min(result['minimum_ms'].values())>0
    (module/'results/relay-loss-window.json').write_text(json.dumps(result,indent=1)+'\n')
    print(result['minimum_ms'])


if __name__=='__main__':
    main()
