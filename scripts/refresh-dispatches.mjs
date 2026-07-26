#!/usr/bin/env node
/*
  refresh-dispatches.mjs

  Fetches the latest Unwritten Dispatches posts from the Beehiiv RSS feed and
  injects them into site/blog.html between <!-- DISPATCHES-START --> and
  <!-- DISPATCHES-END --> markers.

  Runs weekly (Monday 10:00 UTC) via .github/workflows/dispatches-refresh.yml,
  or on-demand via the "Run workflow" button in the GitHub Actions UI.

  Environment:
    FEED_URL (optional) - Beehiiv RSS URL. Defaults to the custom-domain feed.
    MAX_POSTS (optional) - How many posts to show. Defaults to 6.
*/

import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const BLOG_PATH = join(__dirname, '..', 'site', 'blog.html');
const START = '<!-- DISPATCHES-START -->';
const END = '<!-- DISPATCHES-END -->';

const FEED_URLS = [
  process.env.FEED_URL,
  'https://rss.beehiiv.com/feeds/ODHOyDScDq.xml',   // Unwritten Dispatches (canonical Beehiiv RSS)
  'https://dispatches.unwritten.health/feed',        // fallback if custom-domain RSS gets enabled later
  'https://dispatches.unwritten.health/feed.xml',
  'https://dispatches.unwritten.health/rss'
].filter(Boolean);

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

function stripHtml(s) {
  if (!s) return '';
  return String(s).replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ').trim();
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

// --- RSS parsing (minimal, XML.subset for Beehiiv structure) -----------------

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
  return m ? m[1] : '';
}

function parseFeed(xml) {
  // Split into <item> blocks
  const itemMatches = xml.match(/<item[\s\S]*?<\/item>/gi) || [];
  const posts = itemMatches.map(item => ({
    title: extractTag(item, 'title'),
    link: extractTag(item, 'link'),
    pubDate: extractTag(item, 'pubDate'),
    description: extractTag(item, 'description'),
    author: extractTag(item, 'author') || extractTag(item, 'dc:creator'),
    // Beehiiv sometimes uses <media:content url="..."> for the featured image
    image: extractAttr(item, 'media:content', 'url') || extractAttr(item, 'enclosure', 'url')
  }));
  return posts;
}

// --- HTML rendering ----------------------------------------------------------

function renderCards(posts) {
  if (!posts.length) {
    return `      <div class="dispatch-empty" style="grid-column:1/-1;text-align:center;padding:32px;background:var(--cream);border-radius:14px;color:var(--charcoal-soft);">
        <p style="margin-bottom:12px;">No issues fetched right now. Read the archive directly:</p>
        <a href="https://dispatches.unwritten.health" target="_blank" rel="noopener" style="color:var(--green-dark);font-weight:700;text-decoration:underline;">Open Unwritten Dispatches →</a>
      </div>`;
  }

  return posts.map(p => {
    const title = esc(p.title || 'Untitled issue');
    const link = p.link || 'https://dispatches.unwritten.health';
    const date = formatDate(p.pubDate);
    const excerpt = truncate(p.description, 180);
    const imgTag = p.image
      ? `        <div class="dispatch-card-image" style="background-image:url('${esc(p.image)}');background-size:cover;background-position:center;aspect-ratio:16/9;border-radius:12px 12px 0 0;"></div>\n`
      : '';
    return `      <a class="dispatch-card" href="${esc(link)}" target="_blank" rel="noopener" style="display:flex;flex-direction:column;background:var(--white);border-radius:12px;border:1px solid rgba(91,129,112,0.14);overflow:hidden;text-decoration:none;color:inherit;transition:transform 0.2s,box-shadow 0.2s;">
${imgTag}        <div style="padding:22px 24px;display:flex;flex-direction:column;flex:1;">
          ${date ? `<span style="font-size:0.72rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:var(--green-dark);margin-bottom:10px;">${esc(date)}</span>` : ''}
          <h3 style="font-family:var(--font-head);font-size:1.2rem;color:var(--charcoal);line-height:1.3;margin-bottom:10px;font-weight:400;">${title}</h3>
          <p style="font-size:0.9rem;color:var(--charcoal-soft);line-height:1.6;margin-bottom:14px;flex:1;">${esc(excerpt)}</p>
          <span style="font-size:0.82rem;font-weight:700;color:var(--green-dark);">Read on Dispatches →</span>
        </div>
      </a>`;
  }).join('\n');
}

// --- main --------------------------------------------------------------------

async function fetchFirstWorking(urls) {
  const errors = [];
  for (const url of urls) {
    try {
      console.log(`Trying feed: ${url}`);
      const res = await fetch(url, { headers: { 'user-agent': 'unwritten-health-dispatches-refresh/1.0' }, redirect: 'follow' });
      if (!res.ok) { errors.push(`${url}: HTTP ${res.status}`); continue; }
      const text = await res.text();
      if (text && text.includes('<item')) {
        console.log(`  ✓ Got RSS from ${url} (${text.length} bytes)`);
        return { url, text };
      }
      errors.push(`${url}: no <item> tags in response`);
    } catch (err) {
      errors.push(`${url}: ${err.message}`);
    }
  }
  throw new Error(`All feed URLs failed:\n  ${errors.join('\n  ')}`);
}

async function main() {
  const { url, text } = await fetchFirstWorking(FEED_URLS);
  const posts = parseFeed(text).slice(0, MAX_POSTS);
  console.log(`Parsed ${posts.length} post(s) from ${url}`);
  posts.forEach((p, i) => console.log(`  ${i+1}. ${p.title || '(no title)'} - ${p.pubDate || '(no date)'}`));

  const html = renderCards(posts);
  const blog = readFileSync(BLOG_PATH, 'utf8');

  const startIdx = blog.indexOf(START);
  const endIdx = blog.indexOf(END);
  if (startIdx === -1 || endIdx === -1) {
    throw new Error(`Missing markers in blog.html. Expected ${START} ... ${END}`);
  }

  const before = blog.slice(0, startIdx + START.length);
  const after = blog.slice(endIdx);
  const stamp = new Date().toISOString();
  const updated = `${before}\n<!-- refreshed at ${stamp} -->\n${html}\n      ${after}`;

  if (updated === blog) {
    console.log('No changes to blog.html.');
    return;
  }
  writeFileSync(BLOG_PATH, updated);
  console.log(`✓ Updated blog.html at ${BLOG_PATH}`);
}

main().catch(err => {
  console.error('refresh-dispatches failed:', err.message);
  process.exitCode = 1;
});
