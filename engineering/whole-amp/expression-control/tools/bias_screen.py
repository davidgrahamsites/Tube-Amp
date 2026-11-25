"""Physical PNP bias-source candidate. No pedal or native CAD implementation."""
import json, sys, subprocess, hashlib
from pathlib import Path
import ota_screen as ota
BJT=ota.MODULE/'models/MMBT3906.spice.txt'

def deck(case):
    s=ota.deck(case)
    diode_drive='RDI ref db 3.83k' if case.get('diode_resistor',True) else '''RDTOP ref dt 10k
RDBOT dt 0 40k
XDI dt de vp vn do OPAx134
RDB do dbas 1k
QDI db dbas de DI_BC857B
RDE ref de 1k
CDI do de 1n'''
    if case.get('mirror',True):
        diode_drive='''QDR dref dref ref DI_BC857B
QDM db dref ref DI_BC857B
RDR dref 0 4.32k'''
    s=s.replace('ID vp db DC 1m',f'''VREF ref 0 {case.get('reference',5)}
VCTRL target 0 {case.get('target',0)}
{diode_drive}''')
    s=s.replace(f"IABC vp abc DC {case.get('bias',.0005)}",'''XBI target be vp vn bo OPAx134
RBB bo bbas 1k
QBI abc bbas be DI_BC857B
RBE ref be 10k
CBI bo be 1n''')
    if case.get('recovery',True):s=s.replace('CBI bo be 1n','CBI bo be 1n\nRRECOV bo be 100k\nRABC abc vn 1Meg')
    # Stable-reference trim rather than trim spanning uncertain supply rails.
    s=s.replace('RTRIMTOP vp trim','RTRIMTOP ref trim').replace('RTRIMBOT trim vn','RTRIMBOT trim 0')
    s=s.replace('RTRIM trim plus',"RTRIM trim "+case.get('trim_node','minus'))
    s=s.replace('470k',str(case.get('trim_resistance',330000)))
    if case.get('control_ramp'):
        s=s.replace(f"VCTRL target 0 {case.get('target',0)}",'VCTRL target 0 DC 0 PWL(0 0 2m 0 7m 5 20m 5)')
    return s.replace('DI_BC857B','DI_MMBT3906').replace('.end',f'''.include "{BJT}"
.nodeset v(out)=0 v(io)=0 v(plus)=.5 v(minus)=.5 v(be)={case.get('target',0)} v(bo)={case.get('target',0)-.6}
.end''')

def measure(case):
    sys.path.insert(0,str(ota.ROOT/'engineering/whole-amp/tools'))
    import spice_runtime as sp
    import numpy as np
    sp.load(deck(case));sp.cmd('op')
    names=['out','plus','minus','db','abc','be','bbas','bo','ref','target']
    if not case.get('diode_resistor',True) and not case.get('mirror',True):names+=['de','dbas','do']
    try:
        dc={n:float(sp.vector('v('+n+')')[-1]) for n in names}
        qs=['qbi','qdr','qdm'] if case.get('mirror',True) else (['qbi'] if case.get('diode_resistor',True) else ['qbi','qdi'])
        currents={q:float(sp.vector('@'+q+'[ic]')[-1]) for q in qs}
    except (IndexError,AssertionError):
        return dict(status='failed-op',log='\n'.join(sp.logs))
    valid=all(np.isfinite(v) for v in dc.values()) and all(-case.get('rail',15)<dc[n]<case.get('rail',15) for n in ['out','bo'])
    r=dict(op=dc,collector_currents_A=currents,op_within_supply=valid)
    if not valid:
        return r|dict(status='invalid-op',log='\n'.join(sp.logs))
    if not case.get('dc_only'):
        hz=case.get('hz',1000);step=1/(hz*256*case.get('refine',1));stop=16/hz
        sp.cmd(f'tran {step:.12g} {stop:.12g} 0 {step:.12g}')
        t=np.array(sp.vector('time'));y=np.array(sp.vector('v(out)'))
        assert t[-1]>=stop*(1-1e-7)
        samples=np.interp(np.arange(8192)/(hz*1024)+8/hz,t,y)
        a=2*abs(np.fft.rfft(samples))/len(samples);fund=float(a[8]);hs=[float(a[8*i]) for i in range(2,10)]
        r.update(end_s=float(t[-1]),gain=fund/case.get('amplitude',1),fundamental_peak_V=fund,thd_percent=float(np.linalg.norm(hs)/fund*100) if fund>1e-9 else None,dc_V=float(samples.mean()),peak_V=float(max(abs(samples))))
        final={n:float(sp.vector('v('+n+')')[-1]) for n in ['be','bo','bbas','abc','target']}
        reverse=np.array(sp.vector('v(bbas)'))-np.array(sp.vector('v(be)'))
        r.update(final=final,max_reverse_base_emitter_V=float(reverse.max()))
    return r|dict(status='complete',log='\n'.join(sp.logs))

