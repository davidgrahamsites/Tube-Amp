"""Create bounded native repair candidates; adoption is a separate reviewed action.

Only three explicit simple corners and ignored DRC severities are changed.
Bypass placement and part substitutions are outside this operation. Preserve source bytes; refuse output reuse.
Run with KiCad Python and a fresh output directory. No release claim is made.
"""
from pathlib import Path
import hashlib
import json
import math
import shutil
import sys
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
TARGETS = {'Main': ('PI_K',229.6798,118.0002),
           'Power': ('B_EARLY',113.62,87.9998),
           'Control': ('RESET_CT',34.8252,44.375)}
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def point(x,y): return p.VECTOR2I(p.FromMM(x),p.FromMM(y))

def main():
    result={'operation':'bounded layout repair candidates','adopted':False,'boards':{}}
    keep=[]
    for name in ['Main','Power','Control','Reverb']:
        src=ROOT/'boards'/f'Renegade_{name}.kicad_pcb'; dst=OUT/src.name
        assert not dst.exists(), 'Candidate output already exists'
        b=p.LoadBoard(str(src)); keep.append(b); changes=[]
        if name in TARGETS:
            net,x,y=TARGETS[name]; at=point(x,y)
            legs=[]
            for t in b.GetTracks():
                if isinstance(t,(p.PCB_VIA,p.PCB_ARC)) or t.GetNetname()!=net:continue
                for start in [True,False]:
                    v=t.GetStart() if start else t.GetEnd()
                    if (v-at).EuclideanNorm()<p.FromMM(.00005):legs.append((t,start))
            assert len(legs)==2,(name,len(legs))
            assert legs[0][0].GetLayer()==legs[1][0].GetLayer()
            assert not any(q.HitTest(at) for f in b.GetFootprints() for q in f.Pads()),'Corner inside a pad'
            vec=[(t.GetEnd() if s else t.GetStart())-at for t,s in legs]
            lengths=[math.hypot(v.x,v.y) for v in vec]
            trim=min(p.FromMM(.2),*(l/4 for l in lengths)); ends=[]
            for (t,s),v,l in zip(legs,vec,lengths):
                end=at+p.VECTOR2I(round(v.x*trim/l),round(v.y*trim/l)); ends.append(end)
                (t.SetStart if s else t.SetEnd)(end)
            t=p.PCB_TRACK(b); t.SetNetCode(legs[0][0].GetNetCode());t.SetLayer(legs[0][0].GetLayer())
            t.SetStart(ends[0]);t.SetEnd(ends[1]);t.SetWidth(max(z.GetWidth() for z,_ in legs));b.Add(t)
            changes.append({'kind':'bevel','net':net,'corner_mm':[x,y],'trim_mm':p.ToMM(round(trim)),'width_mm':p.ToMM(t.GetWidth())})
        p.SaveBoard(str(dst),b)
        for ext in ['.kicad_pro','.kicad_dru']:shutil.copyfile(src.with_suffix(ext),dst.with_suffix(ext))
        project=dst.with_suffix('.kicad_pro');data=json.loads(project.read_text())
        sev=data['board']['design_settings'].setdefault('rule_severities',{});restored=[]
        for rule,value in sev.items():
            if value=='ignore':sev[rule]='warning';restored.append(rule)
        project.write_text(json.dumps(data,indent=2)+'\n')
        result['boards'][name]={'source_sha256':sha(src),'candidate_sha256':sha(dst),'changes':changes,'restored_checks':restored}
    (OUT/'fp-lib-table').write_text((ROOT/'boards/fp-lib-table').read_text().replace('${KIPRJMOD}',str(ROOT/'boards')))
    (OUT/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
