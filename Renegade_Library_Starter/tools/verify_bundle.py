#!/usr/bin/env python3
"""Check basic bundle structure; NOT a KiCad parser, ERC, DRC or circuit validator."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r'\s*(\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+)')

def parse_sexpr(text: str):
    """Parse lists and quoted strings, rejecting trailing/unbalanced structures."""
    tokens = []
    pos = 0
    while pos < len(text):
        if not text[pos:].strip():
            break
        m = TOKEN.match(text, pos)
        if m is None:
            raise ValueError(f'Invalid token at character {pos}')
        tokens.append(m.group(1))
        pos = m.end()
    stack = []
    result = []
    current = result
    for token in tokens:
        if token == '(':
            child = []
            current.append(child)
            stack.append(current)
            current = child
        elif token == ')':
            if not stack:
                raise ValueError('Unexpected closing parenthesis')
            current = stack.pop()
        elif token.startswith('"'):
            current.append(json.loads(token))
        else:
            current.append(token)
    if stack or len(result) != 1 or not isinstance(result[0], list):
        raise ValueError('Unbalanced or multiple root expressions')
    return result[0]

def children(node, name):
    return [item for item in node if isinstance(item, list) and item and item[0] == name]

def walk(node, name):
    found = []
    if isinstance(node, list):
        if node and node[0] == name:
            found.append(node)
        for part in node:
            if isinstance(part, list):
                found.extend(walk(part, name))
    return found

def require(condition, message):
    if not condition:
        raise ValueError(message)

def main():
    report = []
    library = parse_sexpr((ROOT/'libraries/Renegade_Custom.kicad_sym').read_text())
    require(library[0] == 'kicad_symbol_lib', 'Wrong symbol-library root')
    symbols = children(library, 'symbol')
    require(len(symbols) == 3, 'Expected three custom symbols')
    names = [s[1] for s in symbols]
    require(len(set(names)) == len(names), 'Duplicate symbol names')
    report.append('PASS: symbol library has three uniquely named draft symbols.')
    expected = {
        'SpringTank_4Terminal_Offboard': {'1','2','3','4'},
        'ReverbTransformer_1P1S_Offboard': {'P1','P2','S1','S2'},
        'TRS_Control_Port_Offboard': {'T','R','S'},
    }
    for symbol in symbols:
        require(children(symbol,'on_board') == [['on_board','no']], 'Custom part must be off-board')
        nums = [children(p,'number')[0][1] for p in walk(symbol, 'pin')]
        require(len(nums) == len(set(nums)), f'Duplicate terminal in {symbol[1]}')
        require(set(nums) == expected[symbol[1]], f'Wrong terminal set in {symbol[1]}')
        fps = [p for p in children(symbol,'property') if p[1] == 'Footprint']
        require(len(fps) == 1 and fps[0][2] == '', 'Unexpected footprint assignment')
    report.append('PASS: terminal identifiers match the documented logical interfaces; all three parts are off-board with no footprint.')
    table = parse_sexpr((ROOT/'sym-lib-table').read_text())
    for entry in children(table,'lib'):
        uri = children(entry,'uri')[0][1]
        require(uri.startswith('${KIPRJMOD}/'), 'Library is not project-relative')
        target = ROOT / uri.removeprefix('${KIPRJMOD}/')
        require(target.is_file(), f'Missing library: {target}')
    report.append('PASS: project-specific library table resolves to the bundled library.')
    json.loads((ROOT/'Renegade_Library_Preview.kicad_pro').read_text())
    schematic = parse_sexpr((ROOT/'Renegade_Library_Preview.kicad_sch').read_text())
    require(schematic[0] == 'kicad_sch', 'Wrong schematic root')
    require(not children(schematic,'wire'), 'Preview must not contain circuit wiring')
    instances = children(schematic,'symbol')
    require(len(instances) == 3, 'Expected three preview instances')
    embedded = children(children(schematic,'lib_symbols')[0],'symbol')
    embedded_names = {s[1] for s in embedded}
    for inst in instances:
        require(children(inst,'lib_id')[0][1] in embedded_names, 'Unresolved embedded preview symbol')
    uuids = [u[1] for u in walk(schematic,'uuid')]
    require(len(uuids) == len(set(uuids)), 'Duplicate UUID')
    report.append('PASS: project JSON and schematic basic S-expression structure; preview references resolve to embedded symbols; UUIDs are unique.')
    report.append('NOT RUN: KiCad application-open / native parser validation / rendering / ERC / DRC / SPICE simulation.')
    report.append('NOT VERIFIED: supplier pin mappings, physical footprints, component ratings, circuit operation or electrical safety.')
    report.append('These checks are generic structure checks, not a substitute for KiCad application validation or an engineering review.')
    print('\n'.join(report))

if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, IndexError, KeyError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
