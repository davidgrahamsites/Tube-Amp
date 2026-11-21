"""Bounded electrical checks, not a model or validation of the actual spring tank."""
from pathlib import Path
import ast, hashlib, json, math, sys
ROOT=Path(__file__).resolve().parents[1]
ENG=ROOT.parents[1]
sys.path.insert(0,str(ROOT.parent/'tools'))
from spice_runtime import load,cmd,vector,logs
OUT=ROOT/'simulation'
fit_path=ROOT.parent/'mechanical/fit-register.json'
measured=json.loads(fit_path.read_text())['tank_received']['electrical_measurements']
R_IN=float(measured['input_DC_resistance_ohm'])
R_OUT=float(measured['output_DC_resistance_ohm'])
assert R_IN>0 and R_OUT>0

source=ENG/'solid-state-reverb/tools/simulate_reverb.py'
tree=ast.parse(source.read_text())
base=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='base' for t in n.targets))
model=ENG/'solid-state-reverb/simulation/models/OPAx134.LIB'
base=base.replace('Reverb 0.4','Received tank 600R-1').replace('R601 acin dryin 100k','R601 acin dryin 1meg').replace('R602 dryin 0 10meg','R602 dryin 0 100k')
base=base.replace('R612 drybuf sum 100k','R612 fx mix 100k').replace('C607 outac mix 1u','C607 outac wetac 1u').replace('R617 mix 0 1meg','R617 wetac 0 1meg\nR618 wetac mix 1meg')
# Assert scalar values match the captured native circuit contract.
contract=json.loads((ROOT/'circuit.json').read_text())
values={c['reference']:c['value'] for c in contract['components']}
assert {r:values[r] for r in ['R601','R602','R605','R612','R618']}=={'R601':'1M','R602':'100k','R605':'220','R612':'100k','R618':'1M'}

def deck(dry=1,wet=0,knob=1,muted=False,trim=.25,amp=20,hz=1000,rail=15,z_in=600,r_in=R_IN,z_out=2250,r_out=R_OUT,rs=100000):
    # ASSUMPTION: the seller's impedance figures apply at 1kHz.
    # Default R values are user-measured DC resistances; sweep overrides are sensitivity scenarios.
    # Derived L is still an unverified surrogate, not a measured inductance.
    li=math.sqrt(z_in*z_in-r_in*r_in)/(2*math.pi*1000)
    lo=math.sqrt(z_out*z_out-r_out*r_out)/(2*math.pi*1000)
    s=base.format(model=model,dry=dry,wet=wet,amp=amp,trimtop=max(1,100000*(1-trim)),trimbot=max(1,100000*trim),wettop=max(1,100000*(1-knob)),wetbot=max(1,100000*knob),mute=1 if muted else 1e12)
    return s.replace('VP vp 0 15',f'VP vp 0 {rail}').replace('VN vn 0 -15',f'VN vn 0 {-rail}').replace(f'SIN(0 {amp} 1000)',f'SIN(0 {amp} {hz})').replace('RSOURCE input fx 100k',f'RSOURCE input fx {rs}').replace('RTANK tankin ti 58',f'RTANK tankin ti {r_in}').replace('LTANK ti 0 127m',f'LTANK ti 0 {li}').replace('ROUTT tanksrc to 200',f'ROUTT tanksrc to {r_out}').replace('LOUTT to tankout 409m',f'LOUTT to tankout {lo}')

ac=[];checks=[];dry_curves={}
for rs in [1000,100000]:
    for mode in ['dry','wet']:
        for knob in [0,.5,1]:
            for muted in ([False,True] if mode=='dry' else [False]):
                name=f'{mode}-rs{rs}-knob{knob}-mute{muted}'
                s=deck(dry=int(mode=='dry'),wet=.001 if mode=='wet' else 0,knob=knob,muted=muted,rs=rs)
                (OUT/(name+'.cir')).write_text(s);load(s);cmd('ac dec 30 20 20000')
                freq=[f.real for f in vector('frequency')];mix=vector('v(mix)')
                ix=min(range(len(freq)),key=lambda i:abs(freq[i]-1000))
                ac.append({'name':name,'mix_at_1kHz_V':abs(mix[ix]),'frequency_Hz':freq[ix]})
                if mode=='dry':dry_curves.setdefault(rs,[]).append([abs(v) for v in mix])
                cmd('destroy all')
