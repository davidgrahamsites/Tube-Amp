"""Read-only strict native checks; temporary copies include project rules and library resolution."""
from pathlib import Path
from tempfile import TemporaryDirectory
from collections import Counter
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[5]
MODULE=Path(__file__).resolve().parents[1]
BOARD=ROOT/'engineering/whole-amp/pcb-measured-r/boards'
CAD=ROOT/'engineering/whole-amp/reverb-600/cad'
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def main():
 stage=sys.argv[1];assert stage in ['before','after'];out=MODULE/'results';rows={}
 names=['Control','Reverb'] if stage=='before' else ['Main','Power','Control','Reverb']
 for name in names:
  source=BOARD/f'Renegade_{name}.kicad_pcb';before=hashlib.sha256(source.read_bytes()).hexdigest()
  with TemporaryDirectory(prefix='renegade-fr-drc-') as tmp:
   target=Path(tmp)/source.name
   for ext in ['.kicad_pcb','.kicad_pro','.kicad_dru']:target.with_suffix(ext).write_bytes(source.with_suffix(ext).read_bytes())
   (Path(tmp)/'fp-lib-table').write_text((BOARD/'fp-lib-table').read_text().replace('${KIPRJMOD}',str(BOARD)))
   pro=target.with_suffix('.kicad_pro');data=json.loads(pro.read_text());ds=data['board']['design_settings'];ds['drc_exclusions']=[]
   for key,val in ds.setdefault('rule_severities',{}).items():
    if val=='ignore':ds['rule_severities'][key]='warning'
   pro.write_text(json.dumps(data))
   cmd=[CLI,'pcb','drc','--format','json','--severity-all','--all-track-errors','--refill-zones','-o',str(out/f'{stage}-{name}-drc.json'),str(target)]
   proc=subprocess.run(cmd,capture_output=True,text=True);assert proc.returncode==0,proc.stdout+proc.stderr
   r=json.loads((out/f'{stage}-{name}-drc.json').read_text());rows[name]={'violations':dict(Counter(v['type'] for v in r['violations'])),'unconnected':len(r['unconnected_items']),'source_sha256':before}
  assert before==hashlib.sha256(source.read_bytes()).hexdigest()
 subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(out/f'{stage}.xml'),str(CAD/'Renegade_220V_Reverb.kicad_sch')],check=True,capture_output=True)
 subprocess.run([CLI,'sch','erc','--format','json','--severity-all','-o',str(out/f'{stage}-erc.json'),str(CAD/'Renegade_220V_Reverb.kicad_sch')],check=True,capture_output=True)
 (out/f'{stage}-native-summary.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
