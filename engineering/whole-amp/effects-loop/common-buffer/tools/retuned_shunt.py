"""CB-014. Full-load and delayed-protection confirmation on the revised ladder."""
import json
import sys
from unittest.mock import patch

import fixed_gain as gain
from qualify_sic_shunt import NETWORK as BASE, audio, peaks
from sic_shunt import MODEL_SHA, installed, spice_model

NETWORK=dict(BASE,start=560,mid=150,end=120,feedback=39000,name='CB-014')


def arrival(model):
    cases=json.loads((gain.MODULE/'results/guard-slew.json').read_text())
    cases=[r for r in cases if r['early_droop_enabled']]
    assert len(cases)==468
    rows=[]
    for edge,sign in sorted({(r['edge_us'],r['output_sign']) for r in cases}):
        # Select the latest detector command in this group. Intermediate times are not simulated.
        row=max((r for r in cases if (r['edge_us'],r['output_sign'])==(edge,sign)),key=lambda r:r['closed_us'])
        kw=dict(sign=sign,delay_us=row['closed_us'],rise_us=edge,wire_pF=0,scale=.9,winding_pF=30,
                end_pF=NETWORK['end']*.95,mid_pF=NETWORK['mid']*.95,start_pF=NETWORK['start']*.95)
        summary={k:row[k] for k in ('lost_pin','output_sign','edge_us','pin_fall_us','closed_us')}
        for method in ('trap','gear'):
            original=gain.sp.load
            def load(deck):
                original(deck.rsplit('.end',1)[0]+f'.options method={method} maxord=2\n.end')
            with patch.object(gain.sp,'load',load),installed(model,off=18.5,driver_ohm=3,threshold=-9.75,
                    cap_scale=1.1,wire_ohm=4,isol_pF=12,fault_edge_ns=40),peaks() as traces:
                try:
                    r=gain.sudden_guard.fault('latest detector per edge',fine=True,**kw)
                except AssertionError:
                    summary.setdefault('stopped_at_s',[]).append(float(gain.sp.vector('time')[-1]))
                    gain.pulse_winding._cmd('destroy all')
                    continue
                summary.update(method=method,post_switch_peak_V=r['post_switch_peak_V'],**traces)
                break
        rows.append(summary)
    return rows


if __name__=='__main__':
    group,path=sys.argv[1:]
    model=spice_model(path)
    with gain.fixture():
        gain.STATE['net']=NETWORK
        result={'audio':audio,'arrival':arrival}[group](model)
    (gain.MODULE/f'results/sic-retuned-{group}.json').write_text(json.dumps(dict(model_sha256=MODEL_SHA,
            network=NETWORK,group=group,results=result),indent=1,default=float)+'\n')
