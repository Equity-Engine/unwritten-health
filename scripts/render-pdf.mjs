// Render pages to one-page-per-URL PDFs at desktop width, using Chrome's DevTools protocol.
// Usage: node render-pdf.mjs <outDir> <url> <name> [<url> <name> ...]
// Needs Google Chrome installed. Each web page becomes a single tall PDF page (screen styles, 1280px wide).
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync } from 'node:fs';
import { setTimeout as sleep } from 'node:timers/promises';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 9333;
const WIDTH = 1280;
const [outDir, ...pairs] = process.argv.slice(2);
mkdirSync(outDir, { recursive: true });

const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--hide-scrollbars',
  `--remote-debugging-port=${PORT}`, `--user-data-dir=${outDir}/../chrome-cdp-profile`, 'about:blank'
], { stdio: 'ignore' });

async function json(path, method = 'GET') {
  for (let i = 0; i < 50; i++) {
    try { const r = await fetch(`http://127.0.0.1:${PORT}${path}`, { method }); return await r.json(); }
    catch { await sleep(200); }
  }
  throw new Error('Chrome did not start');
}

function connect(wsUrl) {
  const ws = new WebSocket(wsUrl);
  let id = 0; const pending = new Map(); const listeners = [];
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) { const { res, rej } = pending.get(msg.id); pending.delete(msg.id); msg.error ? rej(new Error(msg.error.message)) : res(msg.result); }
    else listeners.forEach((fn) => fn(msg));
  };
  const ready = new Promise((r) => (ws.onopen = r));
  const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
  const once = (event) => new Promise((r) => listeners.push((m) => m.method === event && r(m.params)));
  return { ready, send, once, close: () => ws.close() };
}

try {
  await json('/json/version');
  for (let i = 0; i < pairs.length; i += 2) {
    const url = pairs[i], name = pairs[i + 1];
    const target = await json('/json/new?about:blank', 'PUT');
    const s = connect(target.webSocketDebuggerUrl); await s.ready;
    await s.send('Page.enable'); await s.send('Runtime.enable');
    await s.send('Emulation.setDeviceMetricsOverride', { width: WIDTH, height: 900, deviceScaleFactor: 1, mobile: false });
    await s.send('Emulation.setEmulatedMedia', { media: 'screen' });
    const loaded = s.once('Page.loadEventFired');
    await s.send('Page.navigate', { url }); await loaded;
    await s.send('Runtime.evaluate', { expression: 'document.fonts ? document.fonts.ready.then(() => true) : true', awaitPromise: true });
    await sleep(700);
    const { result } = await s.send('Runtime.evaluate', { expression: 'Math.ceil(Math.max(document.documentElement.scrollHeight, document.body.scrollHeight))', returnByValue: true });
    const height = result.value;
    const pdf = await s.send('Page.printToPDF', {
      printBackground: true, preferCSSPageSize: false, displayHeaderFooter: false,
      paperWidth: WIDTH / 96, paperHeight: (height + 2) / 96,
      marginTop: 0, marginBottom: 0, marginLeft: 0, marginRight: 0, scale: 1
    });
    writeFileSync(`${outDir}/${name}.pdf`, Buffer.from(pdf.data, 'base64'));
    console.log(`${name}\t${height}px`);
    s.close(); await fetch(`http://127.0.0.1:${PORT}/json/close/${target.id}`).catch(() => {});
  }
} finally {
  chrome.kill();
}
