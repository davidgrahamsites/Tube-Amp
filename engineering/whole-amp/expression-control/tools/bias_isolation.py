"""Causal model isolation, not alternate hardware qualification."""
import hashlib,json,math,subprocess,sys
from pathlib import Path
import bias_screen as bias
ota=bias.ota

def deck(mode):
    trim=json.loads((ota.OUT/'bias-screen.json').read_text())['trim_fraction']
    s=bias.deck(dict(trim_fraction=trim,target=5))
    if mode=='servo-alone':
        s=f'''Bias servo only, collector held at -14 V by diagnostic fixture
.include "{ota.OP}"
.include "{bias.BJT}"
.options rshunt=1e12
VP vp 0 15
VN vn 0 -15
VREF ref 0 5
VCTRL target 0 5
VCOL abc 0 -14
XBI target be vp vn bo OPAx134
RBB bo bbas 1k
QBI abc bbas be DI_MMBT3906
RBE ref be 10k
CBI bo be 1n
RRECOV bo be 100k
.nodeset v(be)=5 v(bo)=5.006
.end'''
    elif mode=='ideal-servo':
        s=s.replace('XBI target be vp vn bo OPAx134','BBI bo 0 V=limit(1e5*(v(target)-v(be)),-14,14)')
    elif mode=='fixed-base':
        s=s.replace('XBI target be vp vn bo OPAx134','VBI bo 0 5.006036')
    elif mode=='fixed-collector':
        s=s.replace('QBI abc bbas be DI_MMBT3906','QBI fixedabc bbas be DI_MMBT3906\nVCOL fixedabc 0 -14\nIABC ref abc 50p')
    elif mode!='complete-circuit':raise ValueError(mode)
    return s

def measure(mode):
    sys.path.insert(0,str(ota.ROOT/'engineering/whole-amp/tools'));import spice_runtime as sp
    sp.load(deck(mode));sp.cmd('op')
    names=['bo','be','abc']+([] if mode=='servo-alone' else ['out'])
    try:op={n:float(sp.vector('v('+n+')')[-1]) for n in names}
    except (IndexError,AssertionError):return dict(status='failed-op',log='\n'.join(sp.logs))
    result=dict(op=op,op_used_transient_fallback=any('Transient op finished successfully' in x for x in sp.logs),status='diagnostic-complete')
    if not all(math.isfinite(v) and abs(v)<15 for v in op.values()):result['status']='invalid-op'
    # A pseudo-transient OP can stop before the servo has settled. Continue without audio.
    if mode=='servo-alone':
        sp.cmd('tran 1u 1m 0 1u')
        try:
            t=sp.vector('time');result['end_s']=t[-1]
            result['final']={n:sp.vector('v('+n+')')[-1] for n in names}
            result['op_to_final_max_delta_V']=max(abs(result['final'][n]-op[n]) for n in names)
            result['reverse_BE_V']=sp.vector('v(bbas)')[-1]-sp.vector('v(be)')[-1]
        except (IndexError,AssertionError):result['status']='failed-settling'
    result['log']='\n'.join(sp.logs);return result

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rows=[]
    for mode in ['complete-circuit','servo-alone','ideal-servo','fixed-base','fixed-collector']:
        dp=ota.OUT/f'isolation-{mode}.cir';dp.write_text(deck(mode));lp=dp.with_suffix('.log')
        try:
            p=subprocess.run([sys.executable,__file__,'--case',mode],capture_output=True,text=True,timeout=25)
            r=json.loads(p.stdout) if not p.returncode else dict(status='failed',error=p.stderr[-1500:])
            log=r.pop('log','')+'\n'+p.stderr
        except subprocess.TimeoutExpired as e:r=dict(status='timeout',seconds=25);log=str(e.stderr or '')
        lp.write_text(log);rows.append(dict(mode=mode,deck=dp.name,deck_sha256=sha(dp),log=lp.name,log_sha256=sha(lp),**r));print(mode,r,flush=True)
    inputs=[Path(__file__),Path(bias.__file__),Path(ota.__file__),ota.OUT/'bias-screen.json',ota.OTA,ota.OP,bias.BJT]
    (ota.OUT/'bias-isolation.json').write_text(json.dumps(dict(scope='Fixed bias and ideal servo are diagnostic substitutions, not selected parts. Transient fallback OP is not automatically a settled DC result.',cases=rows,provenance={str(p.relative_to(ota.ROOT)):sha(p) for p in inputs}),indent=2)+'\n')
if __name__=='__main__':
    if len(sys.argv)>1:print(json.dumps(measure(sys.argv[2])))
    else:main()
