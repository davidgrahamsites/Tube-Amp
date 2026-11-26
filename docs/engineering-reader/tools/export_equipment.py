#!/usr/bin/env python3
"""Export the current equipment guide with embedded local styles, fonts and KaTeX."""
import base64, json, re
from pathlib import Path
from urllib.parse import quote
HOME = Path(__file__).resolve().parents[1]
ROOT = HOME.parents[1]
SOURCE = HOME / 'test-equipment.html'
OUT = HOME / 'exports/test-equipment.html'

def css_inline(file):
    css = file.read_text()
    def font(match):
        path = (file.parent / match[1]).resolve()
        assert path.is_relative_to(HOME / 'assets') and path.is_file()
        mime = {'.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf'}[path.suffix]
        return 'url(data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode() + ')'
    return re.sub(r'url\([\"\']?([^\)\"\']+)[\"\']?\)', font, css)

def main():
    html = SOURCE.read_text()
    license_text = (HOME / 'assets/katex/LICENSE').read_text().replace('--', '—')
    html = html.replace('</head>', '<!-- Embedded KaTeX license:\n' + license_text + '\n--></head>')
    html = re.sub(r'<link rel="stylesheet" href="([^"]+)">', lambda m: '<style>' + css_inline(HOME / m[1]) + '</style>', html)
    html = re.sub(r'<script defer src="([^"]+)"></script>', lambda m: '<script>' + (HOME / m[1]).read_text().replace('</script', '<\\/script') + '</script>', html)
    def link(m):
        href = m[1]
        if href.startswith(('https:', 'http:', '#')): return m[0]
        path = (HOME / href).resolve()
        assert path.is_relative_to(ROOT) and path.is_file()
        return 'href="https://github.com/davidgrahamsites/Tube-Amp/blob/electric-guitar-amp/' + quote(str(path.relative_to(ROOT))) + '"'
    html = re.sub(r'href="([^"]+)"', link, html)
    assert not re.search(r'<(?:script[^>]+src|link[^>]+href)=', html)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html)
    print(json.dumps({'source': str(SOURCE), 'export': str(OUT), 'bytes': OUT.stat().st_size}))
if __name__ == '__main__': main()
