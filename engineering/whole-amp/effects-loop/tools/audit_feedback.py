"""Audit retained feedback evidence and declared failure controls, not hardware."""
import hashlib,json
from pathlib import Path
from fixture import ROOT,WHOLE,fingerprint
OUT=ROOT/'results'
def main():
    checks={};s=json.loads((OUT/'feedback-summary.json').read_text());t=json.loads((OUT/'feedback-transient-summary.json').read_text());r=json.loads((OUT/'feedback-ringdown.json').read_text());ports=json.loads((OUT/'feedback-terminal-checks.json').read_text())
    for label,j in [('AC',s),('ring',r)]:
        checks[label+'_current_source']=j['source_hashes']==fingerprint()
        checks[label+'_factories']=all(hashlib.sha256((WHOLE.parent.parent/p).read_bytes()).hexdigest()==h for p,h in j['factory_hashes'].items())
    checks['AC_identity_and_DC']=s['passed']
    checks['independent_terminal_measurements']=ports['passed'] and len(ports['rows'])==18
    for case in s['cases']:
        for state,h in case['deck_hashes'].items():checks[case['name']+'-'+state+'-deck']=hashlib.sha256((OUT/f'{case["name"]}-{state}.cir').read_bytes()).hexdigest()==h
    for case in t['cases']:
        n=case['name'];checks[n+'-complete']=case['status']=='completed' and case['end_s']>=.5*(1-1e-8)
        checks[n+'-source']=case['source_hashes']==fingerprint()
        checks[n+'-factory']=all(hashlib.sha256((WHOLE.parent.parent/p).read_bytes()).hexdigest()==h for p,h in case['factory_hashes'].items())
        checks[n+'-deck']=hashlib.sha256((OUT/f'{n}.cir').read_bytes()).hexdigest()==case['deck_sha256']
    ring={c['name'].removeprefix('feedback-ring-'):c for c in r['cases']}
    for n,c in ring.items():checks['ring-'+n+'-deck']=hashlib.sha256((OUT/f'{c["name"]}.cir').read_bytes()).hexdigest()==c['deck_sha256']
    checks['bad_compensation_detected_at_HF_resolution']=ring['lead220-fine']['late_tail_peak_V']>.1
    checks['fine_and_refined_oscillation_agree']=abs(ring['lead220-fine']['late_tail_peak_V']/ring['lead220-refined']['late_tail_peak_V']-1)<.01
    checks['coarse_step_hides_failure']=ring['lead220-coarse']['late_tail_peak_V']<1e-4
    checks['lead47_local_burst_decays']=ring['lead47-fine']['late_tail_peak_V']<1e-4
    result=dict(scope='Evidence/provenance and negative controls, not passing all compensation candidates',checks=checks,passed=all(checks.values()),check_count=len(checks),ac_case_count=len(s['cases']),physical_qualified=False,fabrication_ready=False)
    (OUT/'feedback-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(result['check_count'],'checks','PASS' if result['passed'] else 'FAIL');assert result['passed'],[k for k,v in checks.items() if not v]
if __name__=='__main__':main()
