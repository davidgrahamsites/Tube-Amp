from simulate_amp import *
results=[]
try:
 for channel,amp in [('clean',.001),('clean',.02),('clean',.2),('dirty',.001),('dirty',.02),('dirty',.2)]:
  text=circuit(channel,amp);name=f'{channel}-{amp}Vpk';(OUT/(name+'.cir')).write_text(text);load(text);cmd('tran 5u 40m 20m 5u')
  t=vector('time');assert len(t)>100 and t[-1]>=.0399,logs[-10:];out=vector('v(SPEAKER)');fx=vector('v(FX_RETURN)');mix=vector('v(MIX_OUT)');ka=vector('v(K_A)');sa=vector('v(EL34_SA)');bs=vector('v(B_SCREEN)');pa=vector('v(OT_PA)')
  select=[i for i,x in enumerate(t) if x>=.03];dt=sum(t[i]-t[i-1] for i in select if i)
  def avg(v):return sum((v[i]+v[i-1])*.5*(t[i]-t[i-1]) for i in select if i)/dt
  power=avg([v*v/8 for v in out]);plate=avg([(v-k)*(k-(b-s)/1000) for v,k,b,s in zip(pa,ka,bs,sa)]);screen=avg([(s-k)*(b-s)/1000 for s,k,b in zip(sa,ka,bs)])
  row={'case':name,'output_W':power,'plate_A_W':plate,'screen_A_W':screen,'fx_peak_V':max(abs(fx[i]) for i in select),'mix_peak_V':max(abs(mix[i]) for i in select),'sample_count':len(t)};results.append(row);(OUT/'transient-results.json').write_text(json.dumps(results,indent=2));print(row,flush=True)
  with (OUT/(name+'.csv')).open('w') as fi:
   wr=csv.writer(fi);wr.writerow(['s','speaker_V','FX_RETURN_V','MIX_OUT_V','cathode_A_A']);wr.writerows(zip(t,out,fx,mix,ka))
  cmd('destroy all')
 (OUT/'transient-results.json').write_text(json.dumps(results,indent=2))
finally:(OUT/'transient-ngspice.log').write_text('\n'.join(logs))
