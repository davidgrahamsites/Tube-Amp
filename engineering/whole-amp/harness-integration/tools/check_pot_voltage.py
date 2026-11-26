#!/usr/bin/env python3
"""Source-derived, normalized DC coupling-fault screen; no native edits."""
import csv
import html
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import numpy as np

MODULE=Path(__file__).resolve().parents[1]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def number(v):
    match=re.fullmatch(r'([\d.]+)(M|k|m|u|n|p)?',v.split()[0])
    if not match: raise ValueError(v)
    return float(match[1])*{None:1,'M':1e6,'k':1e3,'m':1e-3,'u':1e-6,'n':1e-9,'p':1e-12}[match[2]]

def solve(edges, shorts, source):
    nodes={n for _,a,b,_ in edges for n in (a,b)}|{'GND',source}
    nodes.update(n for pair in shorts for n in pair)
    parent={n:n for n in nodes}
    def root(n):
        while n!=parent[n]:
            parent[n]=parent[parent[n]]; n=parent[n]
        return n
    def join(a,b): parent[root(a)]=root(b)
    for a,b in shorts: join(a,b)
    for _,a,b,r in edges:
        if r==0: join(a,b)
    assert root(source)!=root('GND'), 'Ideal source short: model must include source impedance'
    fixed={root('GND'):0.,root(source):1.}
    unknown=sorted({root(n) for n in nodes}-fixed.keys())
    pos={n:i for i,n in enumerate(unknown)}
    matrix=np.zeros((len(unknown),len(unknown)));rhs=np.zeros(len(unknown))
    branches=[(name,root(a),root(b),r) for name,a,b,r in edges if r>0 and root(a)!=root(b)]
    for _,a,b,r in branches:
        for p,q in ((a,b),(b,a)):
            if p in pos:
                matrix[pos[p],pos[p]]+=1/r
                if q in pos: matrix[pos[p],pos[q]]-=1/r
                else: rhs[pos[p]]+=fixed[q]/r
    values={**fixed,**dict(zip(unknown,np.linalg.solve(matrix,rhs)))}
    currents={n:0. for n in values};power={name:0. for name,*_ in edges}
    for name,a,b,r in branches:
        current=(values[a]-values[b])/r
        currents[a]+=current;currents[b]-=current
        power[name]=current*current*r
    residual=max([abs(currents[n]) for n in unknown] or [0.])
    supplied=currents[root(source)]
    energy_error=abs(sum(power.values())-supplied)
    assert residual<1e-11 and energy_error<1e-11
    assert all(-1e-9 <= v <= 1+1e-9 for v in values.values())
    return {n:float(values[root(n)]) for n in nodes},power,residual,energy_error

