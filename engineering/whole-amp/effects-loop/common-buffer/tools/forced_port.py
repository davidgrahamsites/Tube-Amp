"""Measure external current independently of the recovery stage at the 500 pF target."""
import hashlib
import json

import numpy as np
from integrated_load import M, circuit, sp


def main():
    hz, peak, pf = 20000, 135, 500
    # Keep the entire downstream tube model. Remove only the appended recovery model.
    net = circuit(hz, peak, pf).rsplit('.include "', 1)[0]
    assert 'XV4_1' in net and 'MFOLLOW' not in net
    net += f'VFORCE FX_RETURN 0 DC 0 SIN(0 {peak} {hz})\nCHARNESS FX_RETURN 0 {pf}p\n.end\n'
    sp.load(net)
    sp.cmd('save v(fx_return) v(mix_out) v(in_ac) v(send_in) i(vforce)')
    end = .03
    sp.cmd(f'tran 100n {end} {end-21/hz} 100n')
    t = np.asarray(sp.vector('time'))
    assert t[-1] >= end*(1-1e-8)
    def window(stop):
        times = stop + (np.arange(5000)/500-10)/hz
        voltage, mix, ac, send, source = [np.interp(times,t,sp.vector(n)) for n in
            ('v(fx_return)','v(mix_out)','v(in_ac)','v(send_in)','i(vforce)')]
        resistor = (voltage-mix)/100000 + (ac-send)/1e6
        cap = 2*np.pi*hz*pf*1e-12*peak*np.cos(2*np.pi*hz*times)
        assert max(abs(resistor+cap+source)) < 5e-6
        return -1000*source
    current = window(end)
    prior = window(end-10/hz)
    result = dict(target_Vpk=peak,hz=hz,added_pF=pf,port_mA=[min(current),max(current)],
                  window_difference_rms_mA=np.sqrt(np.mean((current-prior)**2)),
                  end_s=t[-1],max_step_s=1e-7,kcl_abs_error_limit_uA=5,
                  deck_sha256=hashlib.sha256(net.encode()).hexdigest(),
                  scope='Ideal prescribed port voltage. External current only.')
    (M/'results/forced-port.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result)


if __name__ == '__main__':
    main()
