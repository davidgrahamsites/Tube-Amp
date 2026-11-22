"""One-time exact-package integration. Preserve nets and connected track endpoints.

Inputs: existing native drafts, selected coverage, qualified footprint library.
Output: three revised drafts and a hashed change report. No outline/fit release.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
SEL = ROOT.parents[1] / 'component-selection'
LIB = SEL / 'footprints/Renegade_Selected.pretty'
OUT = ROOT / 'review/service-wave-package-integration.json'
assert not OUT.exists(), 'Already applied; preserve subsequent native edits'
io = p.PCB_IO_KICAD_SEXPR()
keep = []
# Exact dimensional equivalence is documented in the LV parts and resistor dossiers.
for source, target, description in [
    ('KNSCHA_MEB104J63V82CB0236', 'KNSCHA_82CL0120',
     '82CL0120; 47nF 63V; nominal7.2x2.5xH6.5mm +/-0.5; pitch5 +/-0.5; lead0.5 +/-0.05; max-body courtyard'),
    ('Yageo_MFR50S_MF0207_P10.16', 'Yageo_FMP100_P10.16',
     'FMP100; body6.3 +/-0.5 x diameter2.4 +/-0.2; lead0.55 +/-0.05; formed pitch10.16; mounting height/thermal clearance require review')]:
    f = io.FootprintLoad(str(LIB), source)
    keep.append(f)
    f.SetFPID(p.LIB_ID('Renegade_Selected', target))
    f.SetValue(target)
    f.SetLibDescription(description)
    f.Models().clear()
    io.FootprintSave(str(LIB), f)

mapping = {'R303': 'Yageo_MFR50S_MF0207_P10.16',
           'R313': 'Yageo_MFR50S_MF0207_P10.16',
           'R39': 'Yageo_FMP100_P10.16', 'R503': 'Yageo_FMP100_P10.16',
           'C321': 'KNSCHA_82CL0120', 'C602': 'KYET_KP223J2J1001'}
selected = {r: c['selected_mpn'] for c in json.loads((SEL / 'coverage.json').read_text())
            if c.get('selected_mpn') for r in c['refs']}
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def xy(v): return [p.ToMM(v.x), p.ToMM(v.y)]
report = {'baseline_git': 'e6811e6', 'kicad_version': p.GetBuildVersion(),
          'scope': 'Six exact packages; existing board outlines unchanged; assembled fit unverified', 'boards': {}}
changed = set()
for name in ['Power', 'Control', 'Reverb']:
    path = ROOT / f'boards/Renegade_{name}.kicad_pcb'
    project = path.with_suffix('.kicad_pro')
    project_bytes = project.read_bytes()
    # Explicit immutable input also permits recovery from an interrupted write.
    relative = path.relative_to(ROOT.parents[2])
    baseline = subprocess.check_output(['git', 'show', 'e6811e6:' + str(relative)])
    before = hashlib.sha256(baseline).hexdigest()
    with tempfile.NamedTemporaryFile(suffix='.kicad_pcb') as source:
        source.write(baseline); source.flush()
        board = p.LoadBoard(source.name)
    keep.append(board)
    changes = []
    for old in list(board.GetFootprints()):
        ref = old.GetReference()
        if ref not in mapping: continue
        keep.append(old)
        new = io.FootprintLoad(str(LIB), mapping[ref]); keep.append(new)
        new.SetReference(ref); new.SetValue(old.GetValue())
        new.SetPosition(old.GetPosition()); new.SetOrientationDegrees(old.GetOrientationDegrees())
        new.SetPath(old.GetPath()); new.SetFPID(p.LIB_ID('Renegade_Selected', mapping[ref]))
        new.SetField('Selected_MPN', selected[ref])
        new.Value().SetVisible(False)
        for field in new.GetFields():
            if field.GetName() not in ['Reference', 'Value']: field.SetVisible(False)
        oldpads = {q.GetNumber(): q for q in old.Pads()}
        newpads = {q.GetNumber(): q for q in new.Pads()}
        assert set(oldpads) == set(newpads) == {'1', '2'}
        endpoints = 0
        pads = []
        for num, pad in newpads.items():
            prev = oldpads[num]
            pad.SetNet(prev.GetNet())
            if pad.GetPosition() != prev.GetPosition():
                for track in board.GetTracks():
                    if track.GetNetCode() != prev.GetNetCode(): continue
                    if track.GetStart() == prev.GetPosition():
                        track.SetStart(pad.GetPosition()); endpoints += 1
                    if track.GetEnd() == prev.GetPosition():
                        track.SetEnd(pad.GetPosition()); endpoints += 1
            pads.append({'number': num, 'net': pad.GetNetname(), 'before_mm': xy(prev.GetPosition()),
                         'after_mm': xy(pad.GetPosition()), 'drill_mm': p.ToMM(pad.GetDrillSize().x)})
        changes.append({'reference': ref, 'mpn': selected[ref], 'from': str(old.GetFPID().GetLibItemName()),
                        'to': mapping[ref], 'pads': pads, 'track_endpoints_adjusted': endpoints})
        board.Remove(old); board.Add(new); changed.add(ref)
    p.SaveBoard(str(path), board)
    # SaveBoard may serialize the temporary input's default project settings.
    # The destination's design rules/netclasses must remain byte-identical.
    project.write_bytes(project_bytes)
    report['boards'][name] = {'before_sha256': before, 'after_sha256': sha(path), 'changes': changes}
assert changed == set(mapping)
OUT.write_text(json.dumps(report, indent=2) + '\n')
print('Integrated six exact packages; run fresh DRC and pad/net checks.')
