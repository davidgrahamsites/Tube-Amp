"""Recover the combined hot-short point using released operating-point guesses."""
import ctypes as ct
import hashlib
import json
import math
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

import guard_audio
import low_line_rail
import pulse_winding
import rail_winding_audio

sp=guard_audio.sp


def voltages():
    sp.lib.ngSpice_CurPlot.restype=ct.c_char_p
    sp.lib.ngSpice_AllVecs.argtypes=[ct.c_char_p]
    sp.lib.ngSpice_AllVecs.restype=ct.POINTER(ct.c_char_p)
    names=sp.lib.ngSpice_AllVecs(sp.lib.ngSpice_CurPlot())
    values={}
    index=0
    while names[index]:
        raw=sp.lib.ngGet_Vec_Info(names[index]).contents
        if raw.type==3 and raw.length and math.isfinite(raw.real[0]):
            values[names[index].decode()]=raw.real[0]
        index+=1
    return values


@contextmanager
def guide(seed_mA):
    original_load=sp.load
    evidence={}
    def load_combined(net):
        start=net.index('VRAW raw7')
        end=net.index('VLV pos15',start)
        rail=net[start:end]
        stiff=net[:start]+'VFIX9 supply 0 310\n'+net[end:]
        def strip_hints(text):
            return '\n'.join(s for s in text.splitlines() if not s.startswith('.nodeset'))+'\n'
        original_load(strip_hints(stiff))
        pulse_winding._cmd('op')
        initial=voltages()
        assert len(initial)>100 and abs(initial['supply']-310)<.01
        original_load(f'Independent hot rail seed\n{rail}\n.temp 85\nISEED supply 0 {seed_mA}m\n.end')
        pulse_winding._cmd('op')
        supply=voltages()
        assert 295<supply['supply']<320
        initial.update(supply)
        guesses='\n'.join(f'.nodeset v({n})={v:.14g}' for n,v in initial.items() if n!='0')
        base=strip_hints(net)
        evidence.update(seed_mA=seed_mA,seed_nodes=len(initial),unconstrained_deck_sha256=hashlib.sha256(base.encode()).hexdigest())
        pulse_winding._cmd('destroy all')
        original_load(base.replace('\n.end\n','\n'+guesses+'\n.end\n'))
    with patch.object(sp,'load',load_combined):
        yield evidence


def main():
    def rail(raw,ctr,threshold,cap,bypass,leak):
        return low_line_rail.variant(raw,ctr,threshold,52.8,bypass,None,**low_line_rail.CAND)
    rows=[]
    with pulse_winding.instrument(),patch.object(guard_audio,'regulator',rail):
        pulse_winding.STATE.update(spec=rail_winding_audio.SPEC,corner={'r_scale':1.236})
        for current in (2,16.5):
            with guide(current) as evidence:
                run=guard_audio.audio(20000,500,220,30,True,85,310,False,1,440,39700)
            assert 305<run['rail_min_V']<315 and abs(run['bias_V']-155)<2
            rows.append(dict(**evidence,result=run))
    assert rows[0]['unconstrained_deck_sha256']==rows[1]['unconstrained_deck_sha256']
    assert abs(rows[0]['result']['chip_W']-rows[1]['result']['chip_W'])<.001
    out=guard_audio.MODULE/'results/hot-short-bias.json'
    out.write_text(json.dumps(dict(rows=rows,physical_startup_verified=False),indent=2)+'\n')
    print([(r['seed_mA'],r['result']['rail_min_V'],r['result']['chip_W']) for r in rows])


if __name__=='__main__':
    main()
