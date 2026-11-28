"""Cross-check CB-008 decisions against the engineering receipts."""
import json
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
AMP = MODULE.parents[1]


def read(folder, name):
    return json.loads((folder/name).read_text())


def check():
    folder=MODULE/'results'
    faults=read(folder,'sudden-guard.json')
    by_name={r['case']:r for r in faults}
    assert len(faults)==28 and .90<by_name['combined quiet corner']['peak_mixer_V']<1
    assert abs(by_name['nominal']['peak_mixer_V']-by_name['refined nominal']['peak_mixer_V'])<.002
    assert by_name['unshielded 2pF']['peak_mixer_V']>1
    slew=read(folder,'guard-slew.json')
    fast=[r for r in slew if r['early_droop_enabled']]
    assert len(fast)==468 and {r['lost_pin'] for r in fast}=={'hv','pos','neg','five','twelve','all'}
    assert max(r['mixer_peak_V'] for r in fast)<1 and max(r['mixer_peak_V'] for r in slew)>20
    noise=read(folder,'guard-noise.json')
    assert noise[0]['closed_us'] is None and noise[1]['closed_us'] is not None
    injection=read(folder,'guard-injection.json')
    assert max(r['peak_V'] for r in injection if r['off_bias_V']==-6.2)<.7
    audio=read(folder,'guard-audio.json')
    trims=[r for r in audio if r['feedback_ohm']!=39700]
    assert len(trims)==2 and all(abs(r['gain_dB'])<.5 and r['thd_pct']<1 for r in trims)
    short=max(r['chip_W'] for r in audio if r['short'])
    hold=read(folder,'guard-handover.json')
    assert min(r['available_ms'] for r in hold['hold'])>7
    assert max(r['peak_V'] for r in hold['runs'] if r['fast_open'])>150
    supply=read(AMP/'aux-supply/results','guard-regulators.json')
    assert supply['case_count']==216 and supply['failed']==0 and supply['max_rms_A']<1.67
    assert all(read(AMP/'aux-supply/results','guard-transformer.json')['checks'].values())
    fit=read(AMP/'mechanical/review','guard-sink-fit.json')['flat_base_candidate']
    assert abs(fit['margin_130_tray_mm']-5.12)<.001 and fit['margin_145_cage_mm']<0
    print(f'{len(fast)} revised rail-loss cases, {len(audio)} audio cases, {len(trims)} trim checks, '
          f'{supply["case_count"]} revised power cases. Short budget {short+.8:.3f} W. Placement held.')


if __name__=='__main__':
    check()
