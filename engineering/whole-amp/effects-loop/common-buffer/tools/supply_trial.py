"""CB-007. Regulator surrogate and CB-006 amplifier share the actual supply node."""
import hashlib
import json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from apex_protection import fixture, sp

MODULE = Path(__file__).resolve().parents[1]


def regulator(raw, ctr, vth, capacitance, bypass=True, leak_mA=0):
    # The equivalent proportional error amplifier includes its feedback pole.
    # Only the normal, already-enabled path is used for audio tests.
    return f"""VRAW raw7 0 {raw}
RFEED raw7 sw7 {1820 + (30 if bypass else 8200)}
RSW sw7 d7 30
RGATE d7 g7 100k
RSTOP g7 mg7 220
MREG d7 mg7 src7 src7 trialpass
.model trialpass NMOS(level=1 vto={vth} kp=1 lambda=0.0001)
CGATE mg7 src7 10.7n
CMILL mg7 d7 200p
DZ src7 g7 z12
.model z12 D(bv=12 ibv=1m)
RSENSE src7 supply 33
QLIMIT g7 src7 supply qlimit7
.model qlimit7 NPN(bf=80 is=1e-14)
CRES supply 0 {capacitance}u
RLEAK supply 0 {310000/max(leak_mA,1e-6)}
RB7 supply 0 360k
RMON7 supply 0 330.49k
RUP7 supply sense7 306k
RDN7 sense7 0 2.49k
VREF7 ref7 0 2.5
RERR inv7 ref7 1k
RFB7 drive7 inv7 499k
CFB7 drive7 comp7 100n
RCOMP7 comp7 inv7 100k
BDRIVE drive7 0 v=max(0,min(11.8,100000*(v(sense7)-v(inv7))))
BLED led7 0 v=max(0,(v(drive7)-1.15)/1500)
ROPT led7 delayed7 1k
COPT delayed7 0 10n
BPHOTO g7 src7 i={ctr}*v(delayed7)*tanh(max(0,v(g7,src7))/0.2)
"""


def run(label, raw, ctr, vth, cap, temperature, short=False, bypass=True, leakage=1.208):
    net = fixture(short=short, temp=temperature).replace(
        'VREC supply 0 310', regulator(raw, ctr, vth, cap, bypass, leakage))
    net = net.replace('RBLEED port 0 1meg', 'RBLEED port 0 1meg\nRNO7 FX_RETURN 0 1meg\nRPORT7 port portref7 1meg\nVPORTREF7 portref7 0 2.5\nRBIAS7 preout 0 2meg')
    if label.startswith('optical'):
        capacitance=150 if label.endswith('150p') else 30
        net=net.replace('VMON port FX_RETURN 0', f'VMON port serial7 0\nRON7 serial7 FX_RETURN 30\nCNC7 port prech7 {capacitance}p\nRPRE7 prech7 0 10k\nCNC8 FX_RETURN shunt7 {capacitance}p\nRSH7 shunt7 0 4.7')
    if label.startswith('bypass-weld-transition'):
        net = net.replace('VRAW raw7 0 440', 'VRAW raw7 0 PWL(0 390 .001 390 .0012 440)')
    if label.endswith('-guided'):
        net=net.replace('.end\n', '.nodeset v(supply)=310 v(preout)=155 v(drive7)=2 v(mg7)=314\n.end\n')
    assert 'VRAW raw7' in net
    sp.load(net)
    sp.cmd('save v(supply) v(fx_return) i(vraw) v(d7) v(src7) v(g7)')
    end, step = .006, 1 / (20000 * 320)
    sp.cmd(f'tran {step} {end} 0 {step}')
    time = np.array(sp.vector('time'))
    assert time[-1] >= end * (1 - 1e-8), sp.logs[-8:]
    points = end + (np.arange(4096) / 409.6 - 10) / 20000

    def signal(name):
        return np.interp(points, time, sp.vector(name))

    port = signal('v(fx_return)')
    harmonics = 2 * abs(np.fft.rfft(port) / len(port))[np.arange(1, 11) * 10]
    rail = signal('v(supply)')
    current = -signal('i(vraw)')
    drain, source, gate = (signal(f'v({n})') for n in ['d7', 'src7', 'g7'])
    row = dict(rail_start_V=sp.vector('v(supply)')[0], rail_final_V=rail[-1],valid_operating_rail=bool(min(rail)>250 and max(rail)<350),case=label, raw_V=raw, CTR=ctr, threshold_V=vth, cap_uF=cap,
               temperature_C=temperature, port_short=short, bypass=bypass, leakage_at_310V_mA=leakage, final_s=time[-1],
               rail_min_V=min(rail), rail_max_V=max(rail), branch_mA=1000*np.mean(current),
               port_Vpk=harmonics[0], thd_pct=100*np.linalg.norm(harmonics[1:])/harmonics[0],
               pass_W=np.mean((drain-source)*(current-(drain-gate)/100000)),
               deck_sha256=hashlib.sha256(net.encode()).hexdigest())
    sp.cmd('destroy all')
    return row


if __name__ == '__main__':
    cases = [('nominal', 390, 1, 4, 44, 25), ('low-line', 340, .4, 5, 17.6, 25),
             ('high-hot', 440, 2, 3, 35.2, 85, False, False), ('brownout', 290, .4, 5, 17.6, 25),
             ('hot-port-short', 440, 1, 4, 35.2, 85, True, False),
             ('bypass-stuck-short', 440, 1, 4, 35.2, 85),
             ('bypass-weld-transition', 440, 1, 4, 35.2, 85),
             ('bypass-weld-transition-guided', 440, 1, 4, 35.2, 85),
             ('optical-30p', 390, 1, 4, 44, 25), ('optical-150p', 390, 1, 4, 44, 25)]
    with ProcessPoolExecutor(max_workers=3) as pool:
        jobs=[pool.submit(run,*case) for case in cases]
        rows=[job.result() for job in jobs]
    (MODULE/'results/supply-audio.json').write_text(json.dumps(rows, indent=2)+'\n')
