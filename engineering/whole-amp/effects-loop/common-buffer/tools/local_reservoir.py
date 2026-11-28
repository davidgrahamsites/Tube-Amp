"""CB-011. An independently wired local film capacitor survives a disconnected bulk branch."""
from itertools import product
import json
from unittest.mock import patch

import cutoff_guard_faults as tests
import cutoff_guard_model as parts
import low_line_rail as rail
from low_line_cutoff import closed_form

# Two equal capacitors. Service and temperature allowance is additional to initial tolerance.
FILM=47.
CMIN=FILM*.95*.95
CMAX=2*FILM*1.05*1.05


def thresholds():
    # Two 80.6k and two 82k in series. Keep CB-007 independent reference and comparator allowances.
    values=[]
    for ref,top,bottom,offset,bias in product((.991,1.009),(.996,1.004),(.996,1.004),(-.004,.004),(-62.5e-9,62.5e-9)):
        rt=325200*top
        values.append((2.5*ref+offset)*(1+rt/(2490*bottom))+bias*rt)
    return min(values),max(values)


def main():
    lo,hi=thresholds()
    assert lo>320
    # The 10 ms interval includes detection, latch and disconnection.
    with patch.object(tests,'TRIP_HI',hi):
        faults=[tests.running_short('local film only',parts.COLD_HIGH,raw,cap=CMIN,guard_delay=.0005)
                for raw in (440,550)]
    starts=[]
    # Keep original four electrolytic leakages as a conservative charge-load allowance.
    with patch.object(rail,'CAP_NOM',CMAX/(4*1.2)):
        for raw in (340,390,440):
            # Two maximum diode drops plus 1 V guard drop included all the way through startup.
            with patch.object(rail,'VBE_ONSET_HOT',.02673*rail.CAND['sense']*1.01):
                starts.append(dict(rail.startup(rail.CAND,raw-5.), applied_raw_V=raw, diode_and_guard_allowance_V=5.))
    ma=48.12
    cases=[]
    for raw,delay in product((440,550),(.002,.01)):
        cases.append(dict(raw_V=raw,total_delay_ms=delay*1000,
            guard_present_V=hi+ma*delay*1000/CMIN,
            guard_bypassed_V=closed_form(raw,855,CMIN*1e-6,delay,start=hi)))
    result=dict(mpn='TDK B32776M4476J000',quantity=2,voltage_V=450,nominal_uF=47,
        sourcing='TDK product catalog, exact code, ±5%, 28 mm body width, 42.5 mm height. Confirm the land pattern in the mechanical drawing.',
        source='https://www.tdk-electronics.tdk.com/en/3191480/products/product-catalog/film-capacitors/capacitors-for-dc-link/search-results-deltacap-capacitors?so=%7B%22orderingCode%22%3A%22B32776M%2A%2A%22%7D',
        wiring='Keep one film directly across the PA supply pins and ground, no detachable bulk connector in its loop; '
               'give the other branch its own supply and return. Either capacitor may open. Physical pin inductance is unmodeled.',
        trip_range_V=[lo,hi],cap_one_survivor_min_uF=CMIN,full_max_uF=CMAX,
        capacitor_max_energy_J=.5*CMAX*1e-6*350**2,guard_cutoff=cases,spice=faults,starts=starts,
        all_caps_absent='Two independent failures or assembly error; inhibit operation until a capacitance/continuity check at the PA pins passes.',
        dual_failure='Loss of current guard plus a 10ms late independent disconnect exceeds the PA absolute maximum.',
        primary_guard_required=True)
    assert all(c['guard_present_V']<350 for c in cases)
    assert all(c['guard_bypassed_V']<350 for c in cases if c['total_delay_ms']==2)
    assert all(r['meets_CB007_timeouts'] for r in starts)
    p=parts.MODULE/'results/local-reservoir.json';p.write_text(json.dumps(result,indent=1)+'\n')
    print(lo,hi,CMIN,CMAX,cases,flush=True)


if __name__=='__main__':
    main()
