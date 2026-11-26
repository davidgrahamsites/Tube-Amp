"""HD-010 large-signal setpoint comparison; separate from supply qualification.

Public seam: worker(case, contract) -> metrics, deck and saved last 20 cycles.
Every nonlinear solve runs in a bounded subprocess; partial runs are failures.
"""
from pathlib import Path
import hashlib,json,subprocess,sys,time
import numpy as np
import supply
M=supply.M;OUT=M/'results'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def worker(case,c):
    text=supply.deck(dict(mode='fixed',pre_V=case['pre_V'],channel=case['channel'],amp=case['amp_Vpk']),json.loads((M/'supply-contract.json').read_text()))
    expected=f"VSOURCE PICKUP 0 DC 0 AC 0 SIN(0 {case['amp_Vpk']} 1000)"
    assert expected in text and 'VTEST RET_DRIVE 0 DC 0 AC 1' in text
    assert 'VMAIN B_MAIN 0 400' in text and 'VSCREEN B_SCREEN 0 380' in text
    path=OUT/f"headroom-{case['id']}";path.with_suffix('.cir').write_text(text)
    sp=supply.sp;sp.cmd('version');sp.load(text);sp.cmd('op')
    nodes=c['nodes'];sp.cmd('save i(vpre) '+' '.join('v('+n.lower()+')' for n in nodes))
    step=1/(1000*c['steps_per_cycle']*case.get('refine',1));end=c['end_s']
    sp.cmd(f'tran {step} {end} {end-.02} {step}')
    t=np.asarray(sp.vector('time'));assert t.size and t[-1]>=end-1e-9
    v={n:np.asarray(sp.vector('v('+n.lower()+')')) for n in nodes};i=-np.asarray(sp.vector('i(vpre)'))
    assert all(np.isfinite(x).all() for x in [t,i,*v.values()])
    times=end-.02+np.arange(5120)/256000
    data=np.column_stack([times,*[np.interp(times,t,v[n]) for n in nodes],np.interp(times,t,i)])
    np.savetxt(path.with_suffix('.csv'),data,delimiter=',',header='time_s,'+','.join(nodes)+',pre_current_A',comments='',fmt='%.12g')
    metrics={n:supply.stats(t,y,1000,end) for n,y in v.items()};early=supply.stats(t,v['SPEAKER'],1000,end-.01)
    r=dict(case=case,status='completed',end_s=float(t[-1]),max_step_s=step,signals=metrics,
           fundamental_W=metrics['SPEAKER']['fundamental_Vpk']**2/(2*c['load_ohm']),
           settled_relative=abs(metrics['SPEAKER']['fundamental_Vpk']-early['fundamental_Vpk'])/max(metrics['SPEAKER']['fundamental_Vpk'],1e-12),
           deck_sha256=sha(path.with_suffix('.cir')),waveform_sha256=sha(path.with_suffix('.csv')))
    path.with_suffix('.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(id=case['id'],watts=r['fundamental_W'],THD=metrics['SPEAKER']['THD_2_to_10_percent'])))
    print('\n'.join(sp.logs[-12:]))
def main():
    c=json.loads((M/'headroom-contract.json').read_text())
    for p,h in c['inputs'].items():assert sha(supply.ROOT/p)==h,p
    rows=[];out=dict(id=c['id'],contract_sha256=sha(M/'headroom-contract.json'),factory_sha256=sha(Path(__file__)),cases=rows,adopted=False,physical_qualified=False,supply_dynamics_qualified=False)
    for case in c['cases']:
        path=OUT/f"headroom-{case['id']}";start=time.monotonic()
        for suffix in ['.json','.csv','.cir','.log']:path.with_suffix(suffix).unlink(missing_ok=True)
        try:
            proc=subprocess.run([sys.executable,str(Path(__file__)),'--worker',json.dumps(case)],capture_output=True,text=True,timeout=c['timeout_s'])
            path.with_suffix('.log').write_text(proc.stdout+proc.stderr)
            r=json.loads(path.with_suffix('.json').read_text()) if proc.returncode==0 else dict(case=case,status='failed',error=(proc.stdout+proc.stderr)[-1400:])
        except subprocess.TimeoutExpired as e:
            r=dict(case=case,status='timeout',error='bounded worker deadline');path.with_suffix('.log').write_bytes((e.stdout or b'')+(e.stderr or b''))
        r['elapsed_s']=time.monotonic()-start;rows.append(r);(OUT/'headroom-screen.json').write_text(json.dumps(out,indent=2)+'\n');print(case['id'],r['status'],r.get('fundamental_W'),flush=True)
if __name__=='__main__':
    if '--worker' in sys.argv:worker(json.loads(sys.argv[-1]),json.loads((M/'headroom-contract.json').read_text()))
    else:main()
