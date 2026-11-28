"""Search the crossover between output-edge detection and local rail detection."""
import itertools
import json
from guard_detector import measure, MODULE


if __name__=='__main__':
    rows=[]
    for rail,pin,sgn,edge in itertools.product(('hv','pos','neg','five','twelve','all'),(.5,4,40),(-1,1),
                                               (.05,.14,.4,1,2,3,4,5,6,8,12,20,40)):
        if rail in ('hv','neg'):
            rows.append(measure(rail,edge,pin,sgn))
        rows.append(measure(rail,edge,pin,sgn,droop=True))
    (MODULE/'results/guard-noise.json').write_text(json.dumps([measure(None,1,1,0,droop=True,ripple=r) for r in (1,5)],indent=2)+'\n')
    (MODULE/'results/guard-slew.json').write_text(json.dumps(rows,indent=1)+'\n')
    print([(p,max(r['mixer_peak_V'] for r in rows if r['pin_fall_us']==p and r['early_droop_enabled'])) for p in (.5,4,40)])
