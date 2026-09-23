#!/usr/bin/env node
/*
  refresh-newsletter.mjs

  Fetches the latest Exclusion Debt posts from the Substack RSS feed and
  injects them into site/blog.html between <!-- NEWSLETTER-START --> and
  <!-- NEWSLETTER-END --> markers.

  Runs weekly (Monday 10:00 UTC) via .github/workflows/newsletter-refresh.yml,
  on-demand via the "Run workflow" button in the GitHub Actions UI, and
  whenever this script or the workflow file changes.

  Substack returns HTTP 403 to GitHub Actions runners, so the script falls back to
  Substack's JSON archive and then to the rss2json.com relay (see SOURCES below).

  Environment:
    FEED_URL (optional) - RSS URL. Defaults to the Exclusion Debt Substack feed.
    MAX_POSTS (optional) - How many posts to show. Defaults to 6.
*/

import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const BLOG_PATH = join(__dirname, '..', 'site', 'blog.html');
const START = '<!-- NEWSLETTER-START -->';
const END = '<!-- NEWSLETTER-END -->';

const NEWSLETTER_NAME = 'Exclusion Debt';
const NEWSLETTER_URL = 'https://exclusiondebt.substack.com';
const SUBSCRIBE_URL = `${NEWSLETTER_URL}/subscribe`;

const FEED_URL = process.env.FEED_URL || `${NEWSLETTER_URL}/feed`;

const MAX_POSTS = Number(process.env.MAX_POSTS || 6);

// --- helpers -----------------------------------------------------------------

