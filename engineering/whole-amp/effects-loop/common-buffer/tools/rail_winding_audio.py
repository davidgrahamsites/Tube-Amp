"""Exercise the two 400 V windings and the low-line pass circuit together."""
import hashlib
import json
import math
from itertools import product
from pathlib import Path
from unittest.mock import patch

import guard_audio
import low_line_rail
import pulse_winding

MODULE = guard_audio.MODULE
COILS = [('MSS1210H-475KED', .0047, 3.4, .53e6), ('MSS1210H-106KED', .010, 7.1, .38e6)]
SPEC = dict(taps=['mid'], coils=[
    dict(part=part, L=L, dcr=dcr, cw_pF=1e12/(L*(2*math.pi*srf)**2), rated_V=400)
    for part, L, dcr, srf in COILS])


def fault_cases():
    pulse_winding.STATE.update(spec=SPEC, corner={})
    quiet = [dict(label='nominal'), dict(label='negative', sign=-1),
             dict(label='combined corner', rise_us=.05, wire_pF=0, scale=.9, winding_pF=30,
                  shunt_pF=50, end_pF=256.5, mid_pF=313.5, start_pF=209, shunt_ohm=18, fine=True)]
    playing = [dict(label='playing', sign=s, live_phase=p) for s in (-1,1) for p in (0,90,180,270)]
    fast = [pulse_winding.with_coils(pulse_winding.sudden_guard.fault(**c)) for c in quiet+playing]
    hand = [pulse_winding.with_coils(pulse_winding.guard_handover.run(**c)) for c in
            ({},dict(sign=-1),dict(stuck=True),dict(open_guard=True))]
    nominal = [max(r['windings'][i]['peak_V'] for r in hand) for i in (0,1)]
    # Explore unequal parasitics around typical SRF and opposite L tolerances.
    # These are sensitivities. The data sheet gives no production SRF limits.
    for ca, cb, la in product((.65,1.5), (.65,1.5), (.9,1.1)):
        corner = dict(c_scales=[ca,cb], l_mismatch=[la,2-la], r_scale=1.236)
        pulse_winding.STATE.update(corner=corner)
        row = pulse_winding.with_coils(pulse_winding.guard_handover.run())
        row['sensitivity'] = corner
        hand.append(row)
    pulse_winding.STATE.update(corner={})
    summary = dict(nominal_handover_by_coil_V=nominal, peak_by_coil_V=[max(r['windings'][i]['peak_V'] for r in fast+hand) for i in (0,1)],
                   peak_by_coil_A=[max(r['windings'][i]['peak_A'] for r in fast+hand) for i in (0,1)],
                   quiet_mixer_V=max(r['peak_mixer_V'] for r in fast if r['phase_deg'] is None),
                   playing_after_switch_V=max(r['post_switch_peak_V'] for r in fast if r['phase_deg'] is not None),
                   handover_V=max(r['peak_V'] for r in hand if not r['fast_open']))
    return dict(summary=summary, runs=dict(fast=fast,handover=hand))


def main():
    checked = fault_cases()
    cfg = low_line_rail.CAND
    cap = (cfg['caps']-1)*low_line_rail.CAP_NOM*(1-low_line_rail.CAP_TOL)
    def rail(raw, ctr, threshold, original_cap, bypass, original_leak):
        return low_line_rail.variant(raw, ctr, threshold, cap, bypass, None, **cfg)
    cases = [(20000,500,220,30,False,25,1.,340,39700),
             (20000,500,600,150,False,85,.9,340,39700),
             (20000,0,80,30,False,25,1.1,340,39700),
             (20000,500,220,30,True,85,1.,440,39700),
             (20000,500,220,30,True,85,1.,None,39700),
             (1000,500,220,30,False,25,1.,340,39700),
             (20000,500,600,150,False,85,.9,340,40600),
             (20000,0,80,30,False,25,1.1,340,38300)]
    audio=[]
    failures=[]
    with patch.object(guard_audio, 'regulator', rail):
        for f, harness, shunt, optical, short, temp, L, raw, fb in cases:
            pulse_winding.STATE.update(spec=SPEC,corner={'r_scale':1+.00393*(temp-25)})
            try:
                audio.append(guard_audio.audio(f,harness,shunt,optical,short,temp,310,False,L,raw,fb))
            except AssertionError as exc:
                failures.append(dict(frequency=f, harness_pF=harness, short=short, raw_V=raw,
                                     temp_C=temp, feedback_ohm=fb, reason=str(exc)))
                pulse_winding._cmd('destroy all')
    files=[Path(__file__)]+[Path(m.__file__) for m in (guard_audio,low_line_rail,pulse_winding)]
    report=dict(sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
                rail_config=cfg,rail_cap_uF=cap,windings=SPEC,
                fault_summary=checked['summary'],fault_runs=checked['runs'],audio=audio,invalid_cases=failures)
    (MODULE/'results/rail-winding-audio.json').write_text(json.dumps(report,indent=1)+'\n')
    print(checked['summary'],flush=True)
    print([(r['gain_dB'],r['short'],r['rail_min_V'],r['chip_W']) for r in audio])


if __name__=='__main__':
    with pulse_winding.instrument():
        main()
