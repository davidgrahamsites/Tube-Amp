"""Capture a NEW native revision. No writes to the historical integrated/PCB files."""
from pathlib import Path
import ast, copy, hashlib, json, shutil, sys, zipfile

ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT.parent
ENG = WHOLE.parent
OLD = ENG / 'solid-state-reverb'
sys.path.insert(0, str(ENG / 'updated-schematic/tools'))
from kicad_factory import Factory, Sheet, parse, serialize, child, children, uid

CAD = ROOT / 'cad'
if (CAD / 'NATIVE_EDIT_GUARD').exists():
    raise SystemExit('Revision already captured. Preserve native edits; do not regenerate in place.')
PROJECT = 'Renegade_220V_Reverb'
source = WHOLE / 'integrated'
hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.glob('*.kicad_sch')}
records = copy.deepcopy(json.loads((OLD / 'design-connectivity.json').read_text())['components'])
records = [c for c in records if c['project'] == PROJECT]
cfg = {k: v for k, v in json.loads((OLD / 'wire-layout.json').read_text()).items() if k.startswith('07')}

# Value/connectivity changes are explicit and confined to the reverb interface.
for c in records:
    ref = c['reference']
    if ref == 'R601': c['value'] = '1M'
    if ref == 'R602': c['value'] = '100k'
    if ref == 'R612':
        c['sheet'] = '07c_reverb_output'
        c['pins'] = {'1': 'FX_RETURN', '2': 'MIX_OUT'}
    if ref == 'C607': c['pins']['2'] = 'WET_AC'
    if ref == 'R617': c['pins']['1'] = 'WET_AC'
    if ref == 'RT1':
        c['value'] = 'Received tank 600:2250 ohm'
        c['rating'] = 'Seller: 3 springs, medium decay, input insulated/output grounded; horizontal open side down; drive limit unmeasured'
    if ref == 'R605': c['rating'] = '220 ohm; select >=2W flameproof part; tank drive current requires commissioning'
    if c['sheet'].startswith('07'):
        c['pins'] = {p: {'DRY_IN': 'SEND_IN', 'DRY_BUF': 'SEND_BUF'}.get(n, n) for p, n in c['pins'].items()}
        c['status'] = '600/2250 received-tank draft; electrical and physical qualification pending'
new = copy.deepcopy(next(c for c in records if c['reference'] == 'R617'))
new.update(reference='R618', value='1M', pins={'1': 'WET_AC', '2': 'MIX_OUT'})
records.append(new)
del cfg['07b_reverb_recovery']['positions']['R612']
cfg['07c_reverb_output']['positions'].update(R612=[457.2, 60.96, 0], R618=[304.8, 99.06, 0], JR5=[419.1, 60.96, 0])
cfg['07a_reverb_send']['notes'] = [[
    'C601 / R601 / R602 feed an attenuated SEND only. Dry does not pass through an op-amp.\n'
    '600 ohm tank input is seller confirmed; coil R/L and allowable current remain unmeasured.\n'
    'Set RV601 to minimum before commissioning. 220R is series isolation, not a guaranteed current limiter.',20,250,1.3]]
cfg['07b_reverb_recovery']['notes'] = [[
    '2250 ohm tank output; high impedance recovery input. RV602 controls wet only.\n'
    'K3 shorts the wet branch via R610. U12A now processes WET ONLY.\n'
    'Expression-pedal gain-control stage remains a separate open interface; this draft does not implement it.',20,300,1.3]]
cfg['07c_reverb_output']['notes'] = [[
    'R612 carries passive dry from FX_RETURN to MIX_OUT. R618 adds wet through 1M.\n'
    'Dry gain is independent of RV602 and K3, but passive loading causes fixed attenuation.\n'
    'No dry audio passes through U10/U11/U12. Original C19/R24 and phase inverter remain.\n'
    'PCB layout must change; the old 160 x 100 board is not this circuit. Cabinet is already delivered.',20,285,1.3]]
cfg['07d_reverb_harness']['notes'] = [[
    'Received Mable tank: 3 springs, 600 ohm input, 2250 ohm output, medium decay, no lock.\n'
    'Install horizontal, OPEN SIDE DOWN. Input insulated; output grounded to tank case.\n'
    'Keep tank return shielded; avoid a second audio/chassis ground bond. Preserve protective earth.\n'
    'Actual tank dimensions and cabinet assembly clearance still require measurement.',20,150,1.3]]
contract = {'revision': '600R-1', 'owner': 'Renegade integration',
    'tank': {'input_impedance_ohm':600,'output_impedance_ohm':2250,'test_frequency_Hz':None,'drive_limit_mA':None},
    'components':records,'layout':cfg}
(ROOT / 'circuit.json').write_text(json.dumps(contract, indent=2)+'\n')

