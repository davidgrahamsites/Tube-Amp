"""HD-009: source-bounded static monitor comparison; no protection release."""
from pathlib import Path
import copy,hashlib,itertools,json,math
import series_protection as s
M=s.M

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def budget(c):
 r=c['reference'];cmp=c['comparator'];e=r['initial_fraction']+r['box_drift_ppm_per_C']*r['box_span_C']*1e-6+r['line_ppm_per_V']*r['line_span_V']*1e-6+r['source_load_ppm_per_mA']*r['source_load_mA']*1e-6+r['unqualified_age_hysteresis_solder_fraction'];top=c['divider_top_each_ohm']*c['divider_top_count'];bot=c['divider_bottom_ohm'];f=c['resistor_total_fraction'];rows=[]
 for a,b,ref,offset,ib,leak in itertools.product([-1,1],repeat=6):
  hi=top*(1+a*f);lo=bot*(1+b*f);v=r['nominal_V']*(1+ref*e)+offset*cmp['offset_abs_V'];current=ib*cmp['input_abs_A']+leak*cmp['board_leakage_allocation_A'];trip=v*(1+hi/lo)+current*hi
  rows.append(dict(signs=[a,b,ref,offset,ib,leak],trip_V=trip))
 return dict(reference_fraction=e,rows=rows,minimum_trip_V=min(x['trip_V'] for x in rows),maximum_trip_V=max(x['trip_V'] for x in rows),nominal_trip_V=r['nominal_V']*(1+top/bot))

def base_config(c):
 b=json.loads((M/'pass-contract.json').read_text())
 for p in b['profiles'].values():p['rlow']*=c['Rlower_candidate_ohm']/c['Rlower_old_ohm']
 return b

def deck(c,case,wrapped=True):
 prior=json.loads((M/'series-contract.json').read_text());base=base_config(c);sens=case.get('sensitivity',dict(vto1=-5,vto2=-5,source_ohm=646))
 text=s.build(prior,base,case['vin'],case['profile'],case['cold'],case['fault'],sens,False,True);mon=c['monitor'];nom=budget(c)['nominal_trip_V'];ref=2.5*case['trip_V']/nom
 extra=f'''VMON MON 0 {mon['rail_V']}
RMON OUT MON {mon['feed_each_ohm']*mon['feed_count']}
RSEN1 OUT SEN {c['divider_top_each_ohm']*c['divider_top_count']}
RSEN2 SEN 0 {c['divider_bottom_ohm']}
VLED MON LD 0
BLED LD 0 I=min({mon['led_limit_A']},max(0,(V(SEN)-{ref})*1))
BQUIET MON 0 I={mon['quiet_A']}
BOP1 GREF BASE1 I=I(VLED)*{mon['ctr_allocation']}*max(0,min(1,V(GREF,BASE1)/.4))
BOP2 GREF2 BASE2 I=I(VLED)*{mon['ctr_allocation']}*max(0,min(1,V(GREF2,BASE2)/.4))
QCTL1 GREF BASE1 OUT QC
QCTL2 GREF2 BASE2 OUT QC
RBE1 BASE1 OUT {mon['base_emitter_ohm']}
RBE2 BASE2 OUT {mon['base_emitter_ohm']}
.model QC NPN IS=1e-14 BF={mon['beta_allocation']} VAF=100
'''
 if wrapped:
  extra=extra.replace('QCTL1 GREF BASE1 OUT QC','XCTL1 GREF BASE1 OUT QFLOAT').replace('QCTL2 GREF2 BASE2 OUT QC','XCTL2 GREF2 BASE2 OUT QFLOAT')
  extra+='''.subckt QFLOAT C B E
EC CC 0 C E 1
EB BB 0 B E 1
QIN CC BB 0 QC
BC C E I=-I(EC)
BBI B E I=-I(EB)
.ends QFLOAT
'''
 return text.replace('\n.end\n','\n'+extra+'.end\n')

def run(c,case,wrapped=True):
 text=deck(c,case,wrapped);n=s.p.op(text,s.NODES+['mon','sen','base1','base2']);currents={v:float(s.p.sp.vector('i('+v+')')[-1]) for v in ['vmon','vled']}
 return dict(case=case,nodes=n,currents=currents,wrapped=wrapped,deck_sha256=hashlib.sha256(text.encode()).hexdigest())

