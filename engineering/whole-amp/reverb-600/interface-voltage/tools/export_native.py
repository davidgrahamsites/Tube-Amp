"""Export actual before/after sources; never reconstruct a visual baseline."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

M=Path(__file__).resolve().parents[1]; ROOT=M.parents[3]; D=M/'results'
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
phase=sys.argv[1]; assert phase in ['before','after']
c=json.loads((M/'contract.json').read_text())
expected=c['native_sha256'] if phase=='before' else json.loads((D/'integration.json').read_text())['after_sha256']
for p,h in expected.items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
s=ROOT/'engineering/whole-amp/reverb-600/cad/Renegade_220V_Reverb.kicad_sch'
b=ROOT/'engineering/whole-amp/pcb-measured-r/boards/Renegade_Reverb.kicad_pcb'
commands=[]
for cmd in [
    [CLI,'sch','export','netlist','--format','kicadxml','-o',str(D/(phase+'.xml')),str(s)],
    [CLI,'sch','erc','--format','json','--severity-all','-o',str(D/(phase+'-erc.json')),str(s)],
    [CLI,'sch','export','pdf','-o',str(D/(phase+'.pdf')),str(s)],
    [CLI,'pcb','drc','--format','json','--severity-all','--all-track-errors','-o',str(D/(phase+'-drc.json')),str(b)]
]:
    r=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
    commands.append(dict(command=cmd,exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr))
    assert r.returncode==0,commands[-1]
(D/(phase+'-commands.json')).write_text(json.dumps(commands,indent=2)+'\n')
print(phase,'native exports complete')
