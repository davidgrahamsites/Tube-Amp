"""Source-derived loop reference. No native schematic/PCB writes."""
from pathlib import Path
import hashlib
import json
import math
import os
import re

ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT.parent
CONTRACT = Path(os.environ.get('RENEGADE_LOOP_INPUT', str(WHOLE / 'reverb-600/circuit.json')))
MODELS = [WHOLE / 'simulation/models/dm12ax7s.inc', WHOLE / 'simulation/models/6ca7s.inc']
PARTS = json.loads(CONTRACT.read_text())['components']
LOOP = {'R1','C601','R601','R602','R612','R616','C607','R617','R618'}

def numeric(value):
    m = re.fullmatch(r'([\d.]+)(M|k|m|u|n|p)?', value.split()[0])
    if not m:
        raise ValueError(value)
    return float(m[1])*{None:1,'M':1e6,'k':1e3,'m':1e-3,'u':1e-6,'n':1e-9,'p':1e-12}[m[2]]

def fingerprint():
    return {str(p.relative_to(WHOLE.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [CONTRACT,*MODELS]}

def deck(channel='clean', mode='native', stimulus='dry', freq=1000, amp=.01,
         supply=278, volume=.25, tone=.5, gain=.5, source_ohm=1000, burst=False, feedback_phase=1,
         guard_pentode_power=False):
    # Electrical pot fractions; not front-panel rotation or audio taper.
    lines=['Renegade existing loop integrated ideal-transformer reference']
    lines += [f'.include "{p}"' for p in MODELS]
    if guard_pentode_power:
        # Bgs defines a nonnegative node. Newton trial values can nevertheless
        # leave that domain. Guard the subsequent fractional power, retaining
        # the original file, copyright and all physical model coefficients.
        model = '\n'.join(line.rstrip() for line in MODELS[1].read_text().replace('\x1a', '').splitlines())
        assert model.count('V=V(gs)^1.5') == 1
        model = model.replace('V=V(gs)^1.5', 'V=URAMP(V(gs))^1.5')
        lines[2] = '* Local numerical domain guard at Bgs2; see solver-review.md\n' + model
    waveform=f'SIN(0 {amp} {freq})'
    if burst:
        waveform='DC 0'  # Gate boundaries must align with sine zero crossings.
    lines += ['.options method=gear maxord=2 reltol=0.001 abstol=1n vntol=10u gmin=1e-10 rshunt=1e12 cshunt=1e-14',
              f'VEARLY B_EARLY 0 {supply}',f'VPRE B_PRE 0 {supply+35}',
              'VMAIN B_MAIN 0 400','VSCREEN B_SCREEN 0 380','VBIAS BIAS_OUT 0 -40',
              f'VSOURCE PICKUP 0 DC 0 AC {1 if stimulus=="dry" else 0} '+waveform,
              'RSOURCE PICKUP INPUT 20k','CCABLE INPUT 0 470p',
              f'VWET OUT_BUF 0 DC 0 AC {1 if stimulus=="wet" else 0}',
              'VTEST RET_DRIVE 0 DC 0 AC 1']
    if burst:
        lines=[l for l in lines if not l.startswith('VSOURCE ')]
        lines += [f'BSOURCE PICKUP 0 V={amp}*sin(2*pi*{freq}*time)*(time>0.1)*(time<0.2)']
    inventory=[]
    for c in PARTS:
        ref=c['reference']; sh=c['sheet']
        if not(sh in {'01_clean','02_dirty','02b_dirty_tone','04_output'} or ref in LOOP):
            continue
        p={k:('0' if n=='GND' else n) for k,n in c['pins'].items()}
        if ref.startswith('RV'):
            fraction=volume if ref in {'RV3','RV8'} else gain if ref=='RV4' else tone
            total=numeric(c['value'])
            lines += [f'{ref}A {p["1"]} {p["2"]} {max(1,total*(1-fraction))}',f'{ref}B {p["2"]} {p["3"]} {max(1,total*fraction)}']
        elif ref.startswith(('R','C')):
            lines += [f'{ref} {p["1"]} {p["2"]} {numeric(c["value"])}']
        elif ref.startswith('V'):
            keys=['3','4','5','8'] if ref in {'V5','V6'} else ['1','2','3'] if '1' in p else ['6','7','8']
            model='6CA7' if ref in {'V5','V6'} else '12AX7A'
            lines += [f'X{ref}_{keys[0]} '+ ' '.join(p[k] for k in keys)+f' {model}']
        else:
            raise ValueError('Unhandled selected part '+ref)
        inventory.append(f'{ref}:{c["unit"]}')
    assert len([l for l in lines if l.startswith('XV')])==10
    end='CLEAN_OUT' if channel=='clean' else 'DIRTY_OUT'
    selected='CL_IN' if channel=='clean' else 'DR_IN'
    inactive='DR_G2' if channel=='clean' else 'CL_G2'
    lines += [f'RK1A INPUT_STOP {selected} .05',f'RK1B {inactive} 0 .05',f'RK2 {end} FX_SEND .05']
    if mode in {'native','send-isolated','send-isolated-short'}:
        lines += ['RNORMAL FX_SEND FX_RETURN .05']
        if mode!='native':
            # Architecture experiment only: 100:1 pad, ideal follower, 100 ohm
            # output resistor. Does not define fault protection or actual parts.
            lines += ['RPAD_HIGH FX_SEND SEND_PAD 9.9meg','RPAD_LOW SEND_PAD 0 100k',
                      'ESEND SEND_DRV 0 SEND_PAD 0 1','RSEND SEND_DRV SEND_PORT 100',
                      'RSEND_LOAD SEND_PORT 0 100k','CSEND_CABLE SEND_PORT 0 2n']
            if mode=='send-isolated-short': lines += ['RSEND_SHORT SEND_PORT 0 .01']
    elif mode=='buffer':
        lines += ['RBUF_IN FX_SEND 0 1meg','EBUF BUF_OUT 0 FX_SEND 0 1',f'RBUF_OUT BUF_OUT FX_RETURN {source_ohm}']
    elif mode=='return-drive': lines += [f'RRETURN RET_DRIVE FX_RETURN {source_ohm}']
    elif mode=='send-short': lines += ['RNORMAL FX_SEND FX_RETURN .05','RSHORT FX_SEND 0 .01']
    else: raise ValueError(mode)
    # Input of reverb follower treated as infinite impedance. Its 1M/100k divider
    # is retained. No clamp or tank transfer: report SEND_IN headroom separately.
    # Wet output ideal source through actual R616/C607/R617/R618. No wet feedback.
    n=math.sqrt(7600/8)/2
    lines += ['RPA OT_PA PA_W 100','RPB OT_PB PB_W 100',
              f'EPA PA_W B_MAIN SPEAKER 0 {n}', f'EPB B_MAIN PB_W SPEAKER 0 {n}',
              f'FSA 0 SPEAKER EPA {n}', f'FSB 0 SPEAKER EPB {n}',
              'RLOAD SPEAKER 0 8',f'ENFB OT_4 0 SPEAKER 0 {feedback_phase/math.sqrt(2)}','.end']
    return '\n'.join(lines)+'\n', inventory
