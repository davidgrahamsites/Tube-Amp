"""Scoped nonlinear preamp sweep. Run from any directory with system Python3."""
from pathlib import Path
import csv
import hashlib
import json
import math
import re
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT.parent
sys.path.insert(0, str(WHOLE / 'tools'))
import spice_runtime as sp

OUT = ROOT / 'results'
CONTRACT = WHOLE / 'reverb-600/circuit.json'
MODEL = WHOLE / 'simulation/models/dm12ax7s.inc'
PARTS = json.loads(CONTRACT.read_text())['components']

def value(v):
    return re.sub('M$', 'meg', v.split()[0])

def numeric(v):
    x = value(v)
    m = re.fullmatch(r'([\d.]+)(meg|k|m|u|n|p)?', x)
    return float(m[1]) * {None:1, 'meg':1e6, 'k':1e3, 'm':1e-3,
                           'u':1e-6, 'n':1e-9, 'p':1e-12}[m[2]]

def deck(channel, supply, freq, amp, volume):
    lines = ['Renegade electric preamp headroom screen',
             f'.include "{MODEL}"',
             '.options method=gear maxord=2 reltol=0.0001 abstol=1p vntol=1u',
             f'VSUP B_EARLY 0 {supply}', f'VPOST B_PRE 0 {supply+35}',
             f'VSOURCE PICKUP 0 SIN(0 {amp} {freq})',
             'RSOURCE PICKUP INPUT 20k', 'CCABLE INPUT 0 470p',
             'R1 INPUT INPUT_STOP 68k']
    sheet = '01_clean' if channel == 'clean' else '02_dirty'
    for c in PARTS:
        if c['sheet'] != sheet and not (channel == 'dirty' and c['sheet'] == '02b_dirty_tone'):
            continue
        r, p = c['reference'], {k: ('0' if n == 'GND' else n) for k,n in c['pins'].items()}
        if r.startswith('RV'):
            f = volume if r in ['RV3','RV8'] else .5
            total = numeric(c['value'])
            lines += [f'{r}A {p["1"]} {p["2"]} {max(1,total*(1-f))}',
                      f'{r}B {p["2"]} {p["3"]} {max(1,total*f)}']
        elif r.startswith(('R','C')):
            lines.append(f'{r} {p["1"]} {p["2"]} {value(c["value"])}')
        elif r.startswith('V'):
            keys = ['1','2','3'] if '1' in p else ['6','7','8']
            lines.append(f'X{r}_{keys[0]} ' + ' '.join(p[k] for k in keys) + ' 12AX7A')
    assert sum(line.startswith('XV') for line in lines) == (2 if channel == 'clean' else 4)
    pre = 'CL' if channel == 'clean' else 'DR'
    end = 'CLEAN_OUT' if channel == 'clean' else 'DIRTY_OUT'
    # Zero-volt probe measures selected grid current after the relay.
    lines += [f'RCONTACT INPUT_STOP SELECTED .05',
              f'VGRID SELECTED {pre}_IN 0',
              f'RLOAD {end} 0 1meg', '.end']
    return '\n'.join(lines)+'\n'

def spectrum(t, v, freq, start_cycle, cycles=10):
    sample_t = (start_cycle + np.arange(cycles*256)/256) / freq
    y = np.interp(sample_t, t, v)
    z = np.fft.rfft(y) / len(y)
    harmonics = 2*np.abs(z[np.arange(1,11)*cycles])
    assert harmonics[0] > 1e-12, 'Missing AC path or invalid Fourier output'
    return {'fundamental_Vpk':float(harmonics[0]),
            'THD_2_to_10_percent':float(100*np.linalg.norm(harmonics[1:])/harmonics[0]),
            'mean_V':float(np.mean(y)), 'min_V':float(y.min()), 'max_V':float(y.max())}

