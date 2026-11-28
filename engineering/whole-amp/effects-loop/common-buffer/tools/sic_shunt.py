"""CB-013. Run the archived UnitedSiC 3.1 JFET model with ngspice."""
import hashlib
import re
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

import fixed_gain as gain

MODEL_SHA='717b15384d332b772881a010334c1156b9f1cda2d6626fd6010f1c7b2c496eae'
PART='UJ3N065080K3S'


def spice_model(path):
    data=Path(path).read_bytes()
    assert hashlib.sha256(data).hexdigest()==MODEL_SHA
    source=re.sub(r'\n\+\s*',' ',data.decode('ascii').replace('\r\n','\n'))
    # LTspice permits nested parameter braces. ngspice requires parentheses inside them.
    chars=[]
    depth=0
    for char in source:
        if char=='{':
            chars.append('(' if depth else '{')
            depth+=1
        elif char=='}':
            depth-=1
            chars.append(')' if depth else '}')
        else:
            chars.append(char)
        assert depth>=0
    assert depth==0
    source=''.join(chars).replace('limit(','clip13(').replace('if(','ternary_fcn(').replace('log(cosh','ln(cosh')
    return '.func clip13(x,a,b) {max(a,min(b,x))}\n'+source


def second_leg(model,threshold,cap_scale):
    # Isolate model namespaces before changing the two independent sample parameters.
    names=re.findall(r'^\.subckt\s+(\w+)',model,re.M|re.I)
    # The free clamp helper is shared. Each subcircuit's model and parameters are local.
    second=model[model.index('*** UJ3N'):]
    for name in sorted(names,key=len,reverse=True):
        second=re.sub(r'\b'+name+r'\b',name+'_B',second,flags=re.I)
    second=second.replace('Vto={vth}',f'Vto={threshold}')
    second=second.replace('acgd={a}',f'acgd={{a*{cap_scale}}}').replace('25p * (a)',f'{25*cap_scale}p * (a)')
    return second


def legs(signal,tail,model,control,driver_ohm,threshold,cap_scale):
    other=second_leg(model,threshold,cap_scale)
    return f'''X13A {signal} gate13 island13 {PART}
X13B {tail} gate13 island13 {PART}_B
Rgate13 cmd13 gate13 {driver_ohm}
Cisol13 island13 0 6p
Risol13 island13 0 1gig
{control}
{model}
{other}
'''


@contextmanager
def installed(model,off=18,driver_ohm=2.,edge_ns=20,threshold=-10,cap_scale=1.,wire_ohm=0,
              signal_threshold=-10,isol_pF=6,fault_edge_ns=None):
    original=gain.sp.load
    def branch(signal,tail,control):
        text=legs(signal,tail,model,control,driver_ohm,threshold,cap_scale)
        # Only the first model still contains this literal after second_leg substitutes Vto.
        assert text.count('Vto={vth}')==1
        return text.replace('Vto={vth}',f'Vto={signal_threshold}').replace('Cisol13 island13 0 6p',f'Cisol13 island13 0 {isol_pF}p')
    def replace(net):
        if 'D8A island8' in net:
            start=net.index('D8A island8')
            end=net.index('RISO8 island8 0 1gig')+len('RISO8 island8 0 1gig')
            audio=branch('FX_RETURN','ret13',f'Vctl13 cmd13 island13 {-off}')
            net=net[:start]+audio+f'Rtail13 ret13 0 {2.2+wire_ohm}\n'+net[end:]
        elif 'VDR gate island' in net:
            start=net.index('CGISE island')
            end=net.index('RPLAYMIX',start)
            control=f'Vctl13 cmd13 island13 PWL(0 {-off} 2.40u {-off} {2.4+edge_ns/1000}u 0)'
            net=net[:start]+branch('mix','retour',control)+net[end:]
        elif 'SSH mix imon cmd' in net:
            if fault_edge_ns is not None:
                def command_edge(match):
                    onset=float(match.group(2))
                    return f'{match.group(1)}{onset} 0 {onset+fault_edge_ns*1e-9} 1)'
                net,n=re.subn(r'^(VTRIP cmd 0 PWL\(0 0 )([^ ]+) 0 [^ ]+ 1\)$',command_edge,net,flags=re.M)
                assert n==1
            start=net.index('SSH mix imon cmd')
            end=net.index('VMON imon',start)
            net=net[:start]+branch('mix','tail13',f'Bctl13 cmd13 island13 V={off}*(v(cmd)-1)')+f'Rtail13 tail13 imon {2.2+wire_ohm}\n'+net[end:]
            # Remove the surrogate capacitance: the JFET model provides it.
            net,count=re.subn(r'^CGUARD8 mix 0 .+$','* JFET pair replaces trial capacitor',net,flags=re.M)
            assert count==1
        original(net)
    with patch.object(gain.sp,'load',replace):
        yield
