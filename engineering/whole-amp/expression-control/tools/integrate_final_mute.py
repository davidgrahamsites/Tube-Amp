"""Guarded two-pin repair: use K3's spare NC pole for the final wet output."""
import copy, hashlib, json, subprocess, sys, uuid
from pathlib import Path
import ota_screen as ota
sys.path.insert(0,str(ota.ROOT/'engineering/whole-amp/tools'))
import native_sexpr as v
sys.path.insert(0,str(ota.ROOT/'engineering/whole-amp/control-switching/tools'))
from integrate_drivers import spans, emit, prop
BASE='df83862dc41f3e43d8d19ec3ee582cc0113abc11'
CIR='engineering/whole-amp/reverb-600/circuit.json'
SCH='engineering/whole-amp/reverb-600/cad/07c_reverb_output.kicad_sch'
PCB='engineering/whole-amp/pcb-measured-r/boards/Renegade_Reverb.kicad_pcb'
Q=json.dumps
uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'renegade/final-wet-mute/2026-11-25/'+s))
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def identity(x):return v.field(x,'uuid')[1] if isinstance(x,list) and v.children(x,'uuid') else None
def patch(text,after):
    before=v.parse(text);old={identity(x):x for x in before[1:] if identity(x)};new={identity(x):x for x in after[1:] if identity(x)}
    edits=[]
    for kind in {x[0] for x in before[1:] if isinstance(x,list)}:
        for start,end in spans(text,kind):
            x=v.parse(text[start:end]);key=identity(x)
            if key and key not in new:edits.append((start,end,''))
            elif key and x!=new[key]:edits.append((start,end,emit(new[key])))
    for start,end,t in sorted(edits,reverse=True):text=text[:start]+t+text[end:]
    additions=[x for x in after[1:] if identity(x) and identity(x) not in old]
    return text.rstrip()[:-1]+'\n'+'\n'.join(emit(x) for x in additions)+')\n'
def wire(p,q,name):return v.parse(f'(wire (pts (xy {p[0]} {p[1]}) (xy {q[0]} {q[1]})) (stroke (width 0) (type default)) (uuid {uid(name)}))')
def renew(x):
    for item in x:
        if isinstance(item,list):
            if item[0]=='uuid':item[1]=uid(item[1])
            else:renew(item)
def main():
    assert sys.argv[1:]==['--apply']
    receipt=ota.OUT/'final-mute-integration.json';assert not receipt.exists()
    old={p:(ota.ROOT/p).read_text() for p in [CIR,SCH,PCB]}
    for p,s in old.items():assert s==subprocess.check_output(['git','show',BASE+':'+p],cwd=ota.ROOT,text=True),p
    circuit=json.loads(old[CIR]);sch=v.parse(old[SCH]);pcb=v.parse(old[PCB])
    row=next(c for c in circuit['components'] if c['reference']=='K3' and c['unit']==3)
    assert row['pins']=={'13':None,'11':None,'9':None}
    row['pins']={'13':'WET_AC','11':'GND','9':None}
    # Place the existing contact directly below its output branch; no symbol replacement.
    contact=next(s for s in v.children(sch,'symbol') if prop(s,'Reference')[2]=='"K3"' and v.field(s,'unit')[1]=='3')
    v.field(contact,'at')[1:]=['243.84','110.49','180']
    for p in v.children(contact,'property'):
        at=v.field(p,'at');at[1:]=['251.46','110.49','0']
    v.field(prop(contact,'Reference'),'at')[2]='106.68'
    v.field(prop(contact,'Value'),'at')[2]='109.22'
    nc=v.children(sch,'no_connect');assert len(nc)==3
    sch=[x for x in sch if x not in nc]
    sch.append(v.parse(f'(no_connect (at 241.3 118.11) (uuid {uid("nc9")}))'))
    branch=next(w for w in v.children(sch,'wire') if v.field(w,'pts')[1:]==[['xy','228.6','90.17'],['xy','266.7','90.17']])
    sch.remove(branch)
    for name,p,q in [('branch-left',(228.6,90.17),(243.84,90.17)),('branch-right',(243.84,90.17),(266.7,90.17)),('common13',(243.84,90.17),(243.84,102.87)),('nc11',(246.38,118.11),(246.38,123.19))]:sch.append(wire(p,q,name))
    sch.append(v.parse(f'(junction (at 243.84 90.17) (diameter 0) (color 0 0 0 0) (uuid {uid("junction")}))'))
    g=copy.deepcopy(next(s for s in v.children(sch,'symbol') if prop(s,'Value')[2]=='"GND"' and v.field(s,'at')[1:3]==['266.7','107.95']))
    renew(g);v.field(g,'at')[1:3]=['246.38','123.19']
    for p in v.children(g,'property'):
        at=v.field(p,'at');at[1]=str(float(at[1])-20.32);at[2]=str(float(at[2])+15.24)
    prop(g,'Reference')[2]='"#PWR0799"'
    v.field(v.field(v.field(v.field(g,'instances'),'project'),'path'),'reference')[1]='"#PWR0799"'
    sch.append(g)
    sch.append(v.parse(f'(text "K3C: final wet shunt when relay is OFF.\\n[TBD-MEASURE] Rail-fault inhibit and release timing." (at 222.25 132.08 0) (effects (font (size 1.1 1.1)) (justify left top)) (uuid {uid("note")}))'))
    f=v.fps(pcb)['K3']
    for n,net in [('13','WET_AC'),('11','GND')]:
        pad=next(p for p in v.children(f,'pad') if p[1]==Q(n));assert not v.children(pad,'net');pad.append(['net',Q(net)])
    for index,(layer,net,p,q) in enumerate([
        ('F.Cu','WET_AC',(121.62,24.62),(123.62,26.62)),
        ('F.Cu','WET_AC',(123.62,26.62),(123.62,30.62)),
        ('B.Cu','WET_AC',(123.62,30.62),(125,32)),
        ('B.Cu','WET_AC',(125,32),(132,32)),
        ('B.Cu','GND',(121.62,29.7),(114,29.7))]):
        pcb.append(v.parse(f'(segment (start {p[0]} {p[1]}) (end {q[0]} {q[1]}) (width 0.4) (layer "{layer}") (net "{net}") (uuid "{uid("route"+str(index))}"))'))
    pcb.append(v.parse(f'(via (at 123.62 30.62) (size 0.8) (drill 0.4) (layers "F.Cu" "B.Cu") (net "WET_AC") (uuid "{uid("via")}"))'))
    changed={CIR:json.dumps(circuit,indent=2)+'\n',SCH:patch(old[SCH],sch),PCB:patch(old[PCB],pcb)}
    for p,s in changed.items():
        if p!=CIR:v.parse(s)
        (ota.ROOT/p).write_text(s)
    receipt.write_text(json.dumps(dict(baseline_commit=BASE,pin_changes={'K3.13':[None,'WET_AC'],'K3.11':[None,'GND']},before_sha256={p:sha(s) for p,s in old.items()},after_sha256={p:sha(s) for p,s in changed.items()},native_checks_pending=True,rail_fault_monitor_implemented=False),indent=2)+'\n')
    print('Connected K3 spare NC contact; native gates pending.')
if __name__=='__main__':main()
