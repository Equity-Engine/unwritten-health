#!/usr/bin/env python3
"""
Build the Unwritten Health site.

  python3 scripts/build_site.py

What it does:
  1. Builds every page in src/pages/*.html into site/<slug>.html, wrapping the
     page content in the shared <head>, header, call-to-action band and footer.
  2. Puts the same header and footer on the older pages we keep (KEPT_PAGES),
     replacing their old menu and footer, and repoints links to retired pages.
  3. Rewrites site/sitemap.xml and the managed block in site/_redirects.

Netlify has no build step: run this locally, then commit the changed files in site/.
Edit page copy in src/pages, not in the generated site/*.html files.

Each src/pages file starts with a JSON header in an HTML comment:
  <!--meta {"slug": "pricing", "title": "...", "description": "...", "nav": "pricing"} -->
Optional keys: "cta": false (no call-to-action band), "sticky": false,
"schema": [extra JSON-LD objects], "og_type", "priority", "changefreq".
In page content, {{icon:NAME}} inlines an icon from src/icons/NAME.svg and
{{BOOK}} / {{BLOG}} expand to the booking and blog URLs.
"""
import datetime
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'
SITE = ROOT / 'site'
BASE = 'https://unwritten.health'
TODAY = datetime.date.today().isoformat()

BOOK = 'https://meetings-eu1.hubspot.com/ashish-rishi?uuid=b7b6b6ed-3b13-4c64-aa8d-d759c67698db'
BLOG = 'https://substack.com/@exclusiondebt'

DESCRIPTOR = 'Patient experience data and patient recruitment, UK'

STAGES = [
    ('Develop', '/patient-involvement'),
    ('Clinical trials', '/clinical-trial-recruitment'),
    ('Launch and access', '/launch-and-access'),
    ('Everyday care', '/everyday-care'),
]
ROLES = [
    ('Clinical development and recruitment', '/clinical-development'),
    ('Patient insight', '/patient-insight'),
    ('Medical affairs', '/medical-affairs'),
    ('Market access and HEOR', '/market-access'),
    ('Medtech and digital health', '/medtech-digital-health'),
    ('Market research agencies', '/market-research-agencies'),
]
# Menu: (key, label, href, dropdown groups or None)
NAV = [
    ('whatwedo', 'What we do', '/#stages', [
        ('Four stages', STAGES),
        ('How we work', [('Ask our data, then members live', '/ask-our-data')]),
    ]),
    ('members', 'Our members', '/patient-panel', None),
    ('who', "Who it's for", '/who-its-for', [
        ('By role', ROLES),
        ('By location', [('Sponsors outside the UK', '/clinical-trials-in-the-uk')]),
    ]),
    ('trust', 'Trust', '/trust', None),
    ('about', 'About', '/about', None),
]
FOOTER_COLUMNS = [
    ('What we do', STAGES + [
        ('Ask our data', '/ask-our-data'), ('The report', '/patient-involvement-report'), ('Sample report', '/sample-report'),
        ('Free panel count', '/panel-count'), ('Tell us about your clinical trial', '/tell-us-about-your-trial'),
    ]),
    ("Who it's for", ROLES + [('Sponsors outside the UK', '/clinical-trials-in-the-uk'), ('NHS teams', '/nhs'), ('Suppliers to the NHS', '/suppliers')]),
    ('Learn', [
        ('Our members', '/patient-panel'), ('Questions', '/questions'), ('Case study', '/case-study-phase-ii-biotech'),
        ('Exclusion debt', '/exclusion-debt'), ('Equity Engine', '/equity-engine'), ('Resources', '/resources'),
        ('Press', '/press'), ('Blog', BLOG),
    ]),
    ('Company', [
        ('About', '/about'), ('Trust', '/trust'), ('Contact', '/contact'), ('Privacy', '/privacy'),
        ('Terms', '/terms'), ('Accessibility', '/accessibility'),
    ]),
]

