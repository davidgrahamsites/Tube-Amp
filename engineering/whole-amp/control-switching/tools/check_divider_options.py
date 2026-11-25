"""Bounded divider comparison: independent resistor errors, leakage and threshold.

Does not alter the historical simulation contract or native CAD.
"""
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
from calculate_bounds import reset_bounds

M=Path(__file__).resolve().parents[1];ROOT=M.parents[2]

def bounds(c, reset, drift, absolute):
    dt=max(abs(t-c['reference_temperature_C']) for t in c['resistor_temperature_screen_C'])
    error=c['initial_tolerance']+c['tcr_per_K']*dt+drift
    endpoints=lambda nominal:[nominal*(1-error)-absolute,nominal*(1+error)+absolute]
    tops,bots=endpoints(c['top_ohm']),endpoints(c['bottom_ohm'])
    assert min(tops+bots)>0
    rows=[]
    for top,bot,acc,leak in itertools.product(tops,bots,
        [1-reset['threshold_tolerance'],1+reset['threshold_tolerance']],
        [-reset['sense_leakage_abs_A'],reset['sense_leakage_abs_A']]):
        rows.append([(reset[k]*acc)*(1+top/bot)+leak*top for k in ['fall_threshold_V','rise_threshold_V']])
    lo=min(x[0] for x in rows);hi=max(x[1] for x in rows)
    # Independent monotonic endpoint expression guards enumeration/polarity.
    expected_lo=reset['fall_threshold_V']*(1-reset['threshold_tolerance'])*(1+tops[0]/bots[1])-reset['sense_leakage_abs_A']*tops[0]
    expected_hi=reset['rise_threshold_V']*(1+reset['threshold_tolerance'])*(1+tops[1]/bots[0])+reset['sense_leakage_abs_A']*tops[1]
    assert math.isclose(lo,expected_lo,abs_tol=1e-12) and math.isclose(hi,expected_hi,abs_tol=1e-12)
    margins=[lo-c['logic_window_V'][0],c['logic_window_V'][1]-hi]
    return dict(corners=len(rows),resistor_fractional_error=error,resistor_absolute_error_ohm=absolute,
        falling_min_V=lo,rising_max_V=hi,noise_margins_V=margins,
        meets_proposed_noise_allocation=min(margins)>=c['noise_allocation_V'])

def main():
    p=M/'divider-contract.json';c=json.loads(p.read_text());base=M/c['baseline_contract']
    assert hashlib.sha256(base.read_bytes()).hexdigest()==c['baseline_sha256']
    source=ROOT/c['manufacturer_source'];assert hashlib.sha256(source.read_bytes()).hexdigest()==c['manufacturer_sha256']
    old=json.loads(base.read_text());reset=old['reset_candidate'];solder=c['soldering_drift']
    profiles={'fresh_after_soldering':bounds(c,reset,solder['fraction'],solder['ohm'])}
    for profile in c['endurance_profiles']:
        profiles[profile['id']]=bounds(c,reset,profile['fraction']+solder['fraction'],profile['ohm']+solder['ohm'])
    env=c['combined_environment_screen'];profile=next(x for x in c['endurance_profiles'] if x['id']==env['base_profile'])
    profiles['combined_environment_sensitivity']=bounds(c,reset,profile['fraction']+solder['fraction']+env['added_fraction'],profile['ohm']+solder['ohm']+env['added_ohm'])
    # Compare the unchanged prior result, not a retroactively weakened criterion.
    prior=reset_bounds(old,True)
    prior['meets_proposed_noise_allocation']=min(prior['falling_margin_above_4p5V'],prior['rising_margin_below_supply_min_V'])>=c['noise_allocation_V']
    bad=copy.deepcopy(c);bad['initial_tolerance']=.01
    assert not bounds(bad,reset,0,0)['meets_proposed_noise_allocation']
    assert not prior['meets_proposed_noise_allocation']
    assert profiles['general_8000h']['meets_proposed_noise_allocation']
    assert not profiles['general_225000h']['meets_proposed_noise_allocation']
    # Each resistor's dissipation is below total network input power. Drop the
    # bottom resistance from that bound and add worst possible sense-pin power.
    # This deliberately loose bound is not a thermal qualification.
    minimum_R=c['top_ohm']*(1-profiles['general_225000h']['resistor_fractional_error'])-profiles['general_225000h']['resistor_absolute_error_ohm']
    rail=max(old['logic_supply_V'])
    total_rail_power_bound_W=rail**2/minimum_R+rail*reset['sense_leakage_abs_A']
    result=dict(passed=True,meaning='Arithmetic/source checks passed; candidate has explicit failed margins',
        prior_Yageo_endurance=prior,profiles=profiles,
        conservative_each_resistor_power_bound_W=total_rail_power_bound_W,
        nominal_5V_divider_current_A=5/(c['top_ohm']+c['bottom_ohm']),
        negative_control_rejected='1% initial resistor pair',native_adopted=False,
        purchase_ready=False,supervisor_qualified=False,fabrication_ready=False,
        source_sha256={str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in [p,base,source,Path(__file__)]})
    (M/'results/divider-options.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'},indent=2))

if __name__=='__main__':main()
