"""HD-011 conservative arithmetic; allocated bounds are not part qualification."""
import copy,json
import detector_candidate as d
M=d.M

def calculate(c):
    m=c['monitor'];rc=m['feed_each_ohm']*m['feed_count'];rlo=rc*(1-m['feed_total_fraction']);rhi=rc*(1+m['feed_total_fraction']);vlo,vhi=m['allocated_V'];ilo=(min(m['input_V'])-vhi)/rhi;ihi=(max(m['input_V'])-vlo)/rlo
    ledlo=(vlo-m['LED_count']*max(m['LED_VF_allocation_V'])-m['VOL_allocation_V'])/(m['LED_resistor_ohm']*(1+m['LED_resistor_fraction']))
    ledhi=(vhi-m['LED_count']*min(m['LED_VF_allocation_V']))/(m['LED_resistor_ohm']*(1-m['LED_resistor_fraction']))
    # Deliberately sum non-simultaneous worst loads to retain a conservative budget.
    fixed=m['comparator_IQ_max_A']+m['reference_IQ_EN_max_A']+m['reference_load_allocation_A']+vhi/(m['pullup_ohm']*.99)+vhi/((m['feedback_upper_ohm']+m['feedback_lower_ohm'])*.99)
    old=json.loads((M/'detector-contract.json').read_text());q=copy.deepcopy(old);q['reference']['source_load_mA']=m['reference_load_allocation_A']*1000
    pose=(old['comparator']['input_abs_A']+m['off_output_leakage_allocation_A']+m['board_leakage_allocation_A'])*m['reference_isolation_ohm']*(1+m['reference_isolation_fraction'])
    q['comparator']['offset_abs_V']+=pose;b=d.budget(q)
    reset=(m['VOL_allocation_V']+q['comparator']['offset_abs_V'])*(1+old['divider_top_each_ohm']*old['divider_top_count']*(1+old['resistor_total_fraction'])/(old['divider_bottom_ohm']*(1-old['resistor_total_fraction'])))+(old['comparator']['input_abs_A']+old['comparator']['board_leakage_allocation_A'])*old['divider_top_each_ohm']*old['divider_top_count']*(1+old['resistor_total_fraction'])
    power=vhi*ihi
    return dict(feed_min_A=ilo,feed_max_A=ihi,LED_min_A=ledlo,LED_max_A=ledhi,fixed_load_bound_A=fixed,shunt_reserve_min_A=ilo-fixed-ledhi,shunt_power_upper_W=power,shunt_temperature_sensitivity_C=m['ambient_assumption_C']+power*m['thermal_resistance_sensitivity_C_per_W'],feed_each_power_upper_W=ihi**2*m['feed_each_ohm']*(1+m['feed_total_fraction']),positive_input_error_allocation_V=pose,trip_min_V=b['minimum_trip_V'],trip_max_V=b['maximum_trip_V'],reset_upper_allocation_V=reset,qualified=False)
if __name__=='__main__':
 c=json.loads((M/'monitor-contract.json').read_text());a=calculate(c);(M/'results/monitor-budget.json').write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a,indent=2))
