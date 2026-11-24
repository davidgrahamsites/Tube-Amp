"""Read-only socket envelope screen on current boards, not a chassis release.

Electrical/socket limits are owned by component-selection/socketing. Mechanical
analysis consumes that small interface, preserving native CAD and fit-register.
"""
import hashlib, json, math, sys
from pathlib import Path
M=Path(__file__).resolve().parents[1]; ROOT=M.parents[2]
sys.path.insert(0,str(M.parent/'tools'))
import native_sexpr as v
ENVELOPE=ROOT/'engineering/component-selection/socketing/socket-envelope.json'

def transform(f,p):
    a=v.field(f,'at');x,y=map(float,a[1:3]);r=math.radians(float(a[3]) if len(a)>3 else 0)
    px,py=map(float,p)
    return (x+px*math.cos(r)+py*math.sin(r), y-px*math.sin(r)+py*math.cos(r))

def box(points):
    return [min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)]

def courtyard(f):
    points=[]
    for g in f:
        if not isinstance(g,list) or not g[0].startswith('fp_'):continue
        if not v.children(g,'layer') or v.field(g,'layer')[1]!='"F.CrtYd"':continue
        if g[0] in ['fp_rect','fp_line']:
            for k in ['start','end']:points.append(transform(f,v.field(g,k)[1:3]))
        elif g[0]=='fp_poly':
            points.extend(transform(f,p[1:3]) for p in v.field(g,'pts')[1:])
        else:return None # Curves need their own exact geometry; do not guess.
    return box(points) if points else None

def overlap(a,b):
    return min(a[2],b[2])>max(a[0],b[0]) and min(a[3],b[3])>max(a[1],b[1])

def main():
    env=json.loads(ENVELOPE.read_text());c=env['common'];rows=[];sources=[ENVELOPE]
    for path in sorted((M.parent/'pcb-measured-r/boards').glob('*.kicad_pcb')):
        sources.append(path);fps=v.fps(v.parse(path.read_text()));bounds={r:courtyard(f) for r,f in fps.items()}
        for package,part in env['packages'].items():
            for ref in part['refs']:
                if ref not in fps:continue
                f=fps[ref];w=c['socket_width_max_mm'];length=max(part['socket_length_max_mm'],part['ic_length_max_mm'])
                cx=c['row_spacing_mm']/2;cy=part['pin_span_mm']/2
                # Symmetric package placement is a planning assumption pending
                # current socket drawing/sample; envelope includes the DIP body.
                b=box([transform(f,(x,y)) for x in [cx-w/2,cx+w/2] for y in [cy-length/2,cy+length/2]])
                drill={p[1].strip('"'):v.field(p,'drill')[1:] for p in v.children(f,'pad')}
                conform=all(d==[str(c['pcb_hole_nominal_mm'])] or d==['1'] for d in drill.values())
                rows.append(dict(reference=ref,board=path.stem,mpn=part['mpn'],body_bbox_mm=b,
                    combined_height_bound_mm=c['combined_height_bound_mm'],planning_top_and_extraction_mm=c['design_height_reserve_mm']+c['extra_extraction_reserve_mm'],
                    existing_drills=drill,drills_match_candidate_drawing=conform,
                    existing_courtyard_contains_body=bounds[ref] is not None and all([bounds[ref][0]<=b[0],bounds[ref][1]<=b[1],bounds[ref][2]>=b[2],bounds[ref][3]>=b[3]]),
                    body_overlaps_other_courtyard=[r for r,q in bounds.items() if r!=ref and q and overlap(b,q)],
                    other_footprints_without_supported_courtyard=[r for r,q in bounds.items() if r!=ref and q is None]))
    assert {r['reference'] for r in rows}=={'U1','U2','U10','U11','U12'}
    assert overlap([0,0,2,2],[1,1,3,3]) and not overlap([0,0,2,2],[2,0,3,1])
    tail=math.hypot(c['tail_width_max_mm'],c['tail_thickness_max_mm'])
    report=dict(scope='Candidate DIP sockets only, current four-board draft; symmetric placement assumption',
        rows=rows,rectangular_tail_max_diagonal_mm=tail,
        minimum_finished_hole_mm=c['pcb_hole_nominal_mm']-c['provisional_finished_hole_tolerance_mm'],
        remaining_diametric_clearance_mm=c['pcb_hole_nominal_mm']-c['provisional_finished_hole_tolerance_mm']-tail,
        unknowns=['final board consolidation and orientation','ceiling and harness obstructions','vertical extraction path and retention','actual drill tool envelope deferred November25','finished-hole tolerance is a proposed fabrication allocation'],
        rear_panel_must_remain_independent=True,chassis_fit_verified=False,fabrication_ready=False,
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})
    (M/'review/socket-fit-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['source_sha256','rows']},indent=2))
    for r in rows:print(r['reference'],'drill_match',r['drills_match_candidate_drawing'],'courtyard_contains',r['existing_courtyard_contains_body'],'body_overlaps',r['body_overlaps_other_courtyard'])

if __name__=='__main__':main()
