"""Measure the exported PDF paths in millimetres, independently of the drawing code."""
import hashlib
import json
from pathlib import Path

import pymupdf as pdf

REVIEW=Path(__file__).resolve().parents[1]/'review'
MM=72/25.4


def geometry(page):
    lines=[]
    rects=[]
    for path in page.get_drawings():
        for kind,*args in path['items']:
            if kind=='l':
                a,b=args
                lines.append((abs(b.x-a.x)/MM,abs(b.y-a.y)/MM))
            elif kind=='re':
                r=args[0]
                rects.append((r.width/MM,r.height/MM))
    return lines,rects


def has(items,width,height,count=1):
    return sum(abs(w-width)<.02 and abs(h-height)<.02 for w,h in items)>=count


def main():
    part=REVIEW/'fischer-recess-fit-template.pdf'
    doc=pdf.open(part)
    assert len(doc)==5
    pages=[geometry(p) for p in doc]
    assert all(abs(p.rect.width/MM-210)<.02 and abs(p.rect.height/MM-297)<.02 for p in doc)
    assert all(has(lines,100,0) and has(lines,0,200) for lines,_ in pages[2:])
    wall,guard,gauges=pages[2:]
    assert has(wall[1],151.4,85) and has(wall[1],115.38,65.38) and has(wall[0],0,85,2)
    # Measure the score-to-score span of page 3.
    folds=[p['items'][0][1].x/MM for p in doc[2].get_drawings() if
           p['items'][0][0]=='l' and abs(p['rect'].height/MM-85)<.02]
    assert abs(abs(folds[0]-folds[1])-121.4)<.02
    assert has(guard[1],115.38,65.38) and has(guard[0],24.88,0,4) and has(guard[0],0,24.88,4)
    assert has(gauges[1],118,22) and has(gauges[1],147.88,21)
    tip=next(p['rect'].x0/MM for p in doc[4].get_drawings() if
             p['items'][0][0]=='l' and abs(p['rect'].height/MM-21)<.02)
    end=next(p['rect'].x1/MM for p in doc[4].get_drawings() if
             p['items'][0][0]=='re' and abs(p['rect'].width/MM-147.88)<.02)
    assert abs(end-tip-5)<.02
    for page in doc:
        for x0,y0,x1,y1,*_ in page.get_text('blocks'):
            assert x0>=8*MM and x1<=202*MM and y0>8*MM and y1<289*MM
    text=doc[0].get_text()+doc[1].get_text()
    assert all(word in text for word in ('Fischer','PA340','thin card','scissors','ruler','original screws','Page 5'))
    result=dict(PDF_sha256=hashlib.sha256(part.read_bytes()).hexdigest(),pages=5,paper='A4 portrait',
                scale_bars_mm=[100,200],pocket_width_mm=abs(folds[0]-folds[1]),gauge_tip_mm=end-tip,
                flat_guard_max_width_height_mm=[115.38,65.38],box_depth_mm=24.88,
                checks='Exported vector lengths, page size, calibration, material list, gauge lengths and textbounds.',
                digital_pass=True,printed_and_cabinet_fit_verified=False)
    (REVIEW/'fischer-template-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result)


if __name__=='__main__':
    main()
