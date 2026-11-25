"""Read-only bridge from native audio/supply interfaces to rail-monitor acceptance."""
import hashlib
import json
from pathlib import Path
import sys

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE.parent/'effects-loop/tools'))
from fixture import numeric


def main():
    cp=BASE/'audio-headroom-contract.json'
    c=json.loads(cp.read_text())
    circuit_path=BASE/c['circuit']
    components=json.loads(circuit_path.read_text())['components']
    audio=[x for x in components if x['reference'] in c['audio_amplifier_refs'] and ('1' in x['pins'] or '7' in x['pins'])]
    assert len(audio)==6 and all(x['value']=='OPA2134PA' and '10Vpk' in x['rating'] for x in audio)
    expected={
        'positive':{'C210':'100n','C211':'10u','C610':'100n','C612':'100n','C614':'100n','C616':'47u'},
        'negative':{'C213':'100n','C214':'10u','C611':'100n','C613':'100n','C615':'100n','C617':'47u'}}
    cap_inventory={}
    for side,refs in expected.items():
        rail='+15V' if side=='positive' else '-15V'
        candidates=[x for x in components if x['reference'].startswith('C') and set(x['pins'].values())=={rail,'GND'}]
        assert {x['reference']:x['value'] for x in candidates}==refs, (side,'capacitor inventory changed')
        cap_inventory[side]={x['reference']:numeric(x['value']) for x in candidates}
    source_path=BASE/c['threshold_result'];source=json.loads(source_path.read_text())
    for path,h in source['inputs'].items():assert hashlib.sha256((BASE/path).read_bytes()).hexdigest()==h,path
    load_path=BASE/c['load_contract'];loads=json.loads(load_path.read_text())['loads']
    peak=c['peak_signal_target_V']
    sides={};timing=[];checks=[]
    for side in ['positive','negative']:
        floor=peak+c[side+'_cm_headroom_allocation_V']
        thresholds=source['results'][side]['abs_ranges_V']
        regulated=c['minimum_regulated_rail_magnitude_V'][side]
        cap=sum(cap_inventory[side].values())*(1-c['capacitor_fraction_allocation'])
        sides[side]=dict(target_peak_V=peak,allocated_valid_rail_floor_V=floor,
            existing_disable_range_V=thresholds['disable'],existing_enable_range_V=thresholds['enable'],
            late_warning_margin_to_allocated_floor_V=thresholds['disable'][0]-floor,
            even_ideal_output_rail_margin_V=thresholds['disable'][0]-peak,
            native_nominal_capacitance_F=sum(cap_inventory[side].values()),screen_low_capacitance_F=cap,
            regulated_minimum_V=regulated,available_static_window_V=regulated-floor,
            existing_monitor_supports_full_target=thresholds['disable'][0]>floor)
        future=c[f'hypothetical_future_{side}_warning_floor_V']
        for load in loads:
            current=load['audio_each_rail_A']
            for delay in c['hypothetical_post_warning_delay_s']:
                delta=future-floor
                timing.append(dict(side=side,load=load['name'],current_A=current,
                    hypothetical_warning_V=future,assumed_delay_s=delay,
                    conditional_isolated_cap_hold_s=cap*delta/current,
                    required_effective_cap_F=current*delay/delta,
                    existing_cap_sufficient_in_isolated_screen=cap*delta/current>=delay))
    reference=json.loads((BASE/'rail-monitor-buffered-contract.json').read_text())['reference_V']
    # Ideal zero-offset/no-hysteresis reference-proportional threshold, best possible retune.
    # The absolute ratio argument alone shows whether the reference's spread fits the window.
    spread=reference[1]/reference[0]
    feasibility={side:dict(ideal_low_trip_V=v['allocated_valid_rail_floor_V'],
                          unavoidable_high_trip_V=v['allocated_valid_rail_floor_V']*spread,
                          healthy_minimum_V=v['regulated_minimum_V'],
                          fits_without_offset_hysteresis_or_resistor_errors=v['allocated_valid_rail_floor_V']*spread<=v['regulated_minimum_V'])
                 for side,v in sides.items()}
    checks=[dict(name='native signal/capacitor inventory bound to source',passed=True),
            dict(name='existing positive and negative warning can occur below the 10V ideal output floor',passed=all(v['even_ideal_output_rail_margin_V']<0 for v in sides.values())),
            dict(name='both existing candidates fail retained common-mode headroom allocation',passed=all(not v['existing_monitor_supports_full_target'] for v in sides.values())),
            dict(name='5V reference spread alone prevents positive-rail retune inside allocated window',passed=not feasibility['positive']['fits_without_offset_hysteresis_or_resistor_errors']),
            dict(name='hold-time boundary scales consistently with each inherited load',passed=all(abs(r['required_effective_cap_F']* (r['hypothetical_warning_V']-sides[r['side']]['allocated_valid_rail_floor_V'])-r['current_A']*r['assumed_delay_s'])<1e-14 for r in timing))]
    inputs=[cp,circuit_path,source_path,load_path,Path(__file__),BASE.parent/'effects-loop/tools/fixture.py',BASE/'rail-monitor-buffered-contract.json']
    out=dict(qualified=False,scope=c['job'],native_capacitor_inventory_F=cap_inventory,sides=sides,
        ideal_reference_retune=feasibility,timing_sensitivity=timing,checks=checks,
        limitations=c['limitations'],provenance={str(p.relative_to(BASE.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
    (BASE/'results/audio-headroom-budget.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(sides=sides,ideal_reference_retune=feasibility,checks=checks),indent=2))
    if not all(x['passed'] for x in checks):sys.exit(1)


if __name__=='__main__':main()
