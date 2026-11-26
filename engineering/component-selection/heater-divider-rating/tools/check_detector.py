"""Independent HD-009 threshold, supply, KCL and audio-comparison audit."""
from pathlib import Path
import hashlib,itertools,json,math
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 c=json.loads((M/'detector-contract.json').read_text());r=json.loads((M/'results/detector-screen.json').read_text());base=json.loads((M/'pass-contract.json').read_text());prior=json.loads((M/'series-contract.json').read_text());checks=[]
 def ck(name,ok):checks.append(dict(name=name,passed=bool(ok)))
 ck('contract hash',r['contract_sha256']==sha(M/'detector-contract.json'));ck('factory hash',r['factory_sha256']==sha(M/'tools/detector_candidate.py'))
 for p,h in c['inputs'].items():ck('input '+p,sha(M/p)==h)
 sc=json.loads((M/'supply-contract.json').read_text())
 for p,h in sc['inputs'].items():ck('audio dependency '+p,sha(ROOT/p)==h)
 ref=c['reference'];cmp=c['comparator'];top=c['divider_top_count']*c['divider_top_each_ohm'];bot=c['divider_bottom_ohm'];f=c['resistor_total_fraction'];err=ref['initial_fraction']+ref['box_drift_ppm_per_C']*ref['box_span_C']/1e6+ref['line_ppm_per_V']*ref['line_span_V']/1e6+ref['source_load_ppm_per_mA']*ref['source_load_mA']/1e6+ref['unqualified_age_hysteresis_solder_fraction'];ib=cmp['input_abs_A']+cmp['board_leakage_allocation_A']
 triplo=(2.5*(1-err)-cmp['offset_abs_V'])*(1+top*(1-f)/(bot*(1+f)))-ib*top*(1-f)
 triphi=(2.5*(1+err)+cmp['offset_abs_V'])*(1+top*(1+f)/(bot*(1-f)))+ib*top*(1+f)
 ck('independent threshold interval',abs(triplo-r['budget']['minimum_trip_V'])<1e-9 and abs(triphi-r['budget']['maximum_trip_V'])<1e-9)
 ck('all64 unique threshold endpoints',len(r['budget']['rows'])==64 and len({tuple(x['signs']) for x in r['budget']['rows']})==64)
 for name,q in base['profiles'].items():
  rl=q['rlow']*c['Rlower_candidate_ohm']/c['Rlower_old_ohm'];v=q['vref']*(1+rl/q['rset'])+q['iadj']*rl
  ck('normal profile '+name,abs(v-r['normal_output_V'][name])<1e-9)
 normalmax=max(r['normal_output_V'].values());ck('normal-to-trip allocated margin',triplo-normalmax>c['limits']['normal_trip_margin_V']);ck('trip-to-ceiling allocated margin',300-triphi>c['limits']['trip_ceiling_margin_V'])
 oldq=base['profiles']['high'];oldmax=oldq['vref']*(1+oldq['rlow']/oldq['rset'])+oldq['iadj']*oldq['rlow'];ck('old setpoint rejected at new threshold',triplo<oldmax)
 expected=set(itertools.product(c['input_V'],c['profiles'],c['cold'],c['faults'],[triplo,triphi],c['vto_sensitivity_V'],c['vto_sensitivity_V'],c['source_ohm']));actual=set();errors=[];minprog=[]
 def balance(row):
  n=row['nodes'];case=row['case'];q=base['profiles'][case['profile']];rl=q['rlow']*c['Rlower_candidate_ohm']/c['Rlower_old_ohm'];source=(n['s']-n['regin'])/case.get('sensitivity',{'source_ohm':646})['source_ohm'];bias=sum((n['in']-n[k])/prior['topology']['gate_bias_total_each_ohm'] for k in ['gref','gref2']);back=sum((n[g]-n[k])/prior['topology']['gate_resistor_each_ohm'] for g,k in [('g','gref'),('g2','gref2')]);load=n['out']/78000+n['adj']/rl+(0 if case['cold'] else n['out']/36200)+(n['out']-n['mon'])/(c['monitor']['feed_count']*c['monitor']['feed_each_ohm'])+(n['out']-n['sen'])/top
  return source+bias+back-load,source-q['iadj']
 for i,row in enumerate(r['dc']):
  n=row['nodes'];case=row['case'];actual.add(tuple(case[k] for k in ['vin','profile','cold','fault','trip_V'])+tuple(case['sensitivity'][k] for k in ['vto1','vto2','source_ohm']));e,program=balance(row);errors.append(e)
  ck(f'{i} finite',all(math.isfinite(v) for v in n.values()));ck(f'{i} output KCL',abs(e)<c['limits']['kcl_A']);ck(f'{i} below ceiling',n['out']<300)
  ck(f'{i} ideal monitor absorbs rather than supplies energy',row['currents']['vmon']>0)
  monI=(n['out']-n['mon'])/(c['monitor']['feed_count']*c['monitor']['feed_each_ohm']);ck(f'{i} monitor KCL',abs(monI-c['monitor']['quiet_A']-row['currents']['vled']-row['currents']['vmon'])<1e-9)
  ck(f'{i} gate limit',max(abs(n['g']-n['mid']),abs(n['g2']-n['s']))<20)
  if case['fault']!='regulator_short':
   minprog.append(program);ck(f'{i} regulator output minimum',program>.005);ck(f'{i} target regulation',abs(n['out']-r['normal_output_V'][case['profile']])<.01);ck(f'{i} differential limit',0<n['regin']-n['out']<40)
  else:ck(f'{i} active control',row['currents']['vled']>0 and 0<=n['out']-case['trip_V']<.1)
 ck('full DC grid',actual==expected and len(r['dc'])==len(expected));rejected,_=balance(r['rejected_unwrapped']);ck('unwrapped false OP retained',abs(rejected)>.001 and r['rejected_unwrapped']['currents']['vmon']<0)
 for row in r['transistor_fixtures']:
  for terminal in ['collector','base']:ck('wrapper fixture '+terminal+str(row['offset_V'])+str(row['vbe_V']),abs(row[f'direct_{terminal}_A']-row[f'wrapped_{terminal}_A'])<1e-9)
 ck('fixture coverage',len(r['transistor_fixtures'])==6)
 for channel in ['clean','dirty']:
  old,new=[a for a in r['audio'] if a['channel']==channel];freq=old['frequency_Hz'];ck(channel+' AC frequency coverage',freq==new['frequency_Hz'] and abs(freq[0]-20)<1e-6 and abs(freq[-1]-20000)<1e-5 and len(freq)==91)
  delta=[20*math.log10(n/o) for n,o in zip(new['speaker_gain'],old['speaker_gain'])];ck(channel+' gain comparison',max(map(abs,delta))<.1)
  for a in [old,new]:
   p=M/f"results/detector-ac-{channel}-{a['pre_V']}.cir";text=p.read_text();ck(channel+' excitation and deck '+str(a['pre_V']),sha(p)==a['deck_sha256'] and 'VSOURCE PICKUP 0 DC 0 AC 1' in text and 'VTEST RET_DRIVE 0 DC 0 AC 0' in text)
 mon=c['monitor'];feed=mon['feed_count']*mon['feed_each_ohm'];full_drive_reserve=(min(r['normal_output_V'].values())-max(mon['required_rail_range_V']))/(feed*(1+mon['feed_fraction_allocation']))-mon['quiet_A']-mon['led_limit_A'];ck('allocated full-drive rail reserve',full_drive_reserve>.001)
 for p,h in r['native_sha256'].items():ck('native '+p,sha(ROOT/p)==h)
 for flag in ['adopted','transient_qualified','physical_qualified']:ck(flag+' false',r[flag] is False)
 out=dict(id=c['id'],passed=all(x['passed'] for x in checks),count=len(checks),checks=checks,maximum_KCL_error_A=max(map(abs,errors)),rejected_KCL_A=rejected,minimum_regulator_output_A=min(minprog),full_drive_rail_reserve_A=full_drive_reserve,normal_trip_margin_V=triplo-normalmax,trip_ceiling_margin_V=300-triphi,result_sha256=sha(M/'results/detector-screen.json'),scope='Conditional static detector/load and limited small-signal comparison; no timing, real monitor supply or part qualification.')
 (M/'results/detector-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='checks'},indent=2));assert out['passed'],[x for x in checks if not x['passed']]
if __name__=='__main__':main()
