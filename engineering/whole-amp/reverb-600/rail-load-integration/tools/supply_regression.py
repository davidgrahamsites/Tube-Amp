"""Re-run existing brownout cases with explicit new native rail-load allocation."""
from pathlib import Path
import copy,hashlib,json,sys
M=Path(__file__).resolve().parents[1];ROOT=M.parents[3];D=M/'results';W=M.parent.parent
sys.path.insert(0,str(W/'control-switching/tools'));from brownout_timing import run
sys.path.insert(0,str(W/'aux-supply/tools'));from calculate_loads import load

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 paths=[W/'control-switching/results/fast-clamp/brownout.json',W/'aux-supply/results/hold-up/comparison.json',W/'control-switching/brownout-timing-contract.json',W/'control-switching/results/rail-monitor-precision-budget.json']
 old,upstream,contract,precision=[json.loads(p.read_text()) for p in paths];paths.append(W/'control-switching/results/ac-loss/screen.json');ac=json.loads(paths[-1].read_text())['thresholds'];budget=load();extra=budget['reverb_rail_loads']['each_rail_maximum_A']
 # Pre-existing decks already include their other load allowances. Add only the new branches.
 changed=copy.deepcopy(upstream)
 for key,deck in changed['decks'].items():
  assert 'IR619' not in deck
  changed['decks'][key]=deck.replace('.end',f'IR619 rawp 0 PWL(0 0 .05 0 .06 {extra:.15g})\nIR620 0 rawn PWL(0 0 .05 0 .06 {extra:.15g})\n.end')
 rows=[];decks={};logs=[]
 for idx,row in enumerate(old['cases']):
  base=next(x for x in upstream['cases'] if x['case']['id']==row['case']['id'])
  result,deck,log=run(contract,old['detector'],ac,precision,changed,base,row['profile'],row['ramp_s'],row['step_s'],row['raw_warning'])
  result['id']=row['id']
  result['previous_healthy_enable_margin_V']=row['healthy_enable_margin_V'];result['previous_min_raw_reserve_s']=min(x['conditional_raw_mute_reserve_s'] for x in row['raw_warning_traces'] if x['conditional_raw_mute_reserve_s'] is not None)
  key=f'brownout-{idx:02d}.cir';(D/key).write_text(deck);decks[key]=sha(D/key);rows.append(result);logs.append(key+'\n'+log)
  if (idx+1)%8==0:print('Loaded brownout cases',idx+1,'/',len(old['cases']),flush=True)
 limiting=min(rows,key=lambda r:min(x['conditional_raw_mute_reserve_s'] for x in r['raw_warning_traces'] if x['conditional_raw_mute_reserve_s'] is not None))
 base=next(x for x in upstream['cases'] if x['case']['id']==limiting['case']['id'])
 fine,deck,log=run(contract,old['detector'],ac,precision,changed,base,limiting['profile'],limiting['ramp_s'],limiting['step_s']/2,limiting['raw_warning']);fine['id']=limiting['id'];(D/'brownout-refined.cir').write_text(deck);decks['brownout-refined.cir']=sha(D/'brownout-refined.cir');logs.append(log)
 reserve=lambda r:min(x['conditional_raw_mute_reserve_s'] for x in r['raw_warning_traces'] if x['conditional_raw_mute_reserve_s'] is not None)
 summary={'cases':len(rows),'extra_each_rail_A':extra,'minimum_conditional_raw_reserve_s':min(map(reserve,rows)),'minimum_healthy_enable_margin_V':min(r['healthy_enable_margin_V'] for r in rows),'reserve_failures':sum(reserve(r)<0 for r in rows),'healthy_enable_failures':sum(r['healthy_enable_margin_V']<0 for r in rows),'refinement_reserve_difference_s':abs(reserve(fine)-reserve(limiting)),'whole_system_qualified':False,'protection_candidate_native_adopted':False}
 out={'summary':summary,'cases':rows,'refinement':fine,'deck_sha256':decks,'input_sha256':{str(p.relative_to(ROOT)):sha(p) for p in paths+[Path(__file__),W/'control-switching/tools/brownout_timing.py',W/'control-switching/tools/ac_loss_detector.py',W/'aux-supply/tools/calculate_loads.py',W/'aux-supply/load-contract.json',M.parent/'circuit.json']},'limitations':['Same conditional source-only supply, warning thresholds and assumed contact latency as VAL-054; no new device dynamic guarantee.','Constant extra current uses18V/9800ohm, conservative until first headroom loss. It is not physical after dropout.','All prior transformer, socket, thermal, current-budget and Shanghai procurement gates remain.']}
 (D/'supply-regression.json').write_text(json.dumps(out,indent=2)+'\n');(D/'supply-simulator.log').write_text('\n\n'.join(logs));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
