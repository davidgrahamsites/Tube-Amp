"""CB-020. Add an independently biased, wired and driven shunt across the mixer."""
from contextlib import contextmanager
from unittest.mock import patch
import re

import fixed_gain as gain
from bridge_shunt import bridge


@contextmanager
def dual_bridge(bias_a=2., bias_b=2., mirrored=False, second_diode=None, late_channel=None, skew_ns=0, charger_pF=None, **settings):
    """Keep one 270 pF receiver capacitor. Each shunt owns its bridge, driver and wire."""
    original=gain._load
    def add(net):
        lines=net.splitlines()
        by_name={line.split()[0]:line for line in lines if line and not line[0].isspace()}
        signal=by_name['D18a'].split()[1]
        tail=by_name['D18b'].split()[1]
        tail_part='RSH' if tail=='retour' else 'Rtail13'
        ctl='Vctl13' if 'Vctl13' in by_name else 'Bctl13'
        # Distinct return resistors converge at the same ideal mixer reference.
        parts=['X13A','D18a','D18b','D18c','D18d','Vhold18','Rlimit18','Rleak18',
               'Rgate13','Cisol13','Risol13',ctl,tail_part,'Rhi18','Rhi018','Rpa18',
               'Dparkp18','Rlo18','Rlo018','Rna18','Dparkn18']
        private='plus18 minus18 rail18 gate13 cmd13 island13 high18 low18 an18 ca18'.split()
        rename={node:node+'B20' for node in private}
        rename[tail]=tail+'B20'
        extras=[]
        for part in parts:
            fields=by_name[part].split()
            fields[0]+='B20'
            fields[1:]=[rename.get(f,f) for f in fields[1:]]
            if part=='X13A':
                fields[-1]+='_B'
            if part=='Vhold18':
                fields[-1]=str(bias_b)
            if mirrored and part in ('D18a','D18b','D18c','D18d'):
                fields[1:3]=[{signal:rename[tail],rename[tail]:signal}.get(f,f) for f in fields[1:3]]
            extras.append(' '.join(fields))
        ix=lines.index('.end')
        lines[ix:ix]=extras
        if charger_pF:
            pos=lines.index('.end')
            lines[pos:pos]=[f'Ccharger20a rail18 0 {charger_pF[0]}p', f'Ccharger20b rail18B20 0 {charger_pF[1]}p']
        if second_diode:
            cj,tt,ratio=second_diode
            for i,line in enumerate(lines):
                if re.match(r'^D18[a-d]B20 ',line):
                    lines[i]=line+'B20'
            pos=lines.index('.end')
            lines[pos:pos]=[f'.model bridge18aB20 D(is=5n n=1.65 rs=.2 cjo={cj}p m=.4 tt={tt}n bv=400 ibv=10u)',
                            f'.model bridge18bB20 D(is={5*ratio}n n=1.65 rs=.2 cjo={cj*ratio}p m=.4 tt={tt}n bv=400 ibv=10u)']
        if skew_ns and late_channel:
            tag=ctl+('B20' if late_channel=='B' else '')
            i=next(i for i,line in enumerate(lines) if line.startswith(tag+' '))
            if ctl=='Bctl13':
                trip=by_name['VTRIP']
                start,end=map(float,re.search(r'PWL\(0 0 (\S+) 0 (\S+) 1\)',trip).groups())
                delay=skew_ns*1e-9
                lines.insert(lines.index('.end'),f'Vskew20 slow20 0 PWL(0 0 {start+delay:.14g} 0 {end+delay:.14g} 1)')
                lines[i]=lines[i].replace('v(cmd)','v(slow20)')
            elif 'PWL' in lines[i]:
                lines[i]=re.sub(r'([0-9.]+)u',lambda m:f'{float(m[1])+skew_ns/1000:.12g}u',lines[i])
        original('\n'.join(lines))
    with patch.object(gain,'_load',add),bridge(held_V=bias_a,**settings):
        yield
