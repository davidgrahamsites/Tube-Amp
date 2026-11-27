"""Read native placements; compare known package bounds with the measured tool.

Owns a conservative bench-access screen, not a full drill or chassis model.
"""
from pathlib import Path
import hashlib, json, math, sys
M = Path(__file__).resolve().parents[1]
ROOT = M.parents[2]
sys.path.insert(0, str(ROOT/'engineering/whole-amp/tools'))
import native_sexpr as sexpr
from check_socket_fit import transform, box

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def distance_to_box(point, bounds):
    dx = max(bounds[0]-point[0], 0, point[0]-bounds[2])
    dy = max(bounds[1]-point[1], 0, point[1]-bounds[3])
    return math.hypot(dx, dy)

def make_body(fp, center, size, height, seat):
    x,y=center; sx,sy=size
    bounds=box([transform(fp,(a,b)) for a in [x-sx/2,x+sx/2] for b in [y-sy/2,y+sy/2]])
    return {'bbox_xy_mm':bounds,'height_max_mm':height,'seating_allowance_mm':seat,'top_bound_mm':height+seat}

def main():
    contract_path=M/'tool-access-study.json'
    contract=json.loads(contract_path.read_text())
    fit=json.loads((M/'fit-register.json').read_text())
    tool=fit['drill_tool_measurements']
    sources=[contract_path,Path(__file__),M/'tools/check_socket_fit.py',ROOT/'engineering/whole-amp/tools/native_sexpr.py']
    candidate_path=M/contract['optional_driver_candidate'];sources.append(candidate_path);candidate=json.loads(candidate_path.read_text())
    specs={}
    for key,path in contract['package_contracts'].items():
        source=ROOT/path; sources.append(source); specs[key]=json.loads(source.read_text())
    seat=contract['additional_package_seating_mm_assumed']
    gap=contract['axial_handling_allowance_mm_assumed']
    head=contract['screw_head_plane_above_board_mm_assumed']
    radial=tool['provisional_radial_allowance_mm']
    radius=tool['chuck_diameter_mm']/2
    assert tool['bit_tip_to_tool_back_mm'] > tool['bit_projection_beyond_chuck_mm'] > 0
    bodies=[]; boards={}; missing={}
    for path in sorted((M.parent/'pcb-measured-r/boards').glob('*.kicad_pcb')):
        sources.append(path); name=path.stem.removeprefix('Renegade_')
        tree=sexpr.parse(path.read_text());fps=sexpr.fps(tree); holes=[]; known=set()
        edges=[e for e in sexpr.children(tree,'gr_line') if sexpr.field(e,'layer')[1]=='"Edge.Cuts"']
        assert len(edges)==4
        outline=[list(map(float,sexpr.field(e,k)[1:3])) for e in edges for k in ['start','end']]
        outline_bounds=box(outline)
        thickness=float(sexpr.field(sexpr.field(tree,'general'),'thickness')[1])
        for ref,fp in fps.items():
            identity=fp[1].strip('"').split(':')[-1]
            assert sexpr.field(fp,'layer')[1]=='"F.Cu"', 'Back-side component needs its own transform'
            if ref.startswith('H'):
                pads=sexpr.children(fp,'pad'); assert len(pads)==1
                p=pads[0]; assert p[2]=='np_thru_hole'
                drill=sexpr.field(p,'drill');assert len(drill)==2
                holes.append({'reference':ref,'xy_mm':list(transform(fp,sexpr.field(p,'at')[1:3])),'diameter_mm':float(drill[1])})
                continue
            item=None; source=None; status='Existing native selected package; assembly assumptions remain'
            sock=specs['sockets']; c=sock['common']
            for part in sock['packages'].values():
                if identity=='TE_'+part['mpn']+f'_DIP{round(2*(part["pin_span_mm"]/c["pitch_mm"]+1))}_Socket':
                    item=make_body(fp,[c['row_spacing_mm']/2,part['pin_span_mm']/2],[c['socket_width_max_mm'],max(part['socket_length_max_mm'],part['ic_length_max_mm'])],c['combined_height_bound_mm'],seat);source='sockets';status=sock['status']
            for part in specs['panasonic_radial']['parts']:
                if identity==part['footprint']:
                    diameter=part['body_diameter_mm']+part['body_diameter_tolerance_mm']
                    item=make_body(fp,[part['pitch_mm']/2,0],[diameter,diameter],part['body_length_mm']+part['body_length_tolerance_mm'],seat);source='panasonic_radial'
            for mpn,part in specs['knscha_film']['parts'].items():
                if identity=='KNSCHA_'+mpn:
                    sx,sy,h=part['body_max_W_T_H_mm']
                    item=make_body(fp,[part['nominal_pitch_mm']/2,0],[sx,sy],h,seat);source='knscha_film'
            part=specs['reverb_coupling']
            if identity==part['footprint'].split(':')[-1]:
                sx,sy,h=part['body']['maximum_mm'];item=make_body(fp,[part['body']['pitch_mm']/2,0],[sx,sy],h,seat);source='reverb_coupling'
            part=specs['power_film']
            if identity=='Panasonic_'+part['mpn']:
                sx,sy,h=[a+b for a,b in zip(part['body_nominal_L_W_H_mm'],part['body_tolerance_plus_minus_mm'])]
                item=make_body(fp,[v/2 for v in part['pitch_nominal_mm']],[sx,sy],h,seat);source='power_film';status=part['status']
            if item:
                item.update(board=name,reference=ref,footprint=identity,source_contract=contract['package_contracts'][source],part_status=status)
                bodies.append(item);known.add(ref)
        boards[name]={'outline_bbox_mm':outline_bounds,'thickness_mm':thickness,'holes':sorted(holes,key=lambda x:x['reference']),'non_mounting_footprints':len(fps)-len(holes),'known_bounds':len(known)}
        missing[name]=sorted(r for r in fps if r not in known and not r.startswith('H'))
    assert len(bodies)==31, len(bodies)
    projection=tool['bit_projection_beyond_chuck_mm']
    clear_projection=max(b['top_bound_mm'] for b in bodies)+gap-head
    cases=[]
    for bit_length,label,case_radius,case_rear in [(projection,'measured_bit',radius,tool['bit_tip_to_tool_back_mm']),(clear_projection,'height_clearance_trial',radius,tool['bit_tip_to_tool_back_mm']+clear_projection-projection),(0,'optional_precision_driver',candidate['body_diameter_mm_published']/2,candidate['body_length_mm_published']+max(candidate['nominal_bit_lengths_mm']))]:
        for board,details in boards.items():
            for hole in details['holes']:
                conflicts=[]; pairs=[]
                for body in [b for b in bodies if b['board']==board]:
                    distance=distance_to_box(hole['xy_mm'],body['bbox_xy_mm'])
                    vertical_gap=head+bit_length-body['top_bound_mm']
                    potential=vertical_gap<gap and distance<case_radius+radial
                    row={'part':body['reference'],'axis_to_body_xy_mm':distance,'radial_margin_mm':distance-case_radius-radial,'vertical_gap_mm':vertical_gap,'potential_chuck_conflict':potential}
                    pairs.append(row)
                    if potential:conflicts.append(row)
                cases.append({'board':board,'hole':hole['reference'],'bit_projection_mm':bit_length,'tool_radius_mm':case_radius,'tool_rear_bound_mm':case_rear,'case':label,'potential_chuck_conflicts':conflicts,'known_part_comparisons':pairs,'all_parts_access_verified':False})
    # Check corner distance and KiCad rotation; a bounding-box hit alone is insufficient.
    checks={'inside_distance':distance_to_box([1,1],[0,0,2,2])==0,'edge_distance':distance_to_box([3,1],[0,0,2,2])==1,'corner_distance':distance_to_box([5,6],[0,0,2,2])==5,'corner_outside_circle':distance_to_box([3,3],[0,0,2,2])>1.3,'corner_inside_circle':distance_to_box([3,3],[0,0,2,2])<1.5,'kicad_rotation':all(abs(a-b)<1e-9 for a,b in zip(transform(['footprint','test',['at','10','20','90']],(2,3)),(13,18))),'sixteen_mounts':sum(len(x['holes']) for x in boards.values())==16,'all_pairs_present':sum(len(c['known_part_comparisons']) for c in cases)==3*4*len(bodies),'trial_known_heights_clear':not any(c['potential_chuck_conflicts'] for c in cases if c['case']=='height_clearance_trial'),'release_held':not contract['fabrication_ready']}
    result={'id':contract['id'],'date':contract['date'],'scope':contract['scope'],'boards':boards,'known_package_bounds':bodies,'unknown_package_refs':missing,'measured_projection_mm':projection,'projection_to_clear_known_heights_mm':clear_projection,'chuck_radius_mm':radius,'radial_allowance_mm':radial,'axial_allowance_mm':gap,'cases':cases,'checks':checks,'checks_passed':all(checks.values()),'native_modified':False,'full_drill_access_verified':False,'fabrication_ready':False,'source_sha256':{str(p.relative_to(ROOT)):digest(p) for p in sources},'tool_source_used_fields':tool,'tool_source_sha256':hashlib.sha256(json.dumps(tool,sort_keys=True).encode()).hexdigest()}
    out=M/'review/bench-tool-access.json';out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'checks':checks,'known_parts':len(bodies),'unknown_parts':sum(map(len,missing.values())),'trial_projection_mm':clear_projection,'conflicts':[{k:v for k,v in c.items() if k!='known_part_comparisons'} for c in cases if c['potential_chuck_conflicts']]},indent=2));assert result['checks_passed']

if __name__=='__main__':main()
