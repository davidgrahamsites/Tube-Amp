"""Use a reachable transient state as solver hints; never as physical startup evidence."""
import json,sys,ctypes as ct,hashlib
from pathlib import Path
import bias_screen as b

def main():
    sys.path.insert(0,str(b.ota.ROOT/'engineering/whole-amp/tools'))
    import spice_runtime as sp
    trim=json.loads((b.ota.OUT/'bias-screen.json').read_text())['trim_fraction']
    case=dict(trim_fraction=trim,control_ramp=True,hz=1000,amplitude=1)
    text=b.deck(case);(b.ota.OUT/'continuation-ramp.cir').write_text(text)
    sp.load(text);sp.cmd('tran 2u 16m 0 2u')
    assert sp.vector('time')[-1]>=.016-1e-10
    sp.lib.ngSpice_CurPlot.restype=ct.c_char_p
    sp.lib.ngSpice_AllVecs.argtypes=[ct.c_char_p];sp.lib.ngSpice_AllVecs.restype=ct.POINTER(ct.c_char_p)
    plot=sp.lib.ngSpice_CurPlot();names=sp.lib.ngSpice_AllVecs(plot)
    seeds={};i=0
    while names[i]:
        name=names[i].decode();v=sp.lib.ngGet_Vec_Info(names[i]).contents
        if v.type==3:
            assert v.length>0
            seeds[name]=float(v.real[v.length-1])
        i+=1
    (b.ota.OUT/'continuation-seeds.json').write_text(json.dumps(seeds,indent=2)+'\n')
    case=dict(trim_fraction=trim,target=5,dc_only=True)
    base='\n'.join(l for l in b.deck(case).splitlines() if not l.startswith('.nodeset'))+'\n'
    lines=['.nodeset v('+n+')='+format(x,'.15g') for n,x in seeds.items()]
    text=base.replace('.end','\n'.join(lines)+'\n.end')
    (b.ota.OUT/'continuation-off.cir').write_text(text)
    sp.cmd('destroy all');sp.load(text);sp.cmd('op')
    try:
        result={n:sp.vector('v('+n+')')[-1] for n in ['out','be','bo','abc','target']}
        status='complete'
    except (IndexError,AssertionError):result={};status='failed'
    (b.ota.OUT/'continuation.log').write_text('\n'.join(sp.logs))
    paths=[Path(__file__),Path(b.__file__),b.ota.OTA,b.ota.OP,b.BJT]
    report=dict(status=status,seeds=len(seeds),op=result,scope='Numerical hints only; not startup qualification',provenance={str(p.relative_to(b.ota.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    (b.ota.OUT/'continuation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
