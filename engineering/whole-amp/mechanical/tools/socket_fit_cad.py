"""FreeCAD consumer: five socket/IC bounds and service volumes in trial poses.

Run after board_fit_cad.py and check_socket_fit.py. No source CAD edits.
"""
import FreeCAD as App
import Part
import hashlib,json
from pathlib import Path
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2];OUT=M/'review'
paths=[OUT/'board-fit-diagnostic.json',OUT/'socket-fit-checks.json',M.parent/'pcb-measured-r/review/mechanical-inventory.json']
base,screen,inv=[json.loads(p.read_text()) for p in paths]
assert base['geometry_checks_passed']
assert base['source_hashes']['mechanical-inventory.json']==hashlib.sha256(paths[2].read_bytes()).hexdigest()
for p,h in screen['source_sha256'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
doc=App.openDocument(str(OUT/'board-fit-diagnostic.FCStd'))
doc.Comment='NOT FOR MANUFACTURE. Five DIP assembly envelopes only; other components omitted; drill clearance pending.'
solids=[doc.getObject(n+'Export') for n in base['poses']];rows=[];services=[]
for row in screen['rows']:
    ref=row['reference'];name=row['board'].removeprefix('Renegade_');pose=base['poses'][name];board=inv['boards'][name]
    assert pose['rotation_z_deg']==0,'Socket transform for rotated PCB requires explicit implementation'
    x0,y0,x1,y1=row['body_bbox_mm'];ox,oy=board['origin_mm'];x,y,z=pose['bbox_min_mm'];z+=board['size_mm'][2]
    at=[x+x0-ox,y+y0-oy,z];size=[x1-x0,y1-y0,row['combined_height_bound_mm']]
    def box(suffix,height):
        o=doc.addObject('Part::Box',ref+suffix);o.Length,o.Width,o.Height=size[0],size[1],height;o.Placement.Base=App.Vector(*at)
        o.addProperty('App::PropertyString','Evidence').Evidence='socket-envelope.json; symmetric placement assumption, sample pending'
        return o
    body=box('SocketICEnvelope',size[2]);body.Label=ref+' socket + IC MAX BOUND (not detailed part)';solids.append(body)
    service=box('VerticalServiceReserve',row['planning_top_and_extraction_mm']);service.Label=ref+' SERVICE SPACE ONLY — provisional 27mm';services.append((ref,name,service,body))
    rows.append(dict(reference=ref,board=name,body_at_mm=at,body_size_mm=size,service_height_mm=service.Height.Value,
      nominal_headroom_to_assumed_ceiling_mm=base['assumed_datum_mm'][2]-(z+service.Height.Value)))
doc.recompute();collisions=[]
for ref,name,service,body in services:
    for other in solids:
        if other==body or other.Name==name+'Export':continue
        intersection=service.Shape.common(other.Shape)
        if intersection.Volume>1e-7:collisions.append(dict(reference=ref,other=other.Name,intersection_mm3=intersection.Volume))
    assert body.Shape.isValid() and service.Shape.isValid()
App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
fc=OUT/'socket-fit-diagnostic.FCStd';step=OUT/'socket-fit-diagnostic.step'
doc.recompute();doc.saveAs(str(fc));Part.export(solids,str(step))
expected=sorted((o.Shape.BoundBox.XMin,o.Shape.BoundBox.YMin,o.Shape.BoundBox.ZMin,o.Shape.BoundBox.XLength,o.Shape.BoundBox.YLength,o.Shape.BoundBox.ZLength) for o in solids)
App.closeDocument(doc.Name);reopened=App.openDocument(str(fc))
native=all(reopened.getObject(row['reference']+'VerticalServiceReserve').Height.Value==row['service_height_mm'] for row in rows)
App.closeDocument(reopened.Name);shape=Part.Shape();shape.read(str(step))
actual=sorted((o.BoundBox.XMin,o.BoundBox.YMin,o.BoundBox.ZMin,o.BoundBox.XLength,o.BoundBox.YLength,o.BoundBox.ZLength) for o in shape.Solids)
roundtrip=len(actual)==len(expected)==9 and all(abs(a-b)<1e-5 for aa,bb in zip(actual,expected) for a,b in zip(aa,bb))
assert native and shape.isValid() and roundtrip
result=dict(scope='Five socket/IC envelopes in existing trial board poses; NOT chassis approval',rows=rows,
  known_solid_service_intersections=collisions,native_reopen_pass=native,step_nine_solids_and_positions_match=roundtrip,
  existing_board_support_plane_failures=base['planes'],missing_component_models=sum(len(b['missing_3d_models']) for b in inv['boards'].values()),
  limits=['Other component/harness/thermal and retention envelopes omitted','27mm service reserve is provisional, not a measured extraction path','Cabinet common datum and three-board consolidation unverified','No rear cover or whole-chassis withdrawal sweep modeled'],
  drill_clearance='PENDING — see fit-register.json/drill_tool_measurements and tool-access-checks.json for partial measurements',rear_cover_attachment_allowed=False,assembly_fit_cleared=False,fabrication_ready=False,
  source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*paths,Path(__file__)]},
  output_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [fc,step]})
(OUT/'socket-fit-cad-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print('SOCKET CAD GEOMETRY VERIFIED; ASSEMBLY NOT CLEARED; KNOWN INTERSECTIONS',len(collisions))
