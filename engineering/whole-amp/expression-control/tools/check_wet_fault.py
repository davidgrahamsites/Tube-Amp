"""Independent SPICE check of the passive fault model; no transistor qualification."""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE.parent / 'tools'))


def deck_for(name, step):
    series = 47000 if name == 'candidate-fast50us' else 100
    deck = f'''Passive wet fault cross-check: incremental 33 V change, ideal switches
Vfault source 0 PWL(0 0 .001 0 .0010001 33 .011 33 .0110001 0 .101 0)
R616 source outac {series}
C607 outac wet 1u
R617 wet 0 1meg
R618 wet mix 1meg
Rreturn mix 0 200k
R24 mix 0 10meg
.options method=gear maxord=2 reltol=1e-7 abstol=1e-12 vntol=1e-9
.save v(mix) v(wet)
.tran {step} .101 0 {step}
'''
    if name != 'native-no-mute':
        deck += '''Vcontact contact 0 PWL(0 0 .016 0 .0160001 1 .101 1)
Scontact wet 0 contact 0 CONTACT
.model CONTACT SW(Ron=.1 Roff=1e15 Vt=.5 Vh=0)
'''
    if name == 'candidate-fast50us':
        deck += '''Vfast fast 0 PWL(0 0 .00105 0 .0010501 1 .101 1)
Sfast wet 0 fast 0 FAST
.model FAST SW(Ron=100 Roff=1e15 Vt=.5 Vh=0)
'''
    return deck + '.end\n'


def run_case(name, step):
    import spice_runtime as sp
    deck = deck_for(name, step)
    try:
        sp.load(deck)
        sp.cmd('run')
        time = sp.vector('time')
        mix = sp.vector('v(mix)')
        assert time[-1] >= .101 - 1e-9, ('incomplete', time[-1])
        assert all(math.isfinite(x) for x in time + mix)
        integral = sum((b-a)*(x*x+y*y)/2 for a,b,x,y in zip(time,time[1:],mix,mix[1:]))
        result = dict(status='complete', peak_mix_V=max(abs(x) for x in mix),
                      mix_squared_integral_V2s=integral, points=len(time), completed_s=time[-1])
    except (AssertionError, ValueError) as error:
        result = dict(status='failed', error=repr(error))
    return dict(name=name, step_s=step, deck=deck, log='\n'.join(sp.logs), **result)


def main():
    source = BASE / 'results/wet-fault-transfer.json'
    analytical = json.loads(source.read_text())
    runs = []
    for name in ['native-no-mute', 'native-contact15ms', 'candidate-fast50us']:
        for step in [2e-6, 5e-7]:
            try:
                child = subprocess.run([sys.executable, __file__, '--case', name, str(step)],
                                       capture_output=True, text=True, timeout=30)
                result = json.loads(child.stdout) if child.returncode == 0 else dict(status='failed', log=child.stderr)
            except subprocess.TimeoutExpired as error:
                result = dict(status='timeout', timeout_s=30, log=str(error), deck=deck_for(name,step))
            result.update(name=name, step_s=step)
            runs.append(result)
            print(name, step, result['status'], flush=True)
    comparisons = []
    for run in runs:
        ref = next(r for r in analytical['transient_cases'] if r['variant']==run['name'] and
                   r['source_ohm']==100000 and r['extra_load_ohm'] is None and
                   r['change_V']==33 and r['duration_s']==.01)
        if run['status'] == 'complete':
            comparisons.append(dict(name=run['name'], step_s=run['step_s'],
                peak_relative_error=abs(run['peak_mix_V']/ref['peak_mix_V']-1),
                integral_relative_error=abs(run['mix_squared_integral_V2s']/ref['mix_squared_integral_V2s']-1)))
    checks = [dict(name='all six bounded runs completed',passed=all(r['status']=='complete' for r in runs)),
              dict(name='peak agrees within 0.1 percent',passed=len(comparisons)==6 and all(r['peak_relative_error']<.001 for r in comparisons)),
              dict(name='squared voltage integral agrees within 0.5 percent',passed=len(comparisons)==6 and all(r['integral_relative_error']<.005 for r in comparisons))]
    refinements=[]
    for name in ['native-no-mute','native-contact15ms','candidate-fast50us']:
        pair=[r for r in runs if r['name']==name]
        if all(r['status']=='complete' for r in pair):
            refinements.append(dict(name=name, integral_relative_delta=abs(pair[0]['mix_squared_integral_V2s']/pair[1]['mix_squared_integral_V2s']-1)))
    checks.append(dict(name='integral timestep refinement within 0.1 percent',passed=len(refinements)==3 and all(r['integral_relative_delta']<.001 for r in refinements)))
    report=dict(qualified=False,scope='Independent passive RC/ideal-switch cross-check at MIX_OUT only',
        limitations=['100 ns input/switch transitions approximate analytical instantaneous events.',
                     'No gate charge, real JFET, detector delay, tube PI, speaker or perceptual silence qualification.'],
        comparisons=comparisons,refinements=refinements,checks=checks,runs=runs,
        provenance={str(p.relative_to(BASE.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,Path(__file__),BASE.parent/'tools/spice_runtime.py']})
    (BASE/'results/wet-fault-crosscheck.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(checks=checks,comparisons=comparisons,refinements=refinements),indent=2))
    if not all(c['passed'] for c in checks):sys.exit(1)


if __name__=='__main__':
    if len(sys.argv)>1:print(json.dumps(run_case(sys.argv[2],float(sys.argv[3]))))
    else:main()
