"""Screen shared heater-reference feasibility from all native tube cathode nodes."""
from pathlib import Path
import hashlib, itertools, json, math, sys
M=Path(__file__).resolve().parents[1]
ROOT=M.parents[2]
sys.path.insert(0,str(ROOT/'engineering/whole-amp/effects-loop/tools'))
sys.path.insert(0,str(ROOT/'engineering/whole-amp/tools'))
import fixture
from spice_runtime import load,cmd,vector,logs

def main():
    c=json.loads((M/'interface-contract.json').read_text())
    inputs={c['source']:c['source_sha256'],**c['input_sha256'],**c['native_sha256']}
    for p,h in inputs.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    source=json.loads((ROOT/c['source']).read_text())['components']
    for ref,nodes in c['cathode_nodes'].items():
        parts=[p for p in source if p['reference']==ref and not p['sheet']=='06_heaters']
        actual={p['pins'][k] for p in parts for k in ['3','8']
                if k in p['pins'] and (not ref in ['V5','V6'] or k=='8')}
        assert actual==set(nodes),(ref,actual,nodes)
    # Explicitly verify that all six packages still share the same two heater nets.
    for ref in c['cathode_nodes']:
        p=next(p for p in source if p['reference']==ref and p['sheet']=='06_heaters')
        assert set(p['pins'].values())=={'HEAT_A','HEAT_B'},ref
    fhi=(1+c['midpoint_tolerance_fraction'])*(1+c['midpoint_extra_drift_allocation'])
    flo=(1-c['midpoint_tolerance_fraction'])*(1-c['midpoint_extra_drift_allocation'])
    heater_peak=c['heater_rms_max_V']*math.sqrt(2)*fhi/(fhi+flo)
    limits=json.loads((ROOT/c['tube_limit_source']).read_text())['references']
    uk={ref:next(t['heater_cathode_limit_V'] for t in limits if t['type']==('JJ EL34' if ref in ['V5','V6'] else 'JJ ECC83S')) for ref in c['cathode_nodes']}
    def windows(nodes):
        out={}
        for group,refs in [('all_six',list(c['cathode_nodes'])),('preamps',['V1','V2','V3','V4']),('power',['V5','V6'])]:
            lo=max(nodes[n]['maximum_V']-uk[ref]+heater_peak for ref in refs for n in c['cathode_nodes'][ref])
            hi=min(nodes[n]['minimum_V']+uk[ref]-heater_peak for ref in refs for n in c['cathode_nodes'][ref])
            out[group]={'minimum_reference_V':lo,'maximum_reference_V':hi,'available_span_V':hi-lo,'nonempty':lo<=hi}
        return out
    results=[]
    def run(supply,channel,amp,gain,stop,start,step,kind):
        deck,inventory=fixture.deck(channel=channel,supply=supply,amp=amp,gain=gain,
                                    freq=c['frequency_Hz'],guard_pentode_power=True)
        names=sorted({n for nodes in c['cathode_nodes'].values() for n in nodes})
        deck=deck.replace('.end\n','.save '+' '.join(f'v({n})' for n in names)+'\n.end\n')
        load(deck);cmd(f'tran {step} {stop} {start} {step}')
        times=vector('time');assert math.isclose(times[-1],stop,abs_tol=1e-9),(kind,supply,channel,times[-1])
        assert min(times)>=start-1e-9 and len(times)>100
        nodes={n:{'minimum_V':min(vector('v('+n+')')),'maximum_V':max(vector('v('+n+')'))} for n in names}
        row={'kind':kind,'early_supply_V':supply,'pre_supply_V':supply+35,'screen_supply_V':380,
             'channel':channel,'input_peak_V':amp,'gain_fraction':gain,'stop_s':stop,
             'measure_start_s':start,'max_step_s':step,'points':len(times),'nodes':nodes,
             'windows':windows(nodes),'deck_sha256':hashlib.sha256(deck.encode()).hexdigest(),
             'source_parts':inventory}
        results.append(row);cmd('destroy all')
    try:
        for supply,channel,amp,gain in itertools.product(c['early_supply_V'],c['channels'],c['input_peak_V'],c['gain_fractions']):
            run(supply,channel,amp,gain,c['stop_s'],c['measure_start_s'],c['max_step_s'],'base')
        for t in c['refinement_cases']:
            run(t['early_supply_V'],t['channel'],t['input_peak_V'],t['gain_fraction'],c['refinement_stop_s'],c['refinement_measure_start_s'],c['refinement_max_step_s'],'extended_refinement')
    finally:(M/'results/interface-simulator.log').write_text('\n'.join(logs)+'\n')
    for p,h in inputs.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    rhigh=(1+c['reference_divider_initial_tolerance'])*(1+c['reference_divider_drift_allocation'])
    rtop,rbottom=c['reference_divider_ohm']
    dc_best=1/(1/rtop+1/rbottom)+c['midpoint_resistor_ohm']/2
    dc_worst=1/(1/(rtop*rhigh)+1/(rbottom*rhigh))+c['midpoint_resistor_ohm']*fhi/2
    bad=[r for r in results if not r['windows']['all_six']['nonempty']]
    comparisons=[]
    for r in results:
        if r['kind']!='extended_refinement':continue
        b=next(b for b in results if b['kind']=='base' and all(b[k]==r[k] for k in ['early_supply_V','channel','input_peak_V','gain_fraction']))
        delta=abs(r['nodes']['DR_CF']['maximum_V']-b['nodes']['DR_CF']['maximum_V'])
        comparisons.append({'early_supply_V':r['early_supply_V'],'cathode_peak_delta_V':delta,
            'both_shared_windows_fail':not b['windows']['all_six']['nonempty'] and not r['windows']['all_six']['nonempty']})
    # The shared window inequality independently compares the required cathode separation.
    for r in results:
        required=r['nodes']['DR_CF']['maximum_V']-min(r['nodes'][n]['minimum_V'] for n in ['K_A','K_B'])+2*heater_peak
        if required>280:assert not r['windows']['all_six']['nonempty']
    result={'completed_cases':len(results),'shared_reference_infeasible_cases':len(bad),
        'heater_endpoint_peak_bound_V':heater_peak,'stiff_rail_nominal_reference_resistance_ohm':dc_best,
        'stiff_rail_corner_reference_resistance_ohm':dc_worst,'EL34_limit_ohm':20000,
        'current_reference_resistance_pass':dc_worst<=20000,'refinement_comparisons':comparisons,
        'cases':results,'native_changes':False,'qualified':False,'input_sha256':inputs,
        'contract_sha256':hashlib.sha256((M/'interface-contract.json').read_bytes()).hexdigest(),
        'factory_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (M/'results/interface-screen.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['cases','input_sha256']},indent=2))

if __name__=='__main__':main()
