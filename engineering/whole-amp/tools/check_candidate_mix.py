"""TI-model AC wet/dry control check for the80ms combined candidate; no acoustic tank model."""
from spice_runtime import *
import csv
out=OUT/'candidate-mix';out.mkdir(exist_ok=True);source=(OUT/'reverb-headroom/combined_80ms.cir').read_text();rows=[]
for channel in ['dirty','clean']:
 for mode in ['dry','wet']:
  for wet in [0,.5,1]:
   for muted in ([False,True] if mode=='dry' else [False]):
    text=source
    if channel=='clean':
     from simulate_amp import circuit
     before=circuit('dirty',.2);after=circuit('clean',.2)
     old=[x for x in before.splitlines() if x.startswith('RK')];new=[x for x in after.splitlines() if x.startswith('RK')]
     for a,b in zip(old,new):text=text.replace(a,b)
    text=text.replace('RREV_WT rv_wettop rv_wetw 100000',f'RREV_WT rv_wettop rv_wetw {max(1,100000*(1-wet))}').replace('RREV_WB rv_wetw 0 1',f'RREV_WB rv_wetw 0 {max(1,100000*wet)}').replace('RREV_MUTE rv_wetmute 0 1','RREV_MUTE rv_wetmute 0 '+('1' if muted else '1e12'))
    if mode=='wet':text=text.replace('DC 0 AC 1 SIN','DC 0 AC 0 SIN').replace('VREV_TANK rv_tanksrc 0 DC 0 AC 0','VREV_TANK rv_tanksrc 0 DC 0 AC .001')
    name=f'{channel}-{mode}-{wet}-{muted}';(out/(name+'.cir')).write_text(text);load(text);cmd('ac dec 30 20 20000');freq=vector('frequency');mix=vector('v(MIX_OUT)');vout=vector('v(SPEAKER)')
    def near(hz):
     ix=min(range(len(freq)),key=lambda i:abs(freq[i].real-hz));return {'Hz':freq[ix].real,'mix_V':abs(mix[ix]),'speaker_V':abs(vout[ix])}
    rows.append({'channel':channel,'mode':mode,'wet_fraction':wet,'muted':muted,'at82Hz':near(82),'at1kHz':near(1000),'at5kHz':near(5000)})
    cmd('destroy all')
checks=[]
for channel in ['dirty','clean']:
 d=[r for r in rows if r['channel']==channel and r['mode']=='dry']
 for freq in ['at82Hz','at1kHz','at5kHz']:
  gain=[r[freq]['mix_V'] for r in d];spread=(max(gain)-min(gain))/max(gain);checks.append({'channel':channel,'frequency':freq,'relative_dry_gain_spread':spread,'pass':spread<.001})
(out/'results.json').write_text(json.dumps({'scope':'Generic tube/TI opamp AC, ideal supply/transformer, independent1mV tank-output injection. Not acoustic transfer.','cases':rows,'dry_control_checks':checks},indent=2)+'\n');(out/'ngspice.log').write_text('\n'.join(logs));assert all(c['pass'] for c in checks)
print(len(rows),'AC cases;',len(checks),'dry independence checks passed; maximum relative spread',max(c['relative_dry_gain_spread'] for c in checks))
