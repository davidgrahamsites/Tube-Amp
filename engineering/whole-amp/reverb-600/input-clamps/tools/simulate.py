"""Source-only rail / ideal clamp witness; explicitly not an opamp macro-model."""
from pathlib import Path
import hashlib
import json
import sys
from analyze import source

M=Path(__file__).resolve().parents[1];ROOT=M.parents[3];D=M/'results'
sys.path.insert(0,str(ROOT/'engineering/whole-amp/tools'));import spice_runtime as sp

def base(load,drop,positive,negative):
    c,_=source();e=c['terminal_envelope'];r1=980000;r2=102000
    lines=['Reverb input rail-injection bound; ideal clamp, no IC load',
           '.options method=gear reltol=1e-6 abstol=1p vntol=1u',
           f'R601 IN_AC SEND_IN {r1}',f'R602 SEND_IN 0 {r2}',
           f'BCP SEND_IN VP I=max(0,(v(SEND_IN)-v(VP)-{drop})/1)',
           f'BCN VN SEND_IN I=max(0,(v(VN)-v(SEND_IN)-{drop})/1)',
           f'C616 VP 0 {e["rail_capacitor_min_F"]} IC={positive}',
           f'C617 0 VN {e["rail_capacitor_min_F"]} IC={-negative}',
           'RleakP VP 0 1e12','RleakN VN 0 1e12']
    if positive:lines.append(f'BREGP 0 VP I=max(0,({positive}-v(VP))/1)')
    if negative:lines.append(f'BREGN VN 0 I=max(0,(v(VN)-({negative}))/1)')
    if load:lines.extend([f'RloadP VP 0 {load*1.02}',f'RloadN VN 0 {load*1.02}'])
    return lines

def run(name,lines,command):
    deck='\n'.join(lines+['.end'])+'\n';(D/(name+'.cir')).write_text(deck)
    sp.load(deck);sp.cmd(command)
    v={n:sp.vector('v('+n.lower()+')') for n in ['IN_AC','SEND_IN','VP','VN']}
    return v

def transient(load,fault,powered,step,r,trans):
    lines=base(load,.5,15 if powered else 0,-15 if powered else 0)
    def element(ref):
        x=r[ref];return ref+' '+' '.join('0' if x['pins'][str(i)]=='GND' else x['pins'][str(i)] for i in [1,2])+' '+x['value'].replace('M','meg')
    lines += [element(ref) for ref in ['R7','R43','C601','R612','R24','R616','C607','R617','R618']]
    lines += [element('C6') if fault=='healthy' else 'VFAULT CL_P2 CLEAN_OUT 0',
              'VNORMAL CLEAN_OUT FX_RETURN 0',
              'BOUTP OUT_BUF VP I=max(0,(v(OUT_BUF)-v(VP)-.5)/1)',
              'BOUTN VN OUT_BUF I=max(0,(v(VN)-v(OUT_BUF)-.5)/1)',
              'ROUTLEAK OUT_BUF 0 1e12',
              'VPLATE B_EARLY 0 PWL(0 0 .1 0 .101 313 5 313 5.001 0 12 0)']
    v=run(f'tran-{load}-{fault}-{powered}-{step}',lines,f'tran {step} 12 0 {step} uic');t=sp.vector('time');assert t[-1]>=12
    outbuf=sp.vector('v(out_buf)');vp=v['VP'];vn=v['VN']
    output_injection=max(max(0,(x-p-.5)) for x,p in zip(outbuf,vp))
    output_injection=max(output_injection,max(max(0,(n-x-.5)) for n,x in zip(vn,outbuf)))
    currents=[abs(a-b)/980000 for a,b in zip(v['IN_AC'],v['SEND_IN'])]
    trans.append({'load_ohm':load,'maxstep_s':step,'fault':fault,'powered_source_only':powered,'end_s':t[-1],
                  'peaks_abs_V':{k:max(map(abs,x)) for k,x in v.items()},
                  'final_V':{k:x[-1] for k,x in v.items()},'maximum_R601_A':max(currents),'maximum_output_clamp_A':output_injection,
                  'maximum_rail_span_V':max(p-n for p,n in zip(v['VP'],v['VN']))})
    sp.cmd('destroy all')

def main():
    c,r=source();e=c['terminal_envelope'];sp.cmd('version');dc=[];trans=[]
    for load in c['comparison_rail_load_ohm']:
        for drop in e['clamp_forward_drop_V']:
            for polarity in [-1,1]:
                for powered in [False,True]:
                    lines=base(load,drop,15 if powered else 0,-15 if powered else 0)
                    v=run(f'dc-{load}-{drop}-{polarity}-{powered}',lines+[f'VTERM IN_AC 0 {polarity*313}'],'op')
                    dc.append({'load_ohm':load,'drop_V':drop,'polarity':polarity,'powered_source_only':powered,
                               'nodes_V':{k:x[-1] for k,x in v.items()},'input_series_A':abs(v['IN_AC'][-1]-v['SEND_IN'][-1])/980000})
                    sp.cmd('destroy all')
    for load in c['comparison_rail_load_ohm']:
        for fault in ['healthy','C6_short']:
            for powered in [False,True]:
                transient(load,fault,powered,.001,r,trans)
    for load in [None,10000]:
        transient(load,'C6_short',True,.0005,r,trans)
    # Independent DC resistor reduction with the declared forward drop.
    errors=[]
    for row in dc:
        rb=row['load_ohm']*1.02 if row['load_ohm'] else None
        g1=1/980000;g2=1/102000;gb=(1/rb if rb else 0)+1e-12;vf=row['drop_V']
        # Include the declared one-ohm conducting clamp and regulator slopes.
        free=(313*g1-vf*(g1+g2))/((g1+g2)*(1+gb)+gb)
        if row['powered_source_only'] and free<15:
            expected=(313*g1-(vf-15)*(g1+g2)+15)/((2+gb)*(g1+g2)+gb+1)
        else:expected=free
        actual=abs(row['nodes_V']['VP' if row['polarity']==1 else 'VN'])
        errors.append(abs(expected-actual))
    assert max(errors)<1e-6,max(errors)
    selected=[x for x in dc if x['load_ohm']==10000]
    assert all(x['nodes_V']['VP']-x['nodes_V']['VN']<36 for x in selected)
    assert all(x['input_series_A']<.01 for x in dc)
    out={'dc':dc,'transients':trans,'independent_DC_max_error_V':max(errors),'all_cases_completed':True,
         'source_sha256':c['circuit_sha256'],'model':'Piecewise zero-reverse-current clamp with0/0.5/1V forward threshold,1ohm slope; no minimum IC load; source-only regulator',
         'native_integrated':False,'hardware_qualified':False,
         'factory_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),M/'tools/analyze.py',M/'contract.json']},
         'deck_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in D.glob('*.cir')}}
    (D/'screen.json').write_text(json.dumps(out,indent=2)+'\n');(D/'spice.log').write_text('\n'.join(sp.logs)+'\n')
    print(json.dumps({'DC_cases':len(dc),'transient_cases':len(trans),'independent_error_V':max(errors),'selected_max_DC_span_V':max(x['nodes_V']['VP']-x['nodes_V']['VN'] for x in selected),'max_transient_rail_span_V':max(x['maximum_rail_span_V'] for x in trans)},indent=2))

if __name__=='__main__':main()
