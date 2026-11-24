import FreeCAD as App
import Part
import json,math,os
from pathlib import Path
out=Path(os.environ['RENEGADE_CAD_SMOKE_DIR']);out.mkdir(parents=True,exist_ok=True)
doc=App.newDocument('AutomationProbe')
plate=doc.addObject('Part::Box','Plate');plate.Length=80;plate.Width=40;plate.Height=2
hole=doc.addObject('Part::Cylinder','Hole');hole.Radius=2;hole.Height=2;hole.Placement.Base=App.Vector(10,10,0)
cut=doc.addObject('Part::Cut','DrilledPlate');cut.Base=plate;cut.Tool=hole
doc.recompute()
expected=80*40*2-math.pi*2**2*2
checks={'valid_solid':cut.Shape.isValid() and len(cut.Shape.Solids)==1,'hole_volume':abs(cut.Shape.Volume-expected)<1e-6}
doc.saveAs(str(out/'automation-probe.FCStd'))
Part.export([cut],str(out/'automation-probe.step'))
App.closeDocument(doc.Name)
reopened=App.openDocument(str(out/'automation-probe.FCStd'))
checks['native_reopens']=abs(reopened.getObject('DrilledPlate').Shape.Volume-expected)<1e-6
checks['editable_parameters']=reopened.getObject('Plate').Length.Value==80 and reopened.getObject('Hole').Radius.Value==2
App.closeDocument(reopened.Name)
shape=Part.Shape();shape.read(str(out/'automation-probe.step'))
checks['step_round_trip']=shape.isValid() and len(shape.Solids)==1 and abs(shape.Volume-expected)<1e-6
checks['dimensions_mm']=all(abs(a-b)<1e-6 for a,b in zip([shape.BoundBox.XLength,shape.BoundBox.YLength,shape.BoundBox.ZLength],[80,40,2]))
result={'version':App.Version(),'scope':'Automation test coupon only; not amplifier geometry','checks':checks,'passed':all(checks.values()),'tested_formats':['FCStd','STEP'],'untested_formats':['DXF flat pattern','TechDraw PDF','rendered image'],'fabrication_ready':False}
(out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
assert result['passed']
