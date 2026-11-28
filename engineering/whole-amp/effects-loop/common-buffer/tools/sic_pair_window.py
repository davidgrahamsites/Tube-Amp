"""CB-014. Test a pair selected for similar threshold and gate charge at several absolute thresholds."""
import json
import sys
from itertools import product
from unittest.mock import patch

import fixed_gain as gain
from qualify_sic_shunt import NETWORK, peaks
from retuned_shunt import NETWORK as REVISED
from sic_shunt import MODEL_SHA, installed, spice_model


def main(path,revised=False):
    model=spice_model(path)
    rows=[]
    with gain.fixture():
        network=REVISED if revised else NETWORK
        gain.STATE['net']=network
        for base,delta,scale,isol,off,step in product((-13.5,-10,-6.5),(-.25,.25),(.9,1.1),(3,12),(17.5,18.5),(-160,0,160)):
            row=dict(base_V=base,delta_V=delta,ground_charge_scale=scale,isol_pF=isol,drive_V=off,step_V=step)
            original=gain.sp.load
            methods=('trap','gear','gear-fine') if revised else ('trap','gear')
            for method in methods:
                integration_method=method.partition('-')[0]
                def solver(net):
                    original(net.rsplit('.end',1)[0]+f'.options method={integration_method} maxord=2\n.end')
                original_cmd=gain.sp.cmd
                def finer(command):
                    if method=='gear-fine' and command.startswith('tran 1n'):
                        command='tran .25n 15u 0 .25n'
                    return original_cmd(command)
                with patch.object(gain.sp,'load',solver),patch.object(gain.sp,'cmd',finer),installed(model,off=off,driver_ohm=3,edge_ns=40,
                        threshold=base+delta,cap_scale=scale,signal_threshold=base,isol_pF=isol),peaks() as trace:
                    try:
                        gain.guard_injection.run(step,1,off)
                    except AssertionError:
                        row.setdefault('stopped_at_s',[]).append(float(gain.sp.vector('time')[-1]))
                        gain.pulse_winding._cmd('destroy all')
                        continue
                    row.update(method=method,**trace)
                    break
            rows.append(row)
    complete=[r for r in rows if 'method' in r]
    worst=max(complete,key=lambda r:r['mixer_peak_V'])
    out=dict(network=network,model_sha256=MODEL_SHA,cases=len(rows),driver_ohm=3,edge_ns=40,limit_V=.7,
             completed=len(complete),violations=sum(1 for r in complete if r['mixer_peak_V']>.7),worst=worst,rows=rows)
    (gain.MODULE/('results/sic-retuned-pair-window.json' if revised else 'results/sic-pair-window.json')).write_text(json.dumps(out,indent=1,default=float)+'\n')
    print(len(rows),worst,flush=True)


if __name__=='__main__':
    main(sys.argv[1],'--revised' in sys.argv[2:])
