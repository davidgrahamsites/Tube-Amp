"""Reconcile four native drafts; preserve source boards and expose routing gaps.

Run with KiCad's bundled Python. Output drafts are intentionally not released.
"""
from pathlib import Path
import hashlib
import json
import shutil
import pcbnew as p
IO = p.PCB_IO_KICAD_SEXPR()
# KiCad10 macOS SWIG wrappers must stay alive through save/reload.
KEEP = []
def retain(items):
    values = list(items)
    KEEP.extend(values)
    return values


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT.parent
SEL = WHOLE.parent / 'component-selection'
LIB = SEL / 'footprints/Renegade_Selected.pretty'
SYSTEM = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
contract_path = WHOLE / 'reverb-600/circuit.json'
contract = json.loads(contract_path.read_text())
parts = {}
for c in contract['components']:
    if c['reference'].startswith('#'):
        continue
    ref = c['reference']
    if ref not in parts:
        parts[ref] = {**c, 'pins': {}}
    parts[ref]['pins'].update(c['pins'])
selected = {ref: g['selected_mpn'] for g in json.loads((SEL / 'coverage.json').read_text())
            if g.get('selected_mpn') for ref in g['refs']}


def selected_fp(mpn):
    if mpn.startswith('CD11AT'):
        return 'CH_CD11AT_25u_400V_D8_P3.5'
    if mpn.startswith('KP'):
        return 'KYET_' + mpn
    if mpn.startswith('3296W'):
        return 'Bourns_3296W_TopAdjust_P2.54'
    if mpn.startswith(('MFR50S', 'MF0207')):
        return 'Yageo_MFR50S_MF0207_P10.16'
    if mpn.startswith('FMP200'):
        return 'Yageo_FMP200_L9.0_D3.9_P15.24'
    if mpn.startswith('NFA200'):
        return 'Samyoung_NFA_10u_200V_D8_P3.5'
    if mpn in ['MEB104J63V82CB0236', 'MEB105J63V82CB0235']:
        return 'KNSCHA_' + mpn
    return None


report = {'revision': '600R-1 PCB integration draft, November20',
          'release': False, 'circuit_sha256': hashlib.sha256(contract_path.read_bytes()).hexdigest(),
          'limitations': ['Board outlines retained provisionally; assembled cabinet fit unverified',
                         'Affected copper removed; rerouting and DRC closure required',
                         'Expression-pedal implementation remains pending',
                         'Unselected packages and protection parts remain unresolved'], 'boards': {}}
