"""Bounded nominal vendor-model dip matrix; failures remain visible.

Does not edit TI model, substitute ideal reset logic, or qualify a real rail.
"""
import hashlib,itertools,json,sys
from pathlib import Path
M=Path(__file__).resolve().parents[1];sys.path.insert(0,str(M.parent/'tools'))
import spice_runtime as s

def run(c,q,floor,ramp,plateau,step):
    r=c['reset_candidate'];fall=.4;low=fall+ramp;rise=low+plateau;high=rise+ramp;end=high+.4
    deck=f'''TPS389001 unmodified nominal brownout matrix
.include "{M/q['model']}"
V5 v5 0 PWL(0 0 .001 0 .011 5 {fall} 5 {low:.12g} {floor} {rise:.12g} {floor} {high:.12g} 5 {end:.12g} 5)
Rtop v5 sense {r['divider_top_ohm']}
Rbottom sense 0 {r['divider_bottom_ohm']}
Rpull v5 rst {r['reset_pullup_ohm']}
Cct ct 0 {r['timing_cap_F']}
Crst rst 0 50p
Xsupervisor rst ct v5 v5 sense 0 TPS389001_TRANS
.save v(v5) v(rst) v(ct)
.tran {step} {end:.12g} 0 {step}
.end
'''
    s.cmd('destroy all');s.load(deck);s.cmd('run')
    t=s.vector('time');rail=s.vector('v(v5)');rst=s.vector('v(rst)')
    assert t[-1]>=end-1e-9 and rst[-1]>.7*rail[-1]
    # Use absolute valid-logic bounds at 4.5V, rather than a shrinking fraction
    # of VDD that can obscure what happens as the rail collapses.
    state=False;events=[]
    for time,supply,reset in zip(t,rail,rst):
        if not state and reset>=3.15:state=True;events.append(dict(time_s=time,state='released',rail_V=supply))
        elif state and reset<=1.35:state=False;events.append(dict(time_s=time,state='asserted',rail_V=supply))
    asserts=[e for e in events if e['state']=='asserted' and e['time_s']>=fall]
    releases=[e for e in events if e['state']=='released' and e['time_s']>=fall]
    assert any(e['state']=='released' and e['time_s']<fall for e in events)
    # Sustained deep dips must visibly assert in the nominal model. Shallow and
    # brief dips are measured outcomes, not forced to pass or reset.
    if floor<=4.4 and plateau>=.0001:assert asserts
    row=dict(floor_V=floor,ramp_s=ramp,plateau_s=plateau,step_s=step,completed_time_s=t[-1],
      events=events,dip_detected=bool(asserts),assertions_below_characterized_rail=sum(e['rail_V']<4.5 for e in asserts),
      release_after_final_rail_recovery_s=releases[-1]['time_s']-high if releases else None,
      samples=len(t),deck_sha256=hashlib.sha256(deck.encode()).hexdigest())
    return row,deck

def main():
    c=json.loads((M/'contract.json').read_text());q=json.loads((M/'brownout-contract.json').read_text())
    digest=hashlib.sha256((M/q['model']).read_bytes()).hexdigest();assert digest==q['model_sha256']
    rows=[];decks={};refinement=None
    try:
        for i,(floor,ramp,plateau) in enumerate(itertools.product(q['supply_floor_V'],q['fall_and_rise_time_s'],q['low_plateau_s'])):
            row,deck=run(c,q,floor,ramp,plateau,q['base_step_s']);rows.append(row);decks[str(i)]=deck
            print(i,floor,ramp,plateau,'detected',row['dip_detected'],flush=True)
            if dict(floor_V=floor,ramp_s=ramp,plateau_s=plateau)==q['refine_case']:
                fine,deck=run(c,q,floor,ramp,plateau,q['refined_step_s']);decks[str(i)+'-fine']=deck
                assert [x['state'] for x in row['events']]==[x['state'] for x in fine['events']]
                delta=max(abs(a['time_s']-b['time_s']) for a,b in zip(row['events'],fine['events']))
                refinement=dict(maximum_transition_delta_s=delta,
                    converged_to_declared_tolerance=delta<q['maximum_refinement_transition_difference_s'],result=fine)
                print('refinement',delta,refinement['converged_to_declared_tolerance'],flush=True)
        assert len(rows)==24 and refinement is not None
        report=dict(nominal_matrix_completed=True,runs=len(rows)+1,rows=rows,refinement=refinement,decks=decks,
          model_sha256=digest,contract_sha256=hashlib.sha256((M/'brownout-contract.json').read_bytes()).hexdigest(),
          limits=['nominal model only, no temperature/part variation','ideal imposed rail, no regulator or short-circuit model','manual-reset CT discrepancy separately documented','absolute 3.15/1.35V observation thresholds; not a complete HC14/HC74/relay simulation'],
          qualification_pass=False,fabrication_ready=False)
        (M/'results/brownout-matrix.json').write_text(json.dumps(report,indent=2)+'\n')
    finally:(M/'results/brownout-matrix.log').write_text('\n'.join(s.logs)+'\n')
if __name__=='__main__':main()