def run(name,case):
    path=ota.OUT/('bias-'+name+'.cir');path.write_text(deck(case))
    try:
        p=subprocess.run([sys.executable,__file__,'--case',json.dumps(case)],capture_output=True,text=True,timeout=35)
        r=json.loads(p.stdout) if not p.returncode else dict(status='failed',error=p.stderr[-2500:])
        log=r.pop('log','')+'\n'+p.stderr
    except subprocess.TimeoutExpired as e:
        r=dict(status='timeout',seconds=35);log=str(e.stderr or '')
    (ota.OUT/('bias-'+name+'.log')).write_text(log)
    print(name,r,flush=True)
    return dict(name=name,case=case,deck=path.name,deck_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),**r)

def main():
    rows=[]
    def add(name,case):
        r=run(name,case);rows.append(r);return r
    a=add('trim0',dict(dc_only=True,trim_fraction=0))
    b=add('trim1',dict(dc_only=True,trim_fraction=1))
    if all(x['status']=='complete' for x in [a,b]):
        trim=-a['op']['out']/(b['op']['out']-a['op']['out'])
        if 0<=trim<=1:
            c=add('calibration',dict(dc_only=True,trim_fraction=trim))
            if c['status']=='complete':
                trim=trim-c['op']['out']*(1-trim)/(b['op']['out']-c['op']['out'])
                assert 0<=trim<=1,trim
                calibrated=add('calibrated',dict(dc_only=True,trim_fraction=trim))
                assert calibrated['status']=='complete' and abs(calibrated['op']['out'])<.001,calibrated
                for rail in [12,15,16.5]:
                    for target in [0,2.5,4.9,5]:
                        add(f'dc-{rail}-{target}',dict(dc_only=True,trim_fraction=trim,rail=rail,target=target))
                for rail in [12,15]:
                    add(f'audio-{rail}',dict(hz=1000,amplitude=8,trim_fraction=trim,rail=rail))
                add('audio-refined',dict(hz=1000,amplitude=8,trim_fraction=trim,refine=2))
                add('audio-10k',dict(hz=10000,amplitude=8,trim_fraction=trim))
                add('control-ramp',dict(hz=1000,amplitude=1,trim_fraction=trim,control_ramp=True))
                for temp in [0,70]:
                    add(f'temperature-{temp}',dict(dc_only=True,trim_fraction=trim,temperature=temp))
                add('resistor-comparison',dict(hz=1000,amplitude=8,trim_fraction=trim,mirror=False))
    else: trim=None
    inputs=[Path(__file__),Path(ota.__file__),ota.OTA,ota.OP,BJT]
    provenance={str(p.relative_to(ota.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    (ota.OUT/'bias-screen.json').write_text(json.dumps(dict(scope='PNP current-source feasibility with ideal 5V reference and control input. Not protected pedal, stability, noise, hotplug, startup or native qualification.',trim_fraction=trim,provenance=provenance,cases=rows),indent=2)+'\n')

if __name__=='__main__':
    if len(sys.argv)>1:print(json.dumps(measure(json.loads(sys.argv[2]))))
    else:main()
