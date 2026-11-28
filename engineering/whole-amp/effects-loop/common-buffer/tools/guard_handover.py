"""Long-time optical handover and independent supply hold-up after command loss."""
import json
import numpy as np
from sudden_guard import MODULE, delay_line, sp


def run(stuck=False, open_guard=False, sign=1):
    # Fault at 2 us. Keep the fast path latched until the entire startup sequence is rearmed.
    impulse=sign*160
    net=f"""CB008 energy and handover
VSTEP src 0 PWL(0 0 2u 0 3u {impulse})
RISO src coupling 3135
CBLOCK coupling common 1.1u
RKEEP common 0 1meg
VCOMMAND pc 0 PWL(0 1 252u 1 252.1u {int(stuck)})
SPLAY common line pc 0 playing
CPLAY common line 150p
.model playing sw(ron=30 roff=300meg vt=.5 vh=.01)
{delay_line('line','mix')}
CBYP src mix .35p
CLOAD mix 0 500p
RMIX mix 0 100k
VFAST fc 0 PWL(0 0 2.5u 0 2.51u {int(not open_guard)})
SFAST mix check fc 0 fast
.model fast sw(ron=18 roff=1g vt=.5 vh=.01)
VSHUNT check 0 0
VOPTO oc 0 PWL(0 0 3.002m 0 3.0021m 1)
SPRE common pre oc 0 shunt
RPRE pre 0 10k
SSH mix sh oc 0 shunt
RSH sh 0 4.7
.model shunt sw(ron=50 roff=30meg vt=.5 vh=.01)
CNC1 common pre 150p
CNC2 mix sh 150p
.end"""
    sp.load(net)
    sp.cmd('save v(mix) v(common) v(line) v(mid8) i(vshunt)')
    stop=.06
    sp.cmd(f'tran .25u {stop} 0 .25u')
    t=np.array(sp.vector('time'))
    assert t[-1]>=stop*(1-1e-8)
    mix,common,line,mid,i=[np.array(sp.vector(n)) for n in ['v(mix)','v(common)','v(line)','v(mid8)','i(vshunt)']]
    result=dict(series_stuck=stuck,fast_open=open_guard,step_V=impulse,
                peak_V=max(abs(mix)),after_3ms_V=max(abs(mix[t>.00301])),
                end_V=mix[-1],optical_contact_peak_V=max(abs(common-line)),
                peak_coil_terminal_V=max(max(abs(line-mid)),max(abs(mid-mix))),
                fast_path_energy_mJ=np.trapezoid(i*i,t)*18*1000,
                final_capacitor_voltage_estimate_V=impulse-common[-1],window_s=stop)
    sp.cmd('destroy all')
    return result


if __name__=='__main__':
    rows=[run(),run(sign=-1),run(True),run(open_guard=True)]
    # Post-isolation capacitance is specified after tolerance and bias derating.
    supplies=[dict(name='logic',effective_uF=176,initial_V=4.6,minimum_V=3.3,load_mA=30),
              dict(name='floating driver',effective_uF=80,initial_V=11.4,minimum_V=9,load_mA=25)]
    for s in supplies:s['available_ms']=s['effective_uF']*(s['initial_V']-s['minimum_V'])/s['load_mA']
    (MODULE/'results/guard-handover.json').write_text(json.dumps(dict(runs=rows,hold=supplies),indent=2)+'\n')
    print(rows,supplies)
