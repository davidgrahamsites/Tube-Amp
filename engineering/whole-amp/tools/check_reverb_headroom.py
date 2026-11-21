"""Candidate passive dry mix + attenuated solid-state send, TI model retained.
Not yet applied to native CAD; recovery gain/tank response remain unqualified.
"""
from simulate_amp import *
import sys,os
channel=sys.argv[1] if len(sys.argv)>1 else 'dirty'
text=circuit(channel,.2)
replacements={
 'RREV_601 rv_acin rv_dryin 100k':'RREV_601 rv_acin rv_dryin 1meg',
 'RREV_602 rv_dryin 0 10meg':'RREV_602 rv_dryin 0 100k',
 'RREV_612 rv_drybuf rv_sum 100k':'RDRY FX_RETURN MIX_OUT 100k',
 'CREV_607 rv_outac MIX_OUT 1u':'CREV_607 rv_outac WET_AC 1u\nRWET WET_AC MIX_OUT 1meg',
 'RREV_617 MIX_OUT 0 1meg':'RREV_617 WET_AC 0 1meg'}
for a,b in replacements.items():assert a in text;text=text.replace(a,b)
variant=sys.argv[2] if len(sys.argv)>2 else 'gear'
text=text.replace('.end',f'.options method={variant} itl1=500 itl4=500\n.end')
p=OUT/'reverb-headroom';p.mkdir(exist_ok=True);channel=channel+'-'+variant;(p/(channel+'.cir')).write_text(text)
try:
 load(text);cmd('tran 1u 80m 0 1u');t=vector('time');os.chdir(p);cmd('write '+channel+'.raw v(FX_RETURN) v(MIX_OUT) v(rv_dryin) v(rv_drybuf) v(rv_driver)')
 result={'channel':channel,'input_peak_V':.2,'complete':t[-1]>=.079999,'end_s':t[-1],'points':len(t)}
 result['diagnostic_peaks_V']={n:max(abs(v) for v in vector('v('+n+')')) for n in ['FX_RETURN','rv_dryin','rv_drybuf','vp','vn']}
 if result['complete']:
  ix=[i for i in range(1,len(t)) if t[i]>=.07];dt=sum(t[i]-t[i-1] for i in ix)
  def avg(y):return sum(.5*(y[i]+y[i-1])*(t[i]-t[i-1]) for i in ix)/dt
  for n in ['FX_RETURN','MIX_OUT','rv_dryin','rv_drybuf','rv_driver','rv_suminv','rv_outbuf']:
   v=vector('v('+n+')');result[n+'_peak_V']=max(abs(v[i]) for i in ix)
  v=vector('v(SPEAKER)');result['output_W']=avg([vv*vv/8 for vv in v])
 (p/(channel+'.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result))
finally:(p/(channel+'.log')).write_text('\n'.join(logs))