def main():
    sp=MODULE/'voltage-screen.json';spec=json.loads(sp.read_text());cp=MODULE/spec['circuit']
    assert spec['normalization_v']==1.0
    components=json.loads(cp.read_text())['components']
    byref={c['reference']:c for c in components if c['reference'].startswith(('R','C'))}
    controls=[]
    # Analytical divider, open capacitor boundary, and a zero-ohm wiper endpoint.
    for label,edges,shorts,expected in [
        ('divider',[('a','S','N',100e3),('b','N','GND',1e6)],[],10/11),
        ('open_capacitor',[('a','S','HOT',100e3),('b','N','GND',1e6)],[],0),
        ('shorted_capacitor',[('a','S','HOT',100e3),('b','N','GND',1e6)],[('HOT','N')],10/11),
        ('zero_endpoint',[('a','S','N',100e3),('b','N','GND',0)],[],0)]:
        v,_,_,_=solve(edges,shorts,'S');assert abs(v['N']-expected)<1e-12
        controls.append({'case':label,'calculated':v['N'],'analytic':expected})
    try: solve([('a','S','GND',0)],[],'S')
    except AssertionError: controls.append({'case':'ideal_source_short','rejected':True})
    else: raise AssertionError('A hard short was accepted')
    summaries=[];rows=[];max_kcl=max_energy=0.;cases=0
    for group in spec['groups']:
        parts=[byref[ref] for ref in group['parts']]
        pots=[c for c in parts if c['reference'].startswith('RV')]
        for fault in [None,*group['faults']]:
            # Each capacitor endpoint comes from the current circuit, never a copied netlist.
            short=[] if fault is None else [tuple(byref[fault]['pins'][p] for p in ('1','2'))]
            maxima={p['reference']:{'voltage_ratio':-1.,'power_w_per_v2':-1.} for p in pots}
            for mode,links in group['modes'].items():
                for fractions in itertools.product(spec['electrical_wiper_fractions'],repeat=len(pots)):
                    setting=dict(zip([p['reference'] for p in pots],fractions));edges=[]
                    for c in parts:
                        ref=c['reference'];pins=c['pins'];r=number(c['value'])
                        if ref.startswith('RV'):
                            f=setting[ref]
                            edges += [(ref+'A',pins['1'],pins['2'],r*(1-f)),(ref+'B',pins['2'],pins['3'],r*f)]
                        else: edges.append((ref,pins['1'],pins['2'],r))
                    v,power,kcl,energy=solve(edges,short+links,group['supply_node'])
                    cases+=1;max_kcl=max(max_kcl,kcl);max_energy=max(max_energy,energy)
                    for pot in pots:
                        ref=pot['reference'];vs=[v[pot['pins'][str(i)]] for i in (1,2,3)]
                        vr=max(abs(x) for x in vs);pw=power[ref+'A']+power[ref+'B']
                        if fault is None: assert vr<1e-10 and pw<1e-15,(group['id'],ref,vs)
                        record={'mode':mode,'settings':setting,'pin_voltage_ratios':vs}
                        if vr>maxima[ref]['voltage_ratio']:
                            maxima[ref]['voltage_ratio']=vr;maxima[ref]['voltage_case']=record
                        if pw>maxima[ref]['power_w_per_v2']:
                            maxima[ref]['power_w_per_v2']=pw;maxima[ref]['power_case']=record
                        rows.append([group['id'],fault or 'none',mode,json.dumps(setting,sort_keys=True),ref,*vs,pw])
            example=spec['illustrative_source_voltages_v'][group['supply_node']]
            for ref,data in maxima.items():
                data['example_terminal_v']=data['voltage_ratio']*example
                data['example_total_track_w']=data['power_w_per_v2']*example**2
                data['source_v_for_comparison_power']=math.sqrt(spec['comparison_track_power_w']/data['power_w_per_v2']) if data['power_w_per_v2']>1e-15 else None
            summaries.append({'group':group['id'],'fault':fault,'source_node':group['supply_node'],
                              'example_source_v':example,'assumption':group['assumption'],'pots':maxima})
    # Source-derived analytic endpoint checks, independent of nodal assembly.
    gain=next(s for s in summaries if s['fault']=='C8')
    expected=number(byref['RV4']['value'])/(number(byref['R12']['value'])+number(byref['RV4']['value']))
    assert abs(gain['pots']['RV4']['voltage_ratio']-expected)<1e-12
    controls.append({'case':'C8_native_endpoint_divider','calculated':gain['pots']['RV4']['voltage_ratio'],'analytic':expected})
    presence=next(s for s in summaries if s['fault']=='C21')
    expected=1/(1+number(byref['R28']['value'])*sum(1/number(byref[r]['value']) for r in ('R31','R32','RV9')))
    assert abs(presence['pots']['RV9']['voltage_ratio']-expected)<1e-12
    controls.append({'case':'C21_native_parallel_load','calculated':presence['pots']['RV9']['voltage_ratio'],'analytic':expected})
    out=MODULE/'results/pot-voltage-cases.csv'
    with out.open('w') as f:
        writer=csv.writer(f,lineterminator="\n");writer.writerow(['group','shorted_capacitor','mode','electrical_settings','pot','pin1_v_per_v','pin2_v_per_v','pin3_v_per_v','total_track_w_per_v2']);writer.writerows(rows)
    paths=[sp,cp,Path(__file__),MODULE/'connector-contract.json']
    result={'id':spec['id'],'inputs_sha256':{str(p.relative_to(MODULE)) if p.is_relative_to(MODULE) else str(p):sha(p) for p in paths},
            'numpy_version':np.__version__,'cases':cases,'pot_rows':len(rows),'controls':controls,
            'max_kcl_residual_a_per_v':max_kcl,'max_power_balance_error_w_per_v2':max_energy,
            'summaries':summaries,'case_csv_sha256':sha(out),'scope':spec['scope'],
            'evidence_checks_pass':True,'actual_maximum_voltage_qualified':False,
            'pot_rating_qualified':False,'harness_insulation_qualified':False,'native_adoption':False}
    (MODULE/'results/pot-voltage-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    render_report(result, spec)
    print(json.dumps({'cases':cases,'pot_rows':len(rows),'controls':len(controls),'max_kcl':max_kcl,'max_power_error':max_energy,
      'faults':[{'group':s['group'],'fault':s['fault'],'source_v':s['example_source_v'],'pots':{r:{k:round(d[k],6) for k in ('voltage_ratio','example_terminal_v','example_total_track_w')} for r,d in s['pots'].items()}} for s in summaries if s['fault']]},indent=2))


def render_report(result, spec):
    table=[]
    for s in result['summaries']:
        if not s['fault']: continue
        vref=max(s['pots'],key=lambda p:s['pots'][p]['example_terminal_v'])
        pref=max(s['pots'],key=lambda p:s['pots'][p]['example_total_track_w'])
        voltage=s['pots'][vref]['example_terminal_v'];power=s['pots'][pref]['example_total_track_w']
        table.append(f"<tr><td>{s['fault']}</td><td>{html.escape(s['source_node'])}</td><td>{s['example_source_v']:g}</td><td>{vref}: {voltage:.3f}</td><td>{pref}: {power:.6f}</td></tr>")
    loaded='<p>The loaded-tube follow-up has not been regenerated against this linear-screen revision.</p>'
    probe_path=MODULE/'results/pot-fault-probe.json'
    if probe_path.exists():
        probe=json.loads(probe_path.read_text())
        key='engineering/whole-amp/harness-integration/results/pot-voltage-checks.json'
        if probe['inputs_sha256'].get(key)==sha(MODULE/'results/pot-voltage-checks.json'):
            rows=[]
            for c in probe['cases']:
                if c['status']!='completed' or not c['case']['fault']:continue
                r=max(c['pots'],key=lambda ref:c['pots'][ref]['total_track_w'])
                rows.append(f"<tr><td>{c['case']['pre_v']:g}</td><td>{c['case']['fault']}</td><td>{c['voltages']['DR_CF']:.3f}</td><td>{r}: {c['pots'][r]['total_track_w']:.6f}</td></tr>")
            loaded='<p>Twelve generic-tube DC solves completed: three selected settings, each intact and failed, at fixed B_PRE values of 267.11 V and 355 V. They use the desired buffered-loop fixture, a 1 Ω pot-endpoint approximation and a 1 mΩ failed capacitor; they are separate from the native-path linear screen.</p><table><thead><tr><th>B_PRE, V</th><th>Short</th><th>Loaded DR_CF, V</th><th>Largest total pot-track power, W</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table><p>The lower setpoint gives about 0.162 W at RV7 with C17 short; the 355 V reference gives about 0.290 W. These values bracket the 0.25 W comparison but do not establish pass or failure of the exact linear pot. The source is loaded, yet exact tube variation, actual supply, other settings, temperature and wiper/partial-track limits remain open. Do not replace the pot or add capacitors on this comparison alone. See <a href="results/pot-fault-probe.json">paired results</a>, <a href="results/pot-fault-example.cir">example deck</a> and <a href="results/pot-fault-probe.log">solver log</a>.</p>'
    scope=''.join(f"<li><strong>{html.escape(g['id'])}:</strong> {html.escape(g['assumption'])}</li>" for g in spec['groups'])
    text=r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Pot harness DC fault screen</title></head><body><main>
<p class="eyebrow">HI-006 · 26 November 2026 · Conditional electrical screen</p>
<h1>Do not classify every pot lead as low voltage</h1>
<p>Several panel pots sit behind coupling capacitors connected to tube-stage DC. A shorted capacitor can put DC onto their harnesses. The candidate connector and wire ratings do not qualify the pot, its insulated joints or the assembled panel.</p>
<h2>What was checked</h2>
<p>@@CASES@@ nominal linear DC networks cover ten listed capacitor shorts, intact-capacitor controls and electrical wiper fractions 0, 0.5 and 1. Fractions represent resistance division, not shaft angle or audio taper. Resistor values and capacitor endpoints come from the current circuit. Zero-resistance endpoints are joined exactly. The native boards and circuit are not edited.</p>
<p>The model opens intact capacitors at DC and omits leakage, nonlinear tube behavior and signal transients. It is a fault-path screen, not a complete single-fault or safety analysis. It does not establish actual maximum voltages, hot ratings, local track heating or the final buffered effects-path behavior.</p>
<ul>@@SCOPE@@</ul>
<h2>How the calculation scales</h2>
<p>Each source boundary is normalized to 1 V. For a particular setting and fault, the circuit gives terminal coefficient \(\alpha\) and total track coefficient \(\beta\):</p>
<p>\[|V_{\mathrm{terminal}}|=\alpha |V_s|,\qquad P_{\mathrm{track}}=\beta V_s^2.\]</p>
<p>A comparison power \(P_c\) gives \(V_{s,c}=\sqrt{P_c/\beta}\). The 0.25 W comparison comes from an earlier A1M customer-sheet review; it is not an approved rating for every proposed pot. Partial-track and wiper limits require separate evidence.</p>
<p>Example: C8 short, RV4 wiper at ground, first tube open. The actual 100 kΩ feed and 1 MΩ pot give:</p>
<p>\[V_{\mathrm{RV4,1}}=V_{B\_EARLY}\frac{1\,\mathrm{M\Omega}}{100\,\mathrm{k\Omega}+1\,\mathrm{M\Omega}}=0.909091V_{B\_EARLY}.\]</p>
<p>With an illustrative 300 V source, that is 272.727 V DC. This example is not a measured operating point or a qualified supply maximum.</p>
<h2>Conditional examples</h2>
<p>Voltages below are explicit source assumptions: 300 V for B_EARLY and DR_CF, 25 V for PI_TAIL_TOP, and 15 V for REC_OUT. They do not claim that those nodes normally reach those voltages. Voltage and power maxima may occur at different sampled settings. No result establishes a full continuous-setting maximum.</p>
<table><thead><tr><th>Shorted capacitor</th><th>Source boundary</th><th>Example source, V</th><th>Highest pot terminal, V DC</th><th>Largest total pot-track power, W</th></tr></thead><tbody>@@TABLE@@</tbody></table>
<p>In the stiff-source C17 screen, RV7 reaches the 0.25 W comparison at about 184.57 V at DR_CF. This flags a dependency on the actual follower behavior and exact pot rating; it does not prove an operating failure. The real follower's source impedance and fault operating point must be included before adopting a remedy.</p>
<p>C19 can feed DC backward into the dirty controls through the native normalled effects path. Recheck this route when the buffered loop is integrated. C21 exposes presence to the PI return network; it is not a direct B+ connection. C606 exposes the reverb control to its recovery-output boundary; this unloaded-wiper screen does not qualify mute or op-amp faults.</p>
<h2>Loaded-tube follow-up</h2>
@@LOADED@@
<h2>Component decision</h2>
<p><a href="https://www.taiwanalpha.com/downloads?id=104&amp;target=products">Alpha's RV24AF family specification</a> lists 250 V AC maximum operation. Its 500 V AC, one-minute dielectric test is not a continuous operating rating. A DC working limit for the exact supplied variants remains unresolved. The <a href="https://cdnimages.opentip.com/Docs/CED/r-va1ma_specification_sheet.pdf">customer sheet</a> used in the earlier parts review does not close every suffix or taper limit.</p>
<p>Keep the existing pot values and functional blocks. Do not approve lower-voltage wire because normal DC is blocked, and do not claim a 600 V connector protects a lower-rated pot. Resolve the actual source bounds, exact pot DC/track/wiper limits and required fault containment before connector adoption. Compare any added blocking component against frequency response, failure modes and populated fit before changing the circuit.</p>
<h2>Evidence and next action</h2>
<p><a href="results/pot-voltage-checks.json">The result record</a> retains source hashes, settings and normalized maxima; <a href="results/pot-voltage-cases.csv">the case table</a> retains every pot result. Seven analytic and rejection controls pass. All solved networks satisfy current balance and input-power balance within the recorded numerical residuals. Intact-capacitor model controls give zero pot DC; that is not a leakage measurement.</p>
<p>Next: use the selected supply and tube models to bound the flagged source voltages, obtain exact pot limits, and check local track and wiper stress. Electrical insulation and populated fit remain open. This generated report is rebuilt by <code>tools/check_pot_voltage.py</code>; edit the source contract and factory, then regenerate and apply the reader decorator.</p>
<h2>Vocabulary key</h2><dl><dt>Coupling capacitor</dt><dd>A capacitor that passes changing signals while blocking steady DC in normal operation.</dd><dt>DC</dt><dd>A voltage or current component that does not alternate polarity.</dd><dt>Track</dt><dd>The resistive element inside a potentiometer.</dd><dt>Wiper</dt><dd>The moving contact on the track.</dd><dt>Source impedance</dt><dd>The electrical resistance and reactance that limit current from a source.</dd><dt>Stiff source</dt><dd>An ideal source whose voltage does not fall when loaded.</dd><dt>Normalized</dt><dd>Expressed for a unit input so another input can be calculated by scaling.</dd><dt>Dielectric test</dt><dd>A specified insulation test; it does not establish a continuous working voltage.</dd><dt>PI</dt><dd>Phase inverter: the stage that drives the two output tubes with opposite signals.</dd><dt>Normalled path</dt><dd>The jack contact path used when no external plug interrupts it.</dd></dl>
</main></body></html>"""
    for key,val in {'CASES':str(result['cases']),'SCOPE':scope,'TABLE':''.join(table),'LOADED':loaded}.items(): text=text.replace('@@'+key+'@@',val)
    (MODULE/'pot-voltage-review.html').write_text(text+'\n')

if __name__=='__main__':main()
