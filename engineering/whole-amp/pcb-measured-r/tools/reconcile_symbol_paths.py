"""Repair only footprint (path ...) metadata against a freshly exported native XML.
Run with KiCad Python: script NATIVE_XML [--apply]. Default checks without writing.
Inputs are the current schematic hierarchy, circuit and four boards. --apply writes
fixed-name evidence, refuses stale native XML, and preserves all non-path bytes.
Does not update nets, packages, geometry, copper or authorize automatic board update.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import tempfile
import xml.etree.ElementTree as ET
import pcbnew

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT.parent / 'reverb-600/cad'
PATH_RE = re.compile(r'\(path\s+"[^"\n]*"\)')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def footprint_blocks(text):
    # KiCad's own serialized boards: top-level footprints have one tab indentation.
    for match in re.finditer(r'^\t\(footprint\s', text, re.M):
        start = match.start() + 1
        depth, quoted, escaped = 0, False, False
        for end in range(start, len(text)):
            ch = text[end]
            if quoted:
                if escaped:
                    escaped = False
                elif ch == '\\':
                    escaped = True
                elif ch == '"':
                    quoted = False
            elif ch == '"':
                quoted = True
            elif ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    yield start, end + 1, text[start:end + 1]
                    break
        else:
            raise ValueError('Unclosed footprint')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('native_xml', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    sources = sorted(CAD.glob('*.kicad_sch'))
    assert args.native_xml.stat().st_mtime >= max(p.stat().st_mtime for p in sources), 'Export native XML again'
    root = (CAD / 'Renegade_220V_Reverb.kicad_sch').read_text()
    root_uuid = re.search(r'\(uuid\s+([^\s)]+)\)', root).group(1)
    xml = ET.parse(args.native_xml).getroot()
    expected = {}
    for comp in xml.findall('./components/comp'):
        ref = comp.attrib['ref']
        assert ref not in expected, ref
        sheet = comp.find('sheetpath').attrib['tstamps']
        # XML timestamps omit the root symbol instance; PCB paths include it.
        assert sheet.startswith('/') and sheet.endswith('/'), (ref, sheet)
        expected[ref] = '/' + root_uuid + sheet + comp.findtext('tstamps').split()[0]
    parts = {}
    circuit = ROOT.parent / 'reverb-600/circuit.json'
    for comp in json.loads(circuit.read_text())['components']:
        if not comp['reference'].startswith('#'):
            parts.setdefault(comp['reference'], {}).update(comp['pins'])
    report = dict(date='2026-11-24',scope='Native footprint identity only; not electrical parity or release',
                  kicad=pcbnew.GetBuildVersion(),native_xml_sha256=sha(args.native_xml.read_bytes()),
                  schematic_sha256={p.name:sha(p.read_bytes()) for p in sources},
                  circuit_sha256=sha(circuit.read_bytes()),fabrication_ready=False,boards={})
    prepared = []
    keep_alive = []
    for name in ['Main','Power','Control','Reverb']:
        path = ROOT / 'boards' / ('Renegade_' + name + '.kicad_pcb')
        before = path.read_bytes(); text = before.decode()
        native = pcbnew.LoadBoard(str(path)); keep_alive.append(native)
        fs = {f.GetReference():f for f in native.GetFootprints()}
        assert len(fs) == len(list(native.GetFootprints())), 'Duplicate native reference'
        changes, seen = [], set()
        result = text
        for start,end,block in reversed(list(footprint_blocks(text))):
            ref = re.search(r'\(property\s+"Reference"\s+"([^"\n]+)"',block).group(1)
            assert ref not in seen; seen.add(ref)
            if ref not in parts:
                continue # Mechanical/support/wire-port items without source symbols.
            assert ref in expected, ref
            matches = list(PATH_RE.finditer(block)); assert len(matches) <= 1, ref
            old = fs[ref].GetPath().AsString()
            assert matches[0].group() == '(path "' + old + '")' if matches else not old, ref
            pads = {p.GetNumber():p for p in fs[ref].Pads() if p.GetNumber()}
            assert set(pads) == set(parts[ref]), ref
            for number,pad in pads.items():
                want = parts[ref][number]; actual = pad.GetNetname()
                assert actual == want or want is None and (not actual or actual.startswith('unconnected-')), (ref,number)
            if old != expected[ref]:
                if matches:
                    replacement = PATH_RE.sub('(path "' + expected[ref] + '")',block)
                else:
                    closing = block.rfind('\n\t)'); assert closing > 0, ref
                    replacement = block[:closing] + '\n\t\t(path "' + expected[ref] + '")' + block[closing:]
                result = result[:start] + replacement + result[end:]
                changes.append(dict(reference=ref,before=old,after=expected[ref]))
        assert seen == set(fs), 'Text/native footprint inventory mismatch'
        normalize = lambda s: re.sub(r'(?m)^\t\t\(path\s+"[^"\n]*"\)\n', '', s)
        assert normalize(text) == normalize(result), 'Non-path data changed'
        with tempfile.TemporaryDirectory(prefix='renegade-path-check-') as tmp:
            candidate = Path(tmp)/path.name; candidate.write_text(result)
            checked = pcbnew.LoadBoard(str(candidate)); keep_alive.append(checked)
            errors = [f.GetReference() for f in checked.GetFootprints() if f.GetReference() in parts and f.GetPath().AsString()!=expected[f.GetReference()]]
            assert not errors, errors
        after = result.encode()
        report['boards'][name] = dict(before_sha256=sha(before),after_sha256=sha(after),
             changes=sorted(changes,key=lambda x:x['reference']),remaining_path_errors=errors,
             non_path_bytes_identical=True,pad_contract_errors=[],native_reload_pass=True,
             source_footprints_checked=sum(r in parts for r in fs))
        prepared.append((path,before,after))
    if args.apply:
        # Check all sources before the first mutation, then apply the validated patch.
        for path,before,after in prepared:
            assert path.read_bytes() == before, 'Concurrent board edit'
        for filename,h in report['schematic_sha256'].items():
            assert sha((CAD/filename).read_bytes()) == h, 'Concurrent schematic edit'
        assert sha(circuit.read_bytes()) == report['circuit_sha256']
        for path,before,after in prepared:
            path.write_bytes(after)
        (ROOT/'review/symbol-path-reconciliation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({name:{'changed':len(r['changes']),'remaining':len(r['remaining_path_errors']),'non_path_bytes_identical':r['non_path_bytes_identical']} for name,r in report['boards'].items()},indent=2))

if __name__ == '__main__':
    main()
