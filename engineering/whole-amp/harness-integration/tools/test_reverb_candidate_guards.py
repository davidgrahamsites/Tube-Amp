#!/usr/bin/env python3
"""Reject width and endpoint corruption in disposable candidate copies."""
import contextlib,io,json,shutil,tempfile
import check_reverb_connector as check

def main():
 current=check.O;spec=json.loads((check.M/'reverb-connector-placement.json').read_text());board=current/'Renegade_Reverb.kicad_pcb';original=board.read_text();out={}
 cases=[('undersized_relay','68488812-29eb-4ed2-afd3-1d0af37df731','width',['0.3'],'declared_native_widths_and_necks'),('altered_ground_endpoint','4b832704-4ee7-46b0-b7b4-31adaf96e301','start',['136.6','26.5'],'existing_routes_only_declared_width_and_endpoint_changes'),('widened_HV_adjacent_neck','c4c22678-0f5a-4707-afb0-16b0b39b7930','width',['0.8'],'declared_native_widths_and_necks')]
 for label,uuid,field,value,gate in cases:
  with tempfile.TemporaryDirectory(prefix='guard-',dir=current) as td:
   check.O=check.Path(td)
   for ext in ['.kicad_pro','.kicad_dru']:shutil.copyfile(board.with_suffix(ext),check.O/(board.stem+ext))
   (check.O/'fp-lib-table').write_text((current/'fp-lib-table').read_text().replace('${KIPRJMOD}',str(current)))
   changed=original;found=False
   for a,z in check.spans(original,'segment'):
    if check.uid(original[a:z])==uuid:
     node=check.v.parse(original[a:z]);check.v.field(node,field)[1:]=value
     from integrate_drivers import emit
     changed=original[:a]+emit(node)+original[z:];found=True;break
   assert found
   (check.O/board.name).write_text(changed);rejected=False
   try:
    with contextlib.redirect_stdout(io.StringIO()):check.main()
   except AssertionError:rejected=True
   receipt=json.loads((check.O/'checks.json').read_text())
   out[label]={'rejected':rejected,'target_gate_failed':receipt['checks'][gate] is False,'failed_checks':[k for k,v in receipt['checks'].items() if not v],'drc':receipt['drc']}
 check.O=current
 assert board.read_text()==original
 result={'id':'HI-008-CU003-GUARDS','input_hashes':{str(q.relative_to(check.ROOT)):check.sha(q) for q in [board,check.M/'reverb-connector-placement.json',check.Path(check.__file__),check.Path(__file__)]},'controls':out,'all_pass':all(q['rejected'] and q['target_gate_failed'] for q in out.values()),'source_candidate_preserved':board.read_text()==original}
 (current/'guard-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert result['all_pass']
if __name__=='__main__':main()
