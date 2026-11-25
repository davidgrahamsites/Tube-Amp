"""Threshold, collapse-rate and asynchronous recovery arithmetic.

Reports failing/unqualified engineering gates without fabricating timing maxima.
"""
import hashlib,json
from pathlib import Path
from calculate_bounds import reset_bounds
M=Path(__file__).resolve().parents[1]

def main():
    c=json.loads((M/'contract.json').read_text());q=json.loads((M/'brownout-contract.json').read_text());e=json.loads((M/'edge-contract.json').read_text())
    fresh=reset_bounds(c);life=reset_bounds(c,True);noise=q['threshold_noise_allocation_V']
    margins={k:dict(falling_V=v['falling_margin_above_4p5V'],rising_V=v['rising_margin_below_supply_min_V'],meets_proposed_20mV_allocation=min(v['falling_margin_above_4p5V'],v['rising_margin_below_supply_min_V'])>=noise) for k,v in [('fresh',fresh),('endurance',life)]}
    downstream=2*e['hc14']['propagation_each_max_s']+q['hc74_clear_to_Q_max_s']
    # Unknown supervisor and raw-output delays cannot become zero or typical.
    # These are conditional budgets only, with NO qualified slew-rate result.
    budgets=[]
    for delay in [10e-6,50e-6,100e-6,1e-3]:
        margin=life['falling_margin_above_4p5V']
        budgets.append(dict(assumed_total_supervisor_and_raw_edge_s=delay,post_edge_logic_bound_s=downstream,
          conditional_max_linear_fall_rate_V_per_s=margin/(delay+downstream),with_noise_allocation_has_positive_budget=margin>noise))
    clocks=[dict(offset_s=t,meets_clear_inactive_setup=t>=q['hc74_clear_inactive_setup_s']) for t in q['clock_offsets_after_reset_s']]
    assert clocks[0]['meets_clear_inactive_setup'] is False and clocks[-1]['meets_clear_inactive_setup'] is True
    assert not margins['endurance']['meets_proposed_20mV_allocation']
    # Candidate fixed-threshold alternative rejected using maximum limits,
    # not the ±0.5% typical headline of the TLV803E family.
    tlv=dict(falling_min_V=4.63*.98,rising_max_V=4.63*1.02*1.015)
    assert tlv['rising_max_V']>q['steady_rail_min_V']
    report=dict(computation_completed=True,qualification_pass=False,threshold_margins=margins,
      conditional_collapse_budgets=budgets,maximum_qualified_collapse_rate_V_per_s=None,
      external_clock_recovery_checks=clocks,arbitrary_clock_coincidence_qualified=False,
      explanation='HC74 operates down to 2V, but the adopted gate-drive bounds use 4.5V. Crossing 4.5V first means those bounds no longer prove performance; it does not itself prove physical malfunction.',
      tlv803e_4p63V_alternative=dict(**tlv,adopted=False,reason='Maximum release exceeds 4.75V minimum rail; standard 3-pin packages also lack MR'),
      unresolved=['TPS3808G50 native threshold versus low-rail release','Candidate endurance/noise margin','Missing guaranteed supervisor/raw-output assertion bound','Actual regulator/rail collapse and relay-rail persistence','Reset release versus asynchronous clock setup','Hot CT and board leakage','Removable U3 carrier and full socket capacitance'],
      source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [M/'contract.json',M/'brownout-contract.json',M/'edge-contract.json']},fabrication_ready=False)
    (M/'results/brownout-limits.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
