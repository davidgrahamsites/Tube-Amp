"""HD-005: supply feed budget and bounded regulator boundary. No physical adoption."""
from pathlib import Path
import copy,hashlib,itertools,json,subprocess,sys,time
import supply
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2];OUT=M/'results'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def config(c,profile,feed):
 x=copy.deepcopy(c['supply_contract']);p=x['regulator'];p['series_feed_candidate_ohm']=feed
 if profile=='low':p.update(Rset_ohm=201,Rlower_ohm=42984,reference_V=[1.2]*3,adjust_A=[0]*3)
 if profile=='high':p.update(Rset_ohm=199,Rlower_ohm=43416,reference_V=[1.313]*3,adjust_A=[.000101]*3)
 return x

def run():
 c=json.loads((M/'ceiling-contract.json').read_text());base=c['supply_contract']
 for path,h in {**base['inputs'],**base['native_sha256']}.items():assert sha(ROOT/path)==h,path
 s=dict(adopted=False,hardware_qualified=False,contract_sha256=sha(M/'ceiling-contract.json'),factory_sha256=sha(Path(__file__)),adapter_sha256=sha(M/'tools/supply.py'),dc=[],audio=[],inputs=base['inputs'],native_sha256=base['native_sha256'])
 s['shunt_min_feed_W']=(550-300)**2/(10000*1.05)
 feed_low,feed_high=c['feed_range_ohm']
 s['short_with_current_limit']=dict(pass_W=(550-.03*feed_low)*.03,feed_W=.03**2*feed_high)
 s['pass_short_unlimited']=dict(current_A=550/feed_low,feed_W=550**2/feed_low)
 s['models']='HD-004 behavioral limiter; generic tubes/transformer. All profiles diagnostic; no startup/fault device model.'
 for profile,vin,feed,cold in itertools.product(['low','nominal','high'],[320,380,550],[feed_low,feed_high],[False,True]):
  case=dict(id=f'ceiling-{profile}-{vin}-{feed}-'+('cold' if cold else 'warm'),mode='limited',input_V=vin,cold=cold)
  x=config(c,profile,feed);r=supply.dc(case,x);r.update(profile=profile,feed_ohm=feed,target_V=supply.budget(x)['nominal_V']);s['dc'].append(r)
 (OUT/'ceiling-dc.log').write_text('\n'.join(supply.sp.logs))
 cases=[dict(id='ceiling-audio-'+p,mode='limited',input_V=320,profile=p,feed_ohm=feed_high) for p in ['low','nominal','high']]
 cases.append(dict(id='ceiling-audio-high-fine',mode='limited',input_V=320,profile='high',feed_ohm=feed_high,refine=2))
 path=OUT/'ceiling-screen.json'
 for case in cases:
  name=case['id'];start=time.monotonic();receipt=OUT/f'supply-{name}.json'
  try:
   p=subprocess.run([sys.executable,str(Path(__file__)),'--worker',json.dumps(case)],capture_output=True,text=True,timeout=120)
   (OUT/f'supply-{name}.log').write_text(p.stdout+p.stderr)
   r=json.loads(receipt.read_text()) if p.returncode==0 else dict(status='failed',case=case,error=(p.stdout+p.stderr)[-1200:])
  except subprocess.TimeoutExpired as e:r=dict(status='timeout',case=case,error='120s wall limit')
  r['elapsed_s']=time.monotonic()-start;s['audio'].append(r);receipt.write_text(json.dumps(r,indent=2)+'\n');path.write_text(json.dumps(s,indent=2)+'\n');print(name,r['status'],r.get('fundamental_W'),flush=True)
 for key in ['inputs','native_sha256']:
  for p,h in s[key].items():assert sha(ROOT/p)==h,p
if __name__=='__main__':
 if '--worker' in sys.argv:
  c=json.loads((M/'ceiling-contract.json').read_text());case=json.loads(sys.argv[-1])
  try:
   r=supply.worker(case,config(c,case['profile'],case['feed_ohm']));(OUT/f'supply-{case["id"]}.json').write_text(json.dumps(r,indent=2)+'\n')
  finally:print('\n'.join(supply.sp.logs[-80:]))
 else:run()