# Older pages kept live but out of the menu. They get the new header and footer.
KEPT_PAGES = [
    'blog', 'blog-1-inclusion-infrastructure', 'blog-2-lived-experience-data', 'blog-3-portfolio-inclusion',
    'blog-4-mhra-2026-regulatory-revolution', 'blog-5-frequency-of-exclusion', 'contact', 'privacy', 'terms',
    'refund-policy', 'accessibility',
]
# Retired pages: old address -> new address (301). Links on kept pages are repointed too.
RETIRED = {
    'solutions': '/who-its-for',
    'solutions-jca': '/market-access',
    'solutions-patient-council': '/patient-insight',
    'solutions-samd': '/medtech-digital-health',
    'solutions-pmcf': '/medtech-digital-health',
    'solutions-esf-dtac': '/medtech-digital-health',
    'solutions-nihr-ppi': '/clinical-development',
    'regulatory-alignment': '/patient-involvement-report',
    'trust-ethics': '/trust',
    # October 2026: prices taken off the site; Toolkits and Scorecard retired
    'pricing': '/panel-count',
    'scorecard': '/panel-count',
    'toolkits': '/resources',
    'how-it-works': '/patient-involvement',
    # Agreed wording, 19 October 2026: the free same-day count is a "panel count"
    'panel-check': '/panel-count',
    # Positioning bible, 20 October 2026: audiences by role, not sector
    'researchers': '/clinical-development',
    'academic-research': '/clinical-development',
    'pharma': '/clinical-development',
    'biotech': '/clinical-development',
    'medtech': '/medtech-digital-health',
    'digital-health': '/medtech-digital-health',
}

ORG = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    '@id': BASE + '/#organization',
    'name': 'Unwritten Health',
    'url': BASE + '/',
    'logo': BASE + '/images/logo-mark.png',
    'slogan': DESCRIPTOR + '.',
    'description': 'Unwritten Health is a UK patient experience data company. 13,050 people across the UK living with long-term conditions have joined us, and growing daily; clients ask them questions and recruit from them.',
    'knowsAbout': ['Patient experience data', 'Patient recruitment', 'Clinical trial recruitment', 'Clinical trials in the UK', 'Clinical trial feasibility', 'Patient and public involvement (PPI)', 'Patient advisory boards', 'Healthcare market research recruitment'],
    'identifier': {'@type': 'PropertyValue', 'propertyID': 'Companies House company number', 'value': '16561594'},
    'address': {
        '@type': 'PostalAddress',
        'streetAddress': 'First Floor, Swan Buildings, 20 Swan Street',
        'addressLocality': 'Manchester',
        'postalCode': 'M4 5JW',
        'addressCountry': 'GB',
    },
    'areaServed': {'@type': 'Country', 'name': 'United Kingdom'},
    'founder': {'@type': 'Person', 'name': 'Ashish Rishi'},
}


def icon(name, cls=''):
    svg = (SRC / 'icons' / f'{name}.svg').read_text(encoding='utf-8')
    svg = re.sub(r'<!--.*?-->', '', svg, flags=re.S).strip()
    svg = re.sub(r'\s(width|height|class)="[^"]*"', '', svg, count=3)
    svg = re.sub(r'\s+', ' ', svg).replace('> <', '><')
    extra = f' class="{cls}"' if cls else ''
    return svg.replace('<svg', f'<svg aria-hidden="true" focusable="false"{extra}', 1)


EXT = '<span class="uh-sr"> (opens in a new tab)</span>'


def link(label, href, cls=''):
    c = f' class="{cls}"' if cls else ''
    if href.startswith('http'):
        return f'<a{c} href="{href}" target="_blank" rel="noopener">{html.escape(label)}{EXT}</a>'
    return f'<a{c} href="{href}">{html.escape(label)}</a>'


