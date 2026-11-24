"""FreeCAD diagnostic: native PCB outlines/holes in a declared trial arrangement.
Inputs are the fit register and read-only PCB mechanical inventory. No final chassis.
"""
import FreeCAD as App
import Part
from pathlib import Path
import hashlib,json,math
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'review'
r=json.loads((ROOT/'fit-register.json').read_text(encoding='utf-8'));study=r['pcb_envelope_study'];m=r['cabinet']['user_measurements']
invpath=ROOT.parent/'pcb-measured-r/review/mechanical-inventory.json';inv=json.loads(invpath.read_text(encoding='utf-8'))
# This object is a datum assumption, not a model of cabinet walls or clear space.
w=m['A_rear_clear_width_mm'];d=m['B_rear_edge_depth_mm'];h=m['P3_obstruction_report']['P3_inside_height_mm']
for b in inv['boards'].values():assert hashlib.sha256((ROOT.parents[2]/b['path']).read_bytes()).hexdigest()==b['sha256']
doc=App.newDocument('BoardFitDiagnostic');doc.Comment='NOT FOR MANUFACTURE. Board-only trial; no populated fit or drill approval.'
def box(name,size,at):
    o=doc.addObject('Part::Box',name);o.Length,o.Width,o.Height=size;o.Placement.Base=App.Vector(*at);return o
space=box('AssumedCabinetDatumEnvelope',[w,d,h],[0,0,0]);space.addProperty('App::PropertyString','Evidence').Evidence='467 and383 user readings;160 depth datum uncertain; common rectangular volume unverified'
objects=[];checks={};poses={};planes=[]
for idx,names in enumerate(study['planes']):
    edge=study['construction_edge_allowance_mm'];side=study['side_flange_budget_mm'];gap=study['board_gap_mm'];x=edge+side;y=edge;z=h-study['upper_plane_below_top_mm']-idx*study['plane_spacing_mm'];maxdepth=0
    for name in names:
        b=inv['boards'][name];sx,sy,th=b['size_mm'];plate=box(name+'Blank',[sx,sy,th],[0,0,0]);shape=plate
        expected=sx*sy*th
        for hole in sorted(b['mounting_holes'],key=lambda q:q['ref']):
            holeobj=doc.addObject('Part::Cylinder',name+hole['ref']);holeobj.Radius=hole['diameter_mm']/2;holeobj.Height=th
            holeobj.Placement.Base=App.Vector(*hole['at_from_outline_mm'],0)
            cut=doc.addObject('Part::Cut',name+hole['ref']+'Cut');cut.Base=shape;cut.Tool=holeobj;shape=cut
            expected-=math.pi*holeobj.Radius.Value**2*th
        rot=name in study['rotate_90'];extent=[sy,sx,th] if rot else [sx,sy,th]
        # Use an App::Part group so the editable solid/holes transform together.
        group=doc.addObject('App::Part',name+'Board')
        members=[o for o in doc.Objects if o.Name.startswith(name) and o!=group]
        for o in members:group.addObject(o)
        group.Placement=App.Placement(App.Vector(x+sy if rot else x,y,z),App.Rotation(App.Vector(0,0,1),90 if rot else 0))
        shape.Label=name+' PCB ONLY — components omitted';doc.recompute()
        checks[name]=dict(valid_solid=shape.Shape.isValid() and len(shape.Shape.Solids)==1,volume_matches_drilled_outline=abs(shape.Shape.Volume-expected)<1e-6)
        poses[name]=dict(bbox_min_mm=[x,y,z],bbox_size_mm=extent,rotation_z_deg=90 if rot else 0,within_assumed_datum_box=x+extent[0]<=w and y+extent[1]<=d and z+th<=h)
        # Export a transformed solid explicitly; group placement is global placement.
        export=doc.addObject('Part::Feature',name+'Export');export.Shape=shape.Shape.copy();export.Placement=group.Placement;objects.append(export)
        x+=extent[0]+gap;maxdepth=max(maxdepth,extent[1])
    required=[x-gap+edge+side,maxdepth+2*edge]
    planes.append(dict(boards=names,required_support_budget_mm=required,width_excess_mm=max(0,required[0]-w),depth_excess_mm=max(0,required[1]-d)))
doc.recompute()
# Native products are current-only; disable automatic full document backups here.
App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
fc=OUT/'board-fit-diagnostic.FCStd';step=OUT/'board-fit-diagnostic.step'
doc.saveAs(str(fc));Part.export(objects,str(step))
expected_volume=sum(o.Shape.Volume for o in objects);App.closeDocument(doc.Name)
reopened=App.openDocument(str(fc));native_checks={n:all(abs(a-b)<1e-6 for a,b in zip([reopened.getObject(n+'Blank').Length.Value,reopened.getObject(n+'Blank').Width.Value,reopened.getObject(n+'Blank').Height.Value],inv['boards'][n]['size_mm'])) for n in poses};App.closeDocument(reopened.Name)
s=Part.Shape();s.read(str(step));expected_boxes=sorted(tuple(q['bbox_min_mm']+q['bbox_size_mm']) for q in poses.values())
actual_boxes=sorted((q.BoundBox.XMin,q.BoundBox.YMin,q.BoundBox.ZMin,q.BoundBox.XLength,q.BoundBox.YLength,q.BoundBox.ZLength) for q in s.Solids)
position_check=len(actual_boxes)==len(expected_boxes) and all(abs(a-b)<1e-5 for aa,bb in zip(actual_boxes,expected_boxes) for a,b in zip(aa,bb))
roundtrip=s.isValid() and len(s.Solids)==4 and abs(s.Volume-expected_volume)<1e-5 and position_check
result=dict(scope='Existing four-board diagnostic; NOT a populated assembly or manufactured chassis',version=App.Version(),source_hashes={'fit-register-used-fields':hashlib.sha256(json.dumps(dict(datum_mm=[w,d,h],study=study),sort_keys=True).encode()).hexdigest(),'mechanical-inventory.json':hashlib.sha256(invpath.read_bytes()).hexdigest(),'factory':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},assumed_datum_mm=[w,d,h],poses=poses,planes=planes,solid_checks=checks,native_reopen_checks=native_checks,step_round_trip=roundtrip,step_positions_match=position_check,geometry_checks_passed=all(all(c.values()) for c in checks.values()) and all(native_checks.values()) and roundtrip,missing_component_models=sum(len(b['missing_3d_models']) for b in inv['boards'].values()),drill_clearance='PENDING until tool dimensions supplied',rear_cover_removal='Not geometrically qualified; fixed-support constraint retained',assembly_fit_cleared=False,fabrication_ready=False)
(OUT/'board-fit-diagnostic.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');assert result['geometry_checks_passed'];print('BOARD FIT DIAGNOSTIC GEOMETRY PASS; ASSEMBLY NOT CLEARED')
