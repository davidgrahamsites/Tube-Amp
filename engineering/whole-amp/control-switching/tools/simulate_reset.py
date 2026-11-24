"""Unmodified TI nominal transient model: startup, brownout, bounce, manual reset.
No regulator dynamics, no temperature behavior, no guaranteed propagation maximum.
"""
import hashlib,json,sys
from pathlib import Path
M=Path(__file__).resolve().parents[1];sys.path.insert(0,str(M.parent/'tools'))
import spice_runtime as s

def cases():
 for end in [4.75,5.25]:
  for ramp in [.0001,.1]:
   yield dict(id=f'start-{end:g}-{ramp:g}',supply=f'0 0 .001 0 {ramp+.001} {end} .65 {end}',manual='0 1 .65 1',end=.65)
 yield dict(id='slow-brownout',supply='0 0 .001 0 .011 5 .4 5 .45 4.4 .50 4.4 .55 5 1 5',manual='0 1 1 1',end=1)
 yield dict(id='fast-brownout',supply='0 0 .001 0 .011 5 .4 5 .400001 4.4 .45 4.4 .450001 5 .9 5',manual='0 1 .9 1',end=.9)
 yield dict(id='repeated-dips',supply='0 0 .001 0 .011 5 .4 5 .40001 4.4 .42 4.4 .42001 5 .5 5 .50001 4.4 .52 4.4 .52001 5 1 5',manual='0 1 1 1',end=1)
 yield dict(id='manual-reset',supply='0 0 .001 0 .011 5 .9 5',manual='0 1 .4 1 .400001 0 .42 0 .420001 1 .9 1',end=.9)

def run(c,case,step):
 r=c['reset_candidate'];model=M/'models/TPS389001_TRANS.LIB'
 deck=f'''TPS389001 manufacturer nominal model; candidate, not native adopted
.include "{model}"
V5 v5 0 PWL({case['supply']})
Vmanual manual 0 PWL({case['manual']})
Bmr mr 0 V=V(manual)*V(v5)
Rtop v5 sense {r['divider_top_ohm']}
Rbottom sense 0 {r['divider_bottom_ohm']}
Rpull v5 rst {r['reset_pullup_ohm']}
Cct ct 0 {r['timing_cap_F']}
Crst rst 0 50p
Xsupervisor rst ct v5 mr sense 0 TPS389001_TRANS
.save v(v5) v(rst) v(ct) v(sense)
.tran {step} {case['end']} 0 {step}
.end
'''
 s.cmd('destroy all');s.load(deck);s.cmd('run')
 t=s.vector('time');rst=s.vector('v(rst)');supply=s.vector('v(v5)');ct=s.vector('v(ct)')
 assert t[-1]>=case['end']-1e-9,(case,s.logs[-20:])
 assert rst[-1]>.7*supply[-1],case['id']
 transitions=[];state=False
 for i in range(1,len(t)):
  if supply[i]<1.5:continue
  if not state and rst[i]>.7*supply[i]:
   state=True;transitions.append(dict(time_s=t[i],state='released',rail_V=supply[i]))
  elif state and rst[i]<.3*supply[i]:
   state=False;transitions.append(dict(time_s=t[i],state='asserted',rail_V=supply[i]))
 expected_releases=1 if case['id'].startswith('start') else 2
 assert sum(x['state']=='released' for x in transitions)==expected_releases,(case,transitions)
 flags=[]
 if case['id']=='manual-reset' and transitions[-1]['time_s']-.420001<.181:
  flags.append('manufacturer_model_does_not_repeat_CT_delay_after_manual_reset')
 if case['id']=='fast-brownout' and any(x['state']=='asserted' and x['rail_V']<4.5 for x in transitions):
  flags.append('fast_rail_drop_crosses_4p5V_before_reset_assertion')
 return dict(id=case['id'],step_s=step,completed_time_s=t[-1],transitions=transitions,flags=flags,final_reset_V=rst[-1],maximum_ct_V=max(ct),samples=len(t),deck_sha256=hashlib.sha256(deck.encode()).hexdigest()),deck

def main():
 c=json.loads((M/'contract.json').read_text());rows=[];decks={};refinements=[]
 try:
  for case in cases():
   row,deck=run(c,case,20e-6);rows.append(row);decks[case['id']]=deck
   print(case['id'],row['transitions'],flush=True)
   if case['id'] in ['fast-brownout','manual-reset']:
    fine,deck=run(c,case,5e-6);decks[case['id']+'-fine']=deck
    assert len(fine['transitions'])==len(row['transitions'])
    delta=max(abs(a['time_s']-b['time_s']) for a,b in zip(fine['transitions'],row['transitions']))
    assert delta<50e-6,(case,delta)
    refinements.append(dict(id=case['id'],maximum_transition_delta_s=delta,result=fine))
  result=dict(model_sha256=hashlib.sha256((M/'models/TPS389001_TRANS.LIB').read_bytes()).hexdigest(),contract_sha256=hashlib.sha256((M/'contract.json').read_bytes()).hexdigest(),cases=rows,refinements=refinements,decks=decks,nominal_model_runs_completed=True,guaranteed_timing_qualified=False,fabrication_ready=False)
  (M/'results/reset-screen.json').write_text(json.dumps(result,indent=2)+'\n')
 finally:(M/'results/reset-simulator.log').write_text('\n'.join(s.logs)+'\n')
if __name__=='__main__':main()