def run(channel, supply, freq, amp, volume=.25, steps=128, cycles=60, save_wave=False):
    # Give cathode/coupling capacitors time to settle even at high frequency.
    cycles = max(cycles, math.ceil(freq * (1.0 if steps >= 256 else .5)))
    name = f'{channel}-B{supply}-F{freq}-A{amp}-V{volume}-S{steps}-C{cycles}'
    text = deck(channel, supply, freq, amp, volume)
    (OUT/(name+'.cir')).write_text(text)
    start = len(sp.logs)
    sp.load(text)
    sp.cmd('op')
    pre = 'CL' if channel == 'clean' else 'DR'
    node_names = [pre+'_IN',pre+'_K1',pre+'_P1', 'CLEAN_OUT' if channel=='clean' else 'DIRTY_OUT']
    op = {n:sp.vector('v('+n+')')[-1] for n in node_names[:3]}
    step = 1/(freq*steps)
    sp.cmd(f'tran {step} {cycles/freq} {(cycles-30)/freq} {step}')
    t = np.array(sp.vector('time'))
    assert t[-1] >= cycles/freq*(1-1e-6), (name,t[-1])
    vectors = {n:np.array(sp.vector('v('+n+')')) for n in ['INPUT', *node_names]}
    stats = {n:spectrum(t,y,freq,cycles-10) for n,y in vectors.items()}
    earlier = spectrum(t,vectors[pre+'_P1'],freq,cycles-20)
    vk = vectors[pre+'_IN']-vectors[pre+'_K1']
    # Original model law (not total VGRID current, which includes grid-leak/displacement currents).
    ig = 5e-6*np.maximum(vk+.2,0)**1.5
    last = t >= (cycles-10)/freq
    result = {'id':name,'channel':channel,'B_EARLY_V':supply,'B_PRE_V':supply+35,
              'frequency_Hz':freq,'source_Vpk':amp,'volume_fraction':volume,
              'max_step_s':step,'cycles':cycles,'op':op,'signals':stats,
              'grid_to_cathode_max_V':float(vk[last].max()),
              'model_conductive_grid_current_peak_uA':float(ig[last].max()*1e6),
              'first_stage_settling_fundamental_relative_change':abs(stats[pre+'_P1']['fundamental_Vpk']/earlier['fundamental_Vpk']-1),
              'first_stage_settling_THD_percentage_point_change':abs(stats[pre+'_P1']['THD_2_to_10_percent']-earlier['THD_2_to_10_percent'])}
    result['first_stage_gain'] = stats[pre+'_P1']['fundamental_Vpk']/amp
    if save_wave:
        times=(cycles-2+np.arange(1024)/512)/freq
        with (OUT/(name+'.csv')).open('w') as f:
            w=csv.writer(f,lineterminator="\n"); w.writerow(['time_s',*vectors]);
            w.writerows(zip(times,*[np.interp(times,t,y) for y in vectors.values()]))
    (OUT/(name+'.log')).write_text('\n'.join(sp.logs[start:])+'\n')
    sp.cmd('destroy all')
    return result

def main():
    dirty_only = '--dirty-only' in sys.argv
    old = json.loads((OUT/'summary.json').read_text()) if dirty_only else None
    results=[c for c in old['cases'] if c['channel']=='clean'] if old else []
    for ch in (['dirty'] if dirty_only else ['clean','dirty']):
        for b in [240,278,320]:
            for f in [82.4,1000]:
                cases=[]
                for a in [.01,.1,.25,.5,.75,1,1.5,2,3]:
                    row=run(ch,b,f,a,save_wave=b==278 and f==1000 and a in [.1,1,2])
                    cases.append(row)
                ref=cases[0]['first_stage_gain']
                for row in cases:
                    row['gain_change_dB_from_10mV']=20*math.log10(row['first_stage_gain']/ref)
                results.extend(cases)
                print(ch,b,f,'done',flush=True)
    refinements=[c for c in old['refinements'] if c['channel']=='clean'] if old else []
    for ch in (['dirty'] if dirty_only else ['clean','dirty']):
        for f in [82.4,1000]:
            for a in [1,2]:
                refinements.append(run(ch,278,f,a,steps=256,cycles=120,save_wave=True))
    # Clean volume is after the first triode: verify first-stage overload cannot be repaired here.
    controls=[run('clean',278,1000,1,volume=v,steps=256,cycles=120,save_wave=True) for v in [.05,.01]]
    payload={'model_sha256':hashlib.sha256(MODEL.read_bytes()).hexdigest(),
             'contract_sha256':hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
             'model_provenance':'Duncan Munro 12AX7s V1 1997, educational generic model with grid current; unchanged repository model. Not an exact purchased tube.',
             'scope':'Preamp only, original input; ideal fixed supplies and ideal relay selection, no power stage or reverb.',
             'assumptions':{'source':'20k resistive Thevenin plus470pF cable; not a specific humbucker model','supplies':'B_EARLY240/278/320V, B_PRE35V higher; sensitivity envelope around historical nominal278V, not supply qualification','controls':'tone/gain0.5 electrical fraction; clean volume/dirty master0.25. These are not knob rotation percentages.','output_load':'1M resistive test load, not complete FX/reverb/PI impedance'},
             'screening_criteria':'Record first-stage5%THD and1dB compression crossings; diagnostic thresholds, not an agreed clean product spec.',
             'cases':results,'refinements':refinements,'volume_comparison':controls}
    (OUT/'summary.json').write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
    print('Saved',len(results),'sweep cases and',len(refinements)+len(controls),'refinement/control cases')

if __name__=='__main__':main()
