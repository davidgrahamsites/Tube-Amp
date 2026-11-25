"""Fast K3 candidate: bounded coil calculation and loaded raw-warning comparison.
Never mutates native CAD or previous candidate evidence.
"""
import itertools,json,math,sys,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
DEST=BASE/'results/fast-clamp'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def current_time(i0,i1,r,l,v):return l/r*math.log((i0+v/r)/(i1+v/r))
def solve(c,coil):
    tv=c['tvs'];vmin=tv['vbr_min_25C_V']*(1+tv['alpha_max_per_C']*(tv['cold_C']-25));rows=[]
    for temp,tol,l,v in itertools.product(c['temperatures_C'],[-coil['resistance_tolerance'],coil['resistance_tolerance']],coil['inductance_reference_H'],coil['voltage_V']):
        r=coil['resistance_23C_ohm']*(1+tol)*(1+coil['copper_tcr_screen_per_C']*(temp-23));i0=v/r;target=c['fraction']*i0;ik=tv['ibr_A']
        assert i0>ik>target and vmin>v
        first=current_time(i0,ik,r,l,vmin-v);tail=current_time(ik,target,r,l,0)
        vmax=max(z['vcl_V']-z['rd_ohm']*(z['ipp_A']-i0) for z in tv['clamp_curves'])*(1+tv['alpha_max_per_C']*(tv['hot_C']-25))
        # Energy screen includes supply contribution and the conservative sub-1mA tail.
        # It is not a thermal/pulse rating qualification.
        a=(vmin-v)/r
        charge=(i0+a)*l/r*(1-math.exp(-r*first/l))-a*first + ik*l/r
        rows.append(dict(coil_C=temp,resistance_ohm=r,inductance_H=l,supply_V=v,initial_A=i0,target_A=target,cold_drain_min_V=vmin,hot_drain_formula_max_V=vmax,above_test_current_s=first,conservative_tail_s=tail,decay_to_5percent_s=first+tail,conservative_integrated_charge_C=charge,clamp_energy_formula_screen_J=vmax*charge,coil_initial_energy_J=.5*l*i0*i0))
    return rows

