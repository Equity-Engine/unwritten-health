#!/usr/bin/env python3
"""Makes the favicon set and square logo from the mark in site/images/logo-horizontal.svg.
Writes site/favicon.svg, site/favicon.ico, site/apple-touch-icon.png, site/icon-192.png, site/icon-512.png,
site/site.webmanifest, site/images/mark.svg and site/images/logo-square.png. Needs Google Chrome, Node and Pillow.
Run it again only if the logo changes."""
import json, re, subprocess, tempfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
SAGE, SAGE_DARK_MODE, CREAM = '#5B8170', '#9CC2B0', (250, 248, 245)


def shots(jobs, width, height):
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
        json.dump({'width': width, 'height': height, 'jobs': jobs}, f)
    subprocess.run(['node', str(ROOT / 'scripts' / 'render-shots.mjs'), f.name], check=True, stdout=subprocess.DEVNULL)


svg = (SITE / 'images' / 'logo-horizontal.svg').read_text(encoding='utf-8')
# Every sage element of the logo (the path and its four circles), without the class attribute
shapes = ''.join(re.sub(r'\s*class="cls-2"', '', e) for e in re.findall(r'<(?:path|circle)[^>]*class="cls-2"[^>]*/>', svg))
vb = re.search(r'viewBox="([^"]+)"', svg).group(1)
tmp = Path(tempfile.mkdtemp())

# 1. Measure the mark
(tmp / 'probe.html').write_text(
    f'<svg id="s" xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="1277" height="192"><g id="m">{shapes}</g></svg>'
    '<script>const b=document.getElementById("m").getBBox();window.__info={x:b.x,y:b.y,w:b.width,h:b.height};</script>')
shots([{'url': (tmp / 'probe.html').as_uri(), 'out': str(tmp / 'probe.png')}], 1300, 200)
b = json.loads((tmp / 'probe.png.json').read_text())
side = max(b['w'], b['h']) * 1.04
x0, y0 = b['x'] + b['w'] / 2 - side / 2, b['y'] + b['h'] / 2 - side / 2
square_vb = f'{x0:.2f} {y0:.2f} {side:.2f} {side:.2f}'

# 2. Vector icons
(SITE / 'images' / 'mark.svg').write_text(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{square_vb}"><g fill="{SAGE}">{shapes}</g></svg>\n', encoding='utf-8')
(SITE / 'favicon.svg').write_text(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{square_vb}"><style>g{{fill:{SAGE}}}'
    f'@media (prefers-color-scheme:dark){{g{{fill:{SAGE_DARK_MODE}}}}}</style><g>{shapes}</g></svg>\n', encoding='utf-8')

# 3. Raster master (transparent, 1024px), then every size from it
(tmp / 'mark.html').write_text(
    f'<style>html,body{{margin:0;background:transparent}}</style><img src="{(SITE / "images" / "mark.svg").as_uri()}" width="1024" height="1024">')
shots([{'url': (tmp / 'mark.html').as_uri(), 'out': str(tmp / 'mark.png'), 'transparent': True}], 1024, 1024)
mark = Image.open(tmp / 'mark.png').convert('RGBA')


def on_background(size, fill, bg):
    canvas = Image.new('RGBA', (size, size), bg + (255,) if bg else (0, 0, 0, 0))
    m = mark.resize((round(size * fill),) * 2, Image.LANCZOS)
    canvas.alpha_composite(m, ((size - m.width) // 2, (size - m.height) // 2))
    return canvas


on_background(48, 1.0, None).save(SITE / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
on_background(180, 0.72, CREAM).convert('RGB').save(SITE / 'apple-touch-icon.png', optimize=True)
on_background(192, 0.72, CREAM).convert('RGB').save(SITE / 'icon-192.png', optimize=True)
on_background(512, 0.72, CREAM).convert('RGB').save(SITE / 'icon-512.png', optimize=True)
on_background(512, 0.8, (255, 255, 255)).convert('RGB').save(SITE / 'images' / 'logo-square.png', optimize=True)
(SITE / 'site.webmanifest').write_text(json.dumps({
    'name': 'Unwritten Health', 'short_name': 'Unwritten Health', 'start_url': '/', 'display': 'browser',
    'background_color': '#FAF8F5', 'theme_color': '#FAF8F5',
    'icons': [{'src': '/icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
              {'src': '/icon-512.png', 'sizes': '512x512', 'type': 'image/png'}]}, indent=1) + '\n', encoding='utf-8')
print('icons written; mark viewBox', square_vb)
