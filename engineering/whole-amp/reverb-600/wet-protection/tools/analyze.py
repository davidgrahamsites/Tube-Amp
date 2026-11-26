"""Native-value protection budget. Piecewise clamp is a screen, not a vendor model."""
from pathlib import Path
import hashlib
import itertools
import json
import math
import re
import numpy as np

M = Path(__file__).resolve().parents[1]
ROOT = M.parents[3]


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def inputs():
    c = json.loads((M/'contract.json').read_text())
    assert sha(ROOT/c['source']) == c['source_sha256'], 'Native source changed'
    rows = json.loads((ROOT/c['source']).read_text())['components']
    p = {x['reference']: x for x in rows}
    expected = {'R7': ['B_EARLY','CL_P2'], 'R43': ['CLEAN_OUT','GND'],
                'R612': ['FX_RETURN','MIX_OUT'], 'R24': ['MIX_OUT','GND'],
                'R618': ['WET_AC','MIX_OUT'], 'R617': ['WET_AC','GND'],
                'R616': ['OUT_BUF','OUT_AC'], 'C607': ['OUT_AC','WET_AC'],
                'C601': ['FX_RETURN','IN_AC'], 'R601': ['IN_AC','SEND_IN'],
                'R602': ['SEND_IN','GND']}
    values = {}
    for ref, pins in expected.items():
        assert [p[ref]['pins'][str(i)] for i in [1,2]] == pins, ref
        v, suffix = re.fullmatch(r'([\d.]+)([Mkunp]?)', p[ref]['value']).groups()
        values[ref] = float(v)*{'':1,'M':1e6,'k':1e3,'u':1e-6,'n':1e-9,'p':1e-12}[suffix]
    assert any(x['reference']=='K3' and x['unit']==3 and
               x['pins']=={'13':'WET_AC','11':'GND','9':None} for x in rows)
    return c, values


def dc(r, supply, threshold, slope):
    # Analytic Thevenin reduction viewed at WET_AC, capacitors open at DC.
    source = supply*r['R43']/(r['R7']+r['R43'])
    series = 1/(1/r['R7']+1/r['R43']) + r['R612']
    mix_open = source*r['R24']/(series+r['R24'])
    wet_series = 1/(1/series+1/r['R24']) + r['R618']
    wet_open = mix_open*r['R617']/(wet_series+r['R617'])
    resistance = 1/(1/wet_series+1/r['R617'])
    wet = wet_open if threshold is None or wet_open <= threshold else (
        wet_open*slope+threshold*resistance)/(slope+resistance)
    current = 0 if threshold is None else max(0,(wet-threshold)/slope)
    mix = wet + (wet/r['R617']+current)*r['R618']
    fx = mix + (mix/r['R24']+(mix-wet)/r['R618'])*r['R612']
    return dict(wet_V=wet,mix_V=mix,fx_V=fx,clamp_A=current,
                pair_W=wet*current,R618_V=mix-wet,R618_W=(mix-wet)**2/r['R618'])


def ac(r, hz, source_ohm, capacitance, wet_drive, c607):
    # Reduce the unloaded native SEND attenuation branch to a series impedance.
    jw=2j*math.pi*hz
    ydry=1/source_ohm; ymix=1/r['R612']; ywetmix=1/r['R618']
    ywet=1/(r['R616']+1/(jw*c607))
    ysend=1/(r['R601']+r['R602']+1/(jw*r['C601']))
    a=np.array([[ydry+ymix+ysend,-ymix,0],[-ymix,ymix+ywetmix+1/r['R24'],-ywetmix],
                [0,-ywetmix,ywetmix+ywet+1/r['R617']+jw*capacitance]],complex)
    b=np.array([0 if wet_drive else ydry,0,ywet if wet_drive else 0],complex)
    return np.linalg.solve(a,b)


def main():
    c, nominal=inputs(); dcrows=[]; acrows=[]
    refs=['R7','R43','R612','R24','R618','R617']
    tol=c['dc']['resistor_tolerance']
    for signs in itertools.product([-1,1],repeat=len(refs)):
        r=dict(nominal,**{ref:nominal[ref]*(1+sign*tol) for ref,sign in zip(refs,signs)})
        for supply in c['dc']['supply_V']:
            for clamp in [None,*c['candidate']['clamp_threshold_screen_V']]:
                dcrows.append(dict(signs=signs,supply_V=supply,threshold_V=clamp,
                                   **dc(r,supply,clamp,c['candidate']['slope_screen_ohm'])))
    for hz, rs, scale in itertools.product(c['ac']['frequencies_Hz'],c['ac']['source_ohm'],[.9,1.1]):
        for cp in c['candidate']['pair_capacitance_screen_F']:
            dry=ac(nominal,hz,rs,cp,False,nominal['C607']*scale)
            wet=ac(nominal,hz,rs,cp,True,nominal['C607']*scale)
            dry0=ac(nominal,hz,rs,0,False,nominal['C607']*scale)
            wet0=ac(nominal,hz,rs,0,True,nominal['C607']*scale)
            acrows.append(dict(Hz=hz,source_ohm=rs,C607_scale=scale,pair_F=cp,
                wet_peak_bound_V=abs(dry[2])*c['ac']['dry_peak_V']+abs(wet[2])*c['ac']['wet_peak_V'],
                wet_gain_delta_dB=20*math.log10(abs(wet[1]/wet0[1])),
                dry_gain_delta_dB=20*math.log10(abs(dry[1]/dry0[1]))))
    clamped=[r for r in dcrows if r['threshold_V'] is not None]
    vmax=max(r['wet_V'] for r in clamped)
    rmin=nominal['R616']*(1-c['contact']['series_resistor_tolerance'])
    cmax=nominal['C607']*(1+c['contact']['capacitor_tolerance'])
    # Initial contact current includes a bounded dry-feed branch as well as capacitor discharge.
    dry_i=c['dc']['supply_V'][-1]/(nominal['R618']*(1-tol))
    contact=dict(voltage_V=vmax,current_A=vmax/rmin+dry_i,
                 load_product_W=vmax*(vmax/rmin+dry_i),
                 capacitor_step_energy_J=.5*cmax*vmax*vmax,
                 R616_initial_W=vmax*vmax/rmin,
                 direct_shunt_energy_J=.5*max(c['candidate']['pair_capacitance_screen_F'])*vmax*vmax,
                 note='C607/resistive paths only. Direct diode/PCB capacitance discharges through contact and wiring; peak is not bounded here. Not contact-life or resistor pulse qualification')
    thermal=dict(pair_max_W=max(r['pair_W'] for r in clamped),
                 single_device_allowed_W_at_85C_lead=(175-85)/300,
                 note='Entire pair power assigned to one diode; datasheet lead cooling condition required')
    out=dict(dc=dcrows,ac=acrows,contact=contact,thermal=thermal,
             maximum_normal_wet_V=max(r['wet_peak_bound_V'] for r in acrows),
             max_R618_voltage_V=max(r['R618_V'] for r in clamped),
             max_R618_power_W=max(r['R618_W'] for r in clamped),
             max_audio_change_dB=max(abs(r[k]) for r in acrows for k in ['wet_gain_delta_dB','dry_gain_delta_dB']),
             disposition='Proceed to SPICE and exact-part/native review; no adoption yet',
             source_sha256=c['source_sha256'],contract_sha256=sha(M/'contract.json'),factory_sha256=sha(Path(__file__)),
             native_integrated=False,hardware_qualified=False)
    (M/'results/analytic.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['dc','ac']},indent=2))


if __name__=='__main__': main()
