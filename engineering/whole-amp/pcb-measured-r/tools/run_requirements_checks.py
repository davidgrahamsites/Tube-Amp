"""Native audit runner. Strict checks operate on temporary copies only.

Input: boards plus embedded footprints; output: review/*-strict-drc.json,
review/*-audit.svg, review/requirements-run.json. Never saves live boards.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CLI = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def run(name):
    source = ROOT / 'boards' / f'Renegade_{name}.kicad_pcb'
    inputs = {str(source.with_suffix(ext).relative_to(ROOT)): sha(source.with_suffix(ext)) for ext in ['.kicad_pcb','.kicad_pro','.kicad_dru']}
    with TemporaryDirectory(prefix='renegade-drc-') as tmp:
        target = Path(tmp) / source.name
        for ext in ['.kicad_pcb','.kicad_pro','.kicad_dru']:
            target.with_suffix(ext).write_bytes(source.with_suffix(ext).read_bytes())
        # Resolve library paths exactly as the original project, not /tmp.
        table = (ROOT / 'boards/fp-lib-table').read_text().replace('${KIPRJMOD}', str(ROOT / 'boards'))
        (Path(tmp) / 'fp-lib-table').write_text(table)
        pro = target.with_suffix('.kicad_pro')
        data = json.loads(pro.read_text())
        ds = data.setdefault('board', {}).setdefault('design_settings', {})
        severity = ds.setdefault('rule_severities', {})
        enabled = [k for k,v in severity.items() if v == 'ignore']
        for k in enabled: severity[k] = 'warning'
        ds['drc_exclusions'] = []
        pro.write_text(json.dumps(data, indent=2)+'\n')
        strict_hash = sha(pro)
        command = [CLI, 'pcb', 'drc', '--format', 'json', '--severity-all', '--all-track-errors', '--refill-zones', '-o', str(ROOT / f'review/{name}-strict-drc.json'), str(target)]
        proc = subprocess.run(command, capture_output=True, text=True)
        if proc.returncode: raise RuntimeError(proc.stdout+proc.stderr)
        report = json.loads((ROOT / f'review/{name}-strict-drc.json').read_text())
    # Plot both copper sides and assembly outlines, no source mutations.
    cmd = [CLI, 'pcb', 'export', 'svg', '--layers', 'F.Cu,B.Cu,F.Silkscreen,F.Fab,Edge.Cuts', '--mode-single', '--fit-page-to-board', '--exclude-drawing-sheet', '-o', str(ROOT / f'review/{name}-audit.svg'), str(source)]
    subprocess.run(cmd, check=True, capture_output=True)
    # KiCad adds trailing whitespace; normalize text only, retaining geometry.
    svg = ROOT / f'review/{name}-audit.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')
    unchanged = all(sha(ROOT / path) == h for path,h in inputs.items())
    assert unchanged, name
    return name, {'input_hashes': inputs, 'inputs_unchanged': unchanged, 'strict_copy_enabled_checks': enabled, 'strict_copy_project_sha256': strict_hash, 'strict_violations_by_type': dict(Counter(v['type'] for v in report['violations'])), 'strict_unconnected': len(report['unconnected_items']), 'native_command_flags': ['--severity-all','--all-track-errors','--refill-zones'], 'paired_schematic_parity': 'NOT RUN: no paired board schematics; separate exhaustive contract audit only'}

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = dict(pool.map(run, ['Main','Power','Control','Reverb']))
    result = {'kicad_version': subprocess.check_output([CLI,'version'], text=True).strip(), 'boards': rows, 'fabrication_ready': False}
    (ROOT / 'review/requirements-run.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
