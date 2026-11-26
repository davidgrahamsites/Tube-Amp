"""HD-004 coupled supply load. A behavioral boundary is not a real limiter."""
from pathlib import Path
import hashlib,itertools,json,math,subprocess,sys,time
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2];OUT=M/'results'
sys.path.insert(0,str(ROOT/'engineering/whole-amp/effects-loop/tools'))
import numpy as np
from loaded_feedback_model import build
from run import sp,stats

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def budget(c):
    p=c['regulator'];rows=[]
    for vr,ia,st,sb in itertools.product([p['reference_V'][0],p['reference_V'][-1]],[p['adjust_A'][0],p['adjust_A'][-1]],[-1,1],[-1,1]):
        rt=p['Rset_ohm']*(1+st*p['resistance_total_tolerance']);rb=p['Rlower_ohm']*(1+sb*p['resistance_total_tolerance'])
        v=vr*(1+rb/rt)+ia*rb
        rows.append(dict(vref_V=vr,iadj_A=ia,rt_ohm=rt,rb_ohm=rb,output_V=v,program_A=vr/rt,lower_W=(v-vr)**2/rb))
    return dict(corners=rows,nominal_V=p['reference_V'][1]*(1+p['Rlower_ohm']/p['Rset_ohm'])+p['adjust_A'][1]*p['Rlower_ohm'],
                max_with_allocated_drift_V=max(r['output_V'] for r in rows)*(1+p['long_term_drift_allocation']),
                minimum_program_A=min(r['program_A'] for r in rows),maximum_lower_W=max(r['lower_W'] for r in rows))

def deck(case,c):
    text=build(mode='buffer',source_ohm=1000,supply=278,channel=case.get('channel','clean'),amp=case.get('amp',.009),freq=1000,volume=1,tone=.5,gain=.5)
    assert text.count('VEARLY B_EARLY 0 278')==text.count('VPRE B_PRE 0 313')==1
    text=text.replace('VEARLY B_EARLY 0 278','R17 B_PRE B_EARLY 10000\nC12 B_EARLY 0 50u')
    extra=['RHT B_PRE HREF 39000','RHB HREF 0 39000','C13 B_PRE 0 50u','C25 B_PRE 0 50u']
    mode=case['mode']
    if mode=='fixed':
        text=text.replace('VPRE B_PRE 0 313',f'VPRE B_PRE 0 {case["pre_V"]}')
    elif mode=='passive':
        text=text.replace('VPRE B_PRE 0 313','R35 SUPPLY_IN FEED 10000\nVPRE FEED B_PRE 0')
    elif mode=='limited':
        p=c['regulator'];target=budget(c)['nominal_V']
        text=text.replace('VPRE B_PRE 0 313',f'RFEED SUPPLY_IN PREREG {p["series_feed_candidate_ohm"]}\n'
                          'VPRE REG_OUT B_PRE 0\n'
                          f'BREG PREREG REG_OUT I=max(0,min({p["provisional_current_limit_A"]},min((V(PREREG)-V(REG_OUT)-{p["provisional_input_output_target_V"]})/100,({target}-V(REG_OUT))/.1)))')
        # Feedback-divider current and ADJ current represented as load only.
        # Closed-loop dynamics and pass-device parasitics are deliberately absent.
        total=p['Rset_ohm']+p['Rlower_ohm']
        # KCL: Iinput=(Vout+Iadj*Rset)/(Rset+Rlower).
        extra += [f'RPROGRAM B_PRE 0 {total}',f'IPROGRAM B_PRE 0 {p["adjust_A"][1]*p["Rset_ohm"]/total}']
    else:raise ValueError(mode)
    if 'input_V' in case:extra.append(f'VSUPPLY SUPPLY_IN 0 {case["input_V"]}')
    assert 'VSCREEN B_SCREEN 0 380' in text
    if case.get('cold'):
        text='\n'.join(line for line in text.splitlines() if not line.startswith('XV'))+'\n'
    return text.replace('.end','\n'.join(extra)+'\n.end')

def dc(case,c):
    text=deck(case,c);path=OUT/f'supply-{case["id"]}.cir';path.write_text(text)
    sp.load(text);sp.cmd('op')
    r=dict(case=case,pre_V=sp.vector('v(b_pre)')[-1],early_V=sp.vector('v(b_early)')[-1],
           input_A=-sp.vector('i(vpre)')[-1] if case['mode']=='fixed' else sp.vector('i(vpre)')[-1],deck_sha256=sha(path))
    r['early_A']=(r['pre_V']-r['early_V'])/10000
    if case['mode']=='limited':
        r['pass_V']=sp.vector('v(prereg)')[-1]-r['pre_V'];r['pass_W']=r['pass_V']*r['input_A'];r['feed_W']=r['input_A']**2*c['regulator']['series_feed_candidate_ohm']
    sp.cmd('destroy all');return r

