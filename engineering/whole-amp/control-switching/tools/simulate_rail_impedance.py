"""Sensitivity screen for finite positive harness/rail impedance.

Consumes the recorded cold two-coil driver deck. Does not model the regulator
control loop or qualify real harness inductance, capacitor ESR or diode recovery.
"""
import hashlib
import itertools
import json
import sys
from pathlib import Path

M = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(M.parent / 'tools'))
import spice_runtime as s


def run(template, case, step):
    rail = f'''V12 source12 0 12.6
Rfeed source12 feed .2
Lfeed feed supply {case['feed_H']}
Rcap supply capbulk {case['esr_ohm']}
Cbulk capbulk 0 {case['bulk_F']}
Rcer supply capcer .05
Ccer capcer 0 {case['ceramic_F']}
Lpositive supply positive_wire {case['positive_H']}
Rpositive positive_wire remotep .2'''
    assert template.count('V12 supply 0 12.6') == 1
    deck = template.replace('V12 supply 0 12.6', rail)
    for i in range(2):
        deck = deck.replace(f'Rcoil{i} supply ', f'Rcoil{i} remotep ')
        deck = deck.replace(f'Dfly{i} remote supply DGEN', f'Dfly{i} remote remotep DGEN')
    deck = deck.replace('.save v(drain)', '.save v(supply) v(remotep) i(lfeed) v(drain)')
    deck = deck.replace('.tran 2e-06 .10 0 2e-06', f'.tran {step} .10 0 {step}')
    assert f'.tran {step} .10 0 {step}' in deck
    s.cmd('destroy all'); s.load(deck); s.cmd('run')
    t = s.vector('time'); vd = s.vector('v(drain)'); vr = s.vector('v(supply)')
    vg = s.vector('v(gate)'); iw = s.vector('i(lwire)'); ic = s.vector('i(lcoil0)')
    assert t[-1] >= .1 - 1e-9
    plateau = [j for j, x in enumerate(t) if .055 < x < .059]
    kcl = max(abs(iw[j] + 2 * ic[j]) for j in plateau)
    assert kcl < 1e-6
    flags = []
    if max(vd) > 24: flags.append('VDS_exceeds_24V_engineering_target')
    if max(vd) > 30: flags.append('VDS_exceeds_30V_rating')
    if max(vg) > 12 or min(vg) < -12: flags.append('VGS_exceeds_rating')
    return dict(case=case, step_s=step, completed_time_s=t[-1],
                max_vds_V=max(vd), max_rail_V=max(vr), min_rail_V=min(vr),
                min_vgs_V=min(vg), max_vgs_V=max(vg), steady_kcl_error_A=kcl,
                flags=flags, deck_sha256=hashlib.sha256(deck.encode()).hexdigest()), deck


def main():
    source = M / 'results/driver-screen.json'
    base = json.loads(source.read_text())
    template = base['decks']['2coils-L3.99-wire0.0001-remote_and_local']
    rows, decks, refinement = [], {}, []
    try:
        for feed, positive, esr in itertools.product([1e-6, 100e-6], [1e-6, 100e-6], [.05, 2]):
            case = dict(id=f'feed{feed:g}-positive{positive:g}-esr{esr:g}',
                        feed_H=feed, positive_H=positive, esr_ohm=esr,
                        bulk_F=80e-6, ceramic_F=80e-9)
            row, deck = run(template, case, 2e-6)
            rows.append(row); decks[case['id']] = deck
            print(case['id'], row['max_vds_V'], row['flags'], flush=True)
        case = dict(id='missing-local-decoupling-sensitivity', feed_H=100e-6,
                    positive_H=100e-6, esr_ohm=.05, bulk_F=1e-12, ceramic_F=1e-12)
        control, deck = run(template, case, 2e-6); decks[case['id']] = deck
        for row in [max(rows, key=lambda r:r['max_vds_V']), control]:
            fine, deck = run(template, row['case'], .5e-6)
            decks[row['case']['id']+'-fine'] = deck
            finer, deck = run(template, row['case'], .125e-6)
            decks[row['case']['id']+'-finer'] = deck
            delta = abs(fine['max_vds_V']-finer['max_vds_V'])
            refinement.append(dict(id=row['case']['id'], result=fine, finer_result=finer,
                                   fine_to_finer_delta_V=delta, within_one_percent=delta/finer['max_vds_V'] < .01))
        report = dict(driver_result_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                      cases=rows, missing_decoupling_sensitivity=control,
                      refinements=refinement, decks=decks, fabrication_ready=False,
                      assumptions='C204 100u and C203 100n screened at -20%; ESR and feed/harness inductance are engineering sweeps, not qualified part bounds. Ideal source behind RL; regulator control loop, load steps and simultaneous third coil excluded.')
        (M/'results/rail-impedance-screen.json').write_text(json.dumps(report,indent=2)+'\n')
    finally:
        (M/'results/rail-impedance-simulator.log').write_text('\n'.join(s.logs)+'\n')


if __name__ == '__main__': main()
