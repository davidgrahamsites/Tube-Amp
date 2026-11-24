"""Bounded 25 W target reference sweep; never rates the physical amplifier.
Uses the existing full-window fixture. Ideal OT/stiff rails/generic tubes remain
explicit limitations. No active schematic, part, transformer or PCB mutation.
"""
import hashlib,json,sys
from pathlib import Path
from fixture import ROOT,fingerprint
from run import bounded_case
OUT=ROOT/'results'

def summarize(row):
    if row.get('status')!='completed':return {'status':row.get('status'),'error':row.get('error')}
    s=row['signals']['SPEAKER'];fund=s['fundamental_Vpk']**2/16
    return dict(status='completed',input_Vpk=row['config']['amp'],fundamental_load_W=fund,
                speaker_THD_2_to_10_percent=s['THD_2_to_10_percent'],speaker_DC_V=s['mean_V'],
                ideal_load_DC_W=s['mean_V']**2/8,
                speaker_settling_relative_fundamental=row['settling_relative_fundamental']['SPEAKER'],
                internal_FX_SEND=row['signals']['FX_SEND'],end_s=row['end_s'])
def main():
    if '--target-check' in sys.argv:
        # Separate product: never mix timestep checks into the drive sweep.
        sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in [Path(__file__), ROOT/'tools/fixture.py', ROOT/'tools/run.py']}
        cases=[]
        for label,steps,max_step in [('nominal',96,20e-6),('refined',192,10e-6)]:
            name='power-target-25w-'+label
            row=bounded_case(name,dict(channel='clean',mode='native',freq=1000,amp=.00672,
                supply=278,volume=1,tone=.5,gain=.5,guard_pentode_power=True,
                steps=steps,max_step=max_step),time_limit_s=60)
            cases.append({'name':name,**summarize(row)})
        result=dict(scope='Near-target timestep comparison only; ideal transformer; not hardware rating',
                    source_hashes=fingerprint(),factory_hashes=sources,cases=cases,fabrication_ready=False)
        (OUT/'power-target-25w-check.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
        print(json.dumps(cases,indent=2))
        return
    cases=[]
    amplitudes=[.001,.003,.01,.03,.1,.3]
    if '--refine' in sys.argv:
        prior=json.loads((OUT/'power-target-summary.json').read_text())
        assert prior['source_hashes']==fingerprint(), 'Source changed; do not mix runs'
        cases=prior['cases'];amplitudes=[.005,.006,.007,.008]
        assert not any(c.get('input_Vpk') in amplitudes for c in cases), 'Refinement already recorded'
    for amp in amplitudes:
        name='power-target-clean-'+str(amp).replace('.','p')
        row=bounded_case(name,dict(channel='clean',mode='native',freq=1000,amp=amp,supply=278,volume=1,tone=.5,gain=.5,guard_pentode_power=True),time_limit_s=60)
        cases.append({'name':name,**summarize(row)})
    cases.sort(key=lambda c:c.get('input_Vpk',0))
    summary=dict(scope='1 kHz clean-channel reference, full volume, nominal stiff rails; NOT hardware rating',
        target_W=25,source_hashes=fingerprint(),load_ohm=8,main_supply_V=400,screen_supply_V=380,bias_V=-40,
        early_supply_V=278,cases=cases,limitations=['ideal transformer: no core/leakage/saturation/real losses','generic unqualified 6CA7 and 12AX7 models','no mains transformer regulation or 120/220 V line corners','no physical thermal/current/insulation test','finite drive points do not determine exact 1%/5% THD crossings'],fabrication_ready=False)
    (OUT/'power-target-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(cases,indent=2))
if __name__=='__main__':main()
