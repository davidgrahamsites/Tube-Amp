"""Independent arithmetic, coverage and provenance audit for HD-008."""
from pathlib import Path
import hashlib,itertools,json,math
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 c=json.loads((M/'absolute-contract.json').read_text());r=json.loads((M/'results/absolute-screen.json').read_text());base=json.loads((M/'pass-contract.json').read_text());prior=json.loads((M/'series-contract.json').read_text());checks=[]
 def ck(name,ok):checks.append(dict(name=name,passed=bool(ok)))
 ck('contract hash',r['contract_sha256']==sha(M/'absolute-contract.json'));ck('factory hash',r['factory_sha256']==sha(M/'tools/absolute_authority.py'))
 for p,h in c['input_sha256'].items():ck('input '+p,sha(M/p)==h)
 expected=set(itertools.product(c['modes'],c['input_V'],c['profiles'],c['cold'],c['vto_V'],c['vto_V'],c['source_ohm']));actual=set();kcl=[]
 for i,row in enumerate(r['rows']):
  case=row['case'];n=row['nodes'];a=case['sensitivity'];q=base['profiles'][case['profile']];z=prior['topology'];mode=case['mode']
  actual.add((mode,case['vin'],case['profile'],case['cold'],a['vto1'],a['vto2'],a['source_ohm']))
  source=(n['s']-n['regin'])/a['source_ohm'];bias=sum((n['in']-n[v])/z['gate_bias_total_each_ohm'] for v in ['gref','gref2']);back=(n['g']-n['gref'])/z['gate_resistor_each_ohm']+(n['g2']-n['gref2'])/z['gate_resistor_each_ohm']
  load=n['out']/78000+n['adj']/q['rlow']+n['out']/z['preload_ohm']+(0 if case['cold'] else n['out']/36200)
  err=source+bias+back-load;kcl.append(err)
  ck(f'{i} finite nodes',all(math.isfinite(v) for v in n.values()));ck(f'{i} output KCL',abs(err)<c['limits']['kcl_A'])
  ck(f'{i} gate applicability',max(abs(n['g']-n['mid']),abs(n['g2']-n['s']))<c['limits']['gate_source_V'])
  if mode!='reference_upper_shunt':
   ck(f'{i} forced output below ceiling',n['out']<c['limits']['output_V'])
   nodes=['gref','gref2'] if mode=='direct_both' else ['gref'];cfg=c['actuator']
   for node,current in zip(nodes,row['actuator_A']):
    expected_i=min(cfg['current_cap_A'],max(0,(n[node]-n['out']-cfg['offset_V'])*cfg['conductance_S']))
    ck(f'{i} independently sensed actuator current {node}',abs(current-expected_i)<1e-9 and 0<=current<cfg['current_cap_A'])
 ck('complete unique grid',actual==expected and len(r['rows'])==len(expected))
 weak=[x['nodes']['out'] for x in r['rows'] if x['case']['mode']=='reference_upper_shunt'];ck('weak control failure retained',sum(v>300 for v in weak)==2)
 for mode,summary in r['summary'].items():
  rows=[x for x in r['rows'] if x['case']['mode']==mode];ck('summary '+mode,len(rows)==summary['cases'] and max(x['nodes']['out'] for x in rows)==summary['maximum_output_V'])
 q=base['profiles']['high'];vmax=q['vref']*(1+q['rlow']/q['rset'])+q['iadj']*q['rlow'];w=r['detector_window'];lo=(2.483-.034)/2.495;hi=(2.507+.034)/2.495
 ck('detector necessary window independently reconstructed',abs(w['nominal_trip_min_from_normal_V']-vmax/lo)<1e-9 and abs(w['nominal_trip_max_from_ceiling_V']-300/hi)<1e-9 and vmax/lo>300/hi and not w['feasible'])
 for p,h in r['native_sha256'].items():ck('native '+p,sha(ROOT/p)==h)
 for flag in ['automatic_protection','physical_qualification','adopted']:ck(flag+' remains false',r[flag] is False)
 out=dict(id=c['id'],passed=all(x['passed'] for x in checks),count=len(checks),checks=checks,maximum_KCL_error_A=max(map(abs,kcl)),result_sha256=sha(M/'results/absolute-screen.json'),scope='DC control authority and detector-window arithmetic only.')
 (M/'results/absolute-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='checks'}));assert out['passed'],[a for a in checks if not a['passed']]
if __name__=='__main__':main()
