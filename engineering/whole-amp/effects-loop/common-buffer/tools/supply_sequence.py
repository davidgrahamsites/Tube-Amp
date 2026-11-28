"""CB-007 supervisory logic requirement. Exercise priorities independent of SPICE."""
import json
from pathlib import Path
from dataclasses import dataclass

MODULE=Path(__file__).resolve().parents[1]


@dataclass
class Supervisor:
    armed: bool=False
    played: bool=False
    hv_seen: bool=False
    elapsed: float=0
    quiet: float=0
    previous_button: bool=True
    inhibit_s: float=30.

    def tick(self, dt, rail, button=False, plus=True, minus=True, control=True,
             thermal=True, precharge=.0, offset=.0, over=False):
        previously_armed=self.armed
        self.inhibit_s=max(0.,self.inhibit_s-dt) if control else 30.
        edge=button and not self.previous_button
        self.previous_button=button
        healthy=control and plus and minus and thermal and not over
        if not healthy:
            self.armed=False
        elif edge and rail<=60 and self.inhibit_s==0:
            self.armed=True
        if self.armed:
            self.elapsed+=dt
            if ((self.elapsed>=1 and rail<60) or (self.elapsed>=4 and rail<300)
                or (self.hv_seen and rail<295) or rail>320):
                self.armed=False
        if previously_armed and not self.armed:
            self.inhibit_s=30.
        if not self.armed:
            self.played=self.hv_seen=False
            self.elapsed=self.quiet=0
        else:
            self.hv_seen |= rail>=300
            if not self.played:
                valid=300<=rail<=320 and abs(offset)<=3 and abs(precharge)<=.35
                self.quiet=self.quiet+dt if valid else 0
                self.played=self.quiet>=.25
        return self.armed,self.played


def run(fault):
    s=Supervisor()
    s.tick(30.1,0)
    s.tick(.001,0,button=True)
    s.tick(.4,150)
    s.tick(.2,310)
    pre=s.played
    s.tick(.001,310,precharge=.4)
    s.tick(.2,310)
    s.tick(.001,310,offset=4)
    s.tick(.26,310)
    assert s.played and not pre
    # During PLAY, startup silence guards are intentionally ignored.
    assert s.tick(.01,310,precharge=100,offset=100)==(True,True)
    state=s.tick(.001,**fault)
    assert state==(False,False)
    held=s.tick(.1,310,button=True)
    assert held==(False,False)
    assert s.tick(.1,20,button=True)==(False,False)
    s.tick(.1,20)
    assert s.tick(.001,20,button=True)==(False,False)
    s.tick(30.1,20)
    rearmed=s.tick(.001,20,button=True)
    assert rearmed==(True,False)
    return dict(injected=fault,cleared=not state[0],play_inhibited=not state[1],
                cooldown_rejected=True,held_button_rejected=not held[0],fresh_edge_accepted=rearmed[0])


if __name__=='__main__':
    faults=[dict(rail=310,**{k:False}) for k in ['plus','minus','control','thermal']]
    faults.extend([dict(rail=315,over=True),dict(rail=330),dict(rail=290)])
    rows=[run(fault) for fault in faults]
    (MODULE/'results/supply-sequence.json').write_text(json.dumps(rows,indent=2)+'\n')