for rs,curves in dry_curves.items():
    spread=max((max(v)-min(v))/max(v) for v in zip(*curves))
    checks.append({'name':f'dry_control_independence_rs{rs}_20Hz_to_20kHz','relative_spread':spread,'pass':spread<.001})

# Sweep unknown coil R and nominal impedance. 20Vpeak refers to the source BEFORE
# the selected source impedance. Trim is full-scale to expose the possible current.
coil=[]
for zi in [480,600,720]:
    for ri in [30,56,R_IN,100]:
        name=f'coil-z{zi}-r{ri:g}'
        s=deck(z_in=zi,r_in=ri,trim=1,dry=1)
        (OUT/(name+'.cir')).write_text(s);load(s);cmd('ac dec 60 20 20000')
        freq=[f.real for f in vector('frequency')]
        i=[abs(a-b)/ri for a,b in zip(vector('v(tankin)'),vector('v(ti)'))]
        peak=max(range(len(i)),key=i.__getitem__)
        coil.append({'Z_1k_assumed_ohm':zi,'Rdc_ohm':ri,'Rdc_basis':'user-measured' if ri==R_IN else 'sensitivity assumption','max_current_mArms_at_20Vpeak_source_full_trim':i[peak]*20/math.sqrt(2)*1000,'at_Hz':freq[peak],'max_R605_W':(i[peak]*20/math.sqrt(2))**2*220})
        cmd('destroy all')

trans=[]
for rail in [12,15]:
    for hz in [100,1000,5000]:
        name=f'transient-rail{rail}-hz{hz}'
        s=deck(rail=rail,hz=hz,trim=1)
        (OUT/(name+'.cir')).write_text(s);load(s);cmd('tran 1u 40m 0 1u')
        t=vector('time');assert t[-1]>=.039999
        keep=[i for i,v in enumerate(t) if v>.02]
        # Materialize once: avoid repeated vector reads for every sample.
        def peak(n):
            v=vector(n);return max(abs(v[i]) for i in keep)
        p={n:peak('v('+n+')') for n in ['fx','dryin','driver','mix','recout','outbuf']}
        trans.append({'name':name,'end_s':t[-1],'peaks_V':p})
        checks.append({'name':name+'_driver_headroom','pass':p['driver']<rail-3})
        if rail==12 and hz==1000:
            vectors={n:vector('v('+n+')') for n in ['fx','dryin','driver','mix']}
            import csv
            with (OUT/'headroom-waveform.csv').open('w') as f:
                w=csv.writer(f);w.writerow(['time_s',*vectors]);w.writerows([t[i],*(v[i] for v in vectors.values())] for i in range(0,len(t),20))
        cmd('destroy all')

result={'scope':'TI-model electrical interface only; original PI represented by linear load. User-measured DC resistance only; no measured AC coil data, spring acoustic transfer, VCA/pedal, real PSU, tube/OT or physical qualification.',
    'assumptions':{'tank_impedance_frequency_Hz':1000,'input_Rdc_nominal_ohm':R_IN,'output_Rdc_nominal_ohm':R_OUT,'input_L_nominal_H':math.sqrt(600**2-R_IN**2)/(2*math.pi*1000),'output_L_nominal_H':math.sqrt(2250**2-R_OUT**2)/(2*math.pi*1000),'maximum_actual_drive_current':'UNKNOWN; full trim simulation is not an authorized setting'},
    'measurement_source':{'path':str(fit_path.relative_to(ROOT.parents[2])),'sha256':hashlib.sha256(fit_path.read_bytes()).hexdigest(),'readings':measured},
    'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'ac_cases':ac,'coil_cases':coil,'transient_cases':trans,'checks':checks,'all_scoped_checks_pass':all(c['pass'] for c in checks)}
(OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n');(OUT/'ngspice.log').write_text('\n'.join(logs)+'\n')
print(json.dumps({'ac_cases':len(ac),'coil_cases':len(coil),'transient_cases':len(trans),'checks_pass':result['all_scoped_checks_pass'],'maximum_full_trim_current_mArms':max(c['max_current_mArms_at_20Vpeak_source_full_trim'] for c in coil)},indent=2))
assert result['all_scoped_checks_pass']
