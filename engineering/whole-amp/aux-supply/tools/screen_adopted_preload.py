"""Repeat the raw-supply matrix with R215's bounded current; no regulator macro-model."""
import copy,hashlib,json
from screen_envelope import MODULE,evaluate,spice
from check_preload import load_bounds

def main():
 c=json.loads((MODULE/'envelope-contract.json').read_text());pc=json.loads((MODULE/'preload-contract.json').read_text());b=load_bounds(pc)
 baseline=json.loads((MODULE/'results/envelope/screen.json').read_text());rows=[];decks={};logs=[]
 for old in baseline['cases']:
  case=copy.deepcopy(old['case']);case['id']+='-R215';case['load']['logic_5V_A']+=b['maximum_current_A']
  row,deck=evaluate(c,case,c['simulation']['max_step_s']);rows.append(row);decks[case['id']]=deck;logs.append(case['id']+'\n'+'\n'.join(spice.logs))
  assert 'U5_below_minimum_regulation_load' not in row['screen_flags']
 limiting={min(range(len(rows)),key=lambda i:rows[i]['raw_positive_V']['min']),max(range(len(rows)),key=lambda i:rows[i]['conditional_total_W']),max(range(len(rows)),key=lambda i:max(rows[i]['half_winding_rms_A'].values()))}
 refined=[]
 for i in sorted(limiting):
  fine,deck=evaluate(c,rows[i]['case'],c['simulation']['max_step_s']/2);decks[rows[i]['case']['id']+'-fine']=deck;logs.append(rows[i]['case']['id']+'-fine\n'+'\n'.join(spice.logs))
  dv=abs(fine['raw_positive_V']['min']-rows[i]['raw_positive_V']['min']);di=max(abs(fine['half_winding_rms_A'][k]/rows[i]['half_winding_rms_A'][k]-1) for k in ['i(va)','i(vb)'])
  assert dv<0.01 and di<0.005 and fine['screen_flags']==rows[i]['screen_flags']
  refined.append(dict(coarse_id=rows[i]['case']['id'],fine=fine,positive_min_delta_V=dv,winding_rms_relative_delta=di))
 report=dict(case_count=len(rows),bounds=b,cases=rows,refinements=refined,decks=decks,baseline_screen_sha256=hashlib.sha256((MODULE/'results/envelope/screen.json').read_bytes()).hexdigest(),circuit_sha256=hashlib.sha256((MODULE.parent/'reverb-600/circuit.json').read_bytes()).hexdigest(),preload_contract_sha256=hashlib.sha256((MODULE/'preload-contract.json').read_bytes()).hexdigest(),limits='Raw rectifier constant-load and conditional heat model; worst preload current used across all profiles. No L78/L79 control, startup, stability, exact transformer or socket thermal model.')
 dest=MODULE/'results/preload';(dest/'raw-screen.json').write_text(json.dumps(report,indent=2)+'\n');(dest/'simulator.log').write_text('\n\n'.join(logs)+'\n')
 print(json.dumps(dict(cases=len(rows),refinements=len(refined),flagged=sum(bool(r['screen_flags']) for r in rows),max_conditional_W=max(r['conditional_total_W'] for r in rows),max_winding_A=max(max(r['half_winding_rms_A'].values()) for r in rows))))
if __name__=='__main__':main()
