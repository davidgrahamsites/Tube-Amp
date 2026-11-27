"""FreeCAD model of FIT-012 known bounds, independent solid-intersection check."""
from pathlib import Path
import hashlib,json,math
import FreeCAD as App
import Part
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2];OUT=M/'review'
source=OUT/'bench-tool-access.json';r=json.loads(source.read_text())
for path,h in r['source_sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
assert r['checks_passed']
doc=App.newDocument('BenchAccessBounds')
doc.Comment='FIT-012: known maximum package bounds, exploded board display. NOT populated chassis or fabrication model.'
solids=[];body_objects={};offsets={};checks={};hits=[]
for idx,(name,board) in enumerate(sorted(r['boards'].items())):
    offset=idx*400;offsets[name]=offset
    x0,y0,x1,y1=board['outline_bbox_mm'];th=board['thickness_mm']
    blank=doc.addObject('Part::Box',name+'Blank');blank.Length=x1-x0;blank.Width=y1-y0;blank.Height=th;blank.Placement.Base=App.Vector(x0+offset,y0,-th);current=blank
    expected=(x1-x0)*(y1-y0)*th
    for hole in board['holes']:
        x,y=hole['xy_mm'];c=doc.addObject('Part::Cylinder',name+hole['reference']+'Drill');c.Radius=hole['diameter_mm']/2;c.Height=th;c.Placement.Base=App.Vector(x+offset,y,-th)
        cut=doc.addObject('Part::Cut',name+hole['reference']+'Cut');cut.Base=current;cut.Tool=c;current=cut;expected-=math.pi*c.Radius.Value**2*th
    doc.recompute();checks[name+'_board_volume']=abs(current.Shape.Volume-expected)<1e-7;solids.append(current)
    for body in [b for b in r['known_package_bounds'] if b['board']==name]:
        x0,y0,x1,y1=body['bbox_xy_mm'];o=doc.addObject('Part::Box',name+body['reference']+'Bound');o.Length=x1-x0;o.Width=y1-y0;o.Height=body['top_bound_mm'];o.Placement.Base=App.Vector(offset+x0,y0,0)
        o.Label=name+' '+body['reference']+' MAX BOUND ONLY';o.addProperty('App::PropertyString','Evidence').Evidence=body['source_contract'];o.addProperty('App::PropertyString','Qualification').Qualification=body['part_status'];solids.append(o);body_objects[(name,body['reference'])]=o
    doc.recompute()
    for case in [c for c in r['cases'] if c['board']==name]:
        hole=next(h for h in board['holes'] if h['reference']==case['hole']);x,y=hole['xy_mm'];z=case['bit_projection_mm']-r['axial_allowance_mm']
        tool_shape=Part.makeCylinder(case['tool_radius_mm']+r['radial_allowance_mm'],case['tool_rear_bound_mm']-z,App.Vector(offset+x,y,z))
        for comparison in case['known_part_comparisons']:
            volume=tool_shape.common(body_objects[(name,comparison['part'])].Shape).Volume
            hit=volume>1e-7
            key=name+case['hole']+case['case']+comparison['part'];checks[key]=hit==comparison['potential_chuck_conflict']
            if hit:hits.append({'board':name,'hole':case['hole'],'case':case['case'],'part':comparison['part'],'intersection_mm3':volume})
# Export known body bounds and PCB solids. Tool cylinders are transient check geometry.
doc.recompute();checks['valid_solids']=all(o.Shape.isValid() and len(o.Shape.Solids)==1 for o in solids)
App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
fc=OUT/'bench-access-bounds.FCStd';step=OUT/'bench-access-bounds.step'
def bbox(shape):
    b=shape.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XLength,b.YLength,b.ZLength]
expected_boxes=sorted(bbox(o.Shape) for o in solids);expected_volume=sum(o.Shape.Volume for o in solids)
doc.saveAs(str(fc));Part.export(solids,str(step));App.closeDocument(doc.Name)
doc=App.openDocument(str(fc));checks['editable_body_reopen']=all(abs(doc.getObject(name+ref+'Bound').Height.Value-next(b['top_bound_mm'] for b in r['known_package_bounds'] if b['board']==name and b['reference']==ref))<1e-9 for name,ref in body_objects);App.closeDocument(doc.Name)
shape=Part.Shape();shape.read(str(step));actual_boxes=sorted(bbox(s) for s in shape.Solids)
checks['step_35_solids']=len(shape.Solids)==len(solids)==35
checks['step_positions']=len(actual_boxes)==len(expected_boxes) and all(abs(a-b)<1e-6 for aa,bb in zip(actual_boxes,expected_boxes) for a,b in zip(aa,bb))
checks['step_volume']=abs(shape.Volume-expected_volume)<1e-5
result={'scope':'FIT-012 independent CAD intersections and round-trip; no complete tool/assembly approval','FreeCAD_version':App.Version(),'checks_count':len(checks),'checks':checks,'passed':all(checks.values()),'known_bounds':len(body_objects),'conflicts':hits,'display_board_offsets_x_mm':offsets,'fabrication_ready':False,'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,Path(__file__)]},'output_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [fc,step]}}
(OUT/'bench-access-cad-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':result['passed'],'checks':len(checks),'conflicts':hits},indent=2));assert result['passed']
