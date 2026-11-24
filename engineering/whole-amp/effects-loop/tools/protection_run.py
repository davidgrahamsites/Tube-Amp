"""Bounded candidate comparison. Retains failed runs; never releases CAD.
Run python3 protection_run.py [screen|stress|retry].
"""
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
from fixture import fingerprint, WHOLE
from transformer_run import bounded, OUT

BASE = dict(channel='clean', mode='native', freq=1000, amp=.00672, supply=278,
            volume=1, tone=.5, gain=.5, guard_pentode_power=True)

def cases(group):
    if group == 'acceptance':
        high=dict(screen_ohm=4465,rails_V=dict(VMAIN=440,VSCREEN=418,VBIAS=-36,VEARLY=306,VPRE=344))
        normal=dict(screen_ohm=4700)
        return [(label,dict(BASE,**cfg),tx,steps,exp,600) for label,cfg,tx,steps,exp in [
            ('target',dict(amp=.0087),{},96,normal),
            ('target-refined',dict(amp=.0087),{},192,normal),
            ('clean-overload',dict(amp=.1),{},96,normal),
            ('dirty-1k',dict(channel='dirty',amp=1),{},96,normal),
            ('dirty-5k',dict(channel='dirty',amp=1,freq=5000),{},96,normal),
            ('peaking-20k',dict(freq=20000),dict(half_primary_H=40,coupling=.995),96,normal),
            ('bass-overload',dict(freq=82.4,amp=.1),{},96,normal),
            ('high-clean',dict(amp=.1),{},96,high),
            ('high-dirty',dict(channel='dirty',amp=1),{},96,high),
            ('high-bass',dict(freq=82.4,amp=.1),{},96,high)]]
    if group == 'compare':
        return [(f'{r}-{label}',dict(BASE,**cfg),{},96,dict(screen_ohm=r),240)
                for r in [3300,4700] for label,cfg in [
                    ('target',dict(amp=.00803 if r==3300 else .0087)),
                    ('dirty-1k',dict(channel='dirty',amp=1)),
                    ('bass-overload',dict(freq=82.4,amp=.1))]]
    if group == 'retry':
        return [(label,dict(BASE,**cfg),tx,96,dict(screen_ohm=4700),600)
                for label,cfg,tx in [
                    ('peaking-20k',dict(freq=20000),dict(half_primary_H=40,coupling=.995))]]
    if group == 'corners':
        exp=dict(screen_ohm=4465,rails_V=dict(VMAIN=440,VSCREEN=418,VBIAS=-36,VEARLY=306,VPRE=344))
        return [(label,dict(BASE,**cfg),{},96,exp,240) for label,cfg in [
            ('clean-overload',dict(amp=.1)),('dirty-overload',dict(channel='dirty',amp=1)),
            ('bass-overload',dict(freq=82.4,amp=.1)),('target',dict(amp=.0087))]]
    if group == 'target':
        return [(f'{r}-{amp:g}',dict(BASE,amp=amp),{},96,dict(screen_ohm=r),120)
                for r in [3300,4700] for amp in [.008,.009,.010]]
    if group == 'screen':
        return [(f'{r}-{label}',dict(BASE,amp=amplitude),{},96,dict(screen_ohm=r),120)
                for r in [2200,3300,4700] for label,amplitude in [('nominal',.00672),('overload',.1)]]
    if group == 'stress':
        return [(label,dict(BASE,**cfg),tx,steps,dict(screen_ohm=4700),180)
                for label,cfg,tx,steps in [
                    ('nominal-refined',{}, {},192),
                    ('bass',dict(freq=82.4),{},96),
                    ('bass-lowL',dict(freq=82.4),dict(half_primary_H=2.5),96),
                    ('dirty-1k',dict(channel='dirty',amp=1),{},96),
                    ('dirty-5k',dict(channel='dirty',amp=1,freq=5000),{},96),
                    ('peaking-20k',dict(freq=20000),dict(half_primary_H=40,coupling=.995),96)]]
    raise ValueError(group)

def main():
    group=sys.argv[1] if len(sys.argv)>1 else 'screen'
    source=fingerprint()
    inputs=cases(group)
    result=dict(scope='Screen protection candidate, no native adoption; assumed linear transformer, stiff rails, generic EL34',
                source_hashes=source, cases=[], physical_qualified=False, fabrication_ready=False)
    def run(c):
        label,cfg,tx,steps,exp,limit=c
        return bounded('protection-'+group+'-'+label,cfg,tx,steps,exp,limit)
    with ThreadPoolExecutor(max_workers=2) as pool:
        for row in pool.map(run, inputs):
            result['cases'].append(row)
            (OUT/f'protection-{group}-summary.json').write_text(json.dumps(result,indent=2)+'\n')
            print(json.dumps(dict(name=row['name'],status=row['status'],W=row.get('fundamental_load_W'),stress=row.get('stress'))),flush=True)
    assert fingerprint()==source
    paths=[Path(__file__),*[(Path(__file__).parent/p) for p in ['protection_model.py','transformer_model.py','transformer_run.py','fixture.py','run.py']],WHOLE/'tools/spice_runtime.py']
    result['factory_hashes']={str(p.relative_to(WHOLE.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (OUT/f'protection-{group}-summary.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
