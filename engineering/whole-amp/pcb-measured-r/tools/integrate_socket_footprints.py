"""Guarded socket-only native integration. Never rerun on adopted CAD.

Geometry comes from the socket module's library; this adapter preserves board
pad identity/copper and updates footprint metadata in source and native sheets.
"""
import copy,json,subprocess,sys,uuid
from pathlib import Path
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2]
S=ROOT/'engineering/component-selection/socketing'
sys.path.insert(0,str(M.parent/'tools'));import native_sexpr as v
sys.path.insert(0,str(M.parent/'control-switching/tools'))
from integrate_drivers import emit,prop

def spans(text,kind):
    depth=0;quoted=False;escaped=False;start=None
    for i,ch in enumerate(text):
        if quoted:
            if escaped:escaped=False
            elif ch=='\\':escaped=True
            elif ch=='"':quoted=False
        elif ch=='"':quoted=True
        elif ch=='(':
            if depth==1 and text.startswith('('+kind,i) and text[i+len(kind)+1].isspace():start=i
            depth+=1
        elif ch==')':
            depth-=1
            if depth==1 and start is not None:yield start,i+1;start=None

def repair_bypass(t,c):
    r=c['local_clearance_repair'];replacements=[]
    for start,end in spans(t,'footprint'):
        f=v.parse(t[start:end])
        if prop(f,'Reference')[2]==json.dumps(r['reference']):
            assert float(v.field(f,'at')[2])==r['from_y_mm']
            v.field(f,'at')[2]=str(r['to_y_mm']);replacements.append((start,end,emit(f)))
    count=0
    for start,end in spans(t,'segment'):
        s=v.parse(t[start:end]);uid=v.field(s,'uuid')[1].strip('"')
        for k,(before,after) in r['track_endpoint_y_changes'].get(uid,{}).items():
            assert float(v.field(s,k)[2])==before;v.field(s,k)[2]=str(after)
        if uid in r['track_endpoint_y_changes']:count+=1;replacements.append((start,end,emit(s)))
    assert count==4 and len(replacements)==5
    for start,end,new in sorted(replacements,reverse=True):t=t[:start]+new+t[end:]
    return t

def main():
    assert sys.argv[1:]==['--apply']
    c=json.loads((S/'footprint-contract.json').read_text());assign=c['assignments'];base=c['baseline_commit']
    cad=M.parent/'reverb-600/cad';cir=M.parent/'reverb-600/circuit.json'
    paths=[cir,*cad.glob('*.kicad_sch'),*[M/'boards'/('Renegade_'+b+'.kicad_pcb') for b in ['Control','Reverb']]]
    original={p:p.read_text() for p in paths}
    for p,t in original.items():
        assert t==subprocess.check_output(['/usr/bin/git','show',base+':'+str(p.relative_to(ROOT))],cwd=ROOT).decode(),p
    changes={};source=json.loads(original[cir])
    for row in source['components']:
        if row['reference'] in assign:row['footprint']='Renegade_Selected:'+assign[row['reference']]
    changes[cir]=json.dumps(source,indent=2)+'\n'
    for p,t in original.items():
        if p==cir:continue
        kind='footprint' if p.suffix=='.kicad_pcb' else 'symbol';replacements=[]
        for start,end in spans(t,kind):
            node=v.parse(t[start:end]);ref=prop(node,'Reference')[2].strip('"')
            if ref not in assign:continue
            if kind=='symbol':prop(node,'Footprint')[2]=json.dumps('Renegade_Selected:'+assign[ref])
            else:
                lib=v.parse((S.parent/'footprints/Renegade_Selected.pretty'/(assign[ref]+'.kicad_mod')).read_text())
                node[1]=json.dumps('Renegade_Selected:'+assign[ref])
                # Remove generic DIP visual/model geometry, retain pad UUIDs and net mapping.
                node[:]=[x for x in node if not (isinstance(x,list) and (x[0].startswith('fp_') or x[0] in ['model','descr','tags']))]
                node.append(copy.deepcopy(v.field(lib,'descr')))
                for i,g in enumerate(x for x in lib if isinstance(x,list) and x[0].startswith('fp_')):
                    g=copy.deepcopy(g);g.append(['uuid',json.dumps(str(uuid.uuid5(uuid.NAMESPACE_URL,'renegade/socket/'+ref+'/'+str(i))))]);node.append(g)
                for pad in v.children(node,'pad'):
                    assert v.field(pad,'drill')[1]=='0.8'
                    v.field(pad,'drill')[1]=str(c['drill_mm'])
                    assert list(map(float,v.field(pad,'size')[1:]))==[c['pad_size_mm']]*2
            replacements.append((start,end,emit(node)))
        for start,end,new in reversed(replacements):t=t[:start]+new+t[end:]
        if p.name=='Renegade_Control.kicad_pcb':t=repair_bypass(t,c)
        if replacements:changes[p]=t
    for p,t in changes.items():p.write_text(t)
    print('\n'.join(str(p.relative_to(ROOT)) for p in changes))
if __name__=='__main__':main()
