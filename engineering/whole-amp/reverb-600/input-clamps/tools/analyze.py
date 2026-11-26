"""Pointwise rail-current barrier, independent of transient simulation."""
from pathlib import Path
import hashlib
import json

M=Path(__file__).resolve().parents[1];ROOT=M.parents[3]

def source():
    c=json.loads((M/'contract.json').read_text());p=M.parent/'circuit.json'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==c['circuit_sha256']
    rows=json.loads(p.read_text())['components'];r={x['reference']:x for x in rows}
    expected={'R601':('1M',{'1':'IN_AC','2':'SEND_IN'}),'R602':('100k',{'1':'SEND_IN','2':'GND'}),'C601':('100n',{'1':'FX_RETURN','2':'IN_AC'}),'D601':('1N4148',{'1':'+15V','2':'SEND_IN'}),'D602':('1N4148',{'1':'SEND_IN','2':'-15V'})}
    for ref,(value,pins) in expected.items():assert r[ref]['value']==value and r[ref]['pins']==pins,ref
    return c,r

def main():
    c,r=source();e=c['terminal_envelope'];v=e['absolute_V'];t=e['resistor_fraction']
    r1=1e6*(1-t);r2=1e5*(1+t);rows=[]
    # Zero forward drop and low input-series/high shunt/rail-load resistances
    # maximize rail injection. R602 remains a guaranteed current sink.
    # Additional output-interface injection is a separately declared allocation.
    for nominal in c['comparison_rail_load_ohm']:
        rb=nominal*(1+t) if nominal else None
        den=1+r1/r2+(r1/rb if rb else 0)
        limit=max((v+e['output_clamp_injection_allocation_A']*r1)/den,e['output_clamp_injection_allocation_A']*rb) if rb else None
        inj15=max(0,(v-15)/r1-15/r2)+e['output_clamp_injection_allocation_A']
        sink15=15/rb if rb else 0
        rows.append({'nominal_rail_load_ohm':nominal,'maximum_equilibrium_magnitude_V':limit,
                     'two_rail_span_bound_V':2*max(15,limit) if limit is not None else None,'maximum_input_clamp_A':v/r1,
                     'injection_at_15V_A':inj15,'minimum_sink_at_15V_A':sink15,
                     'margin_at_15V_A':sink15-inj15,'holds_15V_without_regulator_sink':sink15>=inj15,
                     'less_than_36V_total':limit is not None and 2*max(15,limit)<36})
    selected=next(x for x in rows if x['nominal_rail_load_ohm']==10000)
    assert not rows[0]['holds_15V_without_regulator_sink'] and not rows[0]['less_than_36V_total']
    assert selected['holds_15V_without_regulator_sink'] and selected['less_than_36V_total']
    assert v/r1<e['input_absmax_A']
    out={'comparison':rows,'selected_10k_max_power_at_18V_W':18**2/(10000*(1-t)),
         'selected_MF0207_power_allowance_at_100C_W':.6*(155-100)/(155-70),
         'R601_max_power_upper_W':v*v/r1,'R601_selected_working_rating_V':350,
         'R601_source_metadata_minimum_V':250,'R601_metadata_needs_exact_part_sync':True,
         'isolated_charge_100n_plus20percent_times313V_C':120e-9*v,
         'single_pulse_rail_rise_upper_V':120e-9*v/e['rail_capacitor_min_F'],
         'source_sha256':c['circuit_sha256'],'scope':'Sufficient pointwise rail-current barrier under declared bounds; no minimum IC load credited',
         'hardware_qualified':False,'native_correction_integrated':False}
    (M/'results/analytic.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':main()
