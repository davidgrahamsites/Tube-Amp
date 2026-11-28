"""Check CB-007 receipts, failure controls, closed-form limits and native preservation."""
import hashlib
import json
import math
import subprocess
from pathlib import Path

MODULE=Path(__file__).resolve().parents[1]
ROOT=MODULE.parents[3]
RESULT=MODULE/'results'


def read(name):
    return json.loads((RESULT/f'supply-{name}.json').read_text())


def main():
    audio={r['case']:r for r in read('audio')}
    for key in ['nominal','low-line','high-hot','optical-30p','optical-150p']:
        row=audio[key]
        assert abs(20*math.log10(row['port_Vpk']/135))<.5 and row['thd_pct']<1
        assert 300<row['rail_min_V']<=row['rail_max_V']<320 and row['final_s']>=.006
    assert audio['brownout']['thd_pct']>1 and audio['brownout']['rail_max_V']<295
    assert audio['bypass-weld-transition']['rail_start_V']>350
    assert abs(audio['bypass-weld-transition-guided']['rail_start_V']-310)<1
    loop=read('loop')
    for key,lower,upper in [('loop',60,100),('initial_10nF',0,25)]:
        for row in loop[key]:
            assert len(row['crossings'])==1 and lower<row['crossings'][0]['margin_deg']<upper
    assert all(300<r['rail_min_V']<r['rail_max_V']<320 and r['reached_s']>=.4 for r in loop['load_step'])
    sustained=loop['sustained_load']
    assert len(sustained)==10 and min(r['rail_min_V'] for r in sustained if r['bypass'])>309
    assert min(r['rail_min_V'] for r in sustained if not r['bypass'])<295
    detector=read('detector')['runs']
    assert all(r['reached_s']>=.04 for r in detector)
    assert detector[1]['peak_V']<350<detector[2]['peak_V']
    assert detector[3]['disconnect_s'] is None and detector[3]['peak_V']>400
    f=read('faults')
    rows={r['case']:r for r in f['faults']}
    peak=440-(440-f['ov_trip_V'][1])*math.exp(-.002/(.95*1820*17.6e-6))
    assert abs(peak-rows['one reservoir open']['peak_V'])<1e-5 and peak<350
    assert rows['late disconnect']['peak_V']>350 and rows['cutoff welded and pass short']['peak_V']>439
    assert rows['pass short before arm']['disconnected']
    assert not f['startup_envelope'][1]['window_reached']
    assert f['thermal_trip'][0]['peak_case_C']<85<f['thermal_trip'][1]['peak_case_C']
    assert f['thermal_trip'][2]['peak_case_C']>90
    for row in read('sequence'):
        assert all(row[k] for k in ['cleared','play_inhibited','held_button_rejected','fresh_edge_accepted','cooldown_rejected'])
    mute=read('mute')
    assert len(mute)==7 and all(r['reached_s']==0 and r['diagnostic'] for r in mute[:4])
    assert all(r['reached_s']>=5 for r in mute[4:])
    assert 1.7<mute[5]['earliest_sustained_release_s']<2.0 and mute[6]['earliest_sustained_release_s'] is None
    optical={r['case']:r['peak_mixer_V'] for r in read('optical-mute')}
    assert optical['large capacitance']<1<optical['initial 100 ohm']
    assert optical['loss at command']>150 and optical['failed series contact']>2
    for name,over in [('aux',72),('aux-optical',48)]:
        rows=read(name)['cases']
        assert len(rows)==len({r['id'] for r in rows})==72
        assert sum(r['rms_A']>.25 for r in rows)==over
        assert all(r['reached_s']>=.6-1e-8 and r['kcl_A']<1e-5 for r in rows)
    baseline='b409cd60047291a5360540b1e442f7267f6bd020'
    # Compare only native sources present at the checkpoint. Later projects
    # may intentionally diverge; this receipt identifies the tested revision.
    native=subprocess.check_output(['git','ls-tree','-r','--name-only',baseline],cwd=ROOT).decode().splitlines()
    native=[p for p in native if p.endswith(('.kicad_pcb','.kicad_sch'))]
    subprocess.run(['git','diff','--quiet',baseline,'--',*native],cwd=ROOT,check=True)
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(RESULT.glob('supply-*.json'))
            if p.name!='supply-audit.json'}
    assert len(hashes)==9
    receipt=dict(passed=True,baseline=baseline,unchanged_tracked_native_files=len(native),
                 evidence_sha256=hashes,hardware_verified=False)
    (RESULT/'supply-audit.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('CB-007 receipt checks passed:',len(hashes),'result sets,',len(native),'native sources')


if __name__=='__main__':
    main()
