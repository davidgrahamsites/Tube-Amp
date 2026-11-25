"""Power-sequence diagnostics for the physical expression bias candidate.

Supply waveforms are test fixtures, not a model of the actual regulator system.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
import bias_screen as bias
ota = bias.ota


def pwl(delay, rise, value, drop=None):
    points = [(0, 0), (delay, 0), (delay+rise, value)]
    if drop is not None:
        points += [(drop, value), (drop+rise, 0)]
    return 'PWL('+' '.join(f'{t:g} {v:g}' for t,v in points)+')'


def deck(case):
    trim = json.loads((ota.OUT/'trim-screen.json').read_text())['calibrated_fractions']['150000']
    s = bias.deck(dict(trim_fraction=trim, trim_resistance=150000))
    lines = []
    for line in s.splitlines():
        if line.startswith('.nodeset'): continue
        if line.startswith('VIN '): line = 'VIN in 0 DC 0'
        if line.startswith('VP '): line = 'VP vp 0 '+pwl(case.get('pos_delay',.001),case.get('rise',.01),15,case.get('pos_drop'))
        if line.startswith('VN '): line = 'VN vn 0 '+pwl(case.get('neg_delay',.001),case.get('rise',.01),-15,case.get('neg_drop'))
        if line.startswith('VREF '):
            line = 'VREF refsrc 0 '+pwl(case.get('ref_delay',.001),case.get('rise',.01),5,case.get('ref_drop'))
            line += '\nRREF refsrc ref '+str(case.get('reference_resistance',.01))
        if line.startswith('VCTRL '): line = 'BCTRL target 0 V=V(ref)*'+str(case.get('control_fraction',1))
        lines.append(line)
    return '\n'.join(lines)+'\n'


def measure(case):
    import numpy as np
    sys.path.insert(0,str(ota.ROOT/'engineering/whole-amp/tools'))
    import spice_runtime as sp
    step=case.get('step',1e-5); stop=case.get('stop',.25)
    sp.load(deck(case))
    sp.cmd('save all @qbi[ic] @qbi[ib] @qdm[ic] @rbb[i] @rref[i]')
    sp.cmd(f'tran {step:g} {stop:g} 0 {step:g} uic')
    try:
        t=np.array(sp.vector('time'))
        if not len(t) or t[-1]<stop*(1-1e-8): raise ValueError('incomplete duration')
        names=['vp','vn','ref','refsrc','target','be','bbas','abc','bo','db','dref','out']
        v={n:np.array(sp.vector('v('+n+')')) for n in names}
        if not all(np.isfinite(x).all() for x in v.values()): raise ValueError('nonfinite nodes')
        currents={n:np.array(sp.vector(n)) for n in ['@qbi[ic]','@qbi[ib]','@qdm[ic]','@rbb[i]','@rref[i]']}
        if not all(np.isfinite(x).all() for x in currents.values()): raise ValueError('nonfinite currents')
        reverse_be={q:float(max(v[b]-v[e])) for q,b,e in [('QBI','bbas','be'),('QDM','dref','ref'),('QDR','dref','ref')]}
        reverse_cb={q:float(max(v[b]-v[c])) for q,b,c in [('QBI','bbas','abc'),('QDM','dref','db')]}
        result=dict(status='complete-diagnostic',end_s=float(t[-1]),
            final={n:float(x[-1]) for n,x in v.items()},
            voltage_ranges={n:[float(x.min()),float(x.max())] for n,x in v.items()},
            current_ranges_A={n:[float(x.min()),float(x.max())] for n,x in currents.items()},
            reverse_BE_max_V=reverse_be,reverse_CB_max_V=reverse_cb,
            reference_absorbed_peak_A=float(max(0,-currents['@rref[i]'].min())),
            output_peak_V=float(max(abs(v['out']))),
            opamp_supply_below_5V_duration_s=float(np.trapz(((v['vp']-v['vn'])<5).astype(float),t)),
            reverse_BE_over_6V=any(x>6 for x in reverse_be.values()),
            command=f'tran {step:g} {stop:g} 0 {step:g} uic')
    except (AssertionError,IndexError,ValueError) as e: result=dict(status='failed',error=str(e)[-1000:])
    return dict(result,log='\n'.join(sp.logs))


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(name,case):
    dp=ota.OUT/('sequence-'+name+'.cir');dp.write_text(deck(case));lp=dp.with_suffix('.log')
    try:
        p=subprocess.run([sys.executable,__file__,'--case',json.dumps(case)],capture_output=True,text=True,timeout=45)
        r=json.loads(p.stdout) if p.returncode==0 else dict(status='failed',error=p.stderr[-2000:])
        log=r.pop('log','')+'\n'+p.stderr
    except subprocess.TimeoutExpired as e:
        r=dict(status='timeout',seconds=45);log=str(e.stderr or '')
    lp.write_text(log)
    print(name,r['status'],r.get('reverse_BE_max_V'),r.get('output_peak_V'),flush=True)
    return dict(name=name,case=case,deck=dp.name,deck_sha256=sha(dp),log=lp.name,log_sha256=sha(lp),**r)


def main():
    cases=[('together',{}),('reference-late',dict(ref_delay=.05)),
           ('reference-first',dict(pos_delay=.05,neg_delay=.05)),
           ('negative-late',dict(neg_delay=.05)),('positive-late',dict(pos_delay=.05)),
           ('reference-loss',dict(ref_drop=.15)),
           ('positive-loss',dict(pos_drop=.15)),('negative-loss',dict(neg_drop=.15))]
    rows=[run(n,c) for n,c in cases]
    inputs=[Path(__file__),Path(bias.__file__),Path(ota.__file__),ota.OTA,ota.OP,bias.BJT,ota.OUT/'trim-screen.json',ota.ROOT/'engineering/whole-amp/tools/spice_runtime.py']
    report=dict(scope='Diagnostic UIC supply sequencing; manufacturer opamp model is not qualified below its 5V total operating supply. Ideal supply/reference waveforms are not the real regulator or mute.',cases=rows,provenance={str(p.relative_to(ota.ROOT)):sha(p) for p in inputs},startup_qualified=False)
    (ota.OUT/'power-sequence.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':
    if len(sys.argv)>1: print(json.dumps(measure(json.loads(sys.argv[2]))))
    else: main()
