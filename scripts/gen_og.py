#!/usr/bin/env python3
"""Makes a 1200x630 link preview card for every page: site/images/og/<slug>.jpg, from the page's kicker and H1.
Run after build_site.py, then run build_site.py again so the pages point at their cards.
Only cards whose text (or this template) changed are re-rendered. Needs Google Chrome and Node."""
import hashlib, html, json, re, subprocess, tempfile, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
OUT = SITE / 'images' / 'og'
MANIFEST = ROOT / 'scripts' / 'og-manifest.json'
DESCRIPTOR = 'Patient experience data and patient recruitment, UK'
# Pages with no card of their own: verification files, internal tools, and pages that keep a custom image
SKIP = {'65f13a4c20d2a636383f5a360a5c3b57', 'admin-report', 'blog-5-frequency-of-exclusion'}
# The home H1 is the descriptor, which the card's footer bar already shows, so it leads with the first promise
OVERRIDES = {'index': {'kicker': 'UK today, Europe next',
                       'title': "Ask the people with lived experience of the condition, before it's final."}}
KICKER_FALLBACK = {'blog': 'Blog', 'contact': 'Contact', 'privacy': 'Privacy', 'terms': 'Terms',
                   'refund-policy': 'Refunds', 'accessibility': 'Accessibility'}

TEMPLATE = '''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Bentham&family=Manrope:wght@500;600;700&display=block" rel="stylesheet">
<style>
html,body{margin:0;width:1200px;height:630px;overflow:hidden;background:#FAF8F5}
body{position:relative;font-family:Manrope,system-ui,sans-serif;color:#2B2B2F}
.mark{position:absolute;right:-60px;top:70px;width:460px;height:460px;opacity:.12}
.logo{position:absolute;left:80px;top:62px;height:34px}
.copy{position:absolute;left:80px;top:138px;width:900px;height:372px;display:flex;flex-direction:column;justify-content:center}
.kicker{font-weight:700;font-size:18px;letter-spacing:.14em;text-transform:uppercase;color:#3f6152;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin:0 0 20px}
h1{font-family:Bentham,Georgia,serif;font-weight:400;font-size:66px;line-height:1.1;margin:0;color:#2B2B2F;letter-spacing:-.005em}
.bar{position:absolute;left:0;right:0;bottom:0;height:84px;background:#2e4a3c;color:#FAF8F5;display:flex;align-items:center;justify-content:space-between;padding:0 80px;font-weight:600;font-size:21px}
.bar .url{color:#e4ece8;font-weight:500}
</style></head><body>
<img class="mark" src="{MARK}" alt="">
<img class="logo" src="{LOGO}" alt="">
<div class="copy"><p class="kicker" id="k"></p><h1 id="t"></h1></div>
<div class="bar"><span>{DESCRIPTOR}</span><span class="url">unwritten.health</span></div>
<script>
window.__ready = false;
const d = JSON.parse(decodeURIComponent(location.hash.slice(1)));
const k = document.getElementById('k'), t = document.getElementById('t');
k.textContent = d.kicker; if (!d.kicker) k.style.display = 'none';
t.textContent = d.title;
document.fonts.ready.then(() => {
  const room = 372 - (d.kicker ? k.offsetHeight + 20 : 0);
  let s = 66;
  while (t.offsetHeight > room && s > 36) { s -= 2; t.style.fontSize = s + 'px'; }
  window.__info = {size: s, overflow: t.offsetHeight > room};
  window.__ready = true;
});
</script></body></html>'''


def text(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


def page_card(path):
    raw = path.read_text(encoding='utf-8')
    body = raw.split('<!-- /UH:HEADER -->')[-1]
    body = body.split('<main id="main">', 1)[-1]
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', body, re.S)
    if not h1:
        return None
    before = body[:h1.start()]
    kk = re.findall(r'<(?:span|p|div)[^>]*class="[^"]*\b(?:hero-kicker|kicker|eyebrow)\b[^"]*"[^>]*>(.*?)</(?:span|p|div)>', before, re.S)
    kicker = text(kk[-1]) if kk else KICKER_FALLBACK.get(path.stem, 'Blog' if path.stem.startswith('blog-') else '')
    return {'kicker': kicker, 'title': text(h1.group(1))}


def main():
    template = (TEMPLATE.replace('{MARK}', (SITE / 'images' / 'mark.svg').as_uri())
                .replace('{LOGO}', (SITE / 'images' / 'logo-horizontal.svg').as_uri())
                .replace('{DESCRIPTOR}', DESCRIPTOR))
    tver = hashlib.sha1(template.encode()).hexdigest()[:10]
    old = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    cards = {}
    for path in sorted(SITE.glob('*.html')):
        if path.stem in SKIP:
            continue
        c = OVERRIDES.get(path.stem) or page_card(path)
        if c:
            cards[path.stem] = c
    cards['_default'] = dict(cards['index'])  # site-wide fallback, also written to images/og-image.jpg
    tmp = Path(tempfile.mkdtemp())
    (tmp / 'card.html').write_text(template, encoding='utf-8')
    jobs, new = [], {}
    for slug, c in cards.items():
        key = hashlib.sha1(json.dumps([tver, c], sort_keys=True).encode()).hexdigest()[:12]
        new[slug] = key
        out = SITE / 'images' / 'og-image.jpg' if slug == '_default' else OUT / f'{slug}.jpg'
        if old.get(slug) != key or not out.exists():
            jobs.append({'url': (tmp / 'card.html').as_uri() + '#' + urllib.parse.quote(json.dumps(c)), 'out': str(out)})
    if jobs:
        spec = tmp / 'jobs.json'
        spec.write_text(json.dumps({'width': 1200, 'height': 630, 'jobs': jobs}))
        subprocess.run(['node', str(ROOT / 'scripts' / 'render-shots.mjs'), str(spec)], check=True, stdout=subprocess.DEVNULL)
        for j in jobs:
            info = Path(j['out'] + '.json')
            if info.exists():
                i = json.loads(info.read_text()); info.unlink()
                if i.get('overflow'):
                    print('WARNING: title too long for its card:', Path(j['out']).name)
    for stale in OUT.glob('*.jpg'):
        if stale.stem not in cards:
            stale.unlink()
    MANIFEST.write_text(json.dumps(new, indent=1, sort_keys=True) + '\n')
    print(f'{len(cards) - 1} page cards, {len(jobs)} rendered')


if __name__ == '__main__':
    main()
