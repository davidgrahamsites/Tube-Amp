"""Independent SPICE branch representation of the declared clamp envelope."""
from pathlib import Path
import itertools
import json
import sys
import numpy as np
from analyze import M, ROOT, sha, inputs, dc, ac
sys.path.insert(0,str(ROOT/'engineering/whole-amp/tools'))
import spice_runtime as sp
D=M/'results'


def base(r, threshold):
    rows=['Wet contact protection envelope; NOT a manufacturer Zener model',
          '.options reltol=1e-7 abstol=1p vntol=1u method=gear']
    pins={'R7':('PLATE','FX_RETURN'),'R43':('FX_RETURN','0'),
          'R612':('FX_RETURN','MIX_OUT'),'R24':('MIX_OUT','0'),
          'R618':('MIX_OUT','WET_AC'),'R617':('WET_AC','0'),
          'R616':('OUT_BUF','OUT_AC'),'C607':('OUT_AC','WET_AC'),
          'C601':('FX_RETURN','IN_AC'),'R601':('IN_AC','SEND_IN'),
          'R602':('SEND_IN','0')}
    rows += [f'{ref} {a} {b} {r[ref]:.12g}' for ref,(a,b) in pins.items()]
    if threshold is not None:
        rows.append(f'BCLAMP WET_AC 0 I=(max(v(WET_AC)-{threshold},0)-max(-v(WET_AC)-{threshold},0))/220')
    return rows


def run(name, lines, command):
    deck='\n'.join(lines+['.end'])+'\n';(D/(name+'.cir')).write_text(deck)
    sp.load(deck);sp.cmd(command)
    v={n:np.array(sp.vector('v('+n.lower()+')')) for n in ['WET_AC','MIX_OUT','FX_RETURN','OUT_AC']}
    return v


def main():
    c,r=inputs();sp.cmd('version');dcs=[];acs=[];trans=[];dcerror=0;acerror=0
    for supply,threshold,polarity in itertools.product(c['dc']['supply_V'],c['candidate']['clamp_threshold_screen_V'],[-1,1]):
        v=run(f'dc-{supply}-{threshold}-{polarity}',base(r,threshold)+[f'VP PLATE 0 {supply*polarity}','VW OUT_BUF 0 0'],'op')
        pred=dc(r,supply,threshold,220)
        error=max(abs(v[n][-1]-polarity*pred[key]) for n,key in [('WET_AC','wet_V'),('MIX_OUT','mix_V'),('FX_RETURN','fx_V')])
        dcerror=max(dcerror,float(error));dcs.append(dict(supply_V=supply,threshold_V=threshold,polarity=polarity,wet_V=float(v['WET_AC'][-1]),error_V=float(error)))
        sp.cmd('destroy all')
    for hz,rs,cp,wet in itertools.product(c['ac']['frequencies_Hz'],c['ac']['source_ohm'],[0,1e-9],[False,True]):
        # Omit cold-plate R7/R43 and drive the port with exactly the analytic source impedance.
        lines=[s for s in base(r,None) if not s.startswith(('R7 ','R43 '))]
        lines += [f'VD DRIVE 0 DC 0 AC {0 if wet else 1}',f'RS DRIVE FX_RETURN {rs}',f'VW OUT_BUF 0 DC 0 AC {1 if wet else 0}']
        if cp:lines.append(f'CP WET_AC 0 {cp}')
        v=run(f'ac-{hz}-{rs}-{cp}-{wet}',lines,f'ac lin 1 {hz} {hz}')
        expected=ac(r,hz,rs,cp,wet,r['C607']);error=max(abs(v[n][-1]-expected[i]) for i,n in enumerate(['FX_RETURN','MIX_OUT','WET_AC']))
        acerror=max(acerror,float(error));acs.append(dict(Hz=hz,source_ohm=rs,pair_F=cp,wet_drive=wet,error_V=float(error)))
        sp.cmd('destroy all')
    cases=list(itertools.product([313,400],[23,40],[-18,0,18],[.5e-6]))
    cases += [(400,40,0,.25e-6)]
    for supply,threshold,wet,step in cases:
        rr=dict(r,R616=r['R616']*.99,C607=r['C607']*1.1)
        lines=base(rr,threshold)+[f'VP PLATE 0 {supply}',f'VW OUT_BUF 0 {wet}',
              'VC CONTROL 0 PWL(0 0 .01 0 .01000001 1 .03 1)',
              'SRELAY WET_AC CONTACT CONTROL 0 CONTACT_MODEL','VSENSE CONTACT 0 0',
              '.model CONTACT_MODEL SW(Ron=.1 Roff=1e12 Vt=.5 Vh=.1)']
        name=f'close-{supply}-{threshold}-{wet}-{step}'
        v=run(name,lines,f'tran {step} .03 0 {step}')
        t=np.array(sp.vector('time'));assert t[-1]>=.03
        i=np.array(sp.vector('i(vsense)'));ir=(wet-v['OUT_AC'])/rr['R616']
        power=ir*ir*rr['R616'];energy=float(np.trapz(power,t))
        row=dict(supply_V=supply,threshold_V=threshold,wet_source_V=wet,maxstep_s=step,
                 initial_wet_V=float(v['WET_AC'][0]),contact_peak_A=float(max(abs(i))),
                 final_wet_V=float(v['WET_AC'][-1]),R616_energy_J=energy,
                 R616_peak_W=float(max(power)),end_s=float(t[-1]),samples=len(t))
        trans.append(row)
        if supply==400 and threshold==40 and wet==0:
            keep=(t>=.00999)&(t<=.011)
            np.savetxt(D/(name+'.csv'),np.column_stack([t[keep],v['WET_AC'][keep],i[keep],power[keep]]),delimiter=',',header='time_s,WET_AC_V,contact_A,R616_W',comments='',fmt='%.12g')
        sp.cmd('destroy all')
    inputs();assert dcerror<1e-5 and acerror<1e-7,(dcerror,acerror)
    out=dict(dc=dcs,ac=acs,closing=trans,DC_independent_max_error_V=dcerror,AC_independent_max_error_V=acerror,
             source_sha256=c['source_sha256'],contract_sha256=sha(M/'contract.json'),factory_sha256={p.name:sha(p) for p in [Path(__file__),M/'tools/analyze.py']},
             deck_sha256={p.name:sha(p) for p in D.glob('*.cir')},waveform_sha256={p.name:sha(p) for p in D.glob('*.csv')},
             model='Symmetric piecewise envelope with220ohm slope; ideal wet voltage source;0.1ohm mechanical switch; no arc/bounce or manufacturer device model',native_integrated=False,hardware_qualified=False)
    (D/'screen.json').write_text(json.dumps(out,indent=2)+'\n');(D/'spice.log').write_text('\n'.join(sp.logs)+'\n')
    print(json.dumps(dict(DC=len(dcs),AC=len(acs),closing=len(trans),DC_error_V=dcerror,AC_error_V=acerror,max_contact_A=max(x['contact_peak_A'] for x in trans)),indent=2))


if __name__=='__main__': main()
