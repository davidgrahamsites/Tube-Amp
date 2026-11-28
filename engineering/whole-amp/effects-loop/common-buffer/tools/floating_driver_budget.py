"""CB-015. DC boundaries for the local source-referenced gate supply."""
import itertools
import json

from pathlib import Path


def limits(reference,upper,lower,input_current):
    stack=[v*(1+upper*a/(lower*b))+i*upper*a for v,a,b,i in itertools.product(
        reference,(.999,1.001),(.999,1.001),(-input_current,input_current))]
    return [min(stack),max(stack)]


def main():
    # Independent 0.1% resistor errors. Check feedback pin current with both signs.
    output=limits((1.193*.98,1.193*1.02),141e3,10e3,.1e-6)
    # TPS3701 INA descending 397..403 mV; ascending 400..413 mV.
    fall=limits((.397,.403),402e3,10e3,25e-9)
    rise=limits((.400,.413),402e3,10e3,25e-9)
    low_hold_V=17.5
    result=dict(output_V=output,regulator_PG_fall_V=[.83*output[0],.93*output[1]],separate_trip_fall_V=fall,
                separate_trip_rise_V=rise,raw_preload_mA=24/4300*1000,raw_preload_W=24**2/4300,
                assumed_held_load_mA=10,assumed_effective_C_uF=80,
                ms_to_16V=80*(low_hold_V-16)/10,ms_to_earliest_trip=80*(low_hold_V-fall[1])/10,
                rail_V_after_3p01ms=low_hold_V-10*3.01/80,source='TPS7A16 Rev F, TPS3701 Rev C, Murata MEJ1 L01',
                boundary='DC corners and constant-current charge balance. Input reverse discharge, regulator fault and propagation need a hardware circuit.')
    assert 17.5<output[0]<output[1]<18.5 and 16<fall[0]<fall[1]<17.5 and rise[1]<17.5
    target=Path(__file__).resolve().parents[1]/'results/floating-driver-budget.json'
    target.write_text(json.dumps(result,indent=1)+'\n')
    print(result)


if __name__=='__main__':
    main()
