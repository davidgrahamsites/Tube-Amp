"""AC diagnostic, not selected-transformer stability validation."""
from spice_runtime import *
p=OUT/'candidate-hf';p.mkdir(exist_ok=True);source=(OUT/'reverb-headroom/combined_80ms.cir').read_text();rows=[]
for gain in ['-.7071067812','0']:
 text=source.replace('ENFB OT_4 0 SPEAKER 0 -.7071067812','ENFB OT_4 0 SPEAKER 0 '+gain);name='feedback' if gain!='0' else 'feedback-source-zero';(p/(name+'.cir')).write_text(text);load(text);cmd('ac dec 80 20 10000000');freq=vector('frequency');out=vector('v(SPEAKER)');mix=vector('v(MIX_OUT)');fx=vector('v(FX_RETURN)')
 with (p/(name+'.csv')).open('w') as f:
  w=csv.writer(f);w.writerow(['Hz','speaker_V_per_V','mix_V_per_V','fx_V_per_V']);w.writerows((ff.real,abs(a),abs(b),abs(c)) for ff,a,b,c in zip(freq,out,mix,fx))
 ix=max(range(len(freq)),key=lambda i:abs(out[i]));at400=min(range(len(freq)),key=lambda i:abs(freq[i].real-412000));at1=min(range(len(freq)),key=lambda i:abs(freq[i].real-1000));rows.append({'variant':name,'peak_Hz':freq[ix].real,'peak_gain':abs(out[ix]),'near412kHz_gain':abs(out[at400]),'at1kHz_gain':abs(out[at1])});cmd('destroy all')
(p/'results.json').write_text(json.dumps(rows,indent=2)+'\n');(p/'ngspice.log').write_text('\n'.join(logs));print(rows)
