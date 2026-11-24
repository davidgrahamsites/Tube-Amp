"""Independent terminal measurements of the explicit magnetics fixture."""
import hashlib,json,sys
import numpy as np
from fixture import ROOT,WHOLE
from feedback_model import build
sys.path.insert(0,str(WHOLE/'tools'))
import spice_runtime as sp

def main():
    rows=[]
    for lm in [10,40,160]:
        for lk in [.005,.02,.08]:
            p=dict(magnetizing_H=lm,leakage_H=lk,primary_cap_F=0,secondary_ohm=0)
            text=build(p)
            # Read the emitted magnetic elements, not an independent reimplementation.
            lines=[x for x in text.splitlines() if x.split(' ')[0] in ['LPA','LPB','LS','KOT','LLA','LLB','RPA','RPB']]
            for terminal in ['open','short']:
                load='RTERM SPEAKER 0 '+('1e12' if terminal=='open' else '1e-9')
                deck='Terminal test\nVDRIVE OT_PA OT_PB DC 0 AC 1\nRCT B_MAIN 0 1gig\n'+'\n'.join(lines+[load,'.end'])+'\n'
                sp.load(deck);sp.cmd('ac lin 1 1000 1000');z=1/-sp.vector('i(vdrive)')[0]
                measured=z.imag/(2*np.pi*1000);expected=lm+lk if terminal=='open' else lk
                rows.append(dict(Lm_H=lm,Lleak_H=lk,termination=terminal,measured_H=measured,expected_H=expected,relative_error=abs(measured/expected-1),measured_DCR_ohm=z.real))
                (ROOT/'results'/f'feedback-terminal-{lm}-{round(lk*1000)}-{terminal}.cir').write_text(deck);sp.cmd('destroy all')
    result=dict(scope='Independent port impedance measurement; no core or physical transformer qualification',rows=rows,passed=all(r['relative_error']<1e-5 and abs(r['measured_DCR_ohm']-200)<1 for r in rows),factory_sha256=hashlib.sha256(__import__('pathlib').Path(__file__).read_bytes()).hexdigest())
    (ROOT/'results/feedback-terminal-checks.json').write_text(json.dumps(result,indent=2)+'\n');assert result['passed'];print(len(rows),'terminal checks PASS')
if __name__=='__main__':main()
