"""Export envelope studies at physical scale; no cut/drill approval."""
from pathlib import Path
import subprocess
import pymupdf as fitz

OUT = Path(__file__).resolve().parents[1] / 'review'
MM = 72 / 25.4
tiled = fitz.open()
for view in ['face', 'underside']:
    path = OUT / f'panel-study-{view}.pdf'
    subprocess.run(['rsvg-convert', '-f', 'pdf', '-o', str(path),
                    str(OUT / f'panel-study-{view}.svg')], check=True)
    source = fitz.open(path)
    assert abs(source[0].rect.width / MM - 332) < .01
    # Two 181 mm wide tiles overlap by 30 mm. A4 portrait, actual size.
    for n, start in enumerate([0, 151], 1):
        page = tiled.new_page(width=210 * MM, height=297 * MM)
        clip = fitz.Rect(start * MM, 0, (start + 181) * MM, 111 * MM)
        destination = fitz.Rect(14 * MM, 35 * MM, 195 * MM, 146 * MM)
        page.show_pdf_page(destination, source, 0, clip=clip)
        page.insert_text((14 * MM, 15 * MM),
                         f'{view.upper()} - tile {n}/2 - FIT STUDY ONLY', fontsize=11)
        page.insert_text((14 * MM, 22 * MM),
                         'Print Actual Size / 100%. Do not use Fit to Page.', fontsize=9)
        page.insert_text((14 * MM, 157 * MM),
                         f'Tile covers drawing x={start} to {start+181} mm.', fontsize=9)
        page.insert_text((14 * MM, 163 * MM),
                         'Trim white paper; align the repeated 30 mm strip and tape.', fontsize=9)
        page.draw_line((14 * MM, 175 * MM), (114 * MM, 175 * MM), width=.7)
        for x in [14, 114]:
            page.draw_line((x * MM, 173 * MM), (x * MM, 177 * MM), width=.7)
        page.insert_text((45 * MM, 182 * MM), '100 mm scale check', fontsize=9)
tiled.save(OUT / 'panel-study-A4-tiles.pdf')
print('Saved full-size face/underside PDFs and four A4 tiles; no drill release.')