function esc(s) {
  if (s == null) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function decodeEntities(s) {
  return String(s)
    .replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n)))
    .replace(/&#x([0-9a-f]+);/gi, (_, n) => String.fromCodePoint(parseInt(n, 16)))
    .replace(/&quot;/g, '"').replace(/&#39;|&apos;/g, "'")
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&');
}

function stripHtml(s) {
  if (!s) return '';
  return decodeEntities(String(s).replace(/<[^>]+>/g, '')).replace(/\s+/g, ' ').trim();
}

function truncate(s, n) {
  s = stripHtml(s);
  if (s.length <= n) return s;
  return s.slice(0, n - 1).replace(/\s+\S*$/, '') + '…';
}

function formatDate(iso) {
  const d = new Date(iso);
  if (isNaN(d.getTime())) return '';
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
}

// --- RSS parsing (minimal, covers Substack's structure) ----------------------

function extractTag(itemXml, tag) {
  const re = new RegExp(`<${tag}[^>]*>([\\s\\S]*?)</${tag}>`, 'i');
  const m = itemXml.match(re);
  if (!m) return '';
  let content = m[1].trim();
  const cdata = content.match(/^\s*<!\[CDATA\[([\s\S]*?)\]\]>\s*$/);
  if (cdata) content = cdata[1];
  return content.trim();
}

function extractAttr(itemXml, tag, attr) {
  const re = new RegExp(`<${tag}[^>]*\\s${attr}\\s*=\\s*"([^"]*)"`, 'i');
  const m = itemXml.match(re);
  return m ? decodeEntities(m[1]) : '';
}

function parseFeed(xml) {
  const itemMatches = xml.match(/<item[\s\S]*?<\/item>/gi) || [];
  return itemMatches.map(item => ({
    title: stripHtml(extractTag(item, 'title')),
    link: stripHtml(extractTag(item, 'link')),
    pubDate: extractTag(item, 'pubDate'),
    description: extractTag(item, 'description'),
    // Substack puts the cover image in <enclosure url="...">
    image: extractAttr(item, 'enclosure', 'url') || extractAttr(item, 'media:content', 'url')
  }));
}

// --- HTML rendering ----------------------------------------------------------

function renderEmpty() {
  return `      <div class="newsletter-empty" style="grid-column:1/-1;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:20px;padding:32px 36px;background:var(--white);border-radius:14px;border:1px solid rgba(91,129,112,0.14);">
        <div style="flex:1 1 320px;">
          <h3 style="font-family:var(--font-head);font-size:1.25rem;color:var(--charcoal);line-height:1.3;margin-bottom:8px;font-weight:400;">The first issue of ${NEWSLETTER_NAME} is on its way.</h3>
          <p style="font-size:0.92rem;color:var(--charcoal-soft);line-height:1.6;margin:0;">Subscribe on Substack and it lands in your inbox the day it publishes. New issues appear here automatically.</p>
        </div>
        <a href="${SUBSCRIBE_URL}" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;padding:13px 26px;border-radius:100px;background:var(--green-darker);color:#ffffff;font-weight:700;font-size:0.88rem;white-space:nowrap;">Subscribe free &rarr;</a>
      </div>`;
}

function renderCards(posts) {
  if (!posts.length) return renderEmpty();

  return posts.map(p => {
    const title = esc(p.title || 'Untitled issue');
    const link = p.link || NEWSLETTER_URL;
    const date = formatDate(p.pubDate);
    const excerpt = truncate(p.description, 180);
    const imgTag = p.image
      ? `        <div class="newsletter-card-image" style="background-image:url('${esc(p.image)}');background-size:cover;background-position:center;aspect-ratio:16/9;border-radius:12px 12px 0 0;"></div>\n`
      : '';
    return `      <a class="newsletter-card" href="${esc(link)}" target="_blank" rel="noopener" style="display:flex;flex-direction:column;background:var(--white);border-radius:12px;border:1px solid rgba(91,129,112,0.14);overflow:hidden;text-decoration:none;color:inherit;transition:transform 0.2s,box-shadow 0.2s;">
${imgTag}        <div style="padding:22px 24px;display:flex;flex-direction:column;flex:1;">
          ${date ? `<span style="font-size:0.72rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:var(--green-dark);margin-bottom:10px;">${esc(date)}</span>` : ''}
          <h3 style="font-family:var(--font-head);font-size:1.2rem;color:var(--charcoal);line-height:1.3;margin-bottom:10px;font-weight:400;">${title}</h3>
          ${excerpt ? `<p style="font-size:0.9rem;color:var(--charcoal-soft);line-height:1.6;margin-bottom:14px;flex:1;">${esc(excerpt)}</p>` : '<div style="flex:1;"></div>'}
          <span style="font-size:0.82rem;font-weight:700;color:var(--green-dark);">Read on Substack →</span>
        </div>
      </a>`;
  }).join('\n');
}

// --- main --------------------------------------------------------------------

const BROWSER_HEADERS = {
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
  'accept-language': 'en-GB,en;q=0.9'
};

// Substack blocks some cloud IP ranges (including GitHub Actions runners) with HTTP 403,
// so try the feed directly first, then Substack's JSON archive, then a public RSS-to-JSON relay.
const SOURCES = [
  {
    name: 'Substack RSS',
    url: FEED_URL,
    accept: 'application/rss+xml, application/xml;q=0.9, */*;q=0.8',
    parse(text) {
      // A brand-new publication has a valid feed with no <item> yet, so accept any RSS channel.
      if (!/<rss[\s>]/i.test(text) || !/<channel[\s>]/i.test(text)) throw new Error('response is not an RSS feed');
      return parseFeed(text);
    }
  },
  {
    name: 'Substack JSON archive',
    url: `${NEWSLETTER_URL}/api/v1/archive?sort=new&limit=${MAX_POSTS}`,
    accept: 'application/json',
    parse(text) {
      const data = JSON.parse(text);
      if (!Array.isArray(data)) throw new Error('unexpected JSON shape');
      return data.map(p => ({
        title: p.title,
        link: p.canonical_url,
        pubDate: p.post_date,
        description: p.subtitle || p.description || '',
        image: p.cover_image || ''
      }));
    }
  },
  {
    name: 'rss2json relay',
    url: `https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent(FEED_URL)}`,
    accept: 'application/json',
    parse(text) {
      const data = JSON.parse(text);
      if (data.status !== 'ok' || !Array.isArray(data.items)) throw new Error(data.message || 'relay returned an error');
      return data.items.map(p => ({
        title: p.title,
        link: p.link,
        pubDate: p.pubDate && p.pubDate.replace(' ', 'T') + 'Z',
        description: p.description || '',
        image: (p.enclosure && p.enclosure.link) || p.thumbnail || ''
      }));
    }
  }
];

async function fetchPosts() {
  const errors = [];
  for (const src of SOURCES) {
    try {
      console.log(`Trying ${src.name}: ${src.url}`);
      const res = await fetch(src.url, { headers: { ...BROWSER_HEADERS, accept: src.accept }, redirect: 'follow' });
      if (!res.ok) { errors.push(`${src.name}: HTTP ${res.status}`); continue; }
      const posts = src.parse(await res.text());
      console.log(`  ✓ ${src.name} returned ${posts.length} post(s)`);
      return { source: src.name, posts };
    } catch (err) {
      errors.push(`${src.name}: ${err.message}`);
    }
  }
  throw new Error(`All newsletter sources failed:\n  ${errors.join('\n  ')}`);
}

async function main() {
  const { source, posts: all } = await fetchPosts();
  const posts = all
    .filter(p => p.title && p.link)
    .sort((a, b) => new Date(b.pubDate) - new Date(a.pubDate))
    .slice(0, MAX_POSTS);
  console.log(`Using ${posts.length} post(s) from ${source}`);
  if (process.env.GITHUB_ACTIONS) console.log(`::notice title=Newsletter source::${source} (${posts.length} post(s))`);
  posts.forEach((p, i) => console.log(`  ${i + 1}. ${p.title || '(no title)'} - ${p.pubDate || '(no date)'}`));

  const html = renderCards(posts);
  const blog = readFileSync(BLOG_PATH, 'utf8');

  const startIdx = blog.indexOf(START);
  const endIdx = blog.indexOf(END);
  if (startIdx === -1 || endIdx === -1) {
    throw new Error(`Missing markers in blog.html. Expected ${START} ... ${END}`);
  }

  const before = blog.slice(0, startIdx + START.length);
  const after = blog.slice(endIdx);
  const current = blog.slice(startIdx + START.length, endIdx).replace(/\n?<!-- refreshed at [^>]* -->\n?/, '\n');

  // Only rewrite (and so only commit) when the posts themselves changed, not just the timestamp.
  if (current.trim() === html.trim()) {
    console.log('No changes to blog.html.');
    return;
  }

  const stamp = new Date().toISOString();
  writeFileSync(BLOG_PATH, `${before}\n<!-- refreshed at ${stamp} -->\n${html}\n      ${after}`);
  console.log(`✓ Updated blog.html at ${BLOG_PATH}`);
}

main().catch(err => {
  console.error('refresh-newsletter failed:', err.message);
  // Surface the reason as a GitHub Actions annotation, visible on the run page without opening the logs
  if (process.env.GITHUB_ACTIONS) console.log(`::error title=Newsletter refresh failed::${err.message.replace(/\n/g, '%0A')}`);
  process.exitCode = 1;
});
