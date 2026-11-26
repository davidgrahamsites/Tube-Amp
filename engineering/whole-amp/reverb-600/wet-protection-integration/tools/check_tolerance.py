"""Recheck normal linear loading with adopted 5% PR01 and temperature allowance."""
from pathlib import Path
import hashlib,importlib.util,itertools,json,math,re
M=Path(__file__).resolve().parents[1];R=M.parents[3];source=R/'engineering/whole-amp/reverb-600/circuit.json'
model=M.parent/'wet-protection/tools/analyze.py';spec=importlib.util.spec_from_file_location('wet_analytic',model);f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
rows=json.loads(source.read_text())['components'];native={x['reference']:x for x in rows};refs=['R616','R612','R618','R617','R24','R601','R602','C601','C607'];v={}
for ref in refs:
 a,b=re.fullmatch(r'([\d.]+)([Mkunp]?)',native[ref]['value']).groups();v[ref]=float(a)*{'':1,'M':1e6,'k':1e3,'u':1e-6,'n':1e-9,'p':1e-12}[b]
assert native['R616']['selected_mpn']=='PR01000101000JA500' and v['R616']==100
assert native['D603']['pins']=={'1':'WET_AC','2':'WET_Z_JOIN'} and native['D604']['pins']=={'1':'GND','2':'WET_Z_JOIN'}
results=[]
for r,hz,rs,scale,cp in itertools.product([93.8125,106.3125],[20,82.4,1000,20000],[1000,40000,200000],[.9,1.1],[0,1e-10,5e-10,1e-9]):
 rr=dict(v,R616=r);dry=f.ac(rr,hz,rs,cp,False,v['C607']*scale);wet=f.ac(rr,hz,rs,cp,True,v['C607']*scale);dry0=f.ac(v,hz,rs,cp,False,v['C607']*scale);wet0=f.ac(v,hz,rs,cp,True,v['C607']*scale)
 results.append(dict(R616_ohm=r,Hz=hz,source_ohm=rs,C607_scale=scale,pair_capacitance_F=cp,dry_gain_delta_dB=20*math.log10(abs(dry[1]/dry0[1])),wet_gain_delta_dB=20*math.log10(abs(wet[1]/wet0[1])),wet_node_sum_V=150*abs(dry[2])+18*abs(wet[2])))
maxgain=max(abs(x[k]) for x in results for k in ['dry_gain_delta_dB','wet_gain_delta_dB']);maxv=max(x['wet_node_sum_V'] for x in results)
assert maxgain<.05 and maxv<20
out=dict(passed=True,cases=results,maximum_tolerance_gain_change_dB=maxgain,maximum_wet_node_sum_V=maxv,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),model_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),limit='Linear passive loading only, not nonlinear IC stability or contact-life qualification',hardware_qualified=False)
(M/'results/tolerance.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items() if k!='cases'})