for p in source.glob('*.kicad_sch'): shutil.copy2(p, CAD / p.name)
for name in ['sym-lib-table', PROJECT+'.kicad_pro']: shutil.copy2(source / name, CAD / name)
shutil.copytree(source / 'libraries', CAD / 'libraries', dirs_exist_ok=True)
# Historical fp-lib-table uses relative paths; use the original project-local libraries explicitly.
(CAD/'fp-lib-table').write_text((source/'fp-lib-table').read_text().replace('${KIPRJMOD}/../libraries', str(WHOLE/'libraries')))
root_tree = parse((CAD/(PROJECT+'.kicad_sch')).read_text())
rootid = child(root_tree,'uuid')[1]
for t in children(root_tree,'text'):
    if 'v0.5' in t[1] or 'v0.4' in t[1]:
        t[1] = 'Received-tank revision 600R-1 | Full amplifier schematic draft\nPassive dry + solid-state spring reverb, 600/2250 ohm tank.\nDelivered cabinet fixed. New PCB layout, expression control and physical qualification pending.'
(CAD/(PROJECT+'.kicad_sch')).write_text(serialize(root_tree)+'\n')
f = Factory(CAD)
f.symbols = {s[1]:copy.deepcopy(s) for s in children(parse((CAD/'libraries/Renegade_Draft.kicad_sym').read_text()),'symbol')}
native_props = {}
for p in source.glob('07*.kicad_sch'):
    for s in children(parse(p.read_text()),'symbol'):
        props={v[1]:v[2] for v in children(s,'property')}
        native_props[props['Reference']]=props
for name, config in cfg.items():
    s = Sheet(f,PROJECT,name,name.replace('_',' '),2,rootid,uid(PROJECT+'/sheet/'+name))
    for c in records:
        if c['sheet'] != name: continue
        key=c['reference'] if c['unit']==1 else c['reference']+'/'+str(c['unit'])
        x,y,rot=config['positions'][key]
        s.sym(c['symbol'],c['reference'],c['value'],x,y,c['pins'],unit=c['unit'],source='600R-1 received-tank revision',rating=c.get('rating',''),status=c['status'],datasheet=c.get('datasheet',''))
    s.write(CAD)
    p=CAD/(name+'.kicad_sch');tree=parse(p.read_text())
    for sym in children(tree,'symbol'):
        props={v[1]:v for v in children(sym,'property')};ref=props['Reference'][2]
        props['Footprint'][2]=native_props.get(ref,native_props.get('R617',{})).get('Footprint','')
    p.write_text(serialize(tree)+'\n')
(CAD/'design-connectivity.json').write_text(json.dumps({'components':records},indent=2)+'\n')
(CAD/'wire-layout.json').write_text(json.dumps(cfg,indent=2)+'\n')
(CAD/'validation').mkdir(exist_ok=True)
with zipfile.ZipFile(CAD/'validation/label-layout-v0.2.zip','w') as z:
    for name in [*cfg,PROJECT]:z.write(CAD/(name+'.kicad_sch'),name+'.kicad_sch')
# Reuse only definitions/imports of the existing wire router; never execute its
# historical startup guard or target directory assignment. Its ROOT is this NEW revision.
router_file=OLD/'tools/wire_layout.py'
tree=ast.parse(router_file.read_text())
allowed=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef,ast.ClassDef))]
ns={'ROOT':CAD,'STEP':1.27,'__name__':'revision_router'}
exec(compile(ast.Module(body=allowed,type_ignores=[]),str(router_file),'exec'),ns)
ns['redraw']()
for name in [*cfg,PROJECT]:
    p=CAD/(name+'.kicad_sch');tree=parse(p.read_text())
    title=child(tree,'title_block');child(title,'rev')[1]='600R-1 DRAFT';child(title,'date')[1]='2026-11-19'
    for t in children(tree,'text'):t[1]=t[1].replace('v0.4','600R-1').replace('v0.3','600R-1')
    for sym in children(tree,'symbol'):
        for prop in children(sym,'property'):
            if prop[1]=='Reference' and prop[2].startswith('#PWR'):prop[2]='#PWR60'+prop[2][4:]
        inst=child(sym,'instances')
        if inst:
            for project in children(inst,'project'):
                for path in children(project,'path'):
                    ref=child(path,'reference')
                    if ref and ref[1].startswith('#PWR'):ref[1]='#PWR60'+ref[1][4:]
    p.write_text(serialize(tree)+'\n')
unchanged=[name for name in hashes if not name.startswith('07') and name!=PROJECT+'.kicad_sch']
assert all(hashlib.sha256((CAD/n).read_bytes()).hexdigest()==hashes[n] for n in unchanged)
assert all(hashlib.sha256((source/n).read_bytes()).hexdigest()==h for n,h in hashes.items())
(ROOT/'review/capture-provenance.json').write_text(json.dumps({'source_hashes':hashes,'unchanged_original_amp_sheets':unchanged,'router_sha256':hashlib.sha256(router_file.read_bytes()).hexdigest()},indent=2)+'\n')
(CAD/'NATIVE_EDIT_GUARD').write_text('Native revision captured. Preserve manual edits. Do not regenerate in place.\n')
print('Captured new revision; unchanged original amp sheets:',len(unchanged))
