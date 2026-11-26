"""Native DRC and drill evidence, guarded by phase-specific source hashes."""
import json
import subprocess
import sys
from integrate import M, ROOT, sha

def main():
    phase=sys.argv[1];assert phase in ['before','after']
    c=json.loads((M/'contract.json').read_text())
    hashes=c['input_sha256'] if phase=='before' else json.loads((M/'results/integration.json').read_text())['after_sha256']
    for path,h in hashes.items():assert sha(ROOT/path)==h,path
    cli='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
    commands=[]
    for path in c['reference_groups']:
        name=path.split('/')[-1].split('.')[0];out=M/'results'/phase/name;out.mkdir(parents=True,exist_ok=True)
        (out.parent/'CONTEXT.md').write_text(f'# {phase} native evidence\nOwner: PCB integration. Inputs: source-bound {phase} boards. Process: tools/export.py. Outputs: board-specific DRC and drill files. Human check: inspect actual pad/hole deltas; no fabrication release.\n')
        (out/'CONTEXT.md').write_text(f'# {name} {phase}\nOwner: PCB integration. Inputs: native {name}. Process: KiCad export. Outputs: DRC/drills. Human check: retain original findings and compare exact enlarged-hole coordinates.\n')
        cmds=[[cli,'pcb','drc','--format','json','--severity-all','--all-track-errors','-o',str(out/'drc.json'),str(ROOT/path)],
              [cli,'pcb','export','drill','--format','excellon','--excellon-units','mm','--output',str(out)+'/',str(ROOT/path)]]
        for cmd in cmds:
            p=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
            commands.append(dict(command=cmd,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,commands[-1]
    (M/'results'/(phase+'-commands.json')).write_text(json.dumps(commands,indent=2)+'\n')
    print(phase,'DRC/drills exported for both boards')

if __name__=='__main__':main()
