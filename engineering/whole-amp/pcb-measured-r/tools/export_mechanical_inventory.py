"""Read-only native board geometry seam for the mechanical fit study.
Exact rectangular outline and NPTH mounting holes, not populated height claims.
"""
from pathlib import Path
import hashlib,json
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]
def mm(v):return round(p.ToMM(v),6)
def point(v):return [mm(v.x),mm(v.y)]
def main():
    rows={};keep=[]
    for name in ['Main','Power','Control','Reverb']:
        path=ROOT/'boards'/f'Renegade_{name}.kicad_pcb';raw=path.read_bytes();b=p.LoadBoard(str(path));keep.append(b)
        edges=[e for e in b.GetDrawings() if e.GetLayer()==p.Edge_Cuts];assert len(edges)==4 and all(e.GetShape()==p.SHAPE_T_SEGMENT for e in edges),'Nonrectangular outline needs explicit adapter'
        segments=[[point(e.GetStart()),point(e.GetEnd())] for e in edges];pts={tuple(v) for e in segments for v in e};assert len(pts)==4
        xs=sorted({q[0] for q in pts});ys=sorted({q[1] for q in pts});assert len(xs)==len(ys)==2
        assert all((a[0]==z[0]) != (a[1]==z[1]) for a,z in segments)
        holes=[];missing=[]
        for f in b.GetFootprints():
            if not list(f.Models()):missing.append(f.GetReference())
            if f.GetReference().startswith('H'):
                for q in f.Pads():
                    drill=point(q.GetDrillSize());assert q.GetAttribute()==p.PAD_ATTRIB_NPTH and drill[0]==drill[1]>0,'Unsupported mount hole geometry'
                    at=point(q.GetPosition());holes.append(dict(ref=f.GetReference(),at_from_outline_mm=[at[0]-xs[0],at[1]-ys[0]],diameter_mm=drill[0],shape='round',plated=False))
        assert raw==path.read_bytes()
        rows[name]=dict(path=str(path.relative_to(ROOT.parent.parent.parent)),sha256=hashlib.sha256(raw).hexdigest(),origin_mm=[xs[0],ys[0]],size_mm=[xs[1]-xs[0],ys[1]-ys[0],mm(b.GetDesignSettings().GetBoardThickness())],mounting_holes=holes,missing_3d_models=sorted(missing))
    result=dict(scope='Native rectangular PCB outline and mounting-hole geometry; no component envelope substitution',boards=rows,factory_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),native_modified=False,fabrication_ready=False)
    (ROOT/'review/mechanical-inventory.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({n:dict(size=v['size_mm'],holes=v['mounting_holes'],missing_models=len(v['missing_3d_models'])) for n,v in rows.items()},indent=2))
if __name__=='__main__':main()
