"""Topology experiment only. Ideal wet source, no qualified tank or full reverb model."""
from simulate_amp import *
p=OUT/'passive-mix';p.mkdir(exist_ok=True);results=[]
try:
 for channel in ['clean','dirty']:
  for mode in ['direct','passive-dry','passive-wet']:
   base=circuit(channel,.2)
   lines=[l for l in base.splitlines() if not re.match(r'^[RCLVDX]REV_',l) and not l.startswith(('.model DC','.end'))]
   if mode=='direct':lines+=['RDIRECT FX_RETURN MIX_OUT .05']
   else:
    # Separate high-headroom dry route from attenuated solid-state send.
    lines+=['RDRY FX_RETURN MIX_OUT 100k','RWET WET_SOURCE MIX_OUT 1meg',f'VWET WET_SOURCE 0 DC 0 AC {1 if mode=="passive-wet" else 0}','CSEND FX_RETURN SEND_AC 100n','RSEND SEND_AC SEND_LOW 1meg','RSHUNT SEND_LOW 0 100k']
   if mode=='passive-wet':lines=[l.replace('AC 1 SIN','AC 0 SIN') if l.startswith('VIN ') else l for l in lines]
   text='\n'.join(lines+['.end']);name=channel+'-'+mode;(p/(name+'.cir')).write_text(text)
   load(text);cmd('ac dec 30 20 20000');f=vector('frequency');out=vector('v(SPEAKER)');mix=vector('v(MIX_OUT)');fx=vector('v(FX_RETURN)')
   row={'channel':channel,'mode':mode}
   for hz in [82,1000,5000]:
    i=min(range(len(f)),key=lambda x:abs(f[x].real-hz));row[str(hz)]={'speaker_gain':abs(out[i]),'mix_gain':abs(mix[i]),'fx_gain':abs(fx[i])}
   results.append(row);cmd('destroy all')
 (p/'results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
finally:(p/'ngspice.log').write_text('\n'.join(logs))
