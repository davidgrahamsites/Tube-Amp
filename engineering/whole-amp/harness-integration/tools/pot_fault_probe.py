#!/usr/bin/env python3
"""Bounded generic-tube DC probes of the dirty tone capacitor-short screen."""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

MODULE=Path(__file__).resolve().parents[1]
ROOT=MODULE.parents[2]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def worker(case,path):
    sys.path.insert(0,str(ROOT/'engineering/component-selection/heater-divider-rating/tools'))
    import supply
    text=supply.deck({'mode':'fixed','pre_V':case['pre_v'],'channel':'dirty','amp':0},json.loads((supply.M/'supply-contract.json').read_text()))
    components=json.loads((MODULE.parent/'reverb-600/circuit.json').read_text())['components']
    parts={c['reference']:c for c in components if c['reference'].startswith(('R','C'))}
    # Existing shared fixture uses a 1-ohm endpoint approximation.
    from fixture import numeric, CONTRACT
    assert CONTRACT.resolve()==(MODULE.parent/'reverb-600/circuit.json').resolve(), 'Unexpected fixture circuit override'
    lines=text.splitlines()
    for ref,f in case['settings'].items():
        c=parts[ref];total=numeric(c['value'])
        for name,resistance in ((ref+'A',max(1,total*(1-f))),(ref+'B',max(1,total*f))):
            hits=[i for i,l in enumerate(lines) if l.split() and l.split()[0]==name]
            assert len(hits)==1,(name,hits)
            words=lines[hits[0]].split();words[3]=str(resistance);lines[hits[0]]=' '.join(words)
    if case['fault']:
        ref=case['fault'];c=parts[ref]
        hits=[i for i,l in enumerate(lines) if l.split() and l.split()[0]==ref];assert len(hits)==1
        lines[hits[0]]=f"RFAULT {c['pins']['1']} {c['pins']['2']} 0.001"
    text='\n'.join(lines)+'\n';sp=supply.sp
    sp.cmd('version');sp.load(text);sp.cmd('op')
    voltages={n:sp.vector('v('+n.lower()+')')[-1] for n in ('B_PRE','B_EARLY','DR_CF','DR_TONE','DR_TREBLE_TOP','DR_TREBLE_W','DR_BASS_TOP','DR_BASS_BOTTOM','DIRTY_OUT')}
    voltages['GND']=0.
    assert all(math.isfinite(v) for v in voltages.values())
    pots={}
    for ref,f in case['settings'].items():
        c=parts[ref];p=c['pins'];total=numeric(c['value'])
        va,vb,vc=[voltages[p[str(i)]] for i in (1,2,3)]
        pa=(va-vb)**2/max(1,total*(1-f));pb=(vb-vc)**2/max(1,total*f)
        pots[ref]={'terminal_v':[va,vb,vc],'segment_power_w':[pa,pb],'total_track_w':pa+pb}
    # At the tone-stack input only R23 and the failed capacitor can conduct DC.
    # Check KCL at DR_TONE for C16/C17 from source-derived components.
    kcl=None
    if case['fault'] in ('C16','C17'):
        target=parts[case['fault']]['pins']['2']
        kcl=(voltages['DR_CF']-voltages['DR_TONE'])/numeric(parts['R23']['value'])-(voltages['DR_TONE']-voltages[target])/.001
        assert abs(kcl)<1e-7,kcl
    assert all(-1e-5<=v<=case['pre_v']+1e-3 for n,v in voltages.items())
    Path(path).write_text(json.dumps({'case':case,'status':'completed','voltages':voltages,'pots':pots,'tone_kcl_residual_a':kcl,'deck':text,'deck_sha256':hashlib.sha256(text.encode()).hexdigest(),'log':sp.logs},indent=2))

def main():
    screen=json.loads((MODULE/'results/pot-voltage-checks.json').read_text())
    settings={}
    for s in screen['summaries']:
        if s['fault'] in ('C15','C16','C17'):
            worst=max(s['pots'],key=lambda r:s['pots'][r]['power_w_per_v2'])
            settings[s['fault']]=s['pots'][worst]['power_case']['settings']
    paths=[Path(__file__),MODULE/'results/pot-voltage-checks.json',MODULE.parent/'reverb-600/circuit.json',ROOT/'engineering/component-selection/heater-divider-rating/tools/supply.py',ROOT/'engineering/component-selection/heater-divider-rating/supply-contract.json',MODULE.parent/'effects-loop/tools/fixture.py',MODULE.parent/'effects-loop/tools/loaded_feedback_model.py',MODULE.parent/'effects-loop/tools/feedback_model.py',MODULE.parent/'effects-loop/tools/run.py',MODULE.parent/'tools/spice_runtime.py',MODULE.parent/'simulation/models/dm12ax7s.inc',MODULE.parent/'simulation/models/6ca7s.inc']
    out={'id':'HI-006-loaded-probe','scope':'Generic tube DC, fixed B_PRE and desired buffer fixture, three selected settings; no exact tube, supply dynamics, faults beyond listed capacitor, thermal/wiper or native adoption qualification.','endpoint_approximation_ohm':1,'fault_short_ohm':.001,'inputs_sha256':{str(p.relative_to(ROOT)):sha(p) for p in paths},'cases':[],'native_adoption':False,'hardware_qualified':False}
    logs=[]
    with tempfile.TemporaryDirectory(prefix='renegade-pot-fault-') as td:
        for pre in (267.11,355.):
            for ref,setting in settings.items():
                for failed in (False,True):
                    case={'pre_v':pre,'settings':setting,'fault':ref if failed else None,'setting_source_fault':ref}
                    target=Path(td)/'result.json';target.unlink(missing_ok=True)
                    try:
                        proc=subprocess.run([sys.executable,str(Path(__file__)),'--worker',json.dumps(case),str(target)],capture_output=True,text=True,timeout=35)
                        logs.append(proc.stdout+proc.stderr)
                        if proc.returncode==0 and target.exists():
                            result=json.loads(target.read_text());logs.extend(result.pop('log'));deck=result.pop('deck')
                            if pre==267.11 and ref=='C17' and failed:(MODULE/'results/pot-fault-example.cir').write_text(deck)
                        else:result={'case':case,'status':'failed','error':(proc.stdout+proc.stderr)[-1600:]}
                    except subprocess.TimeoutExpired as e:
                        result={'case':case,'status':'timeout','error':'35 s worker deadline'};logs.append(str(e))
                    out['cases'].append(result)
                    (MODULE/'results/pot-fault-probe.json').write_text(json.dumps(out,indent=2)+'\n')
                    print(pre,ref,failed,result['status'],result.get('voltages',{}).get('DR_CF'),flush=True)
    (MODULE/'results/pot-fault-probe.log').write_text('\n'.join(logs)+'\n')
    assert all(c['status']=='completed' for c in out['cases'])
    from check_pot_voltage import render_report
    render_report(screen, json.loads((MODULE/'voltage-screen.json').read_text()))

if __name__=='__main__':
    if '--worker' in sys.argv:worker(json.loads(sys.argv[-2]),sys.argv[-1])
    else:main()
