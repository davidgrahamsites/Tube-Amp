from pathlib import Path
import subprocess,json
R=Path(__file__).resolve().parents[1];cli='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli';board=str(R/'pcb/Renegade_Reverb.kicad_pcb');logs=[]
commands=[['pcb','export','gerbers','-o',str(R/'pcb/fabrication-preview')+'/', '-l','F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,Edge.Cuts','--subtract-soldermask',board],['pcb','export','drill','-o',str(R/'pcb/fabrication-preview')+'/','--excellon-separate-th','--generate-map','--map-format','pdf','--generate-report','--report-path',str(R/'validation/drill-report.txt'),board],['pcb','export','svg','--mode-single','--page-size-mode','2','--exclude-drawing-sheet','-o',str(R/'validation/pcb-final.svg'),'-l','B.Cu,F.Cu,F.Silkscreen,Edge.Cuts',board],['sch','export','pdf','--draw-hop-over','-o',str(R/'pcb/Renegade_Reverb.pdf'),str(R/'pcb/Renegade_Reverb.kicad_sch')]]
for args in commands:
 p=subprocess.run([cli,*args],capture_output=True,text=True);logs.append({'command':[cli,*args],'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0,logs[-1]
(R/'validation/final-exports.json').write_text(json.dumps(logs,indent=2));print('Four native export operations passed')
