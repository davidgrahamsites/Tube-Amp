"""Independent saved-waveform audit of HD-010; no imported simulation metrics."""
from pathlib import Path
import hashlib,json,math
import numpy as np
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    c=json.loads((M/'headroom-contract.json').read_text());r=json.loads((M/'results/headroom-screen.json').read_text());checks=[];audit=[]
    def ck(name,ok):checks.append(dict(name=name,passed=bool(ok)))
    ck('contract',sha(M/'headroom-contract.json')==r['contract_sha256']);ck('factory',sha(M/'tools/headroom.py')==r['factory_sha256'])
    for p,h in {**c['inputs'],**c['native_sha256']}.items():ck('dependency '+p,sha(ROOT/p)==h)
    ck('exact case coverage',[x['case'] for x in r['cases']]==c['cases'])
    for row in r['cases']:
        case=row['case'];ident=case['id'];ck(ident+' complete',row['status']=='completed')
        if row['status']!='completed':continue
        path=M/'results'/('headroom-'+ident);data=np.loadtxt(path.with_suffix('.csv'),delimiter=',',skiprows=1);text=path.with_suffix('.cir').read_text()
        ck(ident+' deck',sha(path.with_suffix('.cir'))==row['deck_sha256']);ck(ident+' waveform',sha(path.with_suffix('.csv'))==row['waveform_sha256'])
        ck(ident+' load and independent supplies','RLOAD SPEAKER 0 8.0' in text and 'VMAIN B_MAIN 0 400' in text and 'VSCREEN B_SCREEN 0 380' in text)
        ck(ident+' source',f"VSOURCE PICKUP 0 DC 0 AC 0 SIN(0 {case['amp_Vpk']} 1000)" in text and 'VTEST RET_DRIVE 0 DC 0 AC 1\n' in text)
        ck(ident+' time and finite',data.shape==(5120,12) and np.isfinite(data).all() and abs(row['end_s']-1)<1e-9 and abs(data[0,0]-.98)<1e-9 and np.all(np.diff(data[:,0])>0))
        t=data[-2560:,0];y=data[-2560:,10];angles=2*np.pi*1000*t
        harmonics=np.array([2*abs(np.mean(y*np.exp(-1j*h*angles))) for h in range(1,11)])
        power=harmonics[0]**2/(2*c['load_ohm']);thd=100*np.linalg.norm(harmonics[1:])/harmonics[0]
        ck(ident+' independent power',abs(power-row['fundamental_W'])<1e-6)
        ck(ident+' independent harmonics',abs(thd-row['signals']['SPEAKER']['THD_2_to_10_percent'])<1e-5)
        earlier=data[:2560,10];a=2*abs(np.mean(earlier*np.exp(-2j*np.pi*1000*data[:2560,0])));settling=abs(harmonics[0]-a)/harmonics[0]
        ck(ident+' steady window',settling<c['limits']['settling_relative']);ck(ident+' settling reproduction',abs(settling-row['settled_relative'])<1e-7)
        audit.append(dict(id=ident,fundamental_W=float(power),THD_2_to_10_percent=float(thd),AC_total_W=float(np.mean((y-y.mean())**2)/c['load_ohm']),settling_relative=float(settling)))
    pairs=[]
    for ch in ['clean','dirty']:
        old=[x for x in r['cases'] if x['case']['channel']==ch and x['case']['pre_V']==273.41]
        for o in old:
            new=next(x for x in r['cases'] if x['case']['channel']==ch and x['case']['pre_V']==267.11 and x['case']['amp_Vpk']==o['case']['amp_Vpk'] and 'refine' not in x['case'])
            pairs.append(dict(channel=ch,amp_Vpk=o['case']['amp_Vpk'],old_W=o['fundamental_W'],new_W=new['fundamental_W'],change_percent=100*(new['fundamental_W']/o['fundamental_W']-1),old_THD=o['signals']['SPEAKER']['THD_2_to_10_percent'],new_THD=new['signals']['SPEAKER']['THD_2_to_10_percent']))
        fine=next(x for x in r['cases'] if x['case']['id']==ch+'-fine');normal=next(x for x in r['cases'] if x['case']['channel']==ch and x['case']['pre_V']==267.11 and x['case']['amp_Vpk']==fine['case']['amp_Vpk'] and 'refine' not in x['case'])
        ck(ch+' timestep power refinement',abs(fine['fundamental_W']/normal['fundamental_W']-1)<c['limits']['refinement_relative'])
        ck(ch+' timestep distortion refinement',abs(fine['signals']['SPEAKER']['THD_2_to_10_percent']-normal['signals']['SPEAKER']['THD_2_to_10_percent'])<.05)
    for flag in ['adopted','physical_qualified','supply_dynamics_qualified']:ck(flag+' false',r[flag] is False)
    out=dict(id=c['id'],passed=all(x['passed'] for x in checks),checks=checks,count=len(checks),waveform_audit=audit,comparisons=pairs,result_sha256=sha(M/'results/headroom-screen.json'),scope='Conditional1kHz paired setpoint comparison; no clean25W, exact magnetics or real supply qualification.')
    (M/'results/headroom-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['checks','waveform_audit']},indent=2));assert out['passed'],[x for x in checks if not x['passed']]
if __name__=='__main__':main()
