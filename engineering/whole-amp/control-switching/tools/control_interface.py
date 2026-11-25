"""Shared passive interface budget; no assumptions about unpowered logic function."""
import itertools,json,hashlib,sys
from pathlib import Path
from buffered_rail_budget import solve
from rail_delay_budget import equilibrium,crossing,advance
BASE=Path(__file__).resolve().parents[1];DEST=BASE/'results/control-interface'
sys.path.insert(0,str(BASE.parent/'tools'))
import spice_runtime as sp

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def passive_off(c,p,a,w,series,shunt):
    # Omit reference-divider/negative-network shunts: conservative passive off upper screen.
    # Clamp all positive injection sources at their enclosing voltage bounds.
    f=p['resistor_fraction'];af=a['resistor_total_fraction_allocation'];r=p['positive_resistors_ohm'];ar=a['resistors_ohm'];wr=w['positive_resistors_ohm']
    vmax=p['largest_analog_rail_abs_V']*r['ground']*(1+f)/(r['rail']*(1-f)+r['ground']*(1+f))
    edges=[('OK','REF',p['pullup']['ohm']*(1+p['pullup']['fraction'])),('REF','0',c['reference_bleeder_ohm']*(1+p['reference_bleeder_fraction'])),('OK','PSMAX',r['feedback']*(1-f)),('OK','AC',ar['feedback']*(1-af)),('AC','REF',ar['sense_bias']*(1-af)),('AC','ENV',ar['sense_top']*(1-af)),('AC','0',ar['sense_bottom']*(1+af)),('RAW','RP',wr['rail']*(1-f)),('RAW','0',wr['ground']*(1+f)),('RAW','OK',wr['feedback']*(1-f)),('OK','LOGIC',series),('LOGIC','0',shunt)]
    fixed={'0':0,'PSMAX':vmax,'ENV':c['envelope_max_screen_V'],'RP':c['raw_max_screen_V']};nodes=['OK','REF','AC','RAW','LOGIC'];ib=max(map(abs,p['input_current_A']))
    inj={'OK':4e-6,'REF':4*ib,'AC':ib,'RAW':ib,'LOGIC':c['hc_input_leak_A']}
    mat=[[0.0]*5 for _ in nodes];rhs=[inj.get(n,0) for n in nodes]
    for x,y,r in edges:
        for node,other in [(x,y),(y,x)]:
            if node not in nodes:continue
            i=nodes.index(node);mat[i][i]+=1/r
            if other in nodes:mat[i][nodes.index(other)]-=1/r
            else:rhs[i]+=fixed[other]/r
    values=solve(mat,rhs)
    # Independent SPICE resistor-network solution, same physical assumptions.
    deck='Passive reference-off envelope; not a semiconductor power-sequence model\n'
    for n,v in fixed.items():
        if n!='0':deck+=f'V{n} {n} 0 {v}\n'
    for j,(x,y,r) in enumerate(edges):deck+=f'R{j} {x} {y} {r}\n'
    for n,i in inj.items():deck+=f'I{n} 0 {n} {i}\n'
    deck+='.op\n.end\n';sp.cmd('destroy all');sp.logs.clear();sp.load(deck);sp.cmd('op')
    check=[sp.vector('v('+n.lower()+')')[0] for n in nodes];err=max(abs(x-y) for x,y in zip(values,check));assert err<1e-8
    return {'series_ohm':series,'shunt_ohm':shunt,'nodes_V':dict(zip(nodes,values)),'spice_max_error_V':err,'deck':deck}

