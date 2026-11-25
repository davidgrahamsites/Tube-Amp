"""Resolve the failed 10us-to-1us convergence check without loosening tolerance."""
import hashlib,json
from pathlib import Path
from simulate_brownout_matrix import run,s
M=Path(__file__).resolve().parents[1]

def main():
    c=json.loads((M/'contract.json').read_text());q=json.loads((M/'brownout-contract.json').read_text());p=M/'results/brownout-matrix.json';prior=json.loads(p.read_text())
    assert prior['contract_sha256']==hashlib.sha256((M/'brownout-contract.json').read_bytes()).hexdigest()
    assert prior['model_sha256']==hashlib.sha256((M/q['model']).read_bytes()).hexdigest()
    before=prior['refinement']['result'];case=q['refine_case']
    try:
        after,deck=run(c,q,case['floor_V'],case['ramp_s'],case['plateau_s'],2e-7)
        assert [e['state'] for e in before['events']]==[e['state'] for e in after['events']]
        deltas=[abs(a['time_s']-b['time_s']) for a,b in zip(before['events'],after['events'])]
        result=dict(prior_matrix_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),coarse_check_passed=prior['refinement']['converged_to_declared_tolerance'],
          prior_step_s=before['step_s'],refined_step_s=after['step_s'],transition_differences_s=deltas,
          tolerance_s=q['maximum_refinement_transition_difference_s'],refinement_passed=max(deltas)<q['maximum_refinement_transition_difference_s'],
          result=after,deck=deck,qualification_pass=False,fabrication_ready=False)
        (M/'results/brownout-refinement.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k not in ['result','deck']},indent=2))
    finally:(M/'results/brownout-refinement.log').write_text('\n'.join(s.logs)+'\n')
if __name__=='__main__':main()