def header_html(active=None):
    chevron = icon('chevron-down')
    arrow = icon('arrow-up-right', 'uh-ext')
    links, mobile = [], []
    for key, label, href, groups in NAV:
        cur = ' aria-current="page"' if key == active else ''
        if groups:
            inner = ''.join(
                f'<span class="uh-dd-label">{html.escape(g)}</span>' + ''.join(link(l, h) for l, h in items)
                for g, items in groups)
            links.append(
                f'<div class="uh-dd"><a href="{href}"{cur}>{html.escape(label)}</a>'
                f'<button class="uh-dd-toggle" type="button" aria-expanded="false" aria-controls="uh-dd-{key}" aria-label="Show {html.escape(label)} pages">{chevron}</button>'
                f'<div class="uh-dd-menu" id="uh-dd-{key}">{inner}</div></div>')
            mobile.append(f'<span class="uh-mobile-label uh-mobile-top">{html.escape(label)}</span><div class="uh-mobile-sub">'
                          + ''.join(link(l, h) for _, items in groups for l, h in items) + '</div>')
        else:
            links.append(f'<a href="{href}"{cur}>{html.escape(label)}</a>')
            mobile.append(f'<a href="{href}">{html.escape(label)}</a>')
    links.append(f'<a href="{BLOG}" target="_blank" rel="noopener">Blog{arrow}{EXT}</a>')
    mobile.append(f'<a href="{BLOG}" target="_blank" rel="noopener">Blog{arrow}{EXT}</a>')
    mobile.append('<a class="uh-btn-nav" href="/panel-count">Free panel count</a>')
    mobile.append(f'<a class="uh-mobile-book" href="{BOOK}" target="_blank" rel="noopener">Book 30 minutes with Ashish{EXT}</a>')
    return (
        '<a class="uh-skip" href="#main">Skip to content</a>\n'
        '<header class="uh-header"><div class="uh-header-inner">'
        '<a class="uh-logo" href="/" aria-label="Unwritten Health home"><img src="/images/logo-horizontal.svg" alt="Unwritten Health" width="160" height="28">'
        f'<span class="uh-descriptor">{DESCRIPTOR}</span></a>'
        f'<div class="uh-nav" role="navigation" aria-label="Main">{"".join(links)}</div>'
        '<a class="uh-btn-nav" href="/panel-count">Free panel count</a>'
        '<button class="uh-burger" type="button" aria-expanded="false" aria-controls="uh-mobile" aria-label="Open menu"><span></span><span></span><span></span></button>'
        '</div></header>\n'
        f'<div class="uh-mobile" id="uh-mobile" role="navigation" aria-label="Mobile">{"".join(mobile)}</div>'
    )


def cta_html():
    return (
        '<section class="uh-cta" aria-labelledby="uh-cta-title"><div class="uh-cta-inner">'
        '<div><h2 id="uh-cta-title">How many patients like yours could you involve?</h2>'
        "<p>Find out with a free panel count. Tell us who your clinical trial or product is for, and we'll reply the same working day with how many people like that have joined us, and how they break down.</p></div>"
        '<div class="uh-cta-actions"><a class="uh-btn-light" href="/panel-count">Free panel count</a>'
        f'<a class="uh-cta-link" href="{BOOK}" target="_blank" rel="noopener">Book 30 minutes with Ashish{EXT}</a></div>'
        '</div></section>'
    )


def footer_html(sticky=True):
    cols = ''.join(
        f'<div class="uh-footer-col"><p class="uh-footer-h">{html.escape(t)}</p>' + ''.join(link(l, h) for l, h in items) + '</div>'
        for t, items in FOOTER_COLUMNS)
    out = (
        '<div class="uh-footer" role="contentinfo"><div class="uh-footer-inner">'
        '<div class="uh-footer-top"><div>'
        '<a class="uh-footer-logo" href="/" aria-label="Unwritten Health home"><img src="/images/logo-horizontal.svg" alt="Unwritten Health" width="150" height="26"></a>'
        f'<p class="uh-footer-tag">{DESCRIPTOR}.</p>'
        '<p class="uh-footer-note">UK today, Europe next.</p>'
        f'</div><div class="uh-footer-links">{cols}</div></div>'
        '<div class="uh-footer-legal"><span>Unwritten Health · Company number 16561594 · First Floor, Swan Buildings, 20 Swan Street, Manchester, England, M4 5JW</span>'
        '<a href="#cookie-settings" onclick="if(window.openCookieSettings){window.openCookieSettings();}return false;">Cookie settings</a></div>'
        '</div></div>'
    )
    if sticky:
        out += '\n<a class="uh-sticky" href="/panel-count">Free panel count</a>'
    return out


