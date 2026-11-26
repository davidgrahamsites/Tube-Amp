"""Read-only conditional native spacing check; never change the active rules."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, tempfile

M = Path(__file__).resolve().parents[1]
ROOT = M.parents[3]
D = M/'results'
CLI = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    c = json.loads((M/'contract.json').read_text())
    for p, h in c['native_sha256'].items():
        assert sha(ROOT/p) == h, p
    target = ROOT/c['target']
    base = target.with_suffix('.kicad_dru').read_text()
    condition = ' || '.join(f"{a}.NetName == '{n}'" for a in ['A','B'] for n in c['nets'])
    added = '\n# Conditional screen only; see voltage-spacing/contract.json.\n'
    added += f'''(rule "Tube interface conditional spacing"
  (condition "{condition}")
  (constraint clearance (min {c['screen']['clearance_mm']}mm))
  (constraint creepage (min {c['screen']['creepage_mm']}mm)))
'''
    (D/'candidate.kicad_dru').write_text(base+added)
    commands = []
    with tempfile.TemporaryDirectory(prefix='renegade-voltage-spacing-') as td:
        tmp = Path(td)
        for suffix in ['.kicad_pcb','.kicad_pro','.kicad_dru']:
            shutil.copyfile(target.with_suffix(suffix),tmp/(target.stem+suffix))
        table=(target.parent/'fp-lib-table').read_text()
        table=re.sub(r'\$\{KIPRJMOD\}([^\"]+)',lambda m:str((target.parent/m.group(1).lstrip('/')).resolve()),table)
        (tmp/'fp-lib-table').write_text(table)
        for name, rules in [('baseline',base),('candidate',base+added)]:
            (tmp/(target.stem+'.kicad_dru')).write_text(rules)
            cmd = [CLI,'pcb','drc','--format','json','--severity-all','--all-track-errors',
                   '-o',str(D/(name+'-drc.json')),str(tmp/target.name)]
            p = subprocess.run(cmd,text=True,capture_output=True,timeout=180)
            commands.append(dict(command=cmd,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
            assert p.returncode == 0 and 'Error' not in p.stderr, commands[-1]
        assert sha(tmp/target.name) == c['native_sha256'][c['target']]
    for p, h in c['native_sha256'].items():
        assert sha(ROOT/p) == h, p
    reports = {n:json.loads((D/(n+'-drc.json')).read_text()) for n in ['baseline','candidate']}
    counts = {n:dict(violations=len(d['violations']),opens=len(d['unconnected_items'])) for n,d in reports.items()}
    out = dict(commands=commands,counts=counts,active_native_unchanged=True,
               version=subprocess.check_output([CLI,'version'],text=True).strip(),
               input_sha256={'contract.json':sha(M/'contract.json'),'tools/run.py':sha(Path(__file__))},
               report_sha256={str(p.relative_to(M)):sha(p) for p in [D/'candidate.kicad_dru',D/'baseline-drc.json',D/'candidate-drc.json']},
               full_voltage_envelope_qualified=False,adopted=False)
    (D/'run.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(counts,indent=2))


if __name__ == '__main__':
    main()
