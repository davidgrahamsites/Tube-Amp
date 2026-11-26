"""Current-reference audit and one manufacturer-backed bounded thermal calculation."""
from pathlib import Path
from collections import defaultdict
import csv,hashlib,json,math,sys,copy
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2]
sys.path.insert(0,str(M.parent))
from check_coverage import validate
sys.path.insert(0,str(ROOT/'engineering/whole-amp/tools'))
import native_sexpr as n

def main():
    contract=json.loads((M/'rating-rules.json').read_text())
    def read(key):return json.loads((ROOT/contract[key]).read_text())
    circuit=read('source');coverage=read('coverage');candidates=read('candidates')
    coverage_result=validate(coverage,circuit)
    for path,expected in contract['native_sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
    native=[]
    for part in contract['reconciled_parts']:
        ref=part['ref']
        board=n.parse((ROOT/f"engineering/whole-amp/pcb-measured-r/boards/{part['board']}.kicad_pcb").read_text())
        footprint=n.fps(board)[ref];assert footprint[1].strip('"')==part['footprint']
        pins={pad[1].strip('"'):n.field(pad,'net')[-1].strip('"') for pad in n.children(footprint,'pad')}
        assert pins==part['pins'],(ref,pins)
        sheet=n.parse((ROOT/f"engineering/whole-amp/reverb-600/cad/{part['sheet']}.kicad_sch").read_text())
        symbols=[{p[1].strip('"'):p[2].strip('"') for p in n.children(sym,'property')} for sym in n.children(sheet,'symbol')]
        sym=next(x for x in symbols if x.get('Reference')==ref)
        assert sym[part['native_mpn_property']].split(';')[0]==part['mpn'] and sym['Footprint']==part['footprint'],ref
        source=next(x for x in circuit['components'] if x['reference']==ref)
        assert source['selected_mpn']==part['mpn'] and source['pins']==pins and source['footprint']==part['footprint'],ref
        native.append({'reference':ref,'source_schematic_board_identity':True,'component_drills':0})
    groups={ref:g for g in coverage for ref in g['refs']}
    selected=defaultdict(list)
    for candidate in candidates:selected[candidate['mpn']].append(candidate)
    for group in coverage:
        if group.get('selected_mpn'):
            assert len(selected[group['selected_mpn']])==1,group['selected_mpn']
    classes={symbol:(name,spec['checks']) for name,spec in contract['classes'].items() for symbol in spec['symbols']}
    units=defaultdict(list)
    for part in circuit['components']:
        if part['symbol']!='power_PWR_FLAG':units[part['reference']].append(part)
    rows=[]
    for ref,parts in sorted(units.items()):
        symbols={p['symbol'] for p in parts};assert len(symbols)==1,(ref,symbols)
        family,checks=classes[next(iter(symbols))]
        group=groups[ref]
        rows.append({'reference':ref,'class':family,'source_value':' / '.join(sorted({p['value'] for p in parts})),
          'coverage_id':group['id'],'selected_mpn':group.get('selected_mpn',''),
          'declared_source_rating':' / '.join(sorted({p.get('rating','') for p in parts})),
          'selection_requirement':group.get('requirement',''),'selection_status':group['status'],
          'selection_evidence':group.get('selection_evidence',''),'package_evidence':group.get('package_evidence',''),
          'required_rating_checks':'; '.join(checks),
          'qualification':'Not established by this inventory; review linked evidence and all applicable corners'})
    with (M/'results/parts.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    # Regression: reproduce the actual omission and ensure generation cannot hide it.
    controls=[]
    for name,mutated in [
      ('missing_R304_R314',[g for g in coverage if not set(g['refs'])&{'R304','R314'}]),
      ('duplicate_reference',coverage+[copy.deepcopy(groups['R304'])]),
      ('wrong_explicit_MPN',[dict(g,selected_mpn='WRONG') if 'R304' in g['refs'] else g for g in coverage])]:
        try:validate(mutated,circuit)
        except ValueError as e:controls.append({'case':name,'rejected':True,'reason':str(e)})
        else:raise AssertionError('Bad coverage accepted: '+name)
    c=contract['bounded_case'];sheet=ROOT/c['datasheet'];assert hashlib.sha256(sheet.read_bytes()).hexdigest()==c['datasheet_sha256']
    for ref in c['refs']:
        assert groups[ref]['selected_mpn']==c['mpn']
        assert all(p['value']=='10k' and p['selected_mpn']==c['mpn'] for p in units[ref])
    prior=json.loads((ROOT/c['evidence']).read_text())
    power=c['voltage_bound_V']**2/c['resistance_min_screen_ohm']
    assert math.isclose(power,prior['resistor_power_upper_W'],rel_tol=1e-12)
    thermal=[]
    for temp in c['ambient_screen_C']:
        allowed=c['rated_W_at70C']*max(0,min(1,(c['zero_rating_C']-temp)/(c['zero_rating_C']-70)))
        voltage=min(c['maximum_working_V'],math.sqrt(allowed*c['resistance_min_screen_ohm']))
        thermal.append({'local_ambient_C':temp,'bounded_power_W':power,'allowed_power_W':allowed,
          'utilization_fraction':power/allowed,'continuous_voltage_bound_V':voltage,
          'passed_bounded_case':power<=allowed and c['voltage_bound_V']<=voltage})
    assert all(t['passed_bounded_case'] for t in thermal)
    inputs=[contract[k] for k in ['source','coverage','candidates']]+[c['datasheet'],c['evidence'],str((M/'rating-rules.json').relative_to(ROOT))]
    result={'coverage':coverage_result,'native_identity':native,'unchanged_native_files':len(contract['native_sha256']),'negative_controls':controls,'worksheet_rows':len(rows),
      'bounded_resistors':c['refs'],'bounded_thermal_results':thermal,'maximum_body_mm':c['maximum_body_mm'],
      'rating_screen_limits':c['limitations'],'all_part_ratings_qualified':False,'fabrication_ready':False,
      'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs}}
    (M/'results/checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['coverage','worksheet_rows','bounded_thermal_results','all_part_ratings_qualified']},indent=2))

if __name__=='__main__':main()