for name in ['Main', 'Power', 'Control', 'Reverb']:
    source = WHOLE / 'pcb' / name / f'Renegade_{name}.kicad_pcb'
    out = ROOT / 'boards' / source.name
    assert not out.exists(), f'Preserve existing native edit: {out}'
    before_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    board = p.LoadBoard(str(source))
    KEEP.append(board)
    affected_nets = set()
    changes = []
    for old in retain(board.GetFootprints()):
        ref = old.GetReference()
        mpn = selected.get(ref)
        fp_name = selected_fp(mpn) if mpn else None
        if not fp_name:
            if mpn:
                old.SetField('Selected_MPN', mpn)
                old.SetField('Package_Status', 'Existing package; exact dimensional qualification pending')
            continue
        new = IO.FootprintLoad(str(LIB), fp_name)
        assert new, (ref, fp_name)
        oldpads = {q.GetNumber(): q for q in old.Pads() if q.GetNumber()}
        newpads = {q.GetNumber(): q for q in new.Pads() if q.GetNumber()}
        assert set(oldpads) == set(newpads), (ref, oldpads.keys(), newpads.keys())
        new.SetReference(ref)
        new.SetValue(old.GetValue())
        new.SetPosition(old.GetPosition())
        new.SetOrientationDegrees(old.GetOrientationDegrees())
        new.SetPath(old.GetPath())
        new.SetFPID(p.LIB_ID('Renegade_Selected', fp_name))
        new.SetField('Selected_MPN', mpn)
        new.SetField('Status', 'DRAFT - reroute and fit review required')
        new.Value().SetVisible(False)
        new.Reference().SetTextSize(p.VECTOR2I(p.FromMM(1), p.FromMM(1)))
        new.Reference().SetTextThickness(p.FromMM(.15))
        for num, pad in newpads.items():
            pad.SetNet(oldpads[num].GetNet())
            affected_nets.add(oldpads[num].GetNetCode())
        changes.append({'reference': ref, 'mpn': mpn,
                        'from': str(old.GetFPID().GetLibItemName()), 'to': fp_name})
        board.Remove(old)
        board.Add(new)
    if name == 'Reverb':
        # The passive dry/wet revision splits and reconnects nets; old copper is invalid.
        for track in retain(board.GetTracks()):
            board.Remove(track)
        for zone in retain(board.Zones()):
            board.Remove(zone)
        footprints = {f.GetReference(): f for f in board.GetFootprints()}
        ref = 'R618'
        assert ref not in footprints
        new = IO.FootprintLoad(str(LIB), selected_fp(selected[ref]))
        new.SetReference(ref)
        new.SetPosition(p.VECTOR2I(p.FromMM(132), p.FromMM(32)))
        new.SetFPID(p.LIB_ID('Renegade_Selected', selected_fp(selected[ref])))
        new.SetField('Selected_MPN', selected[ref])
        new.Value().SetVisible(False)
        board.Add(new)
        changes.append({'reference': ref, 'mpn': selected[ref], 'from': None,
                        'to': selected_fp(selected[ref])})
        nets = {net.GetNetname(): net for net in board.GetNetsByNetcode().values()}
        for f in board.GetFootprints():
            ref = f.GetReference()
            if ref.startswith('H'):
                continue
            c = parts[ref]
            f.SetValue(c['value'])
            assert {q.GetNumber() for q in f.Pads() if q.GetNumber()} == set(c['pins']), ref
            for pad in f.Pads():
                n = c['pins'][pad.GetNumber()]
                if n and n not in nets:
                    nets[n] = p.NETINFO_ITEM(board, n)
                    board.Add(nets[n])
                pad.SetNet(nets[n] if n else None)
    else:
        for track in retain(board.GetTracks()):
            if track.GetNetCode() in affected_nets:
                board.Remove(track)
        for zone in retain(board.Zones()):
            if zone.GetNetCode() in affected_nets:
                board.Remove(zone)
    # Board draft label does not claim a replacement for original tube circuit.
    text = p.PCB_TEXT(board)
    text.SetText('600R-1 PART INTEGRATION / DRAFT - DO NOT FABRICATE')
    box = board.GetBoardEdgesBoundingBox()
    text.SetPosition(p.VECTOR2I(box.GetCenter().x, box.GetBottom() - p.FromMM(2)))
    text.SetTextSize(p.VECTOR2I(p.FromMM(1), p.FromMM(1)))
    text.SetTextThickness(p.FromMM(.15))
    text.SetLayer(p.Dwgs_User)
    board.Add(text)
    p.SaveBoard(str(out), board)
    for ext in ['.kicad_pro', '.kicad_dru']:
        src = source.with_suffix(ext)
        if src.exists():
            shutil.copy2(src, out.with_suffix(ext))
    check = p.LoadBoard(str(out))
    KEEP.append(check)
    mismatches = []
    checked = 0
    for f in check.GetFootprints():
        ref = f.GetReference()
        if ref not in parts:
            continue  # Mounting holes and explicit board-only harness terminals.
        c = parts[ref]
        for pad in f.Pads():
            num = pad.GetNumber()
            if not num:
                continue
            actual = pad.GetNetname()
            expected = c['pins'].get(num)
            checked += 1
            if actual != (expected or '') and not (expected is None and actual == f'unconnected-({ref}-Pad{num})'):
                mismatches.append({'ref': ref, 'pad': num, 'actual': actual, 'expected': expected})
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before_hash
    report['boards'][name] = {'source': str(source.relative_to(WHOLE)),
                             'source_sha256': before_hash, 'source_unchanged': True,
                             'footprints': len(list(check.GetFootprints())),
                             'remaining_track_items': len(list(check.GetTracks())),
                             'footprint_changes': changes,
                             'current_contract_pad_checks': checked,
                             'pad_net_mismatches': mismatches}
    print(name, len(changes), 'footprint changes;', checked, 'pad checks;', len(mismatches), 'mismatches')
(ROOT / 'review/integration.json').write_text(json.dumps(report, indent=2) + '\n')
# Schematic parity here is a pad-name contract check, not KiCad paired-assembly parity.
assert not any(row['pad_net_mismatches'] for row in report['boards'].values()), report