def worker(case,c):
    text=deck(case,c);path=OUT/f'supply-{case["id"]}.cir';path.write_text(text)
    sp.load(text);sp.cmd('op');nodes=['B_PRE','B_EARLY','DR_CF','SPEAKER','FX_SEND','PREREG'] if case['mode']=='limited' else ['B_PRE','B_EARLY','DR_CF','SPEAKER','FX_SEND']
    sp.cmd('save i(vpre) '+' '.join('v('+n.lower()+')' for n in nodes))
    end=1.;step=1/(1000*96)/case.get('refine',1);sp.cmd(f'tran {step} {end} .98 {step}')
    t=np.array(sp.vector('time'));assert t[-1]>=end*(1-1e-8)
    values={n:np.array(sp.vector('v('+n.lower()+')')) for n in nodes};i=np.array(sp.vector('i(vpre)'))*(-1 if case['mode']=='fixed' else 1)
    assert all(np.isfinite(y).all() for y in [i,*values.values()])
    metrics={n:stats(t,v,1000,end) for n,v in values.items()};prev=stats(t,values['SPEAKER'],1000,end-.01)
    times=np.arange(2560)/256000+.99;cols=np.column_stack([times,*[np.interp(times,t,values[n]) for n in nodes],np.interp(times,t,i)])
    np.savetxt(OUT/f'supply-{case["id"]}.csv',cols,delimiter=',',header='time_s,'+','.join(nodes)+',pre_current_A',comments='',fmt='%.12g')
    result=dict(status='completed',case=case,signals=metrics,fundamental_W=metrics['SPEAKER']['fundamental_Vpk']**2/16,
                current_mean_A=float(np.mean(cols[:,-1])),current_max_A=float(max(cols[:,-1])),
                settled_relative=abs(metrics['SPEAKER']['fundamental_Vpk']-prev['fundamental_Vpk'])/max(metrics['SPEAKER']['fundamental_Vpk'],1e-12),
                step_s=step,end_s=float(t[-1]),deck_sha256=sha(path))
    return result

def main():
    c=json.loads((M/'supply-contract.json').read_text())
    for path,h in {**c['inputs'],**c['native_sha256']}.items():assert sha(ROOT/path)==h,path
    cases=[dict(id=f'fixed-{v}',mode='fixed',pre_V=v) for v in [260,273.41,280,300]]
    cases += [dict(id=f'{mode}-{v}-'+('cold' if cold else 'warm'),mode=mode,input_V=v,cold=cold) for mode in ['passive','limited'] for v in c['input_supply_V'] for cold in [False,True]]
    sp.cmd('version');out=dict(budget=budget(c),dc=[dc(case,c) for case in cases],audio=[],adopted=False,hardware_qualified=False,
        contract_sha256=sha(M/'supply-contract.json'),factory_sha256=sha(Path(__file__)),inputs=c['inputs'],native_sha256=c['native_sha256'])
    (OUT/'supply-dc.log').write_text('\n'.join(sp.logs));result=OUT/'supply-screen.json';result.write_text(json.dumps(out,indent=2)+'\n')
    acases=[dict(id=f'audio-fixed-{v}',mode='fixed',pre_V=v) for v in [300,273.41]]
    acases += [dict(id=f'audio-limited-{v}',mode='limited',input_V=v) for v in c['input_supply_V']]
    acases += [dict(id='audio-limited-380-fine',mode='limited',input_V=380,refine=2)]
    for case in acases:
        name=case['id'];start=time.monotonic();path=OUT/f'supply-{name}.json'
        for suffix in ['json','cir','csv','log']:(OUT/f'supply-{name}.{suffix}').unlink(missing_ok=True)
        try:
            p=subprocess.run([sys.executable,str(Path(__file__)),'--worker',json.dumps(case)],capture_output=True,text=True,timeout=120)
            (OUT/f'supply-{name}.log').write_text(p.stdout+p.stderr)
            r=json.loads(path.read_text()) if p.returncode==0 else dict(status='failed',case=case,error=(p.stdout+p.stderr)[-1600:])
        except subprocess.TimeoutExpired as e:
            r=dict(status='timeout',case=case,error='120s wall limit');(OUT/f'supply-{name}.log').write_bytes((e.stdout or b'')+(e.stderr or b''))
        r['elapsed_s']=time.monotonic()-start;path.write_text(json.dumps(r,indent=2)+'\n');out['audio'].append(r);result.write_text(json.dumps(out,indent=2)+'\n')
        print(name,r['status'],r.get('fundamental_W'),flush=True)
    for path,h in {**c['inputs'],**c['native_sha256']}.items():assert sha(ROOT/path)==h,path

if __name__=='__main__':
    if '--worker' in sys.argv:
        try:
            case=json.loads(sys.argv[-1]);r=worker(case,json.loads((M/'supply-contract.json').read_text()))
            (OUT/f'supply-{case["id"]}.json').write_text(json.dumps(r,indent=2)+'\n')
        finally:print('\n'.join(sp.logs[-80:]))
    else:main()
