"""Exhaustive independent endpoint corners of a candidate relay-inhibit divider.

Linear nodal equations, not a substitute comparator SPICE model. No CAD writes.
"""
import hashlib
import itertools
import json
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
C=json.loads((BASE/'rail-monitor-contract.json').read_text())

def threshold(kind,r,v5,offset,ip,im,gate):
    if kind=='positive':
        ref=(v5/r['ref_top']+im)/(1/r['ref_top']+1/r['ref_bottom'])
        target=ref+offset
        return r['rail']*(target*(1/r['rail']+1/r['ground']+1/r['feedback'])-gate/r['feedback']-ip)
    ref=(v5/r['ref_top']+gate/r['feedback']+ip)/(1/r['ref_top']+1/r['ref_bottom']+1/r['feedback'])
    sense=ref+offset
    clamp=sense*(1+r['clamp_to_sense']/r['sense_to_ground'])-im*r['clamp_to_sense']
    return r['rail_to_clamp']*(clamp*(1/r['ref_to_clamp']+1/r['rail_to_clamp']+1/r['clamp_to_sense'])-v5/r['ref_to_clamp']-sense/r['clamp_to_sense'])

def corners(kind):
    nominal=C[kind+'_resistors_ohm']; names=list(nominal)
    lo=None;hi=None;minimum_hyst=None;count=0
    ranges={'enable':[],'disable':[]}
    for factors in itertools.product([1-C['resistor_fraction'],1+C['resistor_fraction']],repeat=len(names)):
        r={k:nominal[k]*f for k,f in zip(names,factors)}
        for v5,offset,ip,im in itertools.product(C['reference_V'],C['offset_V'],C['input_current_A'],C['input_current_A']):
            values={}
            for state,gates in [('enable',C['gate_off_V']),('disable',C['gate_on_assumed_V'])]:
                values[state]=[]
                for gate in gates:
                    voltage=threshold(kind,r,v5,offset,ip,im,gate)
                    absolute=voltage if kind=='positive' else -voltage
                    case=dict(state=state,rail_threshold_V=voltage,abs_threshold_V=absolute,resistors_ohm=r,v5=v5,offset_V=offset,ip_A=ip,im_A=im,gate_V=gate)
                    ranges[state].append(absolute);values[state].append(absolute);count+=1
                    if lo is None or absolute<lo['abs_threshold_V']:lo=case
                    if hi is None or absolute>hi['abs_threshold_V']:hi=case
            # Same manufactured resistors, offset and bias at both switching states.
            hyst=min(values['enable'])-max(values['disable'])
            minimum_hyst=hyst if minimum_hyst is None else min(minimum_hyst,hyst)
    return dict(corners=count,nominal_enable_V=threshold(kind,nominal,5,0,0,0,.2),nominal_disable_V=threshold(kind,nominal,5,0,0,0,4.75),abs_ranges_V={k:[min(v),max(v)] for k,v in ranges.items()},minimum_same_corner_hysteresis_V=minimum_hyst,lowest_case=lo,highest_case=hi)

def main():
    results={k:corners(k) for k in ['positive','negative']}
    r=C['negative_resistors_ohm'];tol=C['resistor_fraction']
    divider_max=r['sense_to_ground']*(1+tol)/(r['sense_to_ground']*(1+tol)+r['clamp_to_sense']*(1-tol))
    clamp_input_bound=C['allocated_negative_clamp_max_V']*divider_max + max(abs(i) for i in C['input_current_A'])*r['sense_to_ground']*(1+tol)
    clamp_current_bound=C['largest_analog_rail_abs_V']/(r['rail_to_clamp']*(1-tol))
    checks=[]
    for k,v in results.items():
        checks.extend([dict(name=k+' enable below 12V',passed=v['abs_ranges_V']['enable'][1]<C['screen']['latest_enable_abs_V']),dict(name=k+' disable above 9V',passed=v['abs_ranges_V']['disable'][0]>C['screen']['earliest_disable_abs_V']),dict(name=k+' hysteresis above allocation',passed=v['minimum_same_corner_hysteresis_V']>C['screen']['minimum_hysteresis_V'])])
    checks.append(dict(name='allocated negative clamp input above -0.3V',passed=clamp_input_bound<.3))
    report=dict(scope='Static independent endpoint budget only; conditional gate/clamp bounds and total resistor drift remain unqualified.',results=results,clamp_input_abs_bound_V=clamp_input_bound,clamp_current_upper_A=clamp_current_bound,checks=checks,passed=sum(c['passed'] for c in checks),total=len(checks),qualified=False,inputs={str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),BASE/'rail-monitor-contract.json']})
    (BASE/'results/rail-monitor-budget.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:{'range':v['abs_ranges_V'],'hysteresis':v['minimum_same_corner_hysteresis_V']} for k,v in results.items()},indent=2))
    print('Checks',report['passed'],'/',report['total'],'clamp input bound',clamp_input_bound)

if __name__=='__main__':main()
