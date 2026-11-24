"""Small native KiCad syntax seam; quoted atoms retained verbatim, no CAD regeneration."""
import re

def parse(text):
    stack=[];roots=[]
    for token in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',text):
        if token=='(':
            node=[]
            if stack:stack[-1].append(node)
            else:roots.append(node)
            stack.append(node)
        elif token==')':
            assert stack,'Unbalanced closing parenthesis'
            stack.pop()
        else:
            assert stack,'Atom outside root'
            stack[-1].append(token)
    assert not stack and len(roots)==1,'Unbalanced or multiple roots'
    return roots[0]

def children(node,kind):return [x for x in node if isinstance(x,list) and x[0]==kind]
def field(node,kind):return children(node,kind)[0]
def fps(node):return {next(p[2].strip('"') for p in children(f,'property') if p[1]=='"Reference"'):f for f in children(node,'footprint')}
def nets(xml):return {n.get('name'):sorted(tuple(sorted(x.attrib.items())) for x in n.findall('node')) for n in xml.findall('./nets/net')}
