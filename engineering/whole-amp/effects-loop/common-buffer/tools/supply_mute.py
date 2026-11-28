"""CB-007 startup with the Apex model, silent input and de-energized mute."""
import hashlib
import json
import numpy as np
from apex_protection import fixture, M, sp


def startup(rise, negative_delay, short_gain_leg=False, powered_start=False):
    net = fixture()
    # Keep the identical guarded amplifier and its vendor models. Disconnect the
    # mixer for the normally closed precharge state; PA chips start below range.
    net = net.replace('VREC supply 0 310', f'VREC supply 0 PWL(0 0 .001 0 {rise} 310)')
    net = net.replace('VLV pos15 0 15','VLV pos15 0 PWL(0 0 .001 15)')
    net = net.replace('VNEG neg15 0 -15',f'VNEG neg15 0 PWL(0 0 {negative_delay} 0 {negative_delay+.001} -15)')
    net = net.replace('dc 0 ac 1 SIN(0 1.35 20000)','0')
    assert 'SIN(0 1.35 ' not in net
    net = net.replace('VMON port FX_RETURN 0','RMUTE port 0 10k')
    if short_gain_leg:
        net = net.replace('CG cg 0 47u','RFAULT cg 0 .01')
    if powered_start:
        net = net.replace('PWL(0 0 .001 0 ', 'PWL(0 100 .001 100 ').replace('VLV pos15 0 PWL(0 0 .001 15)', 'VLV pos15 0 15').replace(f'VNEG neg15 0 PWL(0 0 {negative_delay} 0 {negative_delay+.001} -15)', 'VNEG neg15 0 -15')
    sp.load(net)
    sp.cmd('save v(supply) v(preout) v(port) v(pos15) v(neg15)')
    sp.cmd('tran .00025 5 0 .00025')
    time = np.array(sp.vector('time'))
    result = dict(rise_s=rise, neg_delay_s=negative_delay, gain_cap_short=short_gain_leg, initialized_at_100V=powered_start,
                  reached_s=time[-1], deck_sha256=hashlib.sha256(net.encode()).hexdigest())
    if time[-1] < 4.99999:
        result['diagnostic'] = sp.logs[-5:]
    else:
        rail, bias, port, pos, neg = [np.array(sp.vector(f'v({n})')) for n in
                                      ['supply','preout','port','pos15','neg15']]
        ready = ((rail >= 300) & (rail <= 320) & (abs(bias-rail/2) <= 3)
                 & (abs(port) <= .35) & (pos >= 14) & (neg <= -14))
        last_bad = time[~ready][-1] if (~ready).any() else 0
        result.update(max_precharge_V=max(abs(port)), final_bias_V=bias[-1],
                      final_precharge_V=port[-1], last_bad_s=last_bad,
                      earliest_sustained_release_s=last_bad+.25 if time[-1]-last_bad >= .25 else None)
    sp.cmd('destroy all')
    return result


if __name__ == '__main__':
    runs=[startup(.5,.001), startup(.5,.65), startup(.02,.001), startup(.5,.001,True),
          startup(.5,.001,powered_start=True), startup(.02,.001,powered_start=True),
          startup(.5,.001,True,True)]
    (M/'results/supply-mute.json').write_text(json.dumps(runs, indent=2)+'\n')
