"""Guarded routing/presentation stage after integrate_reset_edges.py.

Run only on the recorded intermediate revision. Never regenerate other sheets.
The editable route recipe is independent of the validation implementation.
"""
import hashlib,json,sys
from pathlib import Path
import integrate_reset_edges as e
M=e.M;ROOT=e.ROOT

def final_texts(texts):
    board=texts[e.PCB].rstrip()
    recipe=json.loads((M/'edge-routes.json').read_text())
    texts[e.PCB]=board[:-1]+' '+' '.join(recipe['objects'])+')\n'
    text=texts[e.LATCH];edits=[];adds=[]
    for kind in ['global_label','symbol']:
        for a,b in e.spans(text,kind):
            obj=e.v.parse(text[a:b]);changed=False
            if kind=='global_label' and obj[1] in ['"RESET_RAW_N"','"RESET_INV"']:
                at=e.v.field(obj,'at');x=float(at[1]);at[2]='297.18';changed=True
                adds.append(e.wire((x,304.8),(x,297.18)))
                adds.append(e.v.parse(f'(junction (at {x} 304.8) (diameter 0) (color 0 0 0 0) (uuid {e.uid("label-junction-"+str(x))}))'))
            if kind=='symbol' and e.ref(obj)=='U3':
                for key,y in [('Reference',291),('Display',293.54),('Value',293.54)]:
                    ps=[p for p in e.v.children(obj,'property') if p[1]==json.dumps(key)]
                    if ps:e.v.field(ps[0],'at')[1:3]=['307.34',str(y)]
                changed=True
            if changed:edits.append((a,b,e.emit(obj)))
    for a,b,s in sorted(edits,reverse=True):text=text[:a]+s+text[b:]
    texts[e.LATCH]=text.rstrip()[:-1]+' '+' '.join(e.emit(x) for x in adds)+')\n'
    text=texts[e.POWER];edits=[]
    for a,b in e.spans(text,'symbol'):
        obj=e.v.parse(text[a:b])
        if (e.ref(obj),e.v.field(obj,'unit')[1]) in [('U1','7'),('U2','3')]:
            x=float(e.v.field(obj,'at')[1])-15.24
            for key,y in [('Reference',162.56),('Display',165.1),('Value',165.1)]:
                ps=[p for p in e.v.children(obj,'property') if p[1]==json.dumps(key)]
                if ps:e.v.field(ps[0],'at')[1:3]=[str(x),str(y)]
            edits.append((a,b,e.emit(obj)))
    for a,b,s in reversed(edits):text=text[:a]+s+text[b:]
    texts[e.POWER]=text
    return texts

def main():
    assert sys.argv[1:]==['--apply']
    receipt=json.loads((M/'results/edge-integration.json').read_text())
    paths=[e.PCB,e.LATCH,e.POWER];texts={p:(ROOT/p).read_text() for p in paths}
    for p,t in texts.items():assert hashlib.sha256(t.encode()).hexdigest()==receipt['after_sha256'][p],p
    for p,t in final_texts(texts).items():e.v.parse(t);(ROOT/p).write_text(t)
    print('Reset finalization written; re-export and independently validate before adoption.')

if __name__=='__main__':main()