def main():
    cp=BASE/'fast-clamp-contract.json';c=json.loads(cp.read_text());coil=json.loads((BASE/'contract.json').read_text())['coil'];rows=solve(c,coil)
    # Preserve exact native source/schematic/PCB identities, including existing unsaved project edits.
    native={str(p.relative_to(BASE.parent)):sha(p) for p in BASE.parent.rglob('*') if p.is_file() and (p.suffix in ('.kicad_sch','.kicad_pcb') or p.name=='circuit.json') and '.git' not in p.parts}
    worst=max(r['decay_to_5percent_s'] for r in rows)
    report={'qualified':False,'native_adopted':False,'contact_release_verified':False,'contract':c,'cases':rows,'summary':{'cases':len(rows),'maximum_coil_decay_s':worst,'maximum_formula_drain_V':max(r['hot_drain_formula_max_V'] for r in rows),'minimum_driver_margin_after_overshoot_V':min(c['driver_vds_absolute_max_V']-r['hot_drain_formula_max_V']-c['overshoot_allocation_V'] for r in rows),'maximum_clamp_energy_formula_screen_J':max(r['clamp_energy_formula_screen_J'] for r in rows)},'native_sha256':native,'inputs':{str(p.relative_to(BASE)):sha(p) for p in [cp,BASE/'contract.json',Path(__file__)]}}
    (DEST/'screen.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['summary'],indent=2),flush=True)
    from brownout_timing import run,profiles
    from precision_rail_budget import positive_corners
    paths=[BASE/'raw-warning-contract.json',BASE/'brownout-timing-contract.json',BASE/'ac-loss-contract.json',BASE/'results/ac-loss/screen.json',BASE/'results/rail-monitor-precision-budget.json',BASE.parent/'aux-supply/results/hold-up/comparison.json',BASE/'rail-monitor-precision-contract.json']
    candidate,timing,detector,ac,precision,upstream,static=[json.loads(p.read_text()) for p in paths]
    r=c['warning_change'];candidate['positive_resistors_ohm']={'rail':r['rail_ohm'],'ground':r['ground_ohm'],'feedback':r['feedback_ohm']};candidate['status']='new-fast-clamp-trial-not-native'
    detector['relay_five_percent_current_screen_s']=worst
    static['positive_resistors_ohm']=candidate['positive_resistors_ohm'];static['resistor_fraction']=candidate['resistor_fraction'];threshold=positive_corners(static)
    bases=[r for r in upstream['cases'] if r['case'].get('phase_deg') in timing['phases_deg'] and r['case']['winding_voltage_factor']==timing['winding_factor']]
    profile=next(p for p in profiles(detector) if p['name']=='slow_decay_high_envelope')
    runs=[];decks={};logs=[]
    for base,duration,cap in itertools.product(bases,timing['ramp_durations_s'],candidate['profiles']):
        warning={'profile':cap['name'],'positive_cap_F':candidate['positive_cap_nominal_F']*cap['cap_fraction'],'esr_ohm':cap['esr_ohm'],'cap_leakage_A':candidate['cap_leakage_screen_A'],'resistors_ohm':candidate['positive_resistors_ohm'],'thresholds':threshold['abs_ranges_V']}
        row,deck,log=run(timing,detector,ac['thresholds'],precision,upstream,base,profile,duration,timing['step_s'],warning)
        row['id']+='-'+cap['name'];runs.append(row);decks[row['id']]=deck;logs.append(row['id']+'\n'+log)
        if len(runs)%8==0:print('Fast clamp brownout cases',len(runs),flush=True)
    target=min(runs,key=lambda r:min(z['conditional_raw_mute_reserve_s'] if z['conditional_raw_mute_reserve_s'] is not None else -100 for z in r['raw_warning_traces']))
    base=next(b for b in bases if b['case']['id']==target['case']['id'])
    fine,deck,log=run(timing,detector,ac['thresholds'],precision,upstream,base,profile,target['ramp_s'],timing['step_s']/2,target['raw_warning']);decks[target['id']+'-fine']=deck;logs.append(log)
    delta=max(abs(a['conditional_raw_mute_reserve_s']-b['conditional_raw_mute_reserve_s']) for a,b in zip(target['raw_warning_traces'],fine['raw_warning_traces']) if a['conditional_raw_mute_reserve_s'] is not None and b['conditional_raw_mute_reserve_s'] is not None)
    summary={'cases':len(runs),'failed_healthy_enable_cases':sum(r['healthy_enable_margin_V']<0 for r in runs),'minimum_enable_margin_V':min(r['healthy_enable_margin_V'] for r in runs),'missing_full_fault_pulse_cases':sum(any(z['conditional_raw_mute_reserve_s'] is None for z in r['raw_warning_traces']) for r in runs),'late_cases':sum(any(z['conditional_raw_mute_reserve_s'] is not None and z['conditional_raw_mute_reserve_s']<0 for z in r['raw_warning_traces']) for r in runs),'minimum_conditional_reserve_s':min(z['conditional_raw_mute_reserve_s'] for r in runs for z in r['raw_warning_traces'] if z['conditional_raw_mute_reserve_s'] is not None),'refinement_delta_s':delta}
    output={'qualified':False,'native_adopted':False,'candidate':candidate,'detector':detector,'thresholds':threshold,'summary':summary,'cases':runs,'refinement':{'coarse_id':target['id'],'fine':fine},'decks':decks,'inputs':{str(p.resolve().relative_to(BASE.parent)):sha(p) for p in [*paths,cp,Path(__file__),BASE/'tools/brownout_timing.py',BASE/'tools/ac_loss_detector.py',BASE/'tools/ac_loss_interruptions.py',BASE/'tools/precision_rail_budget.py']}}
    (DEST/'brownout.json').write_text(json.dumps(output,indent=2)+'\n');(DEST/'simulator.log').write_text('\n\n'.join(logs)+'\n');print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':main()