def audio(c):
 import supply
 cfg=json.loads((M/'supply-contract.json').read_text());rows=[]
 # Explicitly route AC excitation through the guitar input, not RETURN's test source.
 for voltage,channel in itertools.product([273.41,267.11],['clean','dirty']):
  text=supply.deck(dict(id='detector-ac',mode='fixed',pre_V=voltage,channel=channel),cfg)
  text=text.replace('VSOURCE PICKUP 0 DC 0 AC 0','VSOURCE PICKUP 0 DC 0 AC 1').replace('VTEST RET_DRIVE 0 DC 0 AC 1','VTEST RET_DRIVE 0 DC 0 AC 0')
  assert 'VSOURCE PICKUP 0 DC 0 AC 1' in text and 'VTEST RET_DRIVE 0 DC 0 AC 0' in text
  supply.sp.cmd('destroy all');supply.sp.load(text);supply.sp.cmd('op');dc={name:float(supply.sp.vector('v('+name+')')[-1]) for name in ['b_pre','b_early','dr_cf']};supply.sp.cmd('ac dec 30 20 20000');freq=supply.sp.vector('frequency');out=supply.sp.vector('v(speaker)');send=supply.sp.vector('v(fx_send)')
  rows.append(dict(pre_V=voltage,channel=channel,dc=dc,frequency_Hz=[float(complex(x).real) for x in freq],speaker_gain=[abs(x) for x in out],send_gain=[abs(x) for x in send],deck_sha256=hashlib.sha256(text.encode()).hexdigest()))
  (M/f'results/detector-ac-{channel}-{voltage}.cir').write_text(text)
 return rows

def transistor_fixtures(c):
 rows=[]
 for offset,vbe in itertools.product([0,300],[.55,.65,.75]):
  text=f"""HD009 local-voltage wrapper equivalence fixture
VE E 0 {offset}
VC C E 2
VB B E {vbe}
QD C B E Q
EC CC 0 C E 1
EB BB 0 B E 1
QW CC BB 0 Q
.model Q NPN IS=1e-14 BF={c['monitor']['beta_allocation']} VAF=100
.end
"""
  s.p.op(text,['c','b','e'])
  rows.append(dict(offset_V=offset,vbe_V=vbe,direct_collector_A=-float(s.p.sp.vector('i(vc)')[-1]),wrapped_collector_A=-float(s.p.sp.vector('i(ec)')[-1]),direct_base_A=-float(s.p.sp.vector('i(vb)')[-1]),wrapped_base_A=-float(s.p.sp.vector('i(eb)')[-1])))
 return rows

def main():
 c=json.loads((M/'detector-contract.json').read_text())
 for path,h in c['inputs'].items():assert sha(M/path)==h,path
 b=budget(c);base=base_config(c);normal={name:q['vref']*(1+q['rlow']/q['rset'])+q['iadj']*q['rlow'] for name,q in base['profiles'].items()};rows=[]
 for vin,profile,cold,fault,trip,v1,v2,rs in itertools.product(c['input_V'],c['profiles'],c['cold'],c['faults'],[b['minimum_trip_V'],b['maximum_trip_V']],c['vto_sensitivity_V'],c['vto_sensitivity_V'],c['source_ohm']):
  case=dict(vin=vin,profile=profile,cold=cold,fault=fault,trip_V=trip,sensitivity=dict(vto1=v1,vto2=v2,source_ohm=rs));rows.append(run(c,case))
 rejected=run(c,dict(vin=550,profile='high',cold=True,fault='none',trip_V=b['nominal_trip_V']),False)
 for fault in ['none','regulator_short']:
  case=dict(vin=550,profile='high',cold=True,fault=fault,trip_V=b['maximum_trip_V']);(M/f'results/detector-{fault}.cir').write_text(deck(c,case))
 fixtures=transistor_fixtures(c);ac=audio(c);comparisons=[]
 for channel in ['clean','dirty']:
  old,new=[x for x in ac if x['channel']==channel];changes=[20*math.log10(n/o) for n,o in zip(new['speaker_gain'],old['speaker_gain'])];comparisons.append(dict(channel=channel,minimum_gain_change_dB=min(changes),maximum_gain_change_dB=max(changes),treble20k_change_dB=changes[-1]))
 out=dict(id=c['id'],contract_sha256=sha(M/'detector-contract.json'),factory_sha256=sha(Path(__file__)),budget=b,transistor_fixtures=fixtures,normal_output_V=normal,dc=rows,rejected_unwrapped=rejected,audio=ac,audio_comparison=comparisons,native_sha256=json.loads((M/'results/series-screen.json').read_text())['native_sha256'],adopted=False,transient_qualified=False,physical_qualified=False)
 (M/'results/detector-screen.json').write_text(json.dumps(out,indent=2)+'\n');(M/'results/detector-simulator.log').write_text('\n'.join(s.p.sp.logs)+'\n')
 print(json.dumps(dict(cases=len(rows),trip=[b['minimum_trip_V'],b['maximum_trip_V']],normal=normal,audio=comparisons),indent=2))
if __name__=='__main__':main()
