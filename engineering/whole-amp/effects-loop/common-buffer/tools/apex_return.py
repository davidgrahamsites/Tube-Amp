"""CB-006: single-rail recovery experiment on the CB-005 downstream network."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import zipfile

import numpy as np
from integrated_load import M, ROOT, circuit, sp

MODELS = Path(os.environ.get('RENEGADE_APEX_MODELS',str(Path.home()/'.cache/renegade/apex')))
TI = ROOT / 'engineering/solid-state-reverb/simulation/models/OPAx134.LIB'


def deck(f, target, pf, rail, isolation, cc, short=False, temperature=25, old_send=False, part="PA341", trimmed=False, guarded=False):
    base = circuit(f, target, pf).rsplit('.include "', 1)[0]
    assert 'XV4_1' in base and 'MFOLLOW' not in base
    if not old_send:
        assert base.count('R601 IN_AC SEND_IN 1000000.0') == 1
        base = base.replace('R601 IN_AC SEND_IN 1000000.0',f'R601 IN_AC SEND_IN {1370000 if trimmed else 1300000}')
    archive = MODELS / (part + '.zip')
    expected = {'PA340':'f32e6faf4b8c17e1f6bbfa1ba0548ead807830cd844c208a8a63ab00cbd676ab','PA341':'af1843a1b5d59fe7ff25699e5c42a7193ad816ae0be16ffff5dfea623c9ebbe6'}[part]
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == expected
    with zipfile.ZipFile(archive) as z:
        apex = z.read(part + '_Berkeley.LIB').decode('ascii')
    chip = ('XPOWER plus minus supply 0 raw cc1 cc2 sense PA341\nRCL sense raw 33'
            if part == 'PA341' else 'XPOWER plus minus supply 0 raw cc1 cc2 PA340')
    return base + apex + f'''
.include "{TI}"
.temp {temperature}
VREC supply 0 {rail}
VLV pos15 0 15
VNEG neg15 0 -15
VINPUT input6 0 dc 0 ac 1 SIN(0 {target/100} {f})
XLOW input6 invlow pos15 neg15 low OPAx134
RLOW1 invlow 0 10k
RLOW2 low invlow {40200 if guarded else (31600 if trimmed else 30000)}
{'RSEP1 low inm 24k' + chr(10) + 'RSEP2 inm ins 24k' if guarded else 'RSEP low ins 1k'}
CIN1 ins cjoin 1u
CIN2 cjoin plus 1u
RB1 supply plus 470k
RB2 plus 0 470k
{chip}
VCHIP raw preout 0
CCOMP cc1 cc2 {cc}p
RF1 preout rfmid 24k
RF2 rfmid minus 24k
RG minus cg 2k
CG cg 0 47u
RISO preout coupling {isolation}
COUT1 coupling cmid 2.2u
COUT2 cmid port 2.2u
RBLEED port 0 1meg
VMON port FX_RETURN 0
CHAR6 FX_RETURN 0 {max(pf, .001)}p
{'RSHORT FX_RETURN 0 .1' if short else '* normal port'}
.end
'''


def run(args):
    f, a, pf, rail, iso, cc, temp = args.hz,args.peak,args.pf,args.rail,args.iso,args.cc,args.temp
    net = deck(f,a,pf,rail,iso,cc,args.short,temp,args.old_send,args.part,args.trimmed,args.guarded)
    sp.load(net)
    sp.cmd('op')
    bias = sp.vector('v(preout)')[-1]
    assert abs(bias-rail/2)<5, bias
    sp.cmd('ac dec 30 10 10meg')
    freq = np.real(sp.vector('frequency'))
    resp = np.asarray(sp.vector('v(fx_return)'))
    gains = {str(point):float(np.interp(np.log(point),np.log(freq),20*np.log10(abs(resp)/100)))
             for point in [20,82.4,1000,20000]}
    names = ['v(fx_return)','i(vmon)','v(send_in)','v(preout)','i(vrec)','i(vchip)','v(minus)','v(plus)']
    sp.cmd('save '+' '.join(names))
    end = args.cycles/f
    dt = 1/(f*args.steps)
    sp.cmd(f'tran {dt} {end} 0 {dt}')
    t=np.asarray(sp.vector('time'))
    result = dict(parameters=vars(args),deck_sha256=hashlib.sha256(net.encode()).hexdigest(),
                  bias_V=bias, ac_gain_error_dB=gains, end_s=end,reached_s=float(t[-1]))
    if t[-1]<end*(1-1e-8):
        result.update(status='incomplete',diagnostic=sp.logs[-5:])
        return result
    def sample(name, stop):
        x=stop + (np.arange(4096)/409.6-10)/f
        return np.interp(x,t,sp.vector(name))
    v,i,send,out,irail,iout,minus,plus = [sample(name,end) for name in names]
    peaks=2*abs(np.fft.rfft(v)/len(v))[np.arange(1,11)*10]
    # VCHIP includes feedback and external output currents.
    # Includes current-limit resistor losses. Subtract external rail-divider power.
    loss=np.mean(-rail*irail - rail*(rail-plus)/470e3 - out*iout)
    result.update(status='completed',fundamental_Vpk=peaks[0],thd_percent=100*np.linalg.norm(peaks[1:])/peaks[0],
                  gain_error_dB=20*np.log10(peaks[0]/a),port_mA=[min(i)*1000,max(i)*1000],
                  chip_output_mA=[min(iout)*1000,max(iout)*1000], send_peak_V=max(abs(send)),
                  power_stage_W=loss, window_delta_Vrms=np.sqrt(np.mean((v-sample(names[0],end-10/f))**2)))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for flag,default in [('hz',20000),('peak',135),('pf',500),('rail',310),('iso',680),('cc',4.7),
                         ('temp',25),('steps',320),('cycles',45)]:
        parser.add_argument('--'+flag,type=float,default=default)
    parser.add_argument('--part',choices=['PA340','PA341'],default='PA341')
    parser.add_argument('--short',action='store_true')
    parser.add_argument('--guarded',action='store_true')
    parser.add_argument('--trimmed',action='store_true')
    parser.add_argument('--old-send',action='store_true')
    print(json.dumps(run(parser.parse_args()),allow_nan=False,indent=2))
