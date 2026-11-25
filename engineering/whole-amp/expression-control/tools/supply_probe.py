"""Causal solver diagnostics around the retained low-supply timeout."""
import json, sys, subprocess, hashlib
from pathlib import Path
import ota_screen as ota

def worker(case):
    sys.path.insert(0,str(ota.ROOT/'engineering/whole-amp/tools'))
    import spice_runtime as sp
    class LiveLogs(list):
        def append(self,line):
            super().append(line)
            if 'stderr' in line or 'Reference value' in line:
                print(line,file=sys.stderr,flush=True)
    sp.logs=LiveLogs()
    ota.deck=text
    # Preserve original deck separately to avoid recursive replacement.
    print('PHASE measure',file=sys.stderr,flush=True)
    print(json.dumps(ota.measure(case)))

original_deck=ota.deck
def text(case):
    s=original_deck(case)
    if case.get('nodeset'):
        s=s.replace('.end',f".nodeset v(out)={case.get('seed',0)} v(io)=0 v(plus)=.5 v(minus)=.5\n.end")
    return s

def main():
    trim=json.loads((ota.OUT/'ota-screen.json').read_text())['trim_fraction']
    rows=[]
    matrix=[('baseline12',{}),('dc12',{'dc_only':True}),
            ('shunt12',{'rshunt':1e10}),('nodeset12',{'nodeset':True}),
            ('seed-minus',{'nodeset':True,'seed':-1}),
            ('seed-plus',{'nodeset':True,'seed':1}),
            ('refined12',{'nodeset':True,'refine':2}),
            ('nodeset15',{'nodeset':True,'rail':15}),
            ('weak-shunt12',{'nodeset':True,'rshunt':1e13})]
    for name,extra in matrix:
        case=dict(rail=12,hz=1000,amplitude=8,trim_fraction=trim)|extra
        deck=text(case); filename='supply-'+name+'.cir';(ota.OUT/filename).write_text(deck)
        try:
            p=subprocess.run([sys.executable,__file__,'--case',json.dumps(case)],text=True,capture_output=True,timeout=25)
            result={'status':'complete',**json.loads(p.stdout)} if not p.returncode else {'status':'failed','error':p.stderr[-2000:]}
            log=p.stderr
        except subprocess.TimeoutExpired as e:
            result={'status':'timeout','seconds':25};log=e.stderr.decode(errors='replace') if isinstance(e.stderr,bytes) else (e.stderr or '')
        (ota.OUT/('supply-'+name+'.log')).write_text(log)
        result.pop('log',None)
        if 'op' in result:
            result['op_within_supply']=abs(result['op']['out'])<case['rail']
            result['interpretation']='physical OP bound passes' if result['op_within_supply'] else 'REJECT: output outside supply rails despite solver success'
        rows.append(dict(name=name,case=case,deck=filename,deck_sha256=hashlib.sha256(deck.encode()).hexdigest(),**result))
        print(name,result,flush=True)
    inputs=[Path(__file__),Path(ota.__file__),ota.OTA,ota.OP,ota.OUT/'ota-screen.json']
    provenance={str(p.relative_to(ota.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    (ota.OUT/'supply-probes.json').write_text(json.dumps({'scope':'Solver diagnostics only; original invalid OP retained as negative control. A rail-bounded OP is necessary, not sufficient for circuit qualification.','cases':rows,'provenance':provenance},indent=2)+'\n')

if __name__=='__main__':
    if len(sys.argv)>1: worker(json.loads(sys.argv[2]))
    else: main()