def head_html(m):
    slug = m['slug']
    url = BASE + ('/' if slug == 'index' else '/' + slug)
    title = html.escape(m['title'])
    desc = html.escape(m['description'])
    schema = [ORG] + m.get('schema', [])
    kw = f'\n<meta name="keywords" content="{html.escape(m["keywords"])}">' if m.get('keywords') else ''
    ld = '\n'.join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schema)
    return f'''<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">{kw}
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{url}">
<link rel="alternate" hreflang="x-default" href="{url}">
<meta property="og:type" content="{m.get('og_type', 'website')}">
<meta property="og:site_name" content="Unwritten Health">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/images/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="en_GB">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{BASE}/images/og-image.jpg">
<link rel="icon" type="image/png" href="/images/logo-mark.png">
<link rel="apple-touch-icon" href="/images/logo-mark.png">
<meta name="theme-color" content="#FAF8F5">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bentham&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/chrome.css">
<link rel="stylesheet" href="/styles.css">
<script defer src="/analytics.js"></script>
<script defer src="/chrome.js"></script>
{ld}
</head>'''


def expand(content):
    content = re.sub(r'\{\{icon:([a-z0-9-]+)\}\}', lambda mm: icon(mm.group(1)), content)
    grid100 = ''.join('<span class="off"></span>' if i < 26 else '<span></span>' for i in range(100))
    content = content.replace('{{grid100}}', grid100)
    return content.replace('{{BOOK}}', BOOK).replace('{{BLOG}}', BLOG).replace('{{EXT}}', EXT)


def build_pages():
    built = []
    for path in sorted((SRC / 'pages').glob('*.html')):
        raw = path.read_text(encoding='utf-8')
        mm = re.match(r'\s*<!--meta\s+(\{.*?\})\s*-->\s*', raw, re.S)
        if not mm:
            raise SystemExit(f'{path.name}: missing <!--meta {{...}} --> header')
        meta = json.loads(mm.group(1))
        body = expand(raw[mm.end():])
        page = (
            head_html(meta) + '\n<body>\n' + header_html(meta.get('nav')) + '\n'
            + f'<main id="main">\n{body.strip()}\n</main>\n'
            + (cta_html() + '\n' if meta.get('cta', True) else '')
            + footer_html(meta.get('sticky', True)) + '\n</body>\n</html>\n'
        )
        (SITE / f"{meta['slug']}.html").write_text(page, encoding='utf-8')
        built.append(meta)
    return built


# ---------- Kept pages ----------

