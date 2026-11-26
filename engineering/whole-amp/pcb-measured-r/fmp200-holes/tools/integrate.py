"""Correct only FMP200 drills, pads, courtyard ends and misleading tags."""
from pathlib import Path
import hashlib
import json
import sys
M=Path(__file__).resolve().parents[1]
ROOT=M.parents[3]
sys.path.insert(0,str(ROOT/'engineering/whole-amp/tools'))
import native_sexpr as n
sys.path.insert(0,str(ROOT/'engineering/whole-amp/reverb-600/interface-voltage/tools'))
from correct_metadata import spans

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def emit(x):return '('+' '.join(emit(y) if isinstance(y,list) else y for y in x)+')'

def correct(f,c):
    pads=n.children(f,'pad');assert len(pads)==2
    for pad in pads:
        assert n.field(pad,'drill')[1:]==[str(c['old_drill_mm'])]
        assert n.field(pad,'size')[1:]==[str(c['old_pad_mm'])]*2
        n.field(pad,'drill')[1]=str(c['new_drill_mm'])
        n.field(pad,'size')[1:]=[str(c['new_pad_mm'])]*2
    court=next(x for x in n.children(f,'fp_rect') if n.field(x,'layer')[1]=='"F.CrtYd"')
    assert [float(n.field(court,k)[1]) for k in ['start','end']]==c['old_courtyard_x_mm']
    for key,x in zip(['start','end'],c['new_courtyard_x_mm']):n.field(court,key)[1]=str(x)
    # Clear the enlarged front pad with the existing lead silkscreen lines.
    count=0
    for line in n.children(f,'fp_line'):
        if n.field(line,'layer')[1]!='"F.SilkS"':continue
        start=n.field(line,'start')
        if start[1:]==['1.04','0']:start[1]='1.15';count+=1
        elif start[1:]==['14.2','0']:start[1]='14.09';count+=1
    assert count==2
    n.field(f,'tags')[1]='"Yageo FMP200 axial flameproof 2W at70C; formed pitch15.24mm"'
    return f

def main():
    assert sys.argv[1:]==['--apply']
    c=json.loads((M/'contract.json').read_text())
    for p,h in c['input_sha256'].items():assert sha(ROOT/p)==h,p
    assert sha(ROOT/c['datasheet_path'])==c['datasheet_sha256']
    changes={};lib=next(iter(c['input_sha256']))
    changes[lib]=emit(correct(n.parse((ROOT/lib).read_text()),c))+'\n'
    for path,refs in c['reference_groups'].items():
        text=(ROOT/path).read_text();changed=[]
        for a,b in reversed(list(spans(text,'footprint'))):
            f=n.parse(text[a:b])
            ref=next(x[2].strip('"') for x in n.children(f,'property') if x[1]=='"Reference"')
            if ref not in refs:continue
            assert f[1].strip('"')==c['library_id']
            text=text[:a]+emit(correct(f,c))+text[b:];changed.append(ref)
        assert set(changed)==set(refs)
        changes[path]=text
    for p,t in changes.items():n.parse(t);(ROOT/p).write_text(t)
    (M/'results/integration.json').write_text(json.dumps({'after_sha256':{p:sha(ROOT/p) for p in changes},'resistors':13,'resized_holes':26,'moved_parts':0,'changed_tracks':0,'fabrication_ready':False},indent=2)+'\n')
    print('Corrected 13 FMP200 packages / 26 holes; no placement or routing changes.')

if __name__=='__main__':main()