def main():
    names=['control-interface-contract.json','rail-monitor-precision-contract.json','ac-loss-contract.json','results/fast-clamp/brownout.json','rail-delay-contract.json','results/rail-monitor-precision-budget.json','../aux-supply/preload-contract.json']
    c,p,a,fast,d,old,pre=[json.loads((BASE/n).read_text()) for n in names];w=fast['candidate'];r=p['positive_resistors_ohm'];n=p['negative_resistors_ohm'];ar=a['resistors_ohm'];wr=w['positive_resistors_ohm'];f=p['resistor_fraction'];af=a['resistor_total_fraction_allocation'];it=c['interface_resistor_fraction'];ib=max(map(abs,p['input_current_A']));ileak=c['hc_input_leak_A']
    series=[c['series_ohm']*(1-it),c['series_ohm']*(1+it)];shunt=[c['shunt_ohm']*(1-it),c['shunt_ohm']*(1+it)];pu=p['pullup']['ohm']*(1+p['pullup']['fraction']);maxfb=max(p['gate_on_assumed_V']);vmin,vmax=p['reference_V']
    fbload=maxfb*sum(1/(v*(1-t)) for v,t in [(r['feedback'],f),(n['feedback'],f),(ar['feedback'],af),(wr['feedback'],f)])
    high_min=vmin-pu*(fbload+maxfb/(series[0]+shunt[0])+4*p['pullup']['comparator_leak_each_A']+ileak)
    posmax=p['largest_analog_rail_abs_V']*r['ground']*(1+f)/(r['rail']*(1-f)+r['ground']*(1+f))
    rawmax=c['raw_max_screen_V']*wr['ground']*(1+f)/(wr['rail']*(1-f)+wr['ground']*(1+f))
    # Prove OK cannot exceed REF while powered: its mandatory divider sink at REF
    # exceeds ALL potentially positive feedback/leak currents. Negative/AC sense
    # nodes are below REF and only help; separately prove these simple envelopes.
    negmax=vmax*n['sense_to_ground']*(1+f)/(n['clamp_to_sense']*(1-f)+n['sense_to_ground']*(1+f))
    acmax=(c['envelope_max_screen_V']/(ar['sense_top']*(1-af))+maxfb/(ar['feedback']*(1-af))+vmax/(ar['sense_bias']*(1-af))+ib)/(1/(ar['sense_bottom']*(1+af))+1/(ar['sense_top']*(1+af)))
    assert negmax<vmin and acmax<vmin
    injection=max(0,posmax-vmin)/(r['feedback']*(1-f))+max(0,rawmax-vmin)/(wr['feedback']*(1-f))+4e-6+ileak
    sink_at_ref=vmin/(series[1]+shunt[1]);assert sink_at_ref>injection
    logic_min=high_min*shunt[0]/(series[1]+shunt[0])-ileak*series[1]
    logic_max=vmax*shunt[1]/(series[0]+shunt[1])+ileak*series[1]
    low_max=max(p['gate_off_V'])*shunt[1]/(series[0]+shunt[1])+ileak*series[1]
    load=old['reference_load_upper_A']+vmax*(1/(c['reference_bleeder_ohm']*(1-p['reference_bleeder_fraction']))-1/(p['reference_bleeder_ohm']*(1-p['reference_bleeder_fraction'])))+vmax/((ar['reference_top']+ar['reference_bottom'])*(1-af))+vmax/(ar['sense_bias']*(1-af))+6*ib
    # Full REF pullup current already bounds all low-state load downstream of OK.
    sinkmax=vmax/(p['pullup']['ohm']*(1-p['pullup']['fraction']))+posmax/(r['feedback']*(1-f))+vmax/(n['feedback']*(1-f))+acmax/(ar['feedback']*(1-af))+rawmax/(wr['feedback']*(1-f))+5e-6
    passive=[passive_off(c,p,a,w,rs,rg) for rs,rg in itertools.product(series,shunt)]
    offmax=max(row['nodes_V']['LOGIC'] for row in passive)
    # Timing capacitor series input resistance changes effective thresholds by ±Iin*Rs.
    # Enclose independently of the existing total timer leakage for a conservative budget.
    timer=[]
    rf=d['resistor_fraction'];cf=d['capacitor_total_fraction_allocation'];timer_series=[c['timer_series_ohm']*(1-it),c['timer_series_ohm']*(1+it)];delta=ileak*timer_series[1]
    input_settle=10*timer_series[1]*c['hc_input_cap_allocation_F']
    for v,charge,dis,cap,leak,sat in itertools.product(d['supply_V'],[d['charge_resistor_ohm']*(1-rf),d['charge_resistor_ohm']*(1+rf)],[d['discharge_resistor_ohm']*(1-rf),d['discharge_resistor_ohm']*(1+rf)],[d['capacitor_F']*(1-cf),d['capacitor_F']*(1+cf)],d['net_delay_leakage_A'],d['saturation_allocation_V']):
        healthy,rh=equilibrium(v,charge,dis,leak,sat,False);fault,rd=equilibrium(v,charge,dis,leak,sat,True)
        for rise,fall in itertools.product([min(d['threshold_rise_V'])-delta,max(d['threshold_rise_V'])+delta],[min(d['threshold_fall_V'])-delta,max(d['threshold_fall_V'])+delta]):
            if fall>=rise:continue
            release=crossing(fault,healthy,rh,cap,rise);discharge=crossing(healthy,fault,rd,cap,fall)+input_settle;after=advance(healthy,fault,rd,cap,.002-input_settle)
            hold=crossing(after,healthy,rh,cap,rise) if after<=fall else 0
            assert all(x is not None for x in [release,discharge,hold])
            timer.append({'release_s':release,'discharge_s':discharge,'hold_after_2ms_s':hold,'healthy_V':healthy,'v5':v,'charge_ohm':charge,'discharge_ohm':dis,'cap_F':cap,'leakage_A':leak,'saturation_V':sat,'rise_V':rise,'fall_V':fall,'healthy_delay_V':healthy,'fault_delay_V':fault})
    premax=pre['value_ohm']*(1+pre['initial_tolerance_fraction']+max(abs(t-pre['reference_temperature_C']) for t in pre['screen_temperature_C'])*pre['tcr_per_C']+pre['environmental_allowance_fraction'])+pre['environmental_allowance_absolute_ohm']
    # Zero-drop input clamp bound, assuming only these newly examined injection paths.
    inj_rail=vmax/series[0];inj_timer=max(t['healthy_V'] for t in timer)/timer_series[0];phantom=(inj_rail+inj_timer)*premax
    checks={'loaded_RAIL_OK_retains_existing_feedback_envelope':high_min>=min(p['gate_on_assumed_V']),'logic_high':logic_min>c['logic_high_threshold_allocation_V'],'logic_low':low_max<c['logic_low_threshold_allocation_V'],'powered_input_below_min_logic_supply':logic_max<min(p['logic_supply_V']),'passive_reference_off_low':offmax<c['logic_low_threshold_allocation_V'],'reference_below10mA':load<.01,'collector_below4mA':sinkmax<.004,'timer_release50ms_to1s':min(t['release_s'] for t in timer)>=.05 and max(t['release_s'] for t in timer)+input_settle<=1,'timer_discharge2ms':max(t['discharge_s'] for t in timer)<.002,'full2ms_pulse_retains50ms_hold':min(t['hold_after_2ms_s'] for t in timer)>=.05,'each_new_input_injection_below20mA':max(inj_rail,inj_timer)<.02,'new_paths_phantom_below_065V_screen':phantom<c['combined_injection_screen_V']}
    report={'qualified':False,'native_adopted':False,'checks':checks,'summary':{'rail_ok_high_min_V':high_min,'logic_high_min_V':logic_min,'logic_max_V':logic_max,'logic_low_max_V':low_max,'passive_ref_off_logic_max_V':offmax,'reference_load_upper_A':load,'comparator_sink_upper_A':sinkmax,'new_paths_phantom_5V_upper_V':phantom,'new_injection_current_A':{'reference_input':inj_rail,'charged_delay_input':inj_timer},'preload_upper_ohm':premax,'input_settling_allocation_s':input_settle,'rejected_10k_timer_phantom_5V_upper_V':(inj_rail+max(t['healthy_V'] for t in timer)/series[0])*premax,'timer_release_range_s':[min(t['release_s'] for t in timer),max(t['release_s'] for t in timer)+input_settle],'minimum_2ms_fault_hold_s':min(t['hold_after_2ms_s'] for t in timer),'timer_corners':len(timer)},'upper_feedback_proof':{'maximum_positive_injection_at_REF_A':injection,'minimum_interface_sink_at_REF_A':sink_at_ref,'negative_sense_max_V':negmax,'ac_sense_max_V':acmax},'passive_off_cases':passive,'timer_cases':timer,'limitations':c['limits'],'native_sha256':json.loads((BASE/'results/fast-clamp/screen.json').read_text())['native_sha256'],'inputs':{str((BASE/n).resolve().relative_to(BASE.parent)):sha(BASE/n) for n in names}}
    # Native charged input capacitors have no series current limiter at the IC pin.
    native_path=BASE.parent/'reverb-600/circuit.json';components=json.loads(native_path.read_text())['components'];hazards=[]
    for ic in components:
        if ic['reference']!='U1' or ic.get('unit',0)==7:continue
        pin=str(2*ic['unit']-1) if ic['unit']<=3 else {4:'9',5:'11',6:'13'}[ic['unit']]
        net=ic['pins'].get(pin)
        if net in [None,'GND']:continue
        for component in components:
            if component['reference'].startswith('C') and net in component['pins'].values():hazards.append({'input':f"U1.{pin}",'net':net,'capacitor':component['reference'],'value':component['value'],'series_input_limit_present':False})
    report['native_direct_capacitor_inputs']=hazards
    report['whole_logic_power_sequence_qualified']=False
    report['new_interface_fault_delay_allocation_s']=10*series[1]*c['hc_input_cap_allocation_F']
    report['prior_brownout_margin_after_added_input_allocation_s']=fast['summary']['minimum_conditional_reserve_s']-report['new_interface_fault_delay_allocation_s']
    report['inputs'][str(Path(__file__).relative_to(BASE.parent))]=sha(Path(__file__))
    for name,h in report['native_sha256'].items():assert sha(BASE.parent/name)==h,name
    (DEST/'screen.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'checks':checks,'summary':report['summary']},indent=2))
if __name__=='__main__':main()