def strip_block(text, start_pat, tag='div'):
    """Remove an element that starts at start_pat, matching nested <tag> elements."""
    m = re.search(start_pat, text)
    if not m:
        return text
    i, depth = m.start(), 0
    for t in re.finditer(rf'<(/?){tag}\b[^>]*>', text[i:]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            end = i + t.end()
            return text[:i] + text[end:].lstrip('\n')
    raise SystemExit(f'Unbalanced <{tag}> from {start_pat!r}')


def chrome_kept(name):
    path = SITE / f'{name}.html'
    t = path.read_text(encoding='utf-8')
    hdr = '<!-- UH:HEADER -->\n' + header_html() + '\n<!-- /UH:HEADER -->'
    ftr = '<!-- UH:FOOTER -->\n' + cta_html() + '\n' + footer_html() + '\n<!-- /UH:FOOTER -->'

    if '<!-- UH:HEADER -->' in t:
        t = re.sub(r'<!-- UH:HEADER -->.*?<!-- /UH:HEADER -->', lambda _: hdr, t, flags=re.S)
        t = re.sub(r'<!-- UH:FOOTER -->.*?<!-- /UH:FOOTER -->', lambda _: ftr, t, flags=re.S)
    else:
        # Old menu (+ inline toggle script + separate mobile menu) -> new header
        t = re.sub(r'<nav class="site-nav" id="mainNav">.*?</nav>\s*'
                   r'(<script>function toggleMenu\(\)\{[^<]*\}</script>\s*)?', '<!--UH-HDR-SLOT-->\n', t, count=1, flags=re.S)
        if '<!--UH-HDR-SLOT-->' not in t:
            raise SystemExit(f'{name}: old menu not found')
        while re.search(r'<div class="mobile-menu"', t):
            t = strip_block(t, r'<div class="mobile-menu"')
        while re.search(r'<div class="sticky-mobile-cta"', t):
            t = strip_block(t, r'<div class="sticky-mobile-cta"')
        t = t.replace('<!--UH-HDR-SLOT-->', hdr, 1)
        # Old site footer -> new footer. The feature catalogue keeps its own document footer.
        if name == 'equity-engine-mvp-2-feature-catalog':
            t = t.replace('</body>', ftr + '\n</body>', 1)
        else:
            t, n = re.subn(r'<footer\b[^>]*>.*?</footer>', lambda _: ftr, t, count=1, flags=re.S)
            if not n:
                raise SystemExit(f'{name}: old footer not found')
        if '/chrome.css' not in t:
            extra = '  <style>body { padding-top: var(--uh-header-h); }</style>\n' if name == 'equity-engine-mvp-2-feature-catalog' else ''
            t = t.replace('</head>', '  <link rel="stylesheet" href="/chrome.css" />\n  <script defer src="/chrome.js"></script>\n' + extra + '</head>', 1)

    # Repoint links to retired pages
    for old, new in RETIRED.items():
        t = re.sub(rf'href="(/?){re.escape(old)}(\.html)?(#[^"]*)?"', f'href="{new}"', t)
    t = t.replace('href="index.html"', 'href="/"')
    path.write_text(t, encoding='utf-8')


# ---------- Sitemap and redirects ----------

def write_sitemap(built):
    urls = []
    for m in built:
        if m.get('sitemap', True) is False:
            continue
        loc = BASE + ('/' if m['slug'] == 'index' else '/' + m['slug'])
        urls.append((loc, m.get('priority', '0.8'), m.get('changefreq', 'monthly')))
    for name in KEPT_PAGES:
        urls.append((f'{BASE}/{name}', '0.4' if name in ('privacy', 'terms', 'refund-policy', 'accessibility') else '0.5', 'monthly'))
    body = '\n'.join(
        f'  <url><loc>{loc}</loc><lastmod>{TODAY}</lastmod><changefreq>{cf}</changefreq><priority>{pr}</priority></url>'
        for loc, pr, cf in urls)
    (SITE / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + body + '\n</urlset>\n', encoding='utf-8')
    return len(urls)


def write_redirects():
    path = SITE / '_redirects'
    t = path.read_text(encoding='utf-8')
    lines = ['# BEGIN build_site.py: retired pages (edit RETIRED in scripts/build_site.py)']
    for old, new in RETIRED.items():
        lines.append(f'/{old}    {new}    301')
        lines.append(f'/{old}.html    {new}    301')
    lines.append('# END build_site.py')
    block = '\n'.join(lines)
    if '# BEGIN build_site.py' in t:
        t = re.sub(r'# BEGIN build_site\.py.*?# END build_site\.py', lambda _: block, t, flags=re.S)
    else:
        t = t.rstrip('\n') + '\n\n' + block + '\n'
    path.write_text(t, encoding='utf-8')


if __name__ == '__main__':
    built = build_pages()
    for name in KEPT_PAGES:
        chrome_kept(name)
    n = write_sitemap(built)
    write_redirects()
    print(f'Built {len(built)} pages, refreshed {len(KEPT_PAGES)} kept pages, sitemap has {n} URLs.')
