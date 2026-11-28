"""Locate quiet-signal failures as a function of the trial junction capacitance."""
import itertools
import json

import assembled_return as assembly
import fixed_gain as gain


def main():
    rows=[]
    with gain.fixture():
        gain.STATE['net']=assembly.NETWORK
        for cjo in (400,650,850,1000,1200,1300,1500,1700,2000,2300,2600):
            corners=[]
            for h,o,t,l,c in itertools.product((0,500),(30,150),(25,85),(.9,1.1),(.977,1.023)):
                args=(20000,h,cjo,o,False,t,310,True,l)
                band=gain.audio(args,cap_scale=c,ac_only=True)['small_signal']
                db=band['band_min_max_dB']+[band['gain_dB']['20'],band['gain_dB']['20000']]
                corners.append(dict(harness_pF=h,contact_pF=o,temp_C=t,L_scale=l,cap_scale=c,low_dB=min(db),high_dB=max(db)))
            low=min(corners,key=lambda r:r['low_dB'])
            high=max(corners,key=lambda r:r['high_dB'])
            rows.append(dict(junction_C0_pF=cjo,low=low,high=high,all_pass=low['low_dB']>=-.5 and high['high_dB']<=.5))
    out=dict(cases=32*len(rows),network=assembly.NETWORK,table=rows,
             interpretation='Assumed square-root junction law. The per-device zero-bias parameter is not equivalent to measured pair capacitance. '
                            'Use measured complex pair admittance at the installed gate drive before accepting any unit.')
    (gain.MODULE/'results/shunt-charge-window.json').write_text(json.dumps(out,indent=1,default=float)+'\n')
    print([(r['junction_C0_pF'],r['all_pass']) for r in rows])


if __name__=='__main__':
    main()
