"""AC return-ratio diagnosis with closed/open transfer identity validation.
No model fitting, CAD edits or physical stability certification.
"""
import hashlib,json,sys
from pathlib import Path
import numpy as np
from fixture import ROOT,WHOLE,fingerprint
from feedback_model import build,DEFAULTS,legacy_inductances
sys.path.insert(0,str(WHOLE/'tools'))
import spice_runtime as sp
OUT=ROOT/'results'

def hashes():
    return {str(p.relative_to(WHOLE.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [Path(__file__),ROOT/'tools/feedback_model.py',ROOT/'tools/transformer_model.py',ROOT/'tools/fixture.py',WHOLE/'tools/spice_runtime.py']}

def response(name,p,state):
    text=build(p,state);path=OUT/f'{name}-{state}.cir';path.write_text(text)
    sp.load(text);sp.cmd('op')
    op={n:float(sp.vector('v('+n+')')[-1]) for n in ['speaker','pi_p1','pi_p2','pi_k','ot_pa','ot_pb']}
    sp.cmd('ac dec 120 .1 10000000')
    f=np.real(sp.vector('frequency'));v=np.array(sp.vector('v(speaker)'))
    sp.cmd('destroy all')
    return f,v,op,hashlib.sha256(text.encode()).hexdigest()

def analyze(f,T,H):
    g=20*np.log10(np.maximum(abs(T),1e-30));phase=np.unwrap(np.angle(T))*180/np.pi
    phase-=360*round(phase[np.argmin(abs(f-1000))]/360)
    unity=[];gm=[]
    for i in range(len(f)-1):
        if g[i]*g[i+1]<0:
            a=-g[i]/(g[i+1]-g[i]);ph=float(phase[i]+a*(phase[i+1]-phase[i]));principal=(ph+180)%360-180
            unity.append(dict(Hz=float(np.exp(np.log(f[i])+a*np.log(f[i+1]/f[i]))),phase_deg=ph,
                              angular_distance_from_minus_one_deg=180-abs(principal),direction='down' if g[i+1]<g[i] else 'up'))
        # Every crossing of the negative real axis, independent of unwrap.
        if T[i].imag*T[i+1].imag<0 and T[i].real<0 and T[i+1].real<0:
            a=-T[i].imag/(T[i+1].imag-T[i].imag)
            gm.append(dict(Hz=float(np.exp(np.log(f[i])+a*np.log(f[i+1]/f[i]))),margin_dB=float(-(g[i]+a*(g[i+1]-g[i])))))
    idx=int(np.argmax(abs(1/(1+T))));ref=abs(H[np.argmin(abs(f-1000))]);band=(f>=1000)&(f<=100000)
    return dict(unity_crossings=unity,negative_real_crossings=gm,
                min_unity_angle_deg=min((r['angular_distance_from_minus_one_deg'] for r in unity),default=None),
                min_gain_margin_dB=min((r['margin_dB'] for r in gm),default=None),
                sensitivity_peak=float(abs(1/(1+T[idx]))),sensitivity_peak_Hz=float(f[idx]),
                HF_peak_relative_1k_dB=float(np.max(20*np.log10(abs(H[band])/ref))),
                points={str(hz):dict(actual_Hz=float(f[i]),gain_V_V=float(abs(H[i])),relative_1k_dB=float(20*np.log10(abs(H[i])/ref)),loop_gain_dB=float(g[i]),loop_phase_deg=float(phase[i])) for hz in [20,82.4,1000,5000,10000,20000,100000] for i in [int(np.argmin(abs(f-hz)))]})

def cases():
    out=[('legacy-ideal',dict(legacy_transformer={})),('legacy-pessimistic',dict(legacy_transformer=dict(half_primary_H=40,coupling=.995)))]
    for lm in [10,40,160]:
        for leak in [.005,.02,.08]:
            for cp in [50e-12,250e-12,1000e-12]:
                out.append((f'lm{lm}-lk{round(leak*1000)}-cp{round(cp*1e12)}',dict(magnetizing_H=lm,leakage_H=leak,primary_cap_F=cp)))
    for presence in [0,1]:
        for load in [4,8,16]: out.append((f'pres{presence}-load{load}',dict(presence=presence,load_ohm=load,load_cap_F=2e-9)))
    for cap in [47e-12,100e-12,220e-12,470e-12]:
        for leak in [.02,.08]:
            for presence in [0,.5,1]:
                out.append((f'comp{round(cap*1e12)}-lk{round(leak*1000)}-pres{presence}',dict(pi_cap_F=cap,leakage_H=leak,presence=presence)))
    for cap in [47e-12,100e-12,220e-12,470e-12]:
        for leak in [.02,.08]:
            for presence in [0,.5,1]:
                out.append((f'lead{round(cap*1e12)}-lk{round(leak*1000)}-pres{presence}',dict(feedback_cap_F=cap,leakage_H=leak,presence=presence)))
    return out

def main():
    source=fingerprint();fact=hashes();rows=[];curves={}
    sp.cmd('version');version=list(sp.logs)
    for label,p in cases():
        name='feedback-'+label
        f,Hc,opc,hc=response(name,p,'closed');_,Ho,opo,ho=response(name,p,'open');_,inj,opi,hi=response(name,p,'injection')
        T=-inj/np.sqrt(2);pred=Ho/(1+T)
        err=float(np.max(abs(pred-Hc)/np.maximum(abs(Hc),1e-8)))
        dc=float(max(abs(opc[n]-op[n]) for op in [opo,opi] for n in opc))
        row=dict(name=name,parameters=dict(DEFAULTS,**p),analysis=analyze(f,T,Hc),transfer_identity_relative_error=err,
                 open_closed_dc_max_difference_V=dc,deck_hashes={'closed':hc,'open':ho,'injection':hi})
        rows.append(row)
        if label in ('legacy-ideal','legacy-pessimistic','lm40-lk20-cp250','lm40-lk80-cp1000'):
            curves[label]=dict(frequency_Hz=f.tolist(),loop_real=T.real.tolist(),loop_imag=T.imag.tolist(),closed_gain=abs(Hc).tolist())
        print(label,'identity',round(err,9),'angle',row['analysis']['min_unity_angle_deg'],flush=True)
    assert source==fingerprint() and fact==hashes(),'Inputs changed during sweep'
    checks=dict(all_transfer_identities=all(r['transfer_identity_relative_error']<1e-5 for r in rows),
                all_DC_operating_points_preserved=all(r['open_closed_dc_max_difference_V']<1e-5 for r in rows),all_finite=all(np.isfinite(r['analysis']['sensitivity_peak']) for r in rows))
    result=dict(scope='Generic-model small-signal sensitivity; not selected transformer or physical stability certification',source_hashes=source,factory_hashes=fact,
                simulator_version_log=version,cases=rows,legacy_pessimistic_inductances=legacy_inductances(40,.995),checks=checks,passed=all(checks.values()),physical_qualified=False,fabrication_ready=False)
    (OUT/'feedback-summary.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    (OUT/'feedback-curves.json').write_text(json.dumps(curves,separators=(',',':'),allow_nan=False)+'\n')
    (OUT/'feedback-sweep.log').write_text('\n'.join(sp.logs)+'\n')
    assert result['passed'],checks

if __name__=='__main__':main()
